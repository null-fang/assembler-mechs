#!/usr/bin/env python3
"""Hand-author SuperMechs-inspired hero starter kits + AssemblerAssets showcase.

Dense layered paneling (bolts, vents, barrels, visors, joints) — SM structure,
invented shapes. Front 3/4 combat-crouch preview.

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
OLIVE_DARK = rgb(62, 92, 48)
CHAR = rgb(42, 44, 48)
STEEL = rgb(110, 118, 128)
STEEL_DARK = rgb(72, 78, 88)
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


def bolt(name: str, pos: list[float], r: float = 0.11) -> dict:
    return part(name, [r, r, r], pos, color=STEEL_DARK, material="DiamondPlate", role="scratched_steel")


def vent(name: str, pos: list[float], size: list[float] | None = None) -> dict:
    return part(name, size or [0.12, 0.5, 0.14], pos, color=darken(CHAR, 0.1), material="Metal", role="carbon_dark")


# ---------------------------------------------------------------------------
# Dense hand kits (socket-local). Quality bar for generate_part_models styles.
# ---------------------------------------------------------------------------


def kit_visor_torso() -> list[dict]:
    """Top-heavy chassis + recessed emissive visor — layered armor, not a slab."""
    kids = [
        # Inner frame + outer hull (hull does not fill the silhouette alone)
        part("CoreFrame", [2.5, 2.1, 1.6], [0, 0.05, -0.1], color=CHAR, material="Metal", role="carbon_dark"),
        part("Hull", [3.4, 2.4, 2.15], [0, 0.08, 0.08], color=OLIVE, material="Metal", role="metal_plate"),
        part("HullSeam", [3.5, 0.1, 2.2], [0, 0.15, 0.08], color=OLIVE_DARK, material="Metal"),
        # Layered chest armor (+Z front)
        part("ChestPlateA", [2.5, 1.35, 0.32], [0, 0.25, 1.2], color=OLIVE_DARK, material="DiamondPlate", role="scratched_steel"),
        part("ChestPlateB", [2.05, 0.95, 0.28], [0, 0.35, 1.4], color=darken(OLIVE, 0.1), material="Metal"),
        part("ChestPlateC", [1.5, 0.55, 0.22], [0, 0.4, 1.55], color=CHAR, material="Metal", role="carbon_dark"),
        part("BreastLower", [2.3, 0.7, 0.3], [0, -0.45, 1.25], color=OLIVE_DARK, material="Metal"),
        part("AccentHazard", [1.9, 0.16, 0.14], [0, -0.85, 1.4], color=ORANGE, material="Neon", role="hazard_stripe"),
        # Head / visor cluster — clear front face
        part("HeadDome", [1.9, 1.15, 1.6], [0, 1.55, 0.2], color=OLIVE_LIGHT, material="Metal", role="metal_plate"),
        part("HeadCap", [1.55, 0.32, 1.25], [0, 2.2, 0.15], color=OLIVE_DARK, material="Metal"),
        part("VisorRecess", [1.85, 0.85, 0.35], [0, 1.4, 1.05], color=CHAR, material="Metal", role="carbon_dark"),
        part("GlowVisor", [1.65, 0.58, 0.28], [0, 1.4, 1.35], color=VISOR, material="Neon", role="emissive_strip"),
        part("GlowVisorCore", [0.55, 0.7, 0.2], [0, 1.4, 1.55], color=lighten(VISOR, 0.25), material="Neon", role="emissive_strip"),
        part("VisorBrow", [1.9, 0.18, 0.45], [0, 1.9, 1.0], color=STEEL, material="Metal"),
        part("VisorChin", [1.4, 0.14, 0.3], [0, 1.05, 1.2], color=STEEL_DARK, material="Metal"),
        part("GlowSlitL", [0.22, 0.4, 0.14], [-1.0, 1.35, 1.2], color=VISOR, material="Neon"),
        part("GlowSlitR", [0.22, 0.4, 0.14], [1.0, 1.35, 1.2], color=VISOR, material="Neon"),
        # Cheeks / pauldrons
        part("CheekL", [0.7, 1.4, 1.2], [-1.9, 0.4, 0.4], color=OLIVE_DARK, material="Metal"),
        part("CheekR", [0.7, 1.4, 1.2], [1.9, 0.4, 0.4], color=OLIVE_DARK, material="Metal"),
        part("CheekVentL", [0.18, 0.7, 0.7], [-2.25, 0.35, 0.5], color=CHAR, material="Metal"),
        part("CheekVentR", [0.18, 0.7, 0.7], [2.25, 0.35, 0.5], color=CHAR, material="Metal"),
        part("PauldronL", [1.2, 0.85, 1.35], [-2.2, 1.15, 0.05], color=OLIVE, material="Metal"),
        part("PauldronR", [1.2, 0.85, 1.35], [2.2, 1.15, 0.05], color=OLIVE, material="Metal"),
        part("PauldronCapL", [0.95, 0.28, 1.05], [-2.25, 1.6, 0.05], color=OLIVE_DARK, material="DiamondPlate", role="scratched_steel"),
        part("PauldronCapR", [0.95, 0.28, 1.05], [2.25, 1.6, 0.05], color=OLIVE_DARK, material="DiamondPlate", role="scratched_steel"),
        part("ShoulderPivotL", [0.65, 0.5, 0.65], [-1.95, 0.85, 0], color=STEEL, material="Metal", shape="Cylinder"),
        part("ShoulderPivotR", [0.65, 0.5, 0.65], [1.95, 0.85, 0], color=STEEL, material="Metal", shape="Cylinder"),
        # Hip / pelvis
        part("HipDisk", [0.95, 0.4, 0.95], [0, -1.2, 0.05], color=STEEL, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("HipYoke", [2.9, 0.45, 1.55], [0, -1.5, 0.1], color=STEEL, material="Metal"),
        part("PelvisPlate", [2.3, 0.28, 1.15], [0, -1.8, 0.25], color=CHAR, material="Metal"),
        part("SkirtL", [0.55, 0.75, 1.05], [-1.6, -1.4, 0.3], color=OLIVE_DARK, material="Metal"),
        part("SkirtR", [0.55, 0.75, 1.05], [1.6, -1.4, 0.3], color=OLIVE_DARK, material="Metal"),
        # Back pack with functional thrusters/vents (not a blank slab)
        part("BackPack", [2.2, 1.5, 0.7], [0, 0.3, -1.35], color=CHAR, material="Metal", role="carbon_dark"),
        part("BackPackLid", [1.9, 0.2, 0.55], [0, 1.1, -1.35], color=STEEL_DARK, material="Metal"),
        part("ThrusterL", [0.55, 0.55, 0.75], [-0.55, 0.15, -1.85], color=STEEL, material="Metal", shape="Cylinder"),
        part("ThrusterR", [0.55, 0.55, 0.75], [0.55, 0.15, -1.85], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowExhaustL", [0.32, 0.32, 0.2], [-0.55, 0.15, -2.3], color=VISOR, material="Neon"),
        part("GlowExhaustR", [0.32, 0.32, 0.2], [0.55, 0.15, -2.3], color=VISOR, material="Neon"),
        part("Antenna", [0.14, 1.05, 0.14], [1.15, 2.25, -0.35], color=STEEL, material="Metal"),
        part("AntennaTip", [0.18, 0.18, 0.18], [1.15, 2.8, -0.35], color=ORANGE, material="Neon"),
        part("SensorPod", [0.35, 0.35, 0.35], [-1.0, 2.0, 0.4], color=STEEL, material="Metal", shape="Ball"),
        part("GlowSensor", [0.18, 0.18, 0.12], [-1.0, 2.0, 0.6], color=VISOR, material="Neon"),
    ]
    # Side vents + bolts
    for i, y in enumerate((-0.2, 0.2, 0.6)):
        kids.append(vent(f"SideVentL{i}", [-1.8, y, 0.95], [0.14, 0.35, 0.12]))
        kids.append(vent(f"SideVentR{i}", [1.8, y, 0.95], [0.14, 0.35, 0.12]))
    for i, y in enumerate((0.1, 0.45, 0.8)):
        kids.append(vent(f"BackVent{i}", [-0.45 + i * 0.45, 0.55, -1.7], [0.14, 0.55, 0.12]))
    for i, p in enumerate(
        [
            [-1.2, 0.9, 1.15],
            [1.2, 0.9, 1.15],
            [-1.0, -0.4, 1.2],
            [1.0, -0.4, 1.2],
            [-0.7, 1.9, 0.75],
            [0.7, 1.9, 0.75],
            [-2.2, 1.15, 0.7],
            [2.2, 1.15, 0.7],
        ]
    ):
        kids.append(bolt(f"HullBolt{i}", p))
    return kids


def kit_plant_leg(side: str) -> list[dict]:
    """Biped leg — visible joints, knee forward combat crouch, armored panels."""
    s = -1.0 if side == "l" else 1.0
    kids = [
        part("HipBall", [0.95, 0.7, 0.95], [0.05 * s, 1.05, 0.05], color=CHAR, material="Metal", shape="Ball", role="scratched_steel"),
        part("HipPin", [0.25, 0.55, 0.25], [0.5 * s, 1.05, 0.05], color=STEEL, material="Metal", shape="Cylinder"),
        part("Thigh", [1.15, 1.05, 1.25], [0.12 * s, 0.45, 0.3], color=OLIVE, material="Metal"),
        part("ThighArmor", [1.0, 0.55, 1.0], [0.14 * s, 0.6, 0.55], color=OLIVE_DARK, material="DiamondPlate", role="scratched_steel"),
        part("ThighPlate", [0.25, 0.85, 0.95], [0.75 * s, 0.45, 0.35], color=OLIVE_DARK, material="Metal"),
        part("ThighSeam", [1.05, 0.08, 1.15], [0.12 * s, 0.2, 0.35], color=CHAR, material="Metal"),
        part("KneeDisk", [1.1, 0.38, 1.1], [0.15 * s, -0.25, 0.6], color=STEEL, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("KneeCap", [0.7, 0.45, 0.35], [0.15 * s, -0.15, 1.05], color=STEEL_DARK, material="Metal"),
        part("KneePin", [0.26, 0.65, 0.26], [0.7 * s, -0.25, 0.6], color=ORANGE, material="Neon"),
        part("Shin", [1.05, 1.2, 1.15], [0.1 * s, -1.0, 0.35], color=OLIVE, material="Metal"),
        part("ShinGuard", [0.9, 0.75, 0.35], [0.1 * s, -0.9, 0.85], color=OLIVE_DARK, material="Metal"),
        part("ShinBrace", [0.22, 0.95, 0.5], [0.65 * s, -0.95, 0.4], color=CHAR, material="Metal"),
        part("PistonRod", [0.18, 0.85, 0.18], [0.35 * s, -0.7, 0.05], color=STEEL, material="Metal", shape="Cylinder"),
        part("Ankle", [1.15, 0.35, 1.1], [0.05 * s, -1.6, 0.45], color=STEEL, material="Metal"),
        part("Boot", [1.5, 0.42, 1.8], [0.05 * s, -1.95, 0.6], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("SolePlate", [1.35, 0.12, 1.55], [0.05 * s, -2.2, 0.55], color=CHAR, material="Metal"),
        part("ToeLip", [1.3, 0.25, 0.4], [0.05 * s, -1.8, 1.4], color=OLIVE_DARK, material="Metal"),
        part("Heel", [1.05, 0.28, 0.4], [0.05 * s, -1.9, -0.2], color=STEEL_DARK, material="Metal"),
        part("AccentShin", [0.16, 0.65, 0.12], [0.55 * s, -1.05, 0.95], color=VISOR, material="Neon"),
        part("GlowAnkle", [0.22, 0.14, 0.14], [0.45 * s, -1.55, 0.9], color=ORANGE, material="Neon"),
    ]
    for i, y in enumerate((-0.85, -1.05, -1.25)):
        kids.append(vent(f"ShinVent{i}", [0.1 * s, y, 1.0], [0.55, 0.1, 0.1]))
    for i, p in enumerate(
        [
            [0.5 * s, 0.7, 0.9],
            [0.45 * s, -0.9, 0.95],
            [-0.35 * s, 0.3, 0.85],
            [0.4 * s, -1.7, 1.2],
        ]
    ):
        kids.append(bolt(f"LegBolt{i}", p))
    return kids


def kit_gatling_arm() -> list[dict]:
    """Forearm multi-barrel — dense receiver, cooling, belt feed."""
    kids = [
        part("Mount", [0.9, 0.7, 0.7], [0, 0, -0.9], color=CHAR, material="Metal"),
        part("MountCollar", [1.0, 0.22, 1.0], [0, 0, -0.55], color=STEEL, material="Metal", shape="Cylinder"),
        part("Forearm", [1.0, 0.85, 1.4], [0, -0.05, 0.05], color=STEEL, material="Metal"),
        part("ForearmPlate", [0.85, 0.55, 0.9], [0, 0.25, 0.2], color=STEEL_DARK, material="DiamondPlate", role="scratched_steel"),
        part("Receiver", [1.15, 1.0, 1.15], [0, 0.05, 1.0], color=darken(STEEL, 0.1), material="Metal"),
        part("ReceiverTop", [0.9, 0.35, 0.85], [0, 0.55, 1.05], color=OLIVE_DARK, material="Metal"),
        part("CoolingJacket", [0.95, 0.95, 0.9], [0, 0.05, 1.6], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelA", [0.26, 0.26, 1.65], [-0.28, 0.22, 2.15], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelB", [0.26, 0.26, 1.65], [0.28, 0.22, 2.15], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelC", [0.26, 0.26, 1.65], [0, -0.18, 2.15], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelD", [0.2, 0.2, 1.35], [0, 0.35, 2.0], color=STEEL_DARK, material="Metal", shape="Cylinder"),
        part("GlowMuzzleA", [0.2, 0.2, 0.14], [-0.28, 0.22, 3.0], color=ORANGE, material="Neon"),
        part("GlowMuzzleB", [0.2, 0.2, 0.14], [0.28, 0.22, 3.0], color=ORANGE, material="Neon"),
        part("GlowMuzzleC", [0.2, 0.2, 0.14], [0, -0.18, 3.0], color=ORANGE, material="Neon"),
        part("BeltBox", [0.7, 0.55, 0.6], [0.75, -0.15, 0.75], color=OLIVE, material="Metal"),
        part("BeltFeed", [0.2, 0.2, 0.75], [0.45, 0.15, 1.15], color=VISOR, material="Neon"),
        part("Mag", [0.45, 0.65, 0.4], [-0.7, -0.25, 0.85], color=CHAR, material="Metal"),
        part("Grip", [0.38, 0.55, 0.38], [0, -0.7, 0.15], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("Sight", [0.14, 0.35, 0.45], [0, 0.7, 0.55], color=STEEL, material="Metal"),
        part("GlowSight", [0.1, 0.1, 0.12], [0, 0.9, 0.7], color=VISOR, material="Neon"),
    ]
    for i, z in enumerate((0.4, 0.7, 1.0, 1.3)):
        kids.append(vent(f"CoolVent{i}", [0, 0.55, z], [0.7, 0.1, 0.1]))
    for i, p in enumerate([[-0.4, 0.35, 0.5], [0.4, 0.35, 0.5], [0, -0.35, 1.4], [0.55, 0.35, 1.3]]):
        kids.append(bolt(f"GunBolt{i}", p))
    return kids


def kit_rivet_ready() -> list[dict]:
    """Sidearm cannon — receiver panels, barrel sleeve, mag, under-rail."""
    kids = [
        part("Mount", [0.85, 0.65, 0.65], [0, 0, -0.95], color=CHAR, material="Metal"),
        part("MountCollar", [0.95, 0.2, 0.95], [0, 0, -0.6], color=STEEL, material="Metal", shape="Cylinder"),
        part("Receiver", [0.95, 0.8, 1.5], [0, 0, 0.05], color=STEEL, material="Metal"),
        part("ReceiverPlate", [0.8, 0.5, 1.0], [0, 0.3, 0.2], color=STEEL_DARK, material="DiamondPlate", role="scratched_steel"),
        part("Breech", [0.75, 0.65, 0.55], [0, 0.05, -0.55], color=CHAR, material="Metal"),
        part("Barrel", [0.38, 0.38, 1.7], [0, 0.12, 1.55], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.55, 0.55, 0.7], [0, 0.12, 0.95], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelRing", [0.5, 0.12, 0.5], [0, 0.12, 1.9], color=STEEL, material="Metal", shape="Cylinder"),
        part("Mag", [0.5, 0.7, 0.4], [0, -0.6, 0.2], color=OLIVE, material="Metal"),
        part("MagLip", [0.55, 0.12, 0.45], [0, -0.95, 0.2], color=OLIVE_DARK, material="Metal"),
        part("Sight", [0.16, 0.4, 0.5], [0, 0.55, 0.55], color=VISOR, material="Neon"),
        part("Muzzle", [0.48, 0.48, 0.28], [0, 0.12, 2.45], color=ORANGE, material="Neon"),
        part("UnderRail", [0.32, 0.18, 1.0], [0, -0.35, 0.95], color=CANNON, material="Metal"),
        part("Grip", [0.3, 0.45, 0.3], [0, -0.55, -0.25], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("AccentHazard", [0.7, 0.12, 0.12], [0, -0.35, 0.4], color=ORANGE, material="Neon", role="hazard_stripe"),
    ]
    for i, z in enumerate((0.0, 0.35, 0.7)):
        kids.append(vent(f"RecvVent{i}", [0, 0.5, z], [0.55, 0.1, 0.1]))
    for i, p in enumerate([[-0.4, 0.3, 0.4], [0.4, 0.3, 0.4], [0, -0.2, 1.3]]):
        kids.append(bolt(f"RivetBolt{i}", p))
    return kids


def kit_ridge_cannon() -> list[dict]:
    """Shoulder ridge cannon — long barrel, breech panels, ammo drum, fins."""
    kids = [
        part("ShoulderMount", [1.25, 0.55, 1.05], [0, -0.2, -0.6], color=CHAR, material="Metal"),
        part("MountBrace", [1.0, 0.25, 0.8], [0, 0.15, -0.45], color=STEEL_DARK, material="Metal"),
        part("Breech", [1.4, 1.1, 1.45], [0, 0.3, 0.2], color=OLIVE, material="Metal"),
        part("BreechPlate", [1.15, 0.7, 0.9], [0, 0.45, 0.5], color=OLIVE_DARK, material="DiamondPlate", role="scratched_steel"),
        part("Collar", [1.5, 0.32, 1.5], [0, 0.3, 0.9], color=STEEL, material="Metal", shape="Cylinder"),
        part("Barrel", [0.65, 0.65, 2.35], [0, 0.35, 2.1], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.9, 0.9, 0.95], [0, 0.35, 1.55], color=darken(STEEL, 0.15), material="Metal", shape="Cylinder"),
        part("BarrelRing", [0.8, 0.16, 0.8], [0, 0.35, 2.7], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowBore", [0.42, 0.42, 0.28], [0, 0.35, 3.3], color=VISOR, material="Neon"),
        part("FinL", [0.18, 0.7, 1.15], [-0.8, 0.6, 0.45], color=OLIVE_DARK, material="Metal"),
        part("FinR", [0.18, 0.7, 1.15], [0.8, 0.6, 0.45], color=OLIVE_DARK, material="Metal"),
        part("FinTipL", [0.14, 0.4, 0.55], [-0.85, 0.85, 0.9], color=CHAR, material="Metal"),
        part("FinTipR", [0.14, 0.4, 0.55], [0.85, 0.85, 0.9], color=CHAR, material="Metal"),
        part("AccentHazard", [1.15, 0.16, 0.16], [0, -0.35, 0.55], color=ORANGE, material="Neon", role="hazard_stripe"),
        part("AmmoDrum", [0.8, 0.8, 0.8], [0.95, -0.1, -0.05], color=CHAR, material="Metal", shape="Cylinder"),
        part("AmmoCap", [0.55, 0.2, 0.55], [0.95, 0.35, -0.05], color=STEEL, material="Metal", shape="Cylinder"),
        part("SideRail", [0.2, 0.35, 1.3], [-0.75, 0.15, 0.7], color=STEEL_DARK, material="Metal"),
    ]
    for i, z in enumerate((0.1, 0.45, 0.8)):
        kids.append(vent(f"BreechVent{i}", [0, 0.9, z], [0.9, 0.1, 0.1]))
    for i, p in enumerate([[-0.5, 0.7, 0.8], [0.5, 0.7, 0.8], [-0.55, 0.1, 1.2], [0.55, 0.1, 1.2]]):
        kids.append(bolt(f"CannonBolt{i}", p))
    return kids


def kit_desk_battery() -> list[dict]:
    return [
        part("Cell", [1.45, 0.85, 0.6], [0, 0, 0], color=CHAR, material="Metal", role="carbon_dark"),
        part("CellCap", [1.3, 0.18, 0.5], [0, 0.5, 0], color=STEEL_DARK, material="Metal"),
        part("Terminal", [0.3, 0.3, 0.22], [0.45, 0.4, 0.35], color=ORANGE, material="Neon"),
        part("TerminalNeg", [0.3, 0.3, 0.22], [-0.45, 0.4, 0.35], color=STEEL, material="Metal"),
        part("Stripe", [1.15, 0.12, 0.1], [0, 0.15, 0.35], color=VISOR, material="Neon"),
        part("ClampL", [0.18, 0.65, 0.45], [-0.75, 0, 0], color=STEEL, material="Metal"),
        part("ClampR", [0.18, 0.65, 0.45], [0.75, 0, 0], color=STEEL, material="Metal"),
        vent("BatVent0", [-0.35, -0.15, 0.35], [0.12, 0.4, 0.08]),
        vent("BatVent1", [0.0, -0.15, 0.35], [0.12, 0.4, 0.08]),
        vent("BatVent2", [0.35, -0.15, 0.35], [0.12, 0.4, 0.08]),
        bolt("BatBolt0", [-0.5, 0.3, 0.3]),
        bolt("BatBolt1", [0.5, 0.3, 0.3]),
    ]


def kit_scrap_cpu() -> list[dict]:
    return [
        part("Board", [0.7, 0.12, 0.7], [0, 0, 0], color=OLIVE_DARK, material="Metal"),
        part("Die", [0.35, 0.22, 0.35], [0, 0.18, 0], color=CHAR, material="Metal"),
        part("GlowPin", [0.14, 0.14, 0.14], [0.22, 0.14, 0.22], color=VISOR, material="Neon"),
        part("HeatSink", [0.5, 0.22, 0.22], [0, 0.35, -0.15], color=STEEL, material="Metal"),
        part("TraceA", [0.4, 0.04, 0.06], [-0.1, 0.08, 0.25], color=VISOR, material="Neon"),
        part("TraceB", [0.06, 0.04, 0.35], [0.25, 0.08, -0.05], color=VISOR, material="Neon"),
        bolt("CpuBolt0", [-0.28, 0.08, -0.28], r=0.08),
        bolt("CpuBolt1", [0.28, 0.08, -0.28], r=0.08),
    ]


def kit_floor_drone() -> list[dict]:
    return [
        part("Body", [0.95, 0.4, 1.05], [0, 0, 0], color=STEEL, material="Metal"),
        part("BodyCap", [0.75, 0.15, 0.8], [0, 0.25, 0], color=STEEL_DARK, material="Metal"),
        part("Eye", [0.35, 0.2, 0.18], [0, 0.2, 0.55], color=VISOR, material="Neon"),
        part("Rotor", [0.65, 0.1, 0.65], [0, 0.4, -0.2], color=CHAR, material="Metal"),
        part("SkidL", [0.14, 0.18, 0.7], [-0.4, -0.3, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("SkidR", [0.14, 0.18, 0.7], [0.4, -0.3, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        bolt("DroneBolt0", [-0.3, 0.15, 0.3], r=0.08),
        bolt("DroneBolt1", [0.3, 0.15, 0.3], r=0.08),
    ]


def kit_chip(color: list[float], glow: list[float]) -> list[dict]:
    return [
        part("Plate", [0.48, 0.1, 0.35], [0, 0, 0], color=color, material="Metal"),
        part("GlowDot", [0.12, 0.08, 0.12], [0.12, 0.1, 0.08], color=glow, material="Neon"),
        part("Pin", [0.08, 0.08, 0.2], [-0.12, -0.02, 0], color=STEEL, material="Metal"),
        part("Pad", [0.1, 0.06, 0.1], [0.15, 0.06, -0.1], color=STEEL_DARK, material="Metal"),
    ]


# ---------------------------------------------------------------------------
# Full showcase mech (torso-local coords; feet near y=-TORSO_Y)
# ---------------------------------------------------------------------------

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
        "Camera": "FrontThreeQuarter",
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
# Front 3/4 orthographic preview (face camera, combat crouch)
# ---------------------------------------------------------------------------


def project_front_3q(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Camera in +X/+Z quadrant looking at origin — visor (+Z) faces viewer."""
    az = math.radians(28)  # from pure front toward +X (see right side)
    el = math.radians(16)  # slight elevation
    # Camera direction from origin toward camera
    cx = math.sin(az) * math.cos(el)
    cy = math.sin(el)
    cz = math.cos(az) * math.cos(el)
    # Forward into scene (away from camera)
    fx, fy, fz = -cx, -cy, -cz
    # Right = normalize(cross(world_up, forward))
    rx, rz = fz, -fx
    rlen = math.hypot(rx, rz) or 1.0
    rx, rz = rx / rlen, rz / rlen
    ry = 0.0
    # Up = cross(forward, right)
    ux = fy * rz - fz * ry
    uy = fz * rx - fx * rz
    uz = fx * ry - fy * rx
    sx = x * rx + y * ry + z * rz
    sy = x * ux + y * uy + z * uz
    # Painter depth: larger = farther from camera
    depth = -(x * cx + y * cy + z * cz)
    return sx, sy, depth


