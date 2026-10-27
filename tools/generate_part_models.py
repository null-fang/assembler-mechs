#!/usr/bin/env python3
"""Generate Rojo .model.json mech part kits for Assembler.

Each Model is multi-Part low-poly (panels, rims, barrels, joints, feet) — never a single cube.
Parts stamp Attribute TextureRole (tools/texture_ids.json). TextureApply bakes TexturePixels
in Play when rbxassetid is empty; Texture children emit only after Studio upload fills IDs.

Local origin = socket attach point. Child named Root is PrimaryPart (set by Assembler).

Regen:
  python3 tools/generate_textures.py   # PNG + embeds + TextureIds
  python3 tools/generate_part_models.py
  python3 tools/emit_catalog_bay.py
  python3 tools/verify_part_coverage.py
  python3 tools/smoke_textured_kits.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "AssemblerAssets" / "Parts"
TEXTURE_IDS_PATH = ROOT / "tools" / "texture_ids.json"


def load_texture_ids() -> dict:
    """Shared contract with Shared.Assembler.TextureIds / TextureApply."""
    if not TEXTURE_IDS_PATH.exists():
        return {"textures": {}, "materialHints": {}, "nameHints": {}}
    return json.loads(TEXTURE_IDS_PATH.read_text(encoding="utf-8"))


TEXTURE_IDS = load_texture_ids()


def texture_role_for(name: str, material: str) -> str:
    hints = TEXTURE_IDS.get("nameHints") or {}
    # Longer prefixes first (Glow before Core so GlowCore → emissive).
    for prefix, key in sorted(hints.items(), key=lambda kv: -len(kv[0])):
        if name.startswith(prefix) or prefix in name:
            return key
    mat_hints = TEXTURE_IDS.get("materialHints") or {}
    return mat_hints.get(material, "metal_plate")


def texture_children(role: str) -> list[dict]:
    """Emit Texture instances when rbxassetid is filled in texture_ids.json."""
    defn = (TEXTURE_IDS.get("textures") or {}).get(role) or {}
    rbx = (defn.get("rbxassetid") or "").strip()
    if not rbx:
        return []
    uri = rbx if rbx.startswith("rbxassetid://") else f"rbxassetid://{rbx}"
    studs = float(defn.get("studsPerTile", 2.0))
    tr = float(defn.get("transparency", 0.35))
    kids = []
    for face in ("Front", "Top"):
        kids.append(
            {
                "Name": f"Tex_{role}_{face}",
                "ClassName": "Texture",
                "Properties": {
                    "Texture": uri,
                    "Face": face,
                    "StudsPerTileU": studs,
                    "StudsPerTileV": studs,
                    "Transparency": tr,
                    "Color3": [1.0, 1.0, 1.0],
                },
                "Attributes": {"AssemblerTexture": True, "TextureRole": role},
            }
        )
    return kids


def rgb(r: int, g: int, b: int) -> list[float]:
    return [r / 255.0, g / 255.0, b / 255.0]


def lerp_rgb(a: list[float], b: list[float], t: float) -> list[float]:
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


def darken(c: list[float], amount: float = 0.25) -> list[float]:
    return [max(0.0, x * (1.0 - amount)) for x in c]


def lighten(c: list[float], amount: float = 0.2) -> list[float]:
    return [min(1.0, x + (1.0 - x) * amount) for x in c]


def part(
    name: str,
    size: list[float],
    pos: list[float],
    *,
    color: list[float],
    material: str = "Metal",
    transparency: float | None = None,
    shape: str | None = None,
) -> dict:
    role = texture_role_for(name, material)
    props: dict = {
        "Anchored": True,
        "CanCollide": False,
        "CanQuery": False,
        "CanTouch": False,
        "CastShadow": True,
        "Size": size,
        "Position": pos,
        "Color": color,
        "Material": material,
        "TopSurface": "Smooth",
        "BottomSurface": "Smooth",
    }
    if transparency is not None:
        props["Transparency"] = transparency
    if shape is not None:
        props["Shape"] = shape
    node: dict = {
        "Name": name,
        "ClassName": "Part",
        "Properties": props,
        "Attributes": {"TextureRole": role},
    }
    kids = texture_children(role)
    if kids and name != "Root" and (transparency is None or transparency < 0.99):
        node["Children"] = kids
    return node


def wedge(
    name: str,
    size: list[float],
    cframe: list[float],
    *,
    color: list[float],
    material: str = "SmoothPlastic",
) -> dict:
    role = texture_role_for(name, material)
    node: dict = {
        "Name": name,
        "ClassName": "WedgePart",
        "Properties": {
            "Anchored": True,
            "CanCollide": False,
            "CanQuery": False,
            "CanTouch": False,
            "CastShadow": True,
            "Size": size,
            "CFrame": cframe,
            "Color": color,
            "Material": material,
            "TopSurface": "Smooth",
            "BottomSurface": "Smooth",
        },
        "Attributes": {"TextureRole": role},
    }
    kids = texture_children(role)
    if kids:
        node["Children"] = kids
    return node


def cf(pos: list[float], *, look_z: bool = True) -> list[float]:
    """CFrame at position with identity rotation (Rojo 12-float form)."""
    x, y, z = pos
    return [x, y, z, 1, 0, 0, 0, 1, 0, 0, 0, 1]


CAUTION = rgb(232, 168, 48)


def rim_front(
    base: str,
    size: list[float],
    pos: list[float],
    *,
    color: list[float],
    thickness: float = 0.1,
    material: str = "Metal",
) -> list[dict]:
    """Thin bevel rim on the +Z face — silhouette read without a flat box."""
    sx, sy, sz = size
    x, y, z = pos
    fz = z + sz / 2 + thickness / 2
    t = thickness
    rim_c = lighten(color, 0.12)
    return [
        part(f"{base}RimT", [sx + t * 2, t, t], [x, y + sy / 2, fz], color=rim_c, material=material),
        part(f"{base}RimB", [sx + t * 2, t, t], [x, y - sy / 2, fz], color=rim_c, material=material),
        part(f"{base}RimL", [t, sy, t], [x - sx / 2 - t / 2, y, fz], color=rim_c, material=material),
        part(f"{base}RimR", [t, sy, t], [x + sx / 2 + t / 2, y, fz], color=rim_c, material=material),
    ]


def inset_front(
    name: str,
    size: list[float],
    pos: list[float],
    *,
    color: list[float],
    material: str = "DiamondPlate",
    depth: float = 0.12,
    shrink: float = 0.18,
) -> dict:
    sx, sy, sz = size
    x, y, z = pos
    return part(
        name,
        [max(0.2, sx - shrink * 2), max(0.2, sy - shrink * 2), depth],
        [x, y, z + sz / 2 + depth / 2],
        color=darken(color, 0.1),
        material=material,
    )


def caution_tape(name: str, size: list[float], pos: list[float]) -> list[dict]:
    """Yellow/black hazard strip (TextureRole → hazard_stripe via nameHints)."""
    return [
        part(name, size, pos, color=CAUTION, material="SmoothPlastic"),
        part(
            name + "Blk",
            [size[0] * 0.45, size[1], size[2] * 1.05],
            [pos[0] - size[0] * 0.2, pos[1], pos[2]],
            color=rgb(24, 24, 26),
            material="SmoothPlastic",
        ),
    ]


def joint_cyl(name: str, size: list[float], pos: list[float], *, color: list[float]) -> dict:
    return part(name, size, pos, color=color, material="Metal", shape="Cylinder")


def root_marker() -> dict:
    """Tiny invisible PrimaryPart at origin."""
    return part(
        "Root",
        [0.2, 0.2, 0.2],
        [0, 0, 0],
        color=rgb(255, 255, 255),
        material="SmoothPlastic",
        transparency=1.0,
    )


def pack_model(children: list[dict]) -> dict:
    return {"ClassName": "Model", "Children": [root_marker()] + children}


def panel_safe(c: list[float]) -> list[float]:
    return darken(c, 0.12)


RARITY_RANK = {
    "Common": 0,
    "Uncommon": 1,
    "Rare": 2,
    "Epic": 3,
    "Legendary": 4,
    "Mythic": 5,
    "Blessed": 6,
    "Relic": 6,
}

import sm_builders

sm_builders.bind(
    {
        "part": part,
        "wedge": wedge,
        "cf": cf,
        "rim_front": rim_front,
        "inset_front": inset_front,
        "joint_cyl": joint_cyl,
        "rgb": rgb,
        "darken": darken,
        "lighten": lighten,
        "panel_safe": panel_safe,
        "CAUTION": CAUTION,
    }
)

# SuperMechs-inspired builders (override legacy flat-box styles)
build_torso = sm_builders.build_torso
build_leg = sm_builders.build_leg
build_lower_weapon = sm_builders.build_lower_weapon
build_shoulder_weapon = sm_builders.build_shoulder_weapon
build_battery = sm_builders.build_battery
build_cpu = sm_builders.build_cpu
build_drone = sm_builders.build_drone
build_chip = sm_builders.build_chip
rarity_trim = sm_builders.rarity_trim





# ---------------------------------------------------------------------------
# Catalog of models: id -> builder
# Colors match / extend Catalog.luau
# ---------------------------------------------------------------------------

PART_RECIPES: dict[str, tuple[str, list[float], dict]] = {}


def reg(pid: str, kind: str, color: list[float], **kwargs) -> None:
    kwargs.setdefault("rarity", "Common")
    PART_RECIPES[pid] = (kind, color, kwargs)


# Existing catalog
reg("rusty_cage", "torso", rgb(140, 96, 72), style="cage")
reg("plate_box", "torso", rgb(92, 104, 118), style="plate")
reg("tin_can", "torso", rgb(168, 174, 160), style="tin")

reg("workboot_l", "leg", rgb(78, 62, 48), style="workboot", side="l")
reg("workboot_r", "leg", rgb(78, 62, 48), style="workboot", side="r")
reg("sprint_peg_l", "leg", rgb(110, 88, 54), style="sprint", side="l")
reg("sprint_peg_r", "leg", rgb(110, 88, 54), style="sprint", side="r")
reg("stump_l", "leg", rgb(64, 58, 52), style="stump", side="l")
reg("stump_r", "leg", rgb(64, 58, 52), style="stump", side="r")

reg("snap_arm", "lower", rgb(120, 118, 110), style="snap")
reg("rivet_gun", "lower", rgb(98, 102, 108), style="rivet")
reg("ember_fist", "lower", rgb(196, 92, 42), style="ember")
reg("needle_jab", "lower", rgb(72, 160, 188), style="needle")

reg("brick_shoulder", "shoulder", rgb(108, 100, 92), style="brick")
reg("arc_rail", "shoulder", rgb(56, 140, 196), style="arc")
reg("long_bite", "shoulder", rgb(204, 78, 36), style="bite")
reg("slag_tube", "shoulder", rgb(160, 64, 40), style="slag")

reg("thick_skin", "chip", rgb(90, 120, 90), style="shield")
reg("heat_sink_chip", "chip", rgb(90, 110, 140), style="heat")
reg("wire_wrap", "chip", rgb(70, 130, 150), style="wire")
reg("grease_film", "chip", rgb(140, 130, 60), style="grease")

reg("desk_brick", "battery", rgb(48, 52, 58), style="desk")
reg("bay_cell", "battery", rgb(40, 72, 88), style="bay")
reg("deep_cell", "battery", rgb(32, 96, 110), style="deep")
reg("scrap_cpu", "cpu", rgb(60, 80, 60), style="scrap")
reg("bay_cpu", "cpu", rgb(50, 100, 70), style="bay")

reg("floor_bit", "drone", rgb(100, 90, 70), style="floor")
reg("spark_moth", "drone", rgb(180, 200, 80), style="moth")
reg("heal_beep", "drone", rgb(80, 160, 120), style="beep")

# Expanded bay — torsos
reg("rivet_crate", "torso", rgb(120, 90, 70), style="rivet")
reg("vault_hulk", "torso", rgb(70, 78, 88), style="vault")
reg("lattice_frame", "torso", rgb(100, 120, 130), style="lattice")
reg("bunker_shell", "torso", rgb(90, 88, 80), style="bunker")
reg("glass_cockpit", "torso", rgb(140, 160, 170), style="glass")
reg("scrap_weld", "torso", rgb(110, 85, 65), style="cage")
reg("iron_locker", "torso", rgb(80, 85, 95), style="vault")
reg("painted_crate", "torso", rgb(130, 110, 70), style="plate")
reg("mesh_cage", "torso", rgb(95, 100, 90), style="lattice")
reg("hot_box", "torso", rgb(150, 80, 50), style="tin")
reg("oil_drum_chest", "torso", rgb(55, 70, 55), style="tin")
reg("panel_wagon", "torso", rgb(105, 95, 85), style="plate")
reg("scaffold_cage", "torso", rgb(150, 140, 90), style="lattice")
reg("slab_fort", "torso", rgb(75, 78, 82), style="bunker")
reg("chrome_can", "torso", rgb(190, 195, 200), style="tin")
reg("bolt_bunker", "torso", rgb(95, 70, 55), style="rivet")
reg("wire_hulk", "torso", rgb(80, 95, 100), style="cage")
reg("dock_locker", "torso", rgb(60, 85, 100), style="vault")

# Legs
for side in ("l", "r"):
    reg(f"digit_{side}", "leg", rgb(85, 90, 95), style="digit", side=side)
    reg(f"piston_{side}", "leg", rgb(100, 105, 110), style="piston", side=side)
    reg(f"tread_{side}", "leg", rgb(70, 72, 68), style="tread", side=side)
    reg(f"claw_{side}", "leg", rgb(95, 70, 55), style="claw", side=side)
    reg(f"strut_{side}", "leg", rgb(120, 115, 100), style="strut", side=side)
    reg(f"mud_{side}", "leg", rgb(60, 55, 45), style="workboot", side=side)
    reg(f"needle_leg_{side}", "leg", rgb(130, 140, 150), style="sprint", side=side)
    reg(f"anvil_{side}", "leg", rgb(55, 55, 60), style="stump", side=side)

# Lower weapons
reg("cleaver_arm", "lower", rgb(140, 140, 145), style="cleaver")
reg("drill_punch", "lower", rgb(110, 100, 80), style="drill")
reg("spray_can", "lower", rgb(180, 90, 50), style="spray")
reg("hook_arm", "lower", rgb(90, 95, 100), style="hook")
reg("bolt_driver", "lower", rgb(100, 110, 120), style="rivet")
reg("slag_glove", "lower", rgb(170, 70, 40), style="ember")
reg("ice_pick", "lower", rgb(100, 160, 190), style="needle")
reg("pipe_club", "lower", rgb(115, 110, 100), style="snap")
reg("wrench_hand", "lower", rgb(130, 125, 110), style="cleaver")
reg("staplegun", "lower", rgb(85, 90, 95), style="rivet")
reg("torch_palm", "lower", rgb(210, 100, 40), style="ember")
reg("spark_probe", "lower", rgb(60, 170, 180), style="needle")

# Shoulder weapons
reg("box_launcher", "shoulder", rgb(95, 100, 90), style="box")
reg("twin_pipe", "shoulder", rgb(110, 115, 120), style="twin")
reg("mortar_pot", "shoulder", rgb(120, 80, 55), style="mortar")
reg("spear_rail", "shoulder", rgb(70, 130, 160), style="spear")
reg("scrap_cannon", "shoulder", rgb(100, 90, 80), style="brick")
reg("volt_lance", "shoulder", rgb(50, 150, 200), style="arc")
reg("furnace_spit", "shoulder", rgb(190, 70, 30), style="bite")
reg("tar_mortar", "shoulder", rgb(70, 55, 45), style="slag")
reg("nail_rack", "shoulder", rgb(120, 120, 115), style="box")
reg("dual_flare", "shoulder", rgb(180, 90, 50), style="twin")
reg("tube_howitzer", "shoulder", rgb(100, 95, 85), style="mortar")
reg("needle_pike", "shoulder", rgb(80, 140, 170), style="spear")

# Batteries / CPUs / drones / chips
reg("stack_cell", "battery", rgb(45, 60, 70), style="stack")
reg("drum_cell", "battery", rgb(35, 85, 95), style="drum")
reg("pocket_brick", "battery", rgb(55, 55, 60), style="desk")
reg("flood_pack", "battery", rgb(30, 70, 100), style="bay")
reg("optic_cpu", "cpu", rgb(40, 90, 110), style="optic")
reg("burnt_cpu", "cpu", rgb(70, 55, 45), style="scrap")
reg("clean_cpu", "cpu", rgb(55, 120, 90), style="bay")
reg("orb_drone", "drone", rgb(100, 140, 180), style="orb")
reg("spider_bit", "drone", rgb(90, 80, 70), style="spider")
reg("yard_rat", "drone", rgb(110, 95, 70), style="floor")
reg("glow_moth", "drone", rgb(200, 180, 60), style="moth")
reg("med_bubble", "drone", rgb(70, 170, 140), style="beep")
reg("chip_pad", "chip", rgb(100, 110, 90), style="skin")
reg("chip_mesh", "chip", rgb(80, 100, 130), style="heat")
reg("chip_coil", "chip", rgb(60, 140, 150), style="wire")
reg("chip_slick", "chip", rgb(150, 140, 70), style="grease")
reg("chip_plate", "chip", rgb(110, 120, 100), style="shield")
reg("chip_rust", "chip", rgb(130, 90, 70), style="skin")

# More weapons / support (deep bay)
reg("saw_arm", "lower", rgb(130, 130, 135), style="cleaver", rarity="Uncommon")
reg("ram_fist", "lower", rgb(100, 95, 90), style="snap", rarity="Uncommon")
reg("plasma_dab", "lower", rgb(90, 180, 210), style="needle", rarity="Uncommon")
reg("coal_mitt", "lower", rgb(160, 80, 40), style="ember", rarity="Uncommon")
reg("auger_bit", "lower", rgb(95, 100, 85), style="drill", rarity="Uncommon")
reg("grapple_hook", "lower", rgb(80, 85, 95), style="hook", rarity="Uncommon")
reg("foam_sprayer", "lower", rgb(160, 160, 150), style="spray", rarity="Uncommon")
reg("hammer_hand", "lower", rgb(120, 110, 100), style="snap", rarity="Uncommon")
reg("crate_mortar", "shoulder", rgb(110, 95, 70), style="mortar", rarity="Uncommon")
reg("coil_spear", "shoulder", rgb(60, 120, 170), style="spear", rarity="Uncommon")
reg("junk_box", "shoulder", rgb(90, 85, 75), style="box", rarity="Uncommon")
reg("flare_twin", "shoulder", rgb(200, 100, 50), style="twin", rarity="Uncommon")
reg("slag_brick", "shoulder", rgb(130, 70, 45), style="brick", rarity="Uncommon")
reg("arc_fork", "shoulder", rgb(70, 160, 210), style="arc", rarity="Uncommon")
reg("heat_lance", "shoulder", rgb(210, 90, 40), style="bite", rarity="Uncommon")
reg("pitch_pot", "shoulder", rgb(55, 45, 40), style="slag", rarity="Uncommon")
reg("cell_strip", "battery", rgb(40, 55, 65), style="stack", rarity="Uncommon")
reg("wet_cell", "battery", rgb(45, 90, 100), style="drum", rarity="Uncommon")
reg("junk_brick", "battery", rgb(60, 58, 55), style="desk", rarity="Uncommon")
reg("surge_pack", "battery", rgb(25, 80, 110), style="bay", rarity="Uncommon")
reg("core_cell", "battery", rgb(30, 100, 120), style="deep", rarity="Uncommon")
reg("fried_cpu", "cpu", rgb(90, 60, 50), style="scrap", rarity="Uncommon")
reg("lab_cpu", "cpu", rgb(70, 130, 110), style="bay", rarity="Uncommon")
reg("prism_cpu", "cpu", rgb(50, 100, 140), style="optic", rarity="Rare")
reg("buzz_drone", "drone", rgb(170, 160, 70), style="moth", rarity="Uncommon")
reg("crate_mite", "drone", rgb(100, 85, 65), style="floor", rarity="Uncommon")
reg("cross_beep", "drone", rgb(90, 170, 130), style="beep", rarity="Uncommon")
reg("glass_orb", "drone", rgb(120, 160, 190), style="orb", rarity="Uncommon")
reg("crawl_bit", "drone", rgb(85, 75, 65), style="spider", rarity="Uncommon")
reg("chip_foam", "chip", rgb(120, 130, 140), style="heat", rarity="Common")
reg("chip_braid", "chip", rgb(50, 130, 140), style="wire", rarity="Common")
reg("chip_oil", "chip", rgb(140, 120, 50), style="grease", rarity="Common")
reg("chip_bulk", "chip", rgb(100, 105, 95), style="shield", rarity="Common")
reg("chip_scab", "chip", rgb(120, 85, 70), style="skin", rarity="Common")

for side in ("l", "r"):
    reg(f"cargo_{side}", "leg", rgb(90, 85, 70), style="workboot", side=side, rarity="Uncommon")
    reg(f"blade_{side}", "leg", rgb(140, 145, 150), style="sprint", side=side, rarity="Uncommon")
    reg(f"block_{side}", "leg", rgb(70, 68, 65), style="stump", side=side, rarity="Uncommon")
    reg(f"grip_{side}", "leg", rgb(100, 90, 80), style="claw", side=side, rarity="Uncommon")
    reg(f"hydro_{side}", "leg", rgb(85, 100, 110), style="piston", side=side, rarity="Uncommon")

# Bay torsos (match prior Uncommon bay)
for pid, col, sty in (
    ("oil_drum_chest", rgb(55, 70, 55), "tin"),
    ("panel_wagon", rgb(105, 95, 85), "plate"),
    ("scaffold_cage", rgb(150, 140, 90), "lattice"),
    ("slab_fort", rgb(75, 78, 82), "bunker"),
    ("chrome_can", rgb(190, 195, 200), "tin"),
    ("bolt_bunker", rgb(95, 70, 55), "rivet"),
    ("wire_hulk", rgb(80, 95, 100), "cage"),
    ("dock_locker", rgb(60, 85, 100), "vault"),
):
    # already registered above without rarity — upgrade in place
    if pid in PART_RECIPES:
        kind, color, kwargs = PART_RECIPES[pid]
        kwargs["rarity"] = "Uncommon"
        PART_RECIPES[pid] = (kind, color, kwargs)

# --- Depth pass: weapons / rarities / silhouettes ---

# Torsos — wedge / rib + improved tin/vault users
reg("wedge_breast", "torso", rgb(110, 100, 90), style="wedge", rarity="Uncommon")
reg("keel_plate", "torso", rgb(85, 95, 105), style="wedge", rarity="Rare")
reg("rib_tower", "torso", rgb(120, 115, 100), style="rib", rarity="Uncommon")
reg("bone_frame", "torso", rgb(160, 155, 145), style="rib", rarity="Rare")
reg("fluted_can", "torso", rgb(150, 155, 150), style="tin", rarity="Uncommon")
reg("apron_hull", "torso", rgb(95, 88, 78), style="plate", rarity="Uncommon")
reg("spike_cage", "torso", rgb(100, 70, 55), style="cage", rarity="Rare")
reg("crest_vault", "torso", rgb(70, 75, 95), style="vault", rarity="Epic")
reg("torch_bunker", "torso", rgb(130, 75, 45), style="bunker", rarity="Rare")
reg("glass_wedge", "torso", rgb(130, 170, 185), style="glass", rarity="Epic")

# Lower — MG / beam / melee / shield
reg("chatter_gun", "lower", rgb(95, 100, 105), style="mg", rarity="Uncommon")
reg("belt_feeder", "lower", rgb(110, 105, 95), style="mg", rarity="Rare")
reg("spit_mg", "lower", rgb(80, 85, 90), style="mg", rarity="Common")
reg("ray_glove", "lower", rgb(70, 160, 200), style="beam", rarity="Rare")
reg("lens_poke", "lower", rgb(90, 140, 180), style="beam", rarity="Uncommon")
reg("pulse_mitt", "lower", rgb(140, 80, 200), style="beam", rarity="Epic")
reg("scrap_blade", "lower", rgb(140, 135, 130), style="melee", rarity="Uncommon")
reg("mace_arm", "lower", rgb(100, 95, 90), style="melee", rarity="Common")
reg("chain_flail", "lower", rgb(120, 110, 100), style="melee", rarity="Rare")
reg("spike_gaunt", "lower", rgb(90, 85, 80), style="melee", rarity="Uncommon")
reg("riot_lid", "lower", rgb(100, 105, 110), style="shield", rarity="Common")
reg("plate_guard", "lower", rgb(85, 90, 100), style="shield", rarity="Uncommon")
reg("buckler_arm", "lower", rgb(130, 120, 100), style="shield", rarity="Rare")
reg("aegis_door", "lower", rgb(70, 90, 140), style="shield", rarity="Epic")

# Shoulder — rocket / beam / MG
reg("rocket_pod", "shoulder", rgb(110, 95, 70), style="rocket", rarity="Rare")
reg("tube_swarm", "shoulder", rgb(90, 80, 65), style="rocket", rarity="Uncommon")
reg("rack_salvo", "shoulder", rgb(120, 85, 55), style="rocket", rarity="Epic")
reg("cluster_rack", "shoulder", rgb(100, 90, 75), style="rocket", rarity="Rare")
reg("hammer_rocket", "shoulder", rgb(130, 70, 50), style="rocket", rarity="Uncommon")
reg("sun_beam", "shoulder", rgb(220, 160, 50), style="beam", rarity="Epic")
reg("prism_mast", "shoulder", rgb(100, 140, 200), style="beam", rarity="Epic")
reg("frost_beam", "shoulder", rgb(100, 180, 210), style="beam", rarity="Rare")
reg("chatter_rack", "shoulder", rgb(95, 100, 105), style="mg", rarity="Uncommon")
reg("spitfire_pod", "shoulder", rgb(140, 90, 60), style="mg", rarity="Rare")
reg("gale_mg", "shoulder", rgb(80, 95, 110), style="mg", rarity="Common")
reg("belt_tower", "shoulder", rgb(105, 100, 90), style="mg", rarity="Uncommon")

# Legs — hoof / hinge pairs + improved stump users
for side in ("l", "r"):
    reg(f"hoof_{side}", "leg", rgb(95, 75, 55), style="hoof", side=side, rarity="Uncommon")
    reg(f"hinge_{side}", "leg", rgb(110, 115, 120), style="hinge", side=side, rarity="Rare")
    reg(f"pad_{side}", "leg", rgb(75, 72, 68), style="stump", side=side, rarity="Common")
    reg(f"spur_{side}", "leg", rgb(120, 90, 70), style="claw", side=side, rarity="Uncommon")
    reg(f"ski_{side}", "leg", rgb(140, 150, 160), style="sprint", side=side, rarity="Rare")

# Support kits
reg("pulse_cell", "battery", rgb(50, 80, 120), style="deep", rarity="Rare")
reg("crystal_pack", "battery", rgb(80, 60, 140), style="bay", rarity="Epic")
reg("arc_cell", "battery", rgb(40, 110, 130), style="drum", rarity="Uncommon")
reg("neural_cpu", "cpu", rgb(60, 100, 140), style="optic", rarity="Epic")
reg("fused_cpu", "cpu", rgb(90, 70, 50), style="bay", rarity="Rare")
reg("scout_mite", "drone", rgb(110, 100, 80), style="spider", rarity="Uncommon")
reg("pulse_moth", "drone", rgb(180, 120, 200), style="moth", rarity="Epic")
reg("chip_glow", "chip", rgb(140, 100, 200), style="wire", rarity="Epic")
reg("chip_vein", "chip", rgb(90, 140, 160), style="heat", rarity="Rare")
reg("chip_mirror", "chip", rgb(160, 170, 180), style="shield", rarity="Uncommon")


def trim_scale_for(kind: str) -> float:
    if kind == "torso":
        return 1.6
    if kind in ("shoulder", "lower"):
        return 1.0
    if kind == "leg":
        return 0.9
    if kind in ("battery", "drone"):
        return 0.7
    if kind == "cpu":
        return 0.45
    return 0.35  # chip


def build_children(kind: str, color: list[float], kwargs: dict) -> list[dict]:
    style = kwargs.get("style", "cage")
    if kind == "torso":
        kids = build_torso(color, style=style)
    elif kind == "leg":
        kids = build_leg(color, style=style, side=kwargs.get("side", "r"))
    elif kind == "lower":
        kids = build_lower_weapon(color, style=style)
    elif kind == "shoulder":
        kids = build_shoulder_weapon(color, style=style)
    elif kind == "battery":
        kids = build_battery(color, style=style)
    elif kind == "cpu":
        kids = build_cpu(color, style=style)
    elif kind == "drone":
        kids = build_drone(color, style=style)
    elif kind == "chip":
        kids = build_chip(color, style=style)
    else:
        raise ValueError(f"unknown kind {kind}")
    kids += rarity_trim(color, rarity=kwargs.get("rarity", "Common"), scale=trim_scale_for(kind))
    return kids


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        for p in OUT.glob("*.model.json"):
            p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    rarities: dict[str, str] = {}
    for pid, (kind, color, kwargs) in sorted(PART_RECIPES.items()):
        children = build_children(kind, color, kwargs)
        assert len(children) >= 3, f"{pid} too few parts ({len(children)})"
        write_model(OUT / f"{pid}.model.json", pack_model(children))
        counts[kind] = counts.get(kind, 0) + 1
        rarities[pid] = kwargs.get("rarity", "Common")

    # Manifest lives outside RS so Rojo does not sync it as an Instance
    manifest = {
        "count": len(PART_RECIPES),
        "byKind": counts,
        "ids": sorted(PART_RECIPES.keys()),
        "rarities": rarities,
    }
    man_path = ROOT / "tools" / "part_models_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(PART_RECIPES)} part models -> {OUT.relative_to(ROOT)}")
    print(f"manifest -> {man_path.relative_to(ROOT)}")
    for k, n in sorted(counts.items()):
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
