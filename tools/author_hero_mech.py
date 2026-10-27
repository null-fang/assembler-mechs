#!/usr/bin/env python3
"""Hand-author SuperMechs-inspired hero starter kits + AssemblerAssets showcase.

Invented silhouettes (visor hull, plant legs, gatling mitt, ridge cannon) —
inspired by SM structure, never pasted SM art.

Writes:
  src/AssemblerAssets/Showcase/HeroStarterMech.model.json
  upgrades starter Part kits used as the generator quality bar
  assets/previews/supermechs-3d-preview.png

Run after generate_part_models.py so hand kits win:
  python tools/generate_part_models.py
  python tools/author_hero_mech.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src" / "AssemblerAssets" / "Parts"
SHOWCASE = ROOT / "src" / "AssemblerAssets" / "Showcase"
PREVIEW_DIR = ROOT / "assets" / "previews"

# Combat-ready torso height (matches Sockets.TORSO_HEIGHT).
TORSO_Y = 3.85


def rgb(r: int, g: int, b: int) -> list[float]:
    return [r / 255.0, g / 255.0, b / 255.0]


def darken(c: list[float], a: float = 0.22) -> list[float]:
    return [max(0.0, x * (1.0 - a)) for x in c]


def lighten(c: list[float], a: float = 0.25) -> list[float]:
    return [min(1.0, x + (1.0 - x) * a) for x in c]


# Bold SM-like palette (original)
OLIVE = rgb(86, 124, 64)
OLIVE_LIGHT = rgb(120, 158, 90)
CHAR = rgb(42, 44, 48)
STEEL = rgb(110, 118, 128)
VISOR = rgb(40, 220, 255)
ORANGE = rgb(255, 140, 48)
RUBBER = rgb(28, 28, 30)
CANNON = rgb(72, 78, 88)


def part(
    name: str,
    size: list[float],
    pos: list[float],
    *,
    color: list[float],
    material: str = "SmoothPlastic",
    transparency: float | None = None,
    shape: str | None = None,
    role: str | None = None,
) -> dict:
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
    attrs: dict = {}
    if role:
        attrs["TextureRole"] = role
    elif material == "Neon":
        attrs["TextureRole"] = "emissive_strip"
    elif material in ("CorrodedMetal", "DiamondPlate"):
        attrs["TextureRole"] = "scratched_steel"
    elif "Rubber" in name or name.startswith("Boot") or name.startswith("Sole"):
        attrs["TextureRole"] = "matte_rubber"
    else:
        attrs["TextureRole"] = "metal_plate"
    node: dict = {"Name": name, "ClassName": "Part", "Properties": props}
    if attrs:
        node["Attributes"] = attrs
    return node


def root_marker() -> dict:
    return part("Root", [0.2, 0.2, 0.2], [0, 0, 0], color=rgb(255, 255, 255), transparency=1.0, role="matte_rubber")


def pack(children: list[dict]) -> dict:
    return {"ClassName": "Model", "Children": [root_marker()] + children}


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Hand kits (socket-local). Quality bar for generate_part_models styles.
# ---------------------------------------------------------------------------


def kit_visor_torso() -> list[dict]:
    """Top-heavy chassis + recessed emissive visor (SM torso read)."""
    return [
        part("Hull", [3.8, 2.7, 2.4], [0, 0.05, 0], color=OLIVE, material="Metal", role="metal_plate"),
        part("Dome", [3.2, 1.1, 2.0], [0, 1.35, 0.05], color=OLIVE_LIGHT, material="Metal", role="metal_plate"),
        part("VisorRecess", [2.4, 0.85, 0.35], [0, 0.55, 1.25], color=CHAR, material="Metal", role="carbon_dark"),
        part("GlowVisor", [2.15, 0.55, 0.22], [0, 0.58, 1.42], color=VISOR, material="Neon", role="emissive_strip"),
        part("CheekL", [0.75, 1.5, 1.3], [-1.85, 0.35, 0.35], color=darken(OLIVE, 0.12), material="Metal"),
        part("CheekR", [0.75, 1.5, 1.3], [1.85, 0.35, 0.35], color=darken(OLIVE, 0.12), material="Metal"),
        part("BreastPlate", [2.8, 1.35, 0.4], [0, -0.35, 1.2], color=darken(OLIVE, 0.18), material="DiamondPlate", role="scratched_steel"),
        part("AccentHazard", [2.2, 0.22, 0.18], [0, -0.85, 1.35], color=ORANGE, material="Neon", role="hazard_stripe"),
        part("HipYoke", [3.2, 0.55, 1.9], [0, -1.45, 0.05], color=STEEL, material="Metal"),
        part("PauldronL", [1.25, 0.95, 1.45], [-2.15, 1.05, 0], color=darken(OLIVE, 0.08), material="Metal"),
        part("PauldronR", [1.25, 0.95, 1.45], [2.15, 1.05, 0], color=darken(OLIVE, 0.08), material="Metal"),
        part("BackPack", [2.6, 1.7, 0.85], [0, 0.25, -1.45], color=CHAR, material="Metal", role="carbon_dark"),
        part("Thruster", [0.7, 0.7, 0.9], [0, 0.1, -2.0], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowExhaust", [0.45, 0.45, 0.35], [0, 0.1, -2.45], color=VISOR, material="Neon"),
        part("Antenna", [0.18, 1.1, 0.18], [1.1, 2.15, -0.4], color=STEEL, material="Metal"),
    ]


def kit_plant_leg(side: str) -> list[dict]:
    """Biped leg with visible joints, knee forward (combat crouch baked)."""
    s = -1.0 if side == "l" else 1.0
    return [
        part("HipBall", [1.0, 0.75, 1.0], [0.05 * s, 1.05, 0.05], color=CHAR, material="Metal", shape="Ball", role="scratched_steel"),
        part("Thigh", [1.25, 1.15, 1.35], [0.12 * s, 0.4, 0.2], color=OLIVE, material="Metal"),
        part("ThighPlate", [0.3, 0.95, 1.1], [0.75 * s, 0.4, 0.25], color=darken(OLIVE, 0.15), material="Metal"),
        part("KneeDisk", [1.15, 0.4, 1.15], [0.15 * s, -0.3, 0.55], color=STEEL, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("KneePin", [0.28, 0.7, 0.28], [0.7 * s, -0.3, 0.55], color=ORANGE, material="Neon"),
        part("Shin", [1.1, 1.25, 1.2], [0.1 * s, -1.05, 0.3], color=OLIVE, material="Metal"),
        part("ShinBrace", [0.25, 1.0, 0.55], [0.65 * s, -1.0, 0.35], color=CHAR, material="Metal"),
        part("Ankle", [1.2, 0.4, 1.15], [0.05 * s, -1.6, 0.4], color=STEEL, material="Metal"),
        part("Boot", [1.55, 0.45, 1.85], [0.05 * s, -1.95, 0.55], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("ToeLip", [1.35, 0.28, 0.45], [0.05 * s, -1.8, 1.35], color=darken(OLIVE, 0.2), material="Metal"),
        part("AccentShin", [0.2, 0.7, 0.15], [0.55 * s, -1.1, 0.85], color=VISOR, material="Neon"),
    ]


def kit_gatling_arm() -> list[dict]:
    """Forearm multi-barrel — reads as arm weapon, not a T-pose block."""
    return [
        part("Mount", [0.95, 0.75, 0.75], [0, 0, -0.85], color=CHAR, material="Metal"),
        part("Forearm", [1.05, 0.9, 1.5], [0, -0.05, 0.05], color=STEEL, material="Metal"),
        part("Receiver", [1.15, 1.0, 1.1], [0, 0.05, 0.95], color=darken(STEEL, 0.1), material="Metal"),
        part("BarrelA", [0.28, 0.28, 1.7], [-0.28, 0.2, 2.0], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelB", [0.28, 0.28, 1.7], [0.28, 0.2, 2.0], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelC", [0.28, 0.28, 1.7], [0, -0.15, 2.0], color=CHAR, material="Metal", shape="Cylinder"),
        part("CoolingJacket", [0.95, 0.95, 0.85], [0, 0.05, 1.55], color=CANNON, material="Metal", shape="Cylinder"),
        part("GlowMuzzle", [0.55, 0.55, 0.25], [0, 0.05, 2.85], color=ORANGE, material="Neon"),
        part("BeltBox", [0.7, 0.55, 0.6], [0.7, -0.15, 0.7], color=OLIVE, material="Metal"),
        part("AccentFeed", [0.18, 0.18, 0.7], [0.4, 0.15, 1.0], color=VISOR, material="Neon"),
        part("Grip", [0.4, 0.55, 0.4], [0, -0.65, 0.1], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
    ]


def kit_rivet_ready() -> list[dict]:
    """Sidearm cannon angled for ready pose."""
    return [
        part("Mount", [0.9, 0.7, 0.7], [0, 0, -0.9], color=CHAR, material="Metal"),
        part("Receiver", [1.0, 0.85, 1.55], [0, 0, 0.05], color=STEEL, material="Metal"),
        part("Barrel", [0.4, 0.4, 1.65], [0, 0.12, 1.45], color=CHAR, material="Metal", shape="Cylinder"),
        part("Mag", [0.55, 0.75, 0.45], [0, -0.6, 0.15], color=OLIVE, material="Metal"),
        part("Sight", [0.18, 0.4, 0.55], [0, 0.55, 0.5], color=VISOR, material="Neon"),
        part("Muzzle", [0.5, 0.5, 0.35], [0, 0.12, 2.25], color=ORANGE, material="Neon"),
        part("UnderRail", [0.35, 0.2, 1.0], [0, -0.35, 0.9], color=CANNON, material="Metal"),
    ]


def kit_ridge_cannon() -> list[dict]:
    """Shoulder ridge cannon — long barrel, glowing bore."""
    return [
        part("ShoulderMount", [1.3, 0.6, 1.1], [0, -0.2, -0.55], color=CHAR, material="Metal"),
        part("Breech", [1.45, 1.15, 1.5], [0, 0.25, 0.15], color=OLIVE, material="Metal"),
        part("Collar", [1.55, 0.35, 1.55], [0, 0.25, 0.85], color=STEEL, material="Metal", shape="Cylinder"),
        part("Barrel", [0.7, 0.7, 2.4], [0, 0.3, 2.0], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.95, 0.95, 1.0], [0, 0.3, 1.5], color=darken(STEEL, 0.15), material="Metal", shape="Cylinder"),
        part("GlowBore", [0.45, 0.45, 0.3], [0, 0.3, 3.2], color=VISOR, material="Neon"),
        part("FinL", [0.2, 0.7, 1.2], [-0.75, 0.55, 0.4], color=darken(OLIVE, 0.1), material="Metal"),
        part("FinR", [0.2, 0.7, 1.2], [0.75, 0.55, 0.4], color=darken(OLIVE, 0.1), material="Metal"),
        part("AccentHazard", [1.2, 0.18, 0.18], [0, -0.35, 0.5], color=ORANGE, material="Neon", role="hazard_stripe"),
        part("AmmoDrum", [0.85, 0.85, 0.85], [0.9, -0.15, -0.1], color=CHAR, material="Metal", shape="Cylinder"),
    ]


def kit_desk_battery() -> list[dict]:
    return [
        part("Cell", [1.5, 0.9, 0.65], [0, 0, 0], color=CHAR, material="Metal", role="carbon_dark"),
        part("Terminal", [0.35, 0.35, 0.25], [0.45, 0.35, 0.35], color=ORANGE, material="Neon"),
        part("Stripe", [1.2, 0.15, 0.12], [0, 0.15, 0.35], color=VISOR, material="Neon"),
        part("ClampL", [0.2, 0.7, 0.5], [-0.75, 0, 0], color=STEEL, material="Metal"),
        part("ClampR", [0.2, 0.7, 0.5], [0.75, 0, 0], color=STEEL, material="Metal"),
    ]


def kit_scrap_cpu() -> list[dict]:
    return [
        part("Board", [0.65, 0.2, 0.65], [0, 0, 0], color=OLIVE, material="Metal"),
        part("Die", [0.35, 0.25, 0.35], [0, 0.2, 0], color=CHAR, material="Metal"),
        part("GlowPin", [0.15, 0.15, 0.15], [0.2, 0.15, 0.2], color=VISOR, material="Neon"),
        part("HeatSink", [0.5, 0.2, 0.2], [0, 0.35, -0.15], color=STEEL, material="Metal"),
    ]


def kit_floor_drone() -> list[dict]:
    return [
        part("Body", [0.95, 0.45, 1.05], [0, 0, 0], color=STEEL, material="Metal"),
        part("Eye", [0.35, 0.2, 0.2], [0, 0.15, 0.5], color=VISOR, material="Neon"),
        part("Rotor", [0.7, 0.12, 0.7], [0, 0.35, -0.15], color=CHAR, material="Metal"),
        part("SkidL", [0.15, 0.2, 0.7], [-0.4, -0.3, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("SkidR", [0.15, 0.2, 0.7], [0.4, -0.3, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
    ]


def kit_chip(color: list[float], glow: list[float]) -> list[dict]:
    return [
        part("Plate", [0.45, 0.12, 0.35], [0, 0, 0], color=color, material="Metal"),
        part("GlowDot", [0.12, 0.08, 0.12], [0.12, 0.1, 0.08], color=glow, material="Neon"),
        part("Pin", [0.08, 0.08, 0.2], [-0.12, -0.02, 0], color=STEEL, material="Metal"),
    ]


# ---------------------------------------------------------------------------
# Full showcase mech (torso-local coords; feet near y=-TORSO_Y)
# Matches combat sockets: bent knees, weapons ready, feet planted.
# ---------------------------------------------------------------------------

# Socket offsets (must stay in sync with Sockets.luau combat pose)
SOCK = {
    "torso": (0.0, 0.0, 0.0),
    "hip_l": (-1.05, -1.85, 0.15),
    "hip_r": (1.05, -1.85, 0.15),
    "lower_l": (-2.15, -0.35, 0.95),
    "lower_r": (2.15, -0.35, 0.95),
    "shoulder_r": (1.75, 1.55, -0.35),
    "battery": (0.0, 0.15, -1.45),
    "cpu": (0.0, 1.15, 0.35),
    "drone": (0.35, 2.15, -1.05),
}


def offset_parts(kids: list[dict], ox: float, oy: float, oz: float, prefix: str) -> list[dict]:
    out = []
    for ch in kids:
        p = dict(ch)
        props = dict(p["Properties"])
        pos = list(props["Position"])
        props["Position"] = [pos[0] + ox, pos[1] + oy, pos[2] + oz]
        p["Properties"] = props
        p["Name"] = f"{prefix}_{ch['Name']}"
        out.append(p)
    return out


def build_showcase() -> dict:
    kids: list[dict] = []
    kids += offset_parts(kit_visor_torso(), *SOCK["torso"], "Torso")
    kids += offset_parts(kit_plant_leg("l"), *SOCK["hip_l"], "LegL")
    kids += offset_parts(kit_plant_leg("r"), *SOCK["hip_r"], "LegR")
    kids += offset_parts(kit_gatling_arm(), *SOCK["lower_l"], "ArmL")
    kids += offset_parts(kit_rivet_ready(), *SOCK["lower_r"], "ArmR")
    kids += offset_parts(kit_ridge_cannon(), *SOCK["shoulder_r"], "ShoulderR")
    kids += offset_parts(kit_desk_battery(), *SOCK["battery"], "Battery")
    kids += offset_parts(kit_scrap_cpu(), *SOCK["cpu"], "CPU")
    kids += offset_parts(kit_floor_drone(), *SOCK["drone"], "Drone")
    # Pedestal under feet for silhouette read
    kids.append(
        part(
            "ShowcasePad",
            [6.5, 0.35, 4.5],
            [0, -TORSO_Y - 0.15, 0.4],
            color=rgb(55, 58, 62),
            material="Metal",
            role="metal_plate",
        )
    )
    kids.append(
        part(
            "ShowcaseStripe",
            [5.5, 0.12, 0.25],
            [0, -TORSO_Y + 0.05, 2.4],
            color=ORANGE,
            material="Neon",
            role="hazard_stripe",
        )
    )
    model = pack(kids)
    model["Name"] = "HeroStarterMech"
    model["Attributes"] = {
        "AssemblerShowcase": True,
        "ArtBar": "SuperMechs3D",
        "Pose": "CombatReady",
    }
    return model


def write_starter_kits() -> None:
    mapping = {
        "rusty_cage": kit_visor_torso(),
        "workboot_l": kit_plant_leg("l"),
        "workboot_r": kit_plant_leg("r"),
        "snap_arm": kit_gatling_arm(),
        "rivet_gun": kit_rivet_ready(),
        "brick_shoulder": kit_ridge_cannon(),
        "desk_brick": kit_desk_battery(),
        "scrap_cpu": kit_scrap_cpu(),
        "floor_bit": kit_floor_drone(),
        "thick_skin": kit_chip(OLIVE, VISOR),
        "heat_sink_chip": kit_chip(STEEL, ORANGE),
    }
    PARTS.mkdir(parents=True, exist_ok=True)
    for pid, kids in mapping.items():
        write_model(PARTS / f"{pid}.model.json", pack(kids))
        print(f"  kit {pid}: {len(kids)} parts")


# ---------------------------------------------------------------------------
# Orthographic 3/4 preview (proves silhouette, not T-pose blob)
# ---------------------------------------------------------------------------


def render_preview(model: dict, out_path: Path) -> None:
    """True 3/4 box faces (painter) so silhouette reads as combat mech, not AABB cards."""

    def project(x: float, y: float, z: float) -> tuple[float, float, float]:
        # Front-right elevated camera
        sx = x * 0.92 - z * 0.62
        sy = y + x * 0.22 + z * 0.28
        depth = -z * 0.85 - x * 0.35 + y * 0.1
        return sx, sy, depth

    faces: list[tuple[float, list[tuple[float, float]], tuple[int, int, int], bool]] = []
    pts_x: list[float] = []
    pts_y: list[float] = []

    for ch in model.get("Children") or []:
        if ch.get("ClassName") != "Part":
            continue
        props = ch.get("Properties") or {}
        if props.get("Transparency", 0) and float(props["Transparency"]) > 0.9:
            continue
        name = ch.get("Name", "")
        if name == "Root":
            continue
        size = props["Size"]
        pos = props["Position"]
        color = props["Color"]
        hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
        # 8 corners in world
        corners_w = []
        for dx in (-hx, hx):
            for dy in (-hy, hy):
                for dz in (-hz, hz):
                    corners_w.append((pos[0] + dx, pos[1] + dy, pos[2] + dz))
        # index: 0---1  (x-, then y-, then z- / z+)
        #        |   |
        # map bits: x in {0,1}, y in {0,2}, z in {0,4} via nested loops order
        # Rebuild with explicit indices
        def corner(ix: int, iy: int, iz: int) -> tuple[float, float, float]:
            return (
                pos[0] + (-hx if ix == 0 else hx),
                pos[1] + (-hy if iy == 0 else hy),
                pos[2] + (-hz if iz == 0 else hz),
            )

        face_defs = [
            # (corners of quad, shade)
            (((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), 1.08),  # +Z front
            (((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), 0.72),  # -Z back
            (((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)), 1.18),  # +Y top
            (((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), 0.62),  # -Y bottom
            (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), 0.9),  # +X
            (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), 0.82),  # -X
        ]
        glow = ("Glow" in name) or ("Visor" in name) or ("Accent" in name)
        for idxs, shade in face_defs:
            proj = [project(*corner(*i)) for i in idxs]
            depth = sum(p[2] for p in proj) / 4.0
            poly = [(p[0], p[1]) for p in proj]
            for px, py in poly:
                pts_x.append(px)
                pts_y.append(py)
            fill = tuple(int(max(0, min(255, c * 255 * shade * (1.15 if glow else 1.0)))) for c in color)
            faces.append((depth, poly, fill, glow))

    faces.sort(key=lambda t: t[0])  # far → near

    W, H = 1200, 960
    img = Image.new("RGB", (W, H), (24, 26, 32))
    draw = ImageDraw.Draw(img)
    # bay floor wash
    draw.rectangle([0, H * 0.62, W, H], fill=(32, 34, 40))

    min_x, max_x = min(pts_x), max(pts_x)
    min_y, max_y = min(pts_y), max(pts_y)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    margin = 90
    scale = (min(W, H) - 2 * margin) / span
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    def to_screen(x: float, y: float) -> tuple[float, float]:
        return W / 2 + (x - cx) * scale, H / 2 - (y - cy) * scale * 0.98 + 20

    for _d, poly, fill, glow in faces:
        screen = [to_screen(x, y) for x, y in poly]
        draw.polygon(screen, fill=fill, outline=(14, 14, 18))
        if glow:
            # soft rim
            draw.line(screen + [screen[0]], fill=tuple(min(255, c + 40) for c in fill), width=2)

    title = "Assembler · Hero starter (SuperMechs-style 3D)"
    draw.rectangle([24, 20, 780, 78], fill=(18, 20, 24))
    try:
        font = ImageFont.truetype("arial.ttf", 26)
        font_sm = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font
    draw.text((36, 28), title, fill=(235, 240, 245), font=font)
    draw.text(
        (36, 56),
        "Combat ready · bent knees · planted feet · shoulder + arm weapons · emissive visor",
        fill=(160, 200, 210),
        font=font_sm,
    )
    draw.text(
        (36, H - 48),
        "AssemblerAssets/Showcase/HeroStarterMech  ·  quality bar for generator kits",
        fill=(140, 145, 155),
        font=font_sm,
    )
    draw.text(
        (36, H - 28),
        "Original part shapes · SM structure only (no pasted SM art)",
        fill=(110, 115, 125),
        font=font_sm,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    print(f"wrote {out_path.relative_to(ROOT)}")


def main() -> None:
    print("authoring hero starter kits + showcase…")
    write_starter_kits()
    showcase = build_showcase()
    write_model(SHOWCASE / "HeroStarterMech.model.json", showcase)
    n = len([c for c in showcase["Children"] if c.get("ClassName") == "Part"]) - 1
    print(f"  showcase HeroStarterMech: {n} visible parts")
    preview = PREVIEW_DIR / "supermechs-3d-preview.png"
    render_preview(showcase, preview)
    # also drop a copy under assets/textures for local browse
    render_preview(showcase, ROOT / "assets" / "textures" / "supermechs-3d-preview.png")
    print("done")


if __name__ == "__main__":
    main()