def render_preview(model: dict, out_path: Path) -> None:
    """Front 3/4 box faces so silhouette reads as combat mech facing camera."""
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

        def corner(ix: int, iy: int, iz: int) -> tuple[float, float, float]:
            return (
                pos[0] + (-hx if ix == 0 else hx),
                pos[1] + (-hy if iy == 0 else hy),
                pos[2] + (-hz if iz == 0 else hz),
            )

        face_defs = [
            (((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), 1.12),  # +Z front
            (((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), 0.68),  # -Z back
            (((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)), 1.2),  # +Y top
            (((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), 0.58),  # -Y bottom
            (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), 0.92),  # +X
            (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), 0.8),  # -X
        ]
        glow = ("Glow" in name) or ("Visor" in name) or ("Accent" in name) or ("Muzzle" in name)
        for idxs, shade in face_defs:
            proj = [project_front_3q(*corner(*i)) for i in idxs]
            depth = sum(p[2] for p in proj) / 4.0
            # Back-face cull via projected cross
            area = (proj[1][0] - proj[0][0]) * (proj[2][1] - proj[0][1]) - (proj[2][0] - proj[0][0]) * (
                proj[1][1] - proj[0][1]
            )
            if area <= 0:
                continue
            poly = [(p[0], p[1]) for p in proj]
            for px, py in poly:
                pts_x.append(px)
                pts_y.append(py)
            fill = tuple(int(max(0, min(255, c * 255 * shade * (1.18 if glow else 1.0)))) for c in color)
            faces.append((depth, poly, fill, glow))

    faces.sort(key=lambda t: t[0])  # far → near

    W, H = 1200, 960
    img = Image.new("RGB", (W, H), (20, 24, 30))
    draw = ImageDraw.Draw(img)
    # bay floor wash
    draw.rectangle([0, int(H * 0.68), W, H], fill=(30, 34, 40))
    draw.ellipse([W * 0.15, H * 0.72, W * 0.85, H * 0.92], fill=(38, 42, 50))

    min_x, max_x = min(pts_x), max(pts_x)
    min_y, max_y = min(pts_y), max(pts_y)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    margin = 90
    scale = (min(W, H) - 2 * margin) / span
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    def to_screen(x: float, y: float) -> tuple[float, float]:
        return W / 2 + (x - cx) * scale, H / 2 - (y - cy) * scale * 0.98 + 30

    for _d, poly, fill, glow in faces:
        screen = [to_screen(x, y) for x, y in poly]
        draw.polygon(screen, fill=fill, outline=(12, 14, 18))
        if glow:
            draw.line(screen + [screen[0]], fill=tuple(min(255, c + 45) for c in fill), width=2)

    title = "Assembler · Hero starter (front 3/4 combat)"
    draw.rectangle([24, 20, 820, 78], fill=(14, 16, 20))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 26)
        font_sm = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        try:
            font = ImageFont.truetype("arial.ttf", 26)
            font_sm = ImageFont.truetype("arial.ttf", 15)
        except OSError:
            font = ImageFont.load_default()
            font_sm = font
    draw.text((36, 28), title, fill=(235, 240, 245), font=font)
    draw.text(
        (36, 56),
        "Visor forward · dense panels/bolts/vents · gatling + ridge cannon · combat crouch",
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
    try:
        print(f"wrote {out_path.relative_to(ROOT)}")
    except ValueError:
        print(f"wrote {out_path}")


def main() -> None:
    print("authoring dense hero starter kits + showcase…")
    write_starter_kits()
    showcase = build_showcase()
    write_model(SHOWCASE / "HeroStarterMech.model.json", showcase)
    n = len([c for c in showcase["Children"] if c.get("ClassName") == "Part"]) - 1
    print(f"  showcase HeroStarterMech: {n} visible parts")
    preview = PREVIEW_DIR / "supermechs-3d-preview.png"
    render_preview(showcase, preview)
    render_preview(showcase, ROOT / "assets" / "textures" / "supermechs-3d-preview.png")
    # Context media (Bob / art review)
    media = Path("/cursor/stores/bc-48ea8082-48b2-43e8-bfa6-d6d6d8d5a5a0/media/supermechs-3d-preview.png")
    render_preview(showcase, media)
    print("done")


if __name__ == "__main__":
    main()
