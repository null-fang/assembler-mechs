#!/usr/bin/env python3
"""Emit CatalogBay.luau for PartIds that have AssemblerAssets models but need catalog rows.

Reads tools/part_models_manifest.json + src/Shared/Parts/Catalog.luau ids,
writes src/Shared/Parts/CatalogBay.luau with compact defs for missing ids.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "part_models_manifest.json"
CATALOG = ROOT / "src" / "Shared" / "Parts" / "Catalog.luau"
OUT = ROOT / "src" / "Shared" / "Parts" / "CatalogBay.luau"

# Kind inference from generate_part_models recipes (id patterns + known maps)
TORSO_STYLES = {
    "oil_drum_chest", "panel_wagon", "scaffold_cage", "slab_fort", "chrome_can",
    "bolt_bunker", "wire_hulk", "dock_locker",
    "wedge_breast", "keel_plate", "rib_tower", "bone_frame", "fluted_can",
    "apron_hull", "spike_cage", "crest_vault", "torch_bunker", "glass_wedge",
}
LOWER = {
    "saw_arm", "ram_fist", "plasma_dab", "coal_mitt", "auger_bit", "grapple_hook",
    "foam_sprayer", "hammer_hand",
    "chatter_gun", "belt_feeder", "spit_mg", "ray_glove", "lens_poke", "pulse_mitt",
    "scrap_blade", "mace_arm", "chain_flail", "spike_gaunt",
    "riot_lid", "plate_guard", "buckler_arm", "aegis_door",
}
SHOULDER = {
    "crate_mortar", "coil_spear", "junk_box", "flare_twin", "slag_brick",
    "arc_fork", "heat_lance", "pitch_pot",
    "rocket_pod", "tube_swarm", "rack_salvo", "cluster_rack", "hammer_rocket",
    "sun_beam", "prism_mast", "frost_beam",
    "chatter_rack", "spitfire_pod", "gale_mg", "belt_tower",
}
BATTERY = {
    "cell_strip", "wet_cell", "junk_brick", "surge_pack", "core_cell",
    "pulse_cell", "crystal_pack", "arc_cell",
}
CPU = {"fried_cpu", "lab_cpu", "prism_cpu", "neural_cpu", "fused_cpu"}
DRONE = {
    "buzz_drone", "crate_mite", "cross_beep", "glass_orb", "crawl_bit",
    "scout_mite", "pulse_moth",
}
CHIP = {
    "chip_foam", "chip_braid", "chip_oil", "chip_bulk", "chip_scab",
    "chip_glow", "chip_vein", "chip_mirror",
}

LEG_PREFIXES = (
    "cargo_", "blade_", "block_", "grip_", "hydro_",
    "hoof_", "hinge_", "pad_", "spur_", "ski_",
)

# Weapon damage / mount flavor for bay emit
LOWER_ENERGY = {"plasma_dab", "ray_glove", "lens_poke", "pulse_mitt"}
LOWER_HEAT = {"coal_mitt", "torch_palm"}
LOWER_SHIELD = {"riot_lid", "plate_guard", "buckler_arm", "aegis_door"}
SHOULDER_ENERGY = {
    "coil_spear", "arc_fork", "sun_beam", "prism_mast", "frost_beam",
}
SHOULDER_HEAT = {
    "flare_twin", "heat_lance", "pitch_pot", "crate_mortar",
    "rocket_pod", "tube_swarm", "rack_salvo", "cluster_rack", "hammer_rocket",
}

NAME_OVERRIDES = {
    "oil_drum_chest": "Oil Drum Chest",
    "panel_wagon": "Panel Wagon",
    "scaffold_cage": "Scaffold Cage",
    "slab_fort": "Slab Fort",
    "chrome_can": "Chrome Can",
    "bolt_bunker": "Bolt Bunker",
    "wire_hulk": "Wire Hulk",
    "dock_locker": "Dock Locker",
    "saw_arm": "Saw Arm",
    "ram_fist": "Ram Fist",
    "plasma_dab": "Plasma Dab",
    "coal_mitt": "Coal Mitt",
    "auger_bit": "Auger Bit",
    "grapple_hook": "Grapple Hook",
    "foam_sprayer": "Foam Sprayer",
    "hammer_hand": "Hammer Hand",
    "crate_mortar": "Crate Mortar",
    "coil_spear": "Coil Spear",
    "junk_box": "Junk Box",
    "flare_twin": "Flare Twin",
    "slag_brick": "Slag Brick",
    "arc_fork": "Arc Fork",
    "heat_lance": "Heat Lance",
    "pitch_pot": "Pitch Pot",
    "cell_strip": "Cell Strip",
    "wet_cell": "Wet Cell",
    "junk_brick": "Junk Brick",
    "surge_pack": "Surge Pack",
    "core_cell": "Core Cell",
    "fried_cpu": "Fried CPU",
    "lab_cpu": "Lab CPU",
    "prism_cpu": "Prism CPU",
    "buzz_drone": "Buzz Drone",
    "crate_mite": "Crate Mite",
    "cross_beep": "Cross Beep",
    "glass_orb": "Glass Orb",
    "crawl_bit": "Crawl Bit",
    "chip_foam": "Chip: Foam Pad",
    "chip_braid": "Chip: Braid Wrap",
    "chip_oil": "Chip: Oil Film",
    "chip_bulk": "Chip: Bulk Plate",
    "chip_scab": "Chip: Scab Seal",
    "wedge_breast": "Wedge Breast",
    "keel_plate": "Keel Plate",
    "rib_tower": "Rib Tower",
    "bone_frame": "Bone Frame",
    "fluted_can": "Fluted Can",
    "apron_hull": "Apron Hull",
    "spike_cage": "Spike Cage",
    "crest_vault": "Crest Vault",
    "torch_bunker": "Torch Bunker",
    "glass_wedge": "Glass Wedge",
    "chatter_gun": "Chatter Gun",
    "belt_feeder": "Belt Feeder",
    "spit_mg": "Spit MG",
    "ray_glove": "Ray Glove",
    "lens_poke": "Lens Poke",
    "pulse_mitt": "Pulse Mitt",
    "scrap_blade": "Scrap Blade",
    "mace_arm": "Mace Arm",
    "chain_flail": "Chain Flail",
    "spike_gaunt": "Spike Gaunt",
    "riot_lid": "Riot Lid",
    "plate_guard": "Plate Guard",
    "buckler_arm": "Buckler Arm",
    "aegis_door": "Aegis Door",
    "rocket_pod": "Rocket Pod",
    "tube_swarm": "Tube Swarm",
    "rack_salvo": "Rack Salvo",
    "cluster_rack": "Cluster Rack",
    "hammer_rocket": "Hammer Rocket",
    "sun_beam": "Sun Beam",
    "prism_mast": "Prism Mast",
    "frost_beam": "Frost Beam",
    "chatter_rack": "Chatter Rack",
    "spitfire_pod": "Spitfire Pod",
    "gale_mg": "Gale MG",
    "belt_tower": "Belt Tower",
    "pulse_cell": "Pulse Cell",
    "crystal_pack": "Crystal Pack",
    "arc_cell": "Arc Cell",
    "neural_cpu": "Neural CPU",
    "fused_cpu": "Fused CPU",
    "scout_mite": "Scout Mite",
    "pulse_moth": "Pulse Moth",
    "chip_glow": "Chip: Glow Trace",
    "chip_vein": "Chip: Vein Line",
    "chip_mirror": "Chip: Mirror Pad",
    "hoof": "Hoof",
    "hinge": "Hinge",
    "pad": "Pad",
    "spur": "Spur",
    "ski": "Ski",
}


def humanize(pid: str) -> str:
    if pid in NAME_OVERRIDES:
        return NAME_OVERRIDES[pid]
    if pid.endswith("_l"):
        return humanize(pid[:-2]) + " L"
    if pid.endswith("_r"):
        return humanize(pid[:-2]) + " R"
    return " ".join(w.capitalize() for w in pid.split("_"))


def classify(pid: str) -> str:
    if pid in TORSO_STYLES:
        return "torso"
    if pid in LOWER:
        return "lower"
    if pid in SHOULDER:
        return "shoulder"
    if pid in BATTERY:
        return "battery"
    if pid in CPU:
        return "cpu"
    if pid in DRONE:
        return "drone"
    if pid in CHIP:
        return "chip"
    for pref in LEG_PREFIXES:
        if pid.startswith(pref):
            return "leg"
    raise KeyError(pid)


def existing_ids() -> set[str]:
    text = CATALOG.read_text(encoding="utf-8")
    return set(re.findall(r"\bid\s*=\s*\"([a-z0-9_]+)\"", text))


RARITIES: dict[str, str] = {}


def rarity_of(pid: str, default: str = "Uncommon") -> str:
    return RARITIES.get(pid, default)


def torso_entry(pid: str) -> str:
    name = humanize(pid)
    rar = rarity_of(pid)
    integ = 280 if rar in ("Epic", "Legendary") else (250 if rar == "Rare" else 240)
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{name}",
\t\tslot = "Torso",
\t\trarity = "{rar}",
\t\tweight = 30,
\t\tsellWorth = 55,
\t\tlevel = 1,
\t\ttooltip = "Bay chassis kit.",
\t\tcontrib = {{ integrity = {integ}, temperatureMax = 105, cooling = 18, batteryMax = 88, batteryRegen = 12 }},
\t\tvisual = {{ color = rgb(100, 100, 100), size = Vector3.new(4.0, 3.1, 2.6) }},
\t\ttorsoStats = {{
\t\t\tintegrity = {integ},
\t\t\ttemperatureMax = 105,
\t\t\tcooling = 18,
\t\t\tbatteryMax = 88,
\t\t\tbatteryRegen = 12,
\t\t\tweightCapacity = 120,
\t\t\tresistPhysical = 5,
\t\t\tresistHeat = 4,
\t\t\tresistEnergy = 3,
\t\t}},
\t}}),"""


def leg_entry(pid: str) -> str:
    side = "LeftLeg" if pid.endswith("_l") else "RightLeg"
    variant = pid.rsplit("_", 1)[0]
    move = 3 if variant in ("blade", "hydro", "ski") else (1 if variant in ("block", "pad") else 2)
    rar = rarity_of(pid)
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "{side}",
\t\trarity = "{rar}",
\t\tweight = 10,
\t\tsellWorth = 36,
\t\tlevel = 1,
\t\ttooltip = "Matched biped kit.",
\t\tlegType = "biped",
\t\tlegVariant = "{variant}",
\t\tcontrib = {{ integrity = 7 }},
\t\tvisual = {{ color = rgb(90, 90, 90), size = Vector3.new(1.3, 2.9, 1.4) }},
\t\tlegStats = {{ moveRange = {move} }},
\t}}),"""


def lower_entry(pid: str) -> str:
    if pid in LOWER_SHIELD:
        dtype = "Physical"
        dmg = 8
        tip = "Guard. Range 1."
        rmax = 1
    elif pid in LOWER_ENERGY:
        dtype = "Energy"
        dmg = 26
        tip = "Energy. Range 1-3."
        rmax = 3
    elif pid in LOWER_HEAT:
        dtype = "Heat"
        dmg = 22
        tip = "Heat. Range 1-3."
        rmax = 3
    else:
        dtype = "Physical"
        dmg = 28
        tip = "Physical. Range 1-3."
        rmax = 3
    rar = rarity_of(pid)
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "LowerLeft",
\t\trarity = "{rar}",
\t\tweight = 9,
\t\tsellWorth = 40,
\t\tlevel = 1,
\t\ttooltip = "Lower mount weapon kit.",
\t\tmountClass = "Lower",
\t\tcontrib = {{ integrity = {"12" if pid in LOWER_SHIELD else "2"} }},
\t\tvisual = {{ color = rgb(110, 110, 110), size = Vector3.new(1.1, 1.0, 2.4) }},
\t\tweaponStats = {{
\t\t\tdamageType = "{dtype}",
\t\t\tdamage = {dmg},
\t\t\theatCost = 6,
\t\t\tbatteryCost = {0 if dtype == "Physical" else 6},
\t\t\trangeMin = 1,
\t\t\trangeMax = {rmax},
\t\t\tapCost = 1,
\t\t\ttooltip = "{tip}",
\t\t}},
\t}}),"""


def shoulder_entry(pid: str) -> str:
    if pid in SHOULDER_ENERGY:
        dtype = "Energy"
    elif pid in SHOULDER_HEAT:
        dtype = "Heat"
    else:
        dtype = "Physical"
    rar = rarity_of(pid)
    dmg = 36 if rar in ("Epic", "Legendary") else 30
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "ShoulderRight",
\t\trarity = "{rar}",
\t\tweight = 13,
\t\tsellWorth = 50,
\t\tlevel = 1,
\t\ttooltip = "Shoulder mount kit.",
\t\tmountClass = "Shoulder",
\t\tcontrib = {{ integrity = 2 }},
\t\tvisual = {{ color = rgb(100, 100, 100), size = Vector3.new(1.5, 1.1, 2.8) }},
\t\tweaponStats = {{
\t\t\tdamageType = "{dtype}",
\t\t\tdamage = {dmg},
\t\t\theatCost = 8,
\t\t\tbatteryCost = {0 if dtype == "Physical" else 10},
\t\t\trangeMin = 2,
\t\t\trangeMax = 6,
\t\t\tapCost = 1,
\t\t\ttooltip = "{dtype}. Range 2-6.",
\t\t}},
\t}}),"""


def battery_entry(pid: str) -> str:
    rar = rarity_of(pid)
    bonus = 48 if rar in ("Epic", "Legendary") else (40 if rar == "Rare" else 32)
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "Battery",
\t\trarity = "{rar}",
\t\tweight = 7,
\t\tsellWorth = 40,
\t\tlevel = 1,
\t\ttooltip = "Pack kit.",
\t\tcontrib = {{ batteryMax = {bonus}, batteryRegen = 7 }},
\t\tvisual = {{ color = rgb(40, 70, 85), size = Vector3.new(1.7, 1.1, 0.85) }},
\t\tbatteryStats = {{ batteryMaxBonus = {bonus}, batteryRegenBonus = 7 }},
\t}}),"""


def cpu_entry(pid: str) -> str:
    rar = rarity_of(pid)
    tier = 4 if pid == "neural_cpu" else (3 if pid in ("prism_cpu", "fused_cpu") else (2 if pid == "lab_cpu" else 1))
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "CPU",
\t\trarity = "{rar}",
\t\tweight = 3,
\t\tsellWorth = 30,
\t\tlevel = 1,
\t\ttooltip = "Board kit.",
\t\tcontrib = {{ cooling = {tier} }},
\t\tvisual = {{ color = rgb(60, 90, 80), size = Vector3.new(0.85, 0.4, 0.85) }},
\t\tcpuStats = {{ tier = {tier} }},
\t}}),"""


def drone_entry(pid: str) -> str:
    dtype = "Energy" if pid in ("buzz_drone", "glass_orb", "pulse_moth") else ("Heat" if pid == "cross_beep" else "Physical")
    rar = rarity_of(pid)
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "Drone",
\t\trarity = "{rar}",
\t\tweight = 5,
\t\tsellWorth = 40,
\t\tlevel = 1,
\t\ttooltip = "Drone kit.",
\t\tcontrib = {{ integrity = 2 }},
\t\tvisual = {{ color = rgb(100, 110, 100), size = Vector3.new(1.1, 0.7, 1.2) }},
\t\tdroneStats = {{
\t\t\tdamageType = "{dtype}",
\t\t\tdamage = 12,
\t\t\theatCost = 1,
\t\t\tbatteryCost = 3,
\t\t\trangeMax = 4,
\t\t\ttooltip = "End of turn. {dtype}. Range <=4.",
\t\t}},
\t}}),"""


def chip_entry(pid: str) -> str:
    rar = rarity_of(pid, "Common")
    return f"""\t{pid} = part({{
\t\tid = "{pid}",
\t\tname = "{humanize(pid)}",
\t\tslot = "Chip",
\t\trarity = "{rar}",
\t\tweight = 2,
\t\tsellWorth = 18,
\t\tlevel = 1,
\t\ttooltip = "Chip kit.",
\t\tcontrib = {{ integrity = 10 }},
\t\tvisual = {{ color = rgb(100, 110, 100) }},
\t\tchipStats = {{ resistPhysical = 4, integrityBonus = 10 }},
\t}}),"""


EMITTERS = {
    "torso": torso_entry,
    "leg": leg_entry,
    "lower": lower_entry,
    "shoulder": shoulder_entry,
    "battery": battery_entry,
    "cpu": cpu_entry,
    "drone": drone_entry,
    "chip": chip_entry,
}


def main() -> None:
    global RARITIES
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    RARITIES = dict(manifest.get("rarities") or {})
    have = existing_ids()
    missing = sorted(pid for pid in manifest["ids"] if pid not in have)
    blocks = []
    for pid in missing:
        kind = classify(pid)
        blocks.append(EMITTERS[kind](pid))

    body = "\n".join(blocks)
    text = f"""-- Auto-generated bay expansion (tools/emit_catalog_bay.py).
-- Merged into Catalog.parts at load. Do not hand-edit bulk rows; regen instead.

local Types = require(script.Parent.Parent.Combat.Types)

export type BayPart = {{
\tid: string,
\tname: string,
\tslot: string,
\trarity: string,
\tweight: number,
\tsellWorth: number,
\tlevel: number?,
\ttooltip: string?,
\tcontrib: {{ [string]: number }}?,
\tvisual: {{ color: Color3, size: Vector3? }}?,
\tlegType: string?,
\tlegVariant: string?,
\tmountClass: string?,
\ttorsoStats: {{ [string]: number }}?,
\tlegStats: {{ moveRange: number }}?,
\tweaponStats: Types.WeaponStats?,
\tchipStats: {{ [string]: number }}?,
\tbatteryStats: {{ batteryMaxBonus: number, batteryRegenBonus: number }}?,
\tcpuStats: {{ tier: number }}?,
\tdroneStats: Types.DroneStats?,
}}

local function rgb(r: number, g: number, b: number): Color3
\treturn Color3.fromRGB(r, g, b)
end

local function part(def: BayPart): BayPart
\treturn def
end

local CatalogBay = {{}}

CatalogBay.parts = {{
{body}
}} :: {{ [string]: BayPart }}

return CatalogBay
"""
    OUT.write_text(text.replace("\\t", "\t"), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(missing)} parts)")


if __name__ == "__main__":
    main()
