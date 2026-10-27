#!/usr/bin/env python3
"""Generate Rojo .model.json mech part kits for Assembler.

Each Model is multi-Part low-poly (panels, barrels, joints, feet) ΓÇö never a single cube.
Local origin = socket attach point. Child named Root is PrimaryPart (set by Assembler).

Regen: python tools/generate_part_models.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "AssemblerAssets" / "Parts"


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
    material: str = "SmoothPlastic",
    transparency: float | None = None,
    shape: str | None = None,
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
    return {"Name": name, "ClassName": "Part", "Properties": props}


def wedge(
    name: str,
    size: list[float],
    cframe: list[float],
    *,
    color: list[float],
    material: str = "SmoothPlastic",
) -> dict:
    return {
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
    }


def cf(pos: list[float], *, look_z: bool = True) -> list[float]:
    """Identity-ish CFrame at position (Rojo CFrame as 12-float row-major?).

    Rojo model.json CFrame is typically [x,y,z, R00,R01,R02, R10,R11,R12, R20,R21,R22]
    or components list. Use Position-only Parts where possible; wedges need CFrame.
    """
    # Position + identity rotation matrix (column-major as used by many Rojo dumps)
    x, y, z = pos
    return [x, y, z, 1, 0, 0, 0, 1, 0, 0, 0, 1]


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


# ---------------------------------------------------------------------------
# Geometry builders ΓÇö each returns child parts (excluding Root)
# ---------------------------------------------------------------------------


def build_torso(base: list[float], *, style: str) -> list[dict]:
    """Chassis styles: cage, plate, tin, rivet, vault, lattice, bunker, glass."""
    kids: list[dict] = []
    hull = base
    panel = darken(base, 0.18)
    accent = lighten(base, 0.35)
    vent = rgb(40, 44, 50)

    if style == "cage":
        kids += [
            part("Hull", [3.6, 2.6, 2.2], [0, 0, 0], color=hull, material="CorrodedMetal"),
            part("RibL", [0.35, 2.8, 2.4], [-1.7, 0, 0], color=panel, material="Metal"),
            part("RibR", [0.35, 2.8, 2.4], [1.7, 0, 0], color=panel, material="Metal"),
            part("ChestBar", [3.2, 0.45, 0.35], [0, 0.4, 1.15], color=accent, material="Metal"),
            part("AccentVent", [1.4, 0.9, 0.25], [0, -0.3, 1.2], color=vent, material="Metal"),
            part("HipPlate", [3.0, 0.5, 1.8], [0, -1.4, 0], color=panel, material="Metal"),
            part("ShoulderStubL", [0.8, 0.7, 1.0], [-2.0, 1.1, 0], color=hull, material="Metal"),
            part("ShoulderStubR", [0.8, 0.7, 1.0], [2.0, 1.1, 0], color=hull, material="Metal"),
            part("BackPack", [2.4, 1.6, 0.7], [0, 0.2, -1.35], color=panel, material="Metal"),
        ]
    elif style == "plate":
        kids += [
            part("Core", [3.2, 2.2, 1.9], [0, 0, 0], color=hull, material="Metal"),
            part("BreastPlate", [3.0, 1.6, 0.4], [0, 0.25, 1.2], color=panel, material="DiamondPlate"),
            part("AccentStripe", [0.3, 2.0, 0.2], [0, 0.15, 1.4], color=accent, material="Neon"),
            part("PauldronL", [1.15, 0.95, 1.3], [-2.05, 1.0, 0], color=panel, material="Metal"),
            part("PauldronR", [1.15, 0.95, 1.3], [2.05, 1.0, 0], color=panel, material="Metal"),
            part("Skirt", [3.2, 0.5, 1.8], [0, -1.4, 0.1], color=darken(hull, 0.12), material="Metal"),
            part("BackRadiator", [2.4, 1.0, 0.45], [0, 0.55, -1.25], color=vent, material="Metal"),
            part("NeckRing", [1.3, 0.3, 1.3], [0, 1.4, 0.1], color=panel, material="Metal"),
            part("SideSkirtL", [0.35, 1.4, 1.4], [-1.85, -0.2, 0], color=darken(hull, 0.08), material="Metal"),
            part("SideSkirtR", [0.35, 1.4, 1.4], [1.85, -0.2, 0], color=darken(hull, 0.08), material="Metal"),
        ]
    elif style == "tin":
        # Stacked rings + flanges — not one stretched can
        kids += [
            part("RingMid", [3.2, 1.1, 1.9], [0, 0.1, 0], color=hull, material="Metal"),
            part("RingTop", [2.9, 0.85, 1.7], [0, 1.05, 0], color=lighten(hull, 0.12), material="Metal"),
            part("RingBot", [3.0, 0.8, 1.75], [0, -0.85, 0], color=darken(hull, 0.1), material="Metal"),
            part("Cap", [2.6, 0.4, 1.5], [0, 1.6, 0], color=panel, material="Metal"),
            part("AccentBand", [3.35, 0.22, 2.0], [0, 0.35, 0], color=accent, material="Neon"),
            part("FlangeL", [0.35, 1.6, 1.4], [-1.7, 0.1, 0], color=panel, material="Metal"),
            part("FlangeR", [0.35, 1.6, 1.4], [1.7, 0.1, 0], color=panel, material="Metal"),
            part("FrontBadge", [0.9, 0.7, 0.2], [0, 0.4, 1.05], color=vent, material="SmoothPlastic"),
            part("HipSkirt", [2.8, 0.45, 1.5], [0, -1.4, 0.05], color=panel, material="Metal"),
            part("Intake", [1.4, 0.55, 0.55], [0, -0.4, -1.15], color=vent, material="Metal"),
        ]
    elif style == "wedge":
        kids += [
            part("Core", [3.0, 2.0, 1.8], [0, -0.1, 0], color=hull, material="Metal"),
            part("SlopePlate", [3.4, 0.35, 2.2], [0, 1.0, 0.15], color=panel, material="DiamondPlate"),
            part("Keel", [2.2, 0.7, 2.0], [0, -1.2, 0.2], color=darken(hull, 0.15), material="Metal"),
            part("AccentCrest", [0.3, 1.6, 0.25], [0, 0.3, 1.15], color=accent, material="Neon"),
            part("CheekL", [0.7, 1.4, 1.2], [-1.7, 0.2, 0.2], color=panel, material="Metal"),
            part("CheekR", [0.7, 1.4, 1.2], [1.7, 0.2, 0.2], color=panel, material="Metal"),
            part("Nose", [1.6, 0.9, 0.7], [0, 0.2, 1.2], color=lighten(hull, 0.1), material="Metal"),
            part("BackFin", [0.35, 1.4, 1.0], [0, 0.6, -1.2], color=vent, material="Metal"),
        ]
    elif style == "rib":
        kids += [
            part("Spine", [1.4, 2.6, 1.6], [0, 0, 0], color=hull, material="Metal"),
            part("Rib1", [3.4, 0.35, 2.0], [0, 0.8, 0], color=panel, material="Metal"),
            part("Rib2", [3.6, 0.35, 2.1], [0, 0.1, 0], color=panel, material="Metal"),
            part("Rib3", [3.2, 0.35, 1.9], [0, -0.6, 0], color=panel, material="Metal"),
            part("AccentWire", [0.15, 2.2, 0.15], [0.5, 0.1, 0.9], color=accent, material="Neon"),
            part("AccentWire2", [0.15, 2.2, 0.15], [-0.5, 0.1, 0.9], color=accent, material="Neon"),
            part("Sternum", [1.8, 1.2, 0.35], [0, 0.2, 1.1], color=darken(hull, 0.1), material="Metal"),
            part("HipYoke", [2.6, 0.5, 1.4], [0, -1.4, 0], color=panel, material="Metal"),
            part("BackCage", [2.0, 1.6, 0.5], [0, 0.2, -1.15], color=vent, material="Metal"),
        ]
    elif style == "rivet":
        kids += [
            part("Hull", [3.8, 2.7, 2.3], [0, 0, 0], color=hull, material="CorrodedMetal"),
            part("PlateA", [1.6, 1.4, 0.3], [-1.0, 0.4, 1.2], color=panel, material="Metal"),
            part("PlateB", [1.6, 1.4, 0.3], [1.0, 0.4, 1.2], color=panel, material="Metal"),
            part("AccentBoltRow", [3.0, 0.25, 0.2], [0, -0.5, 1.25], color=accent, material="Metal"),
            part("SideCageL", [0.5, 2.4, 2.0], [-2.0, 0, 0], color=darken(hull, 0.2), material="Metal"),
            part("SideCageR", [0.5, 2.4, 2.0], [2.0, 0, 0], color=darken(hull, 0.2), material="Metal"),
            part("Exhaust", [0.6, 0.6, 1.2], [0.8, 0.8, -1.5], color=vent, material="Metal"),
            part("Exhaust2", [0.6, 0.6, 1.2], [-0.8, 0.8, -1.5], color=vent, material="Metal"),
        ]
    elif style == "vault":
        # Layered safe — core + plates, not one huge diamond box
        kids += [
            part("Core", [3.2, 2.4, 2.0], [0, 0, 0], color=hull, material="Metal"),
            part("FacePlate", [2.4, 1.8, 0.35], [0, 0.15, 1.25], color=panel, material="DiamondPlate"),
            part("AccentLock", [0.45, 0.45, 0.3], [0.55, 0.15, 1.5], color=accent, material="Neon"),
            part("HingeL", [0.28, 1.8, 0.28], [-1.3, 0.15, 1.25], color=vent, material="Metal"),
            part("HingeR", [0.28, 1.8, 0.28], [1.3, 0.15, 1.25], color=vent, material="Metal"),
            part("CornerL", [0.7, 0.7, 0.7], [-1.8, 1.15, 0.9], color=panel, material="Metal"),
            part("CornerR", [0.7, 0.7, 0.7], [1.8, 1.15, 0.9], color=panel, material="Metal"),
            part("SideBoltL", [0.45, 2.0, 1.6], [-1.9, 0, 0], color=darken(hull, 0.12), material="Metal"),
            part("SideBoltR", [0.45, 2.0, 1.6], [1.9, 0, 0], color=darken(hull, 0.12), material="Metal"),
            part("BackSafe", [2.6, 1.8, 0.7], [0, 0.1, -1.35], color=darken(hull, 0.18), material="Metal"),
            part("RoofLip", [3.4, 0.35, 2.1], [0, 1.4, 0], color=panel, material="Metal"),
        ]
    elif style == "lattice":
        kids += [
            part("Core", [2.6, 2.2, 1.8], [0, 0, 0], color=hull, material="Metal"),
            part("FrameTL", [0.3, 2.8, 0.3], [-1.6, 0, -0.9], color=panel, material="Metal"),
            part("FrameTR", [0.3, 2.8, 0.3], [1.6, 0, -0.9], color=panel, material="Metal"),
            part("FrameBL", [0.3, 2.8, 0.3], [-1.6, 0, 0.9], color=panel, material="Metal"),
            part("FrameBR", [0.3, 2.8, 0.3], [1.6, 0, 0.9], color=panel, material="Metal"),
            part("Cross", [3.4, 0.25, 0.25], [0, 0.5, 0], color=accent, material="Neon"),
            part("Cross2", [0.25, 0.25, 2.2], [0, -0.4, 0], color=accent, material="Neon"),
            part("MeshPanel", [3.2, 1.0, 0.15], [0, 0.8, 1.05], color=vent, material="Metal"),
        ]
    elif style == "bunker":
        kids += [
            part("Hull", [4.4, 2.4, 2.8], [0, -0.2, 0], color=hull, material="Concrete"),
            part("SlopedCrest", [4.0, 0.8, 2.4], [0, 1.2, 0], color=panel, material="Metal"),
            part("ViewSlit", [2.0, 0.35, 0.3], [0, 0.6, 1.45], color=accent, material="Neon"),
            part("SideArmorL", [0.7, 2.2, 2.6], [-2.3, 0, 0], color=darken(hull, 0.1), material="Metal"),
            part("SideArmorR", [0.7, 2.2, 2.6], [2.3, 0, 0], color=darken(hull, 0.1), material="Metal"),
            part("TrackGuard", [4.2, 0.5, 1.2], [0, -1.4, 0.6], color=panel, material="Metal"),
            part("Antenna", [0.2, 1.4, 0.2], [1.2, 2.0, -0.6], color=vent, material="Metal"),
        ]
    else:  # glass / default light shell
        kids += [
            part("Hull", [3.6, 2.5, 2.1], [0, 0, 0], color=hull, material="Metal"),
            part("Canopy", [2.2, 1.2, 1.6], [0, 0.9, 0.5], color=lighten(base, 0.4), material="Glass", transparency=0.35),
            part("AccentRim", [2.4, 0.2, 1.8], [0, 0.35, 0.5], color=accent, material="Neon"),
            part("CheekL", [0.6, 1.0, 1.0], [-1.8, 0.5, 0.4], color=panel, material="Metal"),
            part("CheekR", [0.6, 1.0, 1.0], [1.8, 0.5, 0.4], color=panel, material="Metal"),
            part("Belly", [2.8, 0.8, 1.6], [0, -1.2, 0.2], color=panel, material="Metal"),
            part("BackFin", [0.3, 1.6, 1.2], [0, 0.8, -1.3], color=accent, material="Metal"),
        ]
    return kids


def build_leg(base: list[float], *, style: str, side: str) -> list[dict]:
    """Leg styles: workboot, sprint, stump, digit, piston, tread, claw, strut.
    Geometry is mirrored for left/right via side sign.
    """
    s = -1.0 if side == "l" else 1.0
    kids: list[dict] = []
    armor = base
    joint = darken(base, 0.25)
    accent = lighten(base, 0.3)
    sole = rgb(36, 34, 32)

    # Hip at top of leg socket (~ local 0)
    kids.append(part("HipBall", [0.9, 0.7, 0.9], [0, 1.1, 0], color=joint, material="Metal", shape="Ball"))

    if style == "workboot":
        kids += [
            part("Thigh", [1.1, 1.3, 1.2], [0.05 * s, 0.35, 0], color=armor, material="Metal"),
            part("Knee", [1.0, 0.55, 1.1], [0.1 * s, -0.4, 0.05], color=joint, material="Metal"),
            part("Shin", [1.0, 1.2, 1.15], [0.05 * s, -1.15, 0], color=armor, material="Metal"),
            part("Boot", [1.35, 0.45, 1.7], [0, -1.85, 0.25], color=sole, material="SmoothPlastic"),
            part("AccentBuckle", [0.7, 0.25, 0.2], [0.15 * s, -1.55, 0.7], color=accent, material="Neon"),
            part("AnkleGuard", [1.15, 0.35, 1.0], [0, -1.55, 0], color=darken(armor, 0.1), material="Metal"),
        ]
    elif style == "sprint":
        kids += [
            part("ThighRod", [0.55, 1.5, 0.55], [0.1 * s, 0.3, 0], color=armor, material="Metal"),
            part("KneeCam", [0.7, 0.45, 0.7], [0.15 * s, -0.55, 0], color=joint, material="Metal"),
            part("ShinRod", [0.5, 1.6, 0.5], [0.1 * s, -1.4, 0], color=armor, material="Metal"),
            part("Toe", [0.7, 0.3, 1.2], [0, -2.15, 0.35], color=sole, material="Metal"),
            part("AccentStripe", [0.2, 1.2, 0.15], [0.35 * s, 0.2, 0.25], color=accent, material="Neon"),
            part("HeelSpike", [0.35, 0.5, 0.35], [0, -2.0, -0.4], color=joint, material="Metal"),
        ]
    elif style == "stump":
        # Tapered armor stack + flared foot — not stacked cubes
        kids += [
            part("Thigh", [1.25, 1.15, 1.25], [0.05 * s, 0.4, 0], color=armor, material="CorrodedMetal"),
            part("ThighPlate", [0.25, 0.9, 1.0], [0.7 * s, 0.35, 0.1], color=panel_safe(armor), material="Metal"),
            part("KneeCap", [1.15, 0.45, 1.15], [0.08 * s, -0.3, 0.05], color=joint, material="Metal", shape="Cylinder"),
            part("Shin", [1.05, 1.05, 1.1], [0.05 * s, -1.0, 0], color=armor, material="CorrodedMetal"),
            part("Ankle", [1.2, 0.35, 1.2], [0, -1.55, 0.05], color=joint, material="Metal"),
            part("FootPad", [1.7, 0.35, 1.75], [0, -1.85, 0.2], color=sole, material="SmoothPlastic"),
            part("AccentStud", [0.35, 0.35, 0.35], [0.45 * s, -0.3, 0.65], color=accent, material="Neon"),
            part("ToeLip", [1.4, 0.3, 0.45], [0, -1.7, 0.95], color=panel_safe(armor), material="Metal"),
        ]
    elif style == "hoof":
        kids += [
            part("Thigh", [1.05, 1.2, 1.05], [0.08 * s, 0.4, 0], color=armor, material="Metal"),
            part("Knee", [0.9, 0.4, 0.9], [0.1 * s, -0.35, 0], color=joint, material="Metal"),
            part("Shin", [0.95, 1.1, 0.95], [0.08 * s, -1.05, 0], color=armor, material="Metal"),
            part("Fetlock", [1.05, 0.35, 1.0], [0, -1.6, 0.1], color=joint, material="Metal"),
            part("Hoof", [1.25, 0.4, 1.45], [0, -1.95, 0.25], color=sole, material="SmoothPlastic"),
            part("AccentCalk", [0.3, 0.25, 0.3], [0.15 * s, -2.05, 0.7], color=accent, material="Neon"),
            part("Tendon", [0.2, 1.0, 0.2], [0.5 * s, 0.05, 0.25], color=darken(armor, 0.2), material="Metal"),
        ]
    elif style == "hinge":
        kids += [
            part("Upper", [1.0, 1.1, 1.0], [0.05 * s, 0.45, 0], color=armor, material="Metal"),
            part("HingeDisk", [1.15, 0.3, 1.15], [0.1 * s, -0.2, 0], color=joint, material="Metal", shape="Cylinder"),
            part("Lower", [0.95, 1.2, 0.95], [0.05 * s, -1.0, 0], color=armor, material="Metal"),
            part("PivotPin", [0.25, 0.7, 0.25], [0.55 * s, -0.2, 0], color=accent, material="Neon"),
            part("Foot", [1.35, 0.35, 1.5], [0, -1.75, 0.2], color=sole, material="SmoothPlastic"),
            part("Heel", [0.7, 0.4, 0.5], [0, -1.7, -0.55], color=joint, material="Metal"),
            part("AccentBolt", [0.25, 0.25, 0.25], [0.35 * s, 0.5, 0.5], color=accent, material="Neon"),
        ]
    elif style == "digit":
        kids += [
            part("Thigh", [1.0, 1.2, 1.0], [0.1 * s, 0.4, 0], color=armor, material="Metal"),
            part("Knee", [0.85, 0.4, 0.85], [0.15 * s, -0.35, 0], color=joint, material="Metal"),
            part("Shin", [0.9, 1.1, 0.9], [0.1 * s, -1.05, 0], color=armor, material="Metal"),
            part("ToeMid", [0.45, 0.3, 1.0], [0, -1.7, 0.55], color=sole, material="Metal"),
            part("ToeL", [0.35, 0.25, 0.9], [-0.4, -1.65, 0.45], color=sole, material="Metal"),
            part("ToeR", [0.35, 0.25, 0.9], [0.4, -1.65, 0.45], color=sole, material="Metal"),
            part("AccentActuator", [0.25, 0.9, 0.25], [0.45 * s, 0.1, 0.3], color=accent, material="Neon"),
        ]
    elif style == "piston":
        kids += [
            part("Cylinder", [0.9, 1.8, 0.9], [0, 0.2, 0], color=armor, material="Metal", shape="Cylinder"),
            part("PistonRod", [0.35, 1.4, 0.35], [0, -1.1, 0], color=joint, material="Metal"),
            part("Foot", [1.4, 0.35, 1.5], [0, -1.9, 0.15], color=sole, material="Metal"),
            part("AccentRing", [1.05, 0.2, 1.05], [0, 0.7, 0], color=accent, material="Neon"),
            part("SideBrace", [0.25, 1.5, 0.6], [0.55 * s, 0.1, 0], color=darken(armor, 0.15), material="Metal"),
        ]
    elif style == "tread":
        kids += [
            part("Upper", [1.3, 0.9, 1.4], [0, 0.7, 0], color=armor, material="Metal"),
            part("TrackBox", [1.6, 1.4, 2.0], [0, -0.5, 0.1], color=darken(armor, 0.1), material="DiamondPlate"),
            part("WheelF", [0.5, 0.9, 0.9], [0.55 * s, -1.0, 0.7], color=joint, material="Metal", shape="Cylinder"),
            part("WheelB", [0.5, 0.9, 0.9], [0.55 * s, -1.0, -0.6], color=joint, material="Metal", shape="Cylinder"),
            part("AccentLight", [0.3, 0.3, 0.2], [0, 0.9, 0.75], color=accent, material="Neon"),
        ]
    elif style == "claw":
        kids += [
            part("Thigh", [1.15, 1.25, 1.15], [0.1 * s, 0.35, 0], color=armor, material="Metal"),
            part("Shin", [1.0, 1.15, 1.0], [0.1 * s, -1.0, 0], color=armor, material="Metal"),
            part("Palm", [1.2, 0.35, 1.0], [0, -1.7, 0.2], color=joint, material="Metal"),
            part("ClawL", [0.3, 0.3, 1.1], [-0.4, -1.75, 0.85], color=sole, material="Metal"),
            part("ClawR", [0.3, 0.3, 1.1], [0.4, -1.75, 0.85], color=sole, material="Metal"),
            part("AccentJoint", [0.5, 0.5, 0.5], [0.2 * s, -0.35, 0.4], color=accent, material="Neon"),
        ]
    else:  # strut
        kids += [
            part("StrutA", [0.4, 1.6, 0.4], [-0.25, 0.3, 0], color=armor, material="Metal"),
            part("StrutB", [0.4, 1.6, 0.4], [0.25, 0.3, 0], color=armor, material="Metal"),
            part("KneePlate", [1.1, 0.4, 0.9], [0, -0.55, 0], color=joint, material="Metal"),
            part("ShinStrut", [0.7, 1.3, 0.7], [0, -1.35, 0], color=armor, material="Metal"),
            part("Pad", [1.3, 0.3, 1.4], [0, -2.05, 0.15], color=sole, material="SmoothPlastic"),
            part("AccentWire", [0.12, 1.4, 0.12], [0.45 * s, 0.1, 0.2], color=accent, material="Neon"),
        ]
    return kids


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


def rarity_trim(base: list[float], *, rarity: str, scale: float = 1.0) -> list[dict]:
    """Extra trim density + glow accents by rarity. Glow* lights up on Epic+ at assemble."""
    rank = RARITY_RANK.get(rarity, 0)
    if rank <= 0:
        return []
    accent = lighten(base, 0.4)
    dark = darken(base, 0.3)
    s = scale
    kids: list[dict] = [
        part("AccentTrimA", [0.55 * s, 0.12 * s, 0.12 * s], [0.35 * s, 0.25 * s, 0.4 * s], color=accent, material="Neon"),
    ]
    if rank >= 2:
        kids += [
            part("AccentTrimB", [0.12 * s, 0.55 * s, 0.12 * s], [-0.4 * s, 0.1 * s, 0.35 * s], color=accent, material="Neon"),
            part("TrimStud", [0.2 * s, 0.2 * s, 0.2 * s], [0.5 * s, -0.2 * s, 0.25 * s], color=dark, material="Metal"),
            part("TrimStud2", [0.2 * s, 0.2 * s, 0.2 * s], [-0.5 * s, -0.2 * s, 0.25 * s], color=dark, material="Metal"),
        ]
    if rank >= 3:
        kids += [
            part("GlowCore", [0.35 * s, 0.35 * s, 0.35 * s], [0, 0.35 * s, 0.55 * s], color=accent, material="Neon", transparency=0.15),
            part("GlowHalo", [0.7 * s, 0.08 * s, 0.7 * s], [0, 0.45 * s, 0.2 * s], color=accent, material="Neon", transparency=0.35),
            part("AccentTrimC", [0.9 * s, 0.1 * s, 0.1 * s], [0, -0.35 * s, 0.5 * s], color=accent, material="Neon"),
        ]
    if rank >= 4:
        kids += [
            part("GlowVein", [0.1 * s, 0.8 * s, 0.1 * s], [0.45 * s, 0.1 * s, 0.15 * s], color=accent, material="Neon", transparency=0.2),
            part("AccentCrest", [0.4 * s, 0.25 * s, 0.15 * s], [0, 0.55 * s, 0.45 * s], color=lighten(accent, 0.2), material="Neon"),
        ]
    return kids


def build_lower_weapon(base: list[float], *, style: str) -> list[dict]:
    """Lower/arm weapons: snap, rivet, ember, needle, cleaver, drill, spray, hook, mg, beam, melee, shield."""
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.2)
    accent = lighten(base, 0.35)
    muzzle = rgb(30, 30, 34)

    kids.append(part("Mount", [0.9, 0.7, 0.7], [0, 0, -0.9], color=dark, material="Metal"))

    if style == "snap":
        kids += [
            part("Forearm", [0.85, 0.7, 1.4], [0, 0, -0.1], color=body, material="Metal"),
            part("Fist", [1.1, 0.95, 0.9], [0, 0, 1.0], color=dark, material="Metal"),
            part("Knuckle", [1.15, 0.35, 0.35], [0, 0.35, 1.25], color=accent, material="Neon"),
            part("Thumb", [0.35, 0.35, 0.7], [0.55, 0.1, 0.7], color=body, material="Metal"),
        ]
    elif style == "rivet":
        kids += [
            part("Receiver", [0.9, 0.75, 1.5], [0, 0, 0], color=body, material="Metal"),
            part("Barrel", [0.35, 0.35, 1.4], [0, 0.1, 1.3], color=dark, material="Metal"),
            part("Mag", [0.5, 0.7, 0.4], [0, -0.55, 0.1], color=muzzle, material="Metal"),
            part("AccentSight", [0.15, 0.35, 0.5], [0, 0.5, 0.4], color=accent, material="Neon"),
            part("Muzzle", [0.45, 0.45, 0.3], [0, 0.1, 2.0], color=muzzle, material="Metal"),
        ]
    elif style == "ember":
        kids += [
            part("Gauntlet", [1.1, 1.0, 1.3], [0, 0, 0], color=body, material="CorrodedMetal"),
            part("CoreGlow", [0.6, 0.6, 0.6], [0, 0.15, 0.5], color=accent, material="Neon"),
            part("VentL", [0.25, 0.5, 0.8], [-0.55, 0.2, 0.3], color=dark, material="Metal"),
            part("VentR", [0.25, 0.5, 0.8], [0.55, 0.2, 0.3], color=dark, material="Metal"),
            part("PunchPlate", [1.2, 1.05, 0.35], [0, 0, 1.0], color=muzzle, material="Metal"),
        ]
    elif style == "needle":
        kids += [
            part("Housing", [0.7, 0.6, 1.2], [0, 0, -0.1], color=body, material="Metal"),
            part("Needle", [0.18, 0.18, 2.0], [0, 0.05, 1.2], color=accent, material="Neon"),
            part("Coil", [0.55, 0.55, 0.55], [0, 0.05, 0.5], color=dark, material="Metal"),
            part("Guard", [0.9, 0.15, 0.9], [0, 0.4, 0], color=muzzle, material="Metal"),
        ]
    elif style == "cleaver":
        kids += [
            part("Haft", [0.45, 0.45, 1.6], [0, 0, 0], color=dark, material="Metal"),
            part("Blade", [0.15, 1.2, 1.8], [0, 0.2, 1.2], color=body, material="Metal"),
            part("AccentEdge", [0.08, 1.15, 1.7], [0.12, 0.2, 1.2], color=accent, material="Neon"),
            part("Pommel", [0.55, 0.55, 0.4], [0, 0, -1.0], color=muzzle, material="Metal"),
        ]
    elif style == "drill":
        kids += [
            part("Motor", [1.0, 0.9, 1.1], [0, 0, -0.2], color=body, material="Metal"),
            part("Bit", [0.5, 0.5, 1.6], [0, 0, 1.1], color=dark, material="Metal", shape="Cylinder"),
            part("AccentRing", [1.05, 0.2, 1.05], [0, 0, 0.4], color=accent, material="Neon"),
            part("Handle", [0.4, 0.7, 0.4], [0, -0.7, -0.3], color=muzzle, material="SmoothPlastic"),
        ]
    elif style == "spray":
        kids += [
            part("Tank", [0.95, 0.95, 1.2], [0, 0.1, -0.2], color=body, material="Metal"),
            part("Nozzle", [0.4, 0.4, 1.0], [0, 0.15, 1.0], color=dark, material="Metal"),
            part("AccentValve", [0.35, 0.35, 0.35], [0.4, 0.5, 0], color=accent, material="Neon"),
            part("Hose", [0.2, 0.2, 0.8], [0.5, -0.2, -0.6], color=muzzle, material="SmoothPlastic"),
        ]
    elif style == "mg":
        kids += [
            part("Receiver", [0.85, 0.7, 1.3], [0, 0.05, 0], color=body, material="Metal"),
            part("Barrel", [0.28, 0.28, 1.8], [0, 0.15, 1.4], color=dark, material="Metal"),
            part("CoolingJacket", [0.45, 0.45, 1.0], [0, 0.15, 0.9], color=darken(body, 0.1), material="Metal", shape="Cylinder"),
            part("BeltBox", [0.7, 0.55, 0.55], [0.55, -0.15, 0.1], color=muzzle, material="Metal"),
            part("AccentFeed", [0.2, 0.2, 0.7], [0.35, 0.05, 0.35], color=accent, material="Neon"),
            part("Grip", [0.35, 0.55, 0.35], [0, -0.55, -0.2], color=muzzle, material="SmoothPlastic"),
            part("MuzzleBrake", [0.4, 0.35, 0.35], [0, 0.15, 2.2], color=muzzle, material="Metal"),
        ]
    elif style == "beam":
        kids += [
            part("LensHousing", [0.85, 0.75, 1.1], [0, 0.1, 0], color=body, material="Metal"),
            part("Crystal", [0.45, 0.45, 0.7], [0, 0.15, 0.7], color=accent, material="Glass", transparency=0.25),
            part("Emitter", [0.35, 0.35, 0.9], [0, 0.15, 1.5], color=dark, material="Neon"),
            part("AccentBeam", [0.12, 0.12, 1.4], [0, 0.15, 1.3], color=accent, material="Neon"),
            part("FocusRing", [0.7, 0.15, 0.7], [0, 0.15, 0.35], color=muzzle, material="Metal"),
            part("Capacitor", [0.4, 0.55, 0.4], [0.5, -0.1, -0.2], color=dark, material="Metal"),
        ]
    elif style == "melee":
        kids += [
            part("Forearm", [0.8, 0.65, 1.2], [0, 0, -0.1], color=body, material="Metal"),
            part("Guard", [1.15, 0.25, 0.9], [0, 0.35, 0.5], color=dark, material="Metal"),
            part("Blade", [0.18, 0.55, 1.9], [0, 0.05, 1.4], color=lighten(body, 0.15), material="Metal"),
            part("AccentEdge", [0.08, 0.45, 1.7], [0.12, 0.05, 1.4], color=accent, material="Neon"),
            part("Spike", [0.25, 0.25, 0.7], [0, 0.35, 1.9], color=muzzle, material="Metal"),
            part("Pommel", [0.5, 0.5, 0.35], [0, 0, -0.95], color=muzzle, material="Metal"),
        ]
    elif style == "shield":
        kids += [
            part("Brace", [0.7, 0.55, 1.0], [0, 0, -0.2], color=dark, material="Metal"),
            part("Face", [1.6, 2.0, 0.25], [0, 0.15, 0.7], color=body, material="DiamondPlate"),
            part("Boss", [0.55, 0.55, 0.3], [0, 0.2, 0.9], color=dark, material="Metal"),
            part("AccentRim", [1.7, 0.15, 0.15], [0, 1.05, 0.75], color=accent, material="Neon"),
            part("AccentRimBot", [1.7, 0.15, 0.15], [0, -0.75, 0.75], color=accent, material="Neon"),
            part("LipL", [0.25, 1.6, 0.35], [-0.85, 0.15, 0.7], color=panel_safe(body), material="Metal"),
            part("LipR", [0.25, 1.6, 0.35], [0.85, 0.15, 0.7], color=panel_safe(body), material="Metal"),
        ]
    else:  # hook
        kids += [
            part("Arm", [0.7, 0.55, 1.5], [0, 0, 0], color=body, material="Metal"),
            part("HookCurve", [0.45, 0.9, 0.45], [0, 0.35, 1.1], color=dark, material="Metal"),
            part("HookTip", [0.3, 0.3, 0.8], [0, 0.7, 1.5], color=muzzle, material="Metal"),
            part("AccentChain", [0.2, 0.2, 0.9], [0, -0.35, 0.4], color=accent, material="Neon"),
        ]
    return kids


def build_shoulder_weapon(base: list[float], *, style: str) -> list[dict]:
    """Shoulder weapons: brick, arc, bite, slag, box, twin, mortar, spear, mg, beam, rocket."""
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.22)
    accent = lighten(base, 0.32)
    tip = rgb(28, 30, 34)

    kids.append(part("ShoulderMount", [1.2, 0.55, 1.0], [0, -0.15, -0.7], color=dark, material="Metal"))

    if style == "brick":
        # Broken silhouette — plates + collar instead of one concrete brick
        kids += [
            part("Breech", [1.35, 0.85, 0.9], [0, 0.1, -0.35], color=dark, material="Metal"),
            part("Receiver", [1.2, 0.7, 1.1], [0, 0.2, 0.55], color=body, material="Metal"),
            part("Barrel", [0.5, 0.5, 1.5], [0, 0.25, 1.55], color=dark, material="Metal", shape="Cylinder"),
            part("Collar", [0.85, 0.25, 0.85], [0, 0.25, 0.95], color=panel_safe(body), material="Metal"),
            part("AccentBand", [1.3, 0.18, 0.18], [0, 0.6, 0.2], color=accent, material="Neon"),
            part("SidePlateL", [0.2, 0.7, 1.0], [-0.75, 0.15, 0.2], color=panel_safe(body), material="Metal"),
            part("SidePlateR", [0.2, 0.7, 1.0], [0.75, 0.15, 0.2], color=panel_safe(body), material="Metal"),
        ]
    elif style == "arc":
        kids += [
            part("RailBody", [1.1, 0.7, 2.2], [0, 0.1, 0.4], color=body, material="Metal"),
            part("RailGlow", [0.25, 0.25, 2.4], [0, 0.35, 0.5], color=accent, material="Neon"),
            part("CoilL", [0.35, 0.55, 0.55], [-0.5, 0.15, 0.2], color=dark, material="Metal"),
            part("CoilR", [0.35, 0.55, 0.55], [0.5, 0.15, 0.2], color=dark, material="Metal"),
            part("Emitter", [0.5, 0.5, 0.4], [0, 0.15, 1.7], color=tip, material="Neon"),
        ]
    elif style == "bite":
        kids += [
            part("Tube", [1.2, 0.85, 2.4], [0, 0.1, 0.5], color=body, material="CorrodedMetal"),
            part("HeatSink", [1.4, 0.35, 1.6], [0, 0.55, 0.3], color=dark, material="Metal"),
            part("AccentGlow", [0.4, 0.4, 0.9], [0, 0.15, 1.5], color=accent, material="Neon"),
            part("MuzzleBell", [0.9, 0.9, 0.45], [0, 0.1, 1.9], color=tip, material="Metal"),
        ]
    elif style == "slag":
        kids += [
            part("Drum", [1.5, 1.2, 1.5], [0, 0.2, 0], color=body, material="CorrodedMetal"),
            part("Spout", [0.7, 0.7, 1.3], [0, 0.1, 1.2], color=dark, material="Metal"),
            part("AccentCrust", [1.0, 0.4, 0.4], [0.4, 0.6, 0.3], color=accent, material="Neon"),
            part("Support", [0.4, 0.9, 0.4], [0, -0.5, -0.2], color=tip, material="Metal"),
        ]
    elif style == "box":
        # Pod cluster instead of magazine brick
        kids += [
            part("Cradle", [1.5, 0.55, 1.2], [0, -0.05, 0], color=dark, material="Metal"),
            part("PodA", [0.55, 0.7, 1.1], [-0.45, 0.35, 0.3], color=body, material="Metal"),
            part("PodB", [0.55, 0.7, 1.1], [0.45, 0.35, 0.3], color=body, material="Metal"),
            part("Barrels", [1.1, 0.35, 1.5], [0, 0.25, 1.2], color=dark, material="Metal"),
            part("AccentPanel", [0.25, 0.7, 0.9], [0.9, 0.25, 0], color=accent, material="Neon"),
            part("Hatch", [1.0, 0.15, 0.8], [0, 0.75, 0.1], color=tip, material="Metal"),
            part("FeedBelt", [0.2, 0.2, 0.9], [0, 0.15, 0.5], color=muzzle_safe(), material="Metal"),
        ]
    elif style == "twin":
        kids += [
            part("Cradle", [1.5, 0.6, 1.2], [0, 0, 0], color=dark, material="Metal"),
            part("GunL", [0.4, 0.4, 2.2], [-0.4, 0.25, 0.7], color=body, material="Metal"),
            part("GunR", [0.4, 0.4, 2.2], [0.4, 0.25, 0.7], color=body, material="Metal"),
            part("AccentBridge", [1.0, 0.2, 0.2], [0, 0.5, 0.3], color=accent, material="Neon"),
        ]
    elif style == "mortar":
        kids += [
            part("Base", [1.4, 0.5, 1.4], [0, -0.1, 0], color=dark, material="Metal"),
            part("Tube", [0.9, 0.9, 2.0], [0, 0.5, 0.5], color=body, material="Metal", shape="Cylinder"),
            part("AccentRing", [1.05, 0.2, 1.05], [0, 0.5, 0], color=accent, material="Neon"),
            part("Bipod", [1.2, 0.7, 0.25], [0, -0.2, 0.6], color=tip, material="Metal"),
        ]
    elif style == "mg":
        kids += [
            part("Receiver", [1.2, 0.75, 1.4], [0, 0.2, 0.2], color=body, material="Metal"),
            part("Barrel", [0.32, 0.32, 2.0], [0, 0.25, 1.5], color=dark, material="Metal"),
            part("Jacket", [0.5, 0.5, 1.1], [0, 0.25, 1.0], color=darken(body, 0.12), material="Metal", shape="Cylinder"),
            part("AmmoDrum", [0.85, 0.85, 0.7], [0.7, 0.1, -0.1], color=tip, material="Metal", shape="Cylinder"),
            part("AccentFeed", [0.25, 0.25, 0.8], [0.4, 0.25, 0.3], color=accent, material="Neon"),
            part("Sight", [0.15, 0.4, 0.5], [0, 0.65, 0.4], color=tip, material="Metal"),
            part("Muzzle", [0.4, 0.4, 0.3], [0, 0.25, 2.4], color=tip, material="Metal"),
        ]
    elif style == "beam":
        kids += [
            part("Mast", [0.7, 0.7, 1.6], [0, 0.25, 0.3], color=body, material="Metal"),
            part("Lens", [0.55, 0.55, 0.55], [0, 0.3, 1.2], color=accent, material="Glass", transparency=0.2),
            part("Emitter", [0.4, 0.4, 1.0], [0, 0.3, 1.7], color=dark, material="Neon"),
            part("AccentBeam", [0.15, 0.15, 1.6], [0, 0.45, 0.9], color=accent, material="Neon"),
            part("CoilL", [0.3, 0.5, 0.5], [-0.5, 0.2, 0.1], color=dark, material="Metal"),
            part("CoilR", [0.3, 0.5, 0.5], [0.5, 0.2, 0.1], color=dark, material="Metal"),
            part("Dish", [1.1, 0.15, 1.1], [0, 0.55, 0.2], color=tip, material="Metal"),
        ]
    elif style == "rocket":
        kids += [
            part("Rack", [1.6, 0.45, 1.3], [0, 0.05, 0.1], color=dark, material="Metal"),
            part("TubeL", [0.45, 0.45, 1.8], [-0.45, 0.4, 0.5], color=body, material="Metal", shape="Cylinder"),
            part("TubeR", [0.45, 0.45, 1.8], [0.45, 0.4, 0.5], color=body, material="Metal", shape="Cylinder"),
            part("TubeMid", [0.4, 0.4, 1.5], [0, 0.75, 0.35], color=darken(body, 0.1), material="Metal", shape="Cylinder"),
            part("AccentNose", [0.25, 0.25, 0.35], [0, 0.75, 1.2], color=accent, material="Neon"),
            part("FinL", [0.15, 0.45, 0.5], [-0.75, 0.35, -0.2], color=tip, material="Metal"),
            part("FinR", [0.15, 0.45, 0.5], [0.75, 0.35, -0.2], color=tip, material="Metal"),
        ]
    else:  # spear
        kids += [
            part("Shaft", [0.35, 0.35, 2.8], [0, 0.15, 0.6], color=body, material="Metal"),
            part("Head", [0.7, 0.5, 0.9], [0, 0.2, 2.1], color=dark, material="Metal"),
            part("AccentCore", [0.25, 0.25, 1.2], [0, 0.35, 0.8], color=accent, material="Neon"),
            part("Counter", [0.6, 0.6, 0.6], [0, 0.1, -0.9], color=tip, material="Metal"),
        ]
    return kids


def muzzle_safe() -> list[float]:
    return rgb(30, 30, 34)


def build_battery(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.2)
    accent = lighten(base, 0.4)
    if style == "desk":
        kids += [
            part("Cell", [1.4, 0.85, 0.65], [0, 0, 0], color=body, material="Plastic"),
            part("Terminal+", [0.25, 0.25, 0.2], [-0.4, 0.5, 0], color=rgb(200, 60, 50), material="Neon"),
            part("Terminal-", [0.25, 0.25, 0.2], [0.4, 0.5, 0], color=rgb(50, 50, 55), material="Metal"),
            part("AccentLabel", [0.9, 0.35, 0.1], [0, 0.1, 0.35], color=accent, material="Neon"),
        ]
    elif style == "bay":
        kids += [
            part("Pack", [1.6, 1.0, 0.75], [0, 0, 0], color=body, material="Metal"),
            part("CellA", [0.4, 0.7, 0.5], [-0.45, 0, 0.15], color=dark, material="Glass", transparency=0.3),
            part("CellB", [0.4, 0.7, 0.5], [0.45, 0, 0.15], color=dark, material="Glass", transparency=0.3),
            part("AccentBus", [1.5, 0.15, 0.15], [0, 0.55, 0], color=accent, material="Neon"),
            part("Clamp", [1.7, 0.2, 0.2], [0, -0.55, 0], color=rgb(40, 40, 44), material="Metal"),
        ]
    elif style == "deep":
        kids += [
            part("Core", [1.8, 1.2, 0.85], [0, 0, 0], color=body, material="Metal"),
            part("Ring", [2.0, 0.25, 1.0], [0, 0.3, 0], color=accent, material="Neon"),
            part("CapTop", [1.5, 0.3, 0.7], [0, 0.7, 0], color=dark, material="Metal"),
            part("CapBot", [1.5, 0.3, 0.7], [0, -0.7, 0], color=dark, material="Metal"),
            part("Port", [0.4, 0.4, 0.3], [0, 0, 0.55], color=rgb(30, 80, 90), material="Neon"),
        ]
    elif style == "stack":
        kids += [
            part("Layer1", [1.5, 0.35, 0.7], [0, -0.4, 0], color=body, material="Metal"),
            part("Layer2", [1.5, 0.35, 0.7], [0, 0, 0], color=dark, material="Metal"),
            part("Layer3", [1.5, 0.35, 0.7], [0, 0.4, 0], color=body, material="Metal"),
            part("AccentStripe", [0.15, 1.1, 0.15], [0.7, 0, 0.3], color=accent, material="Neon"),
        ]
    else:  # drum
        kids += [
            part("Drum", [1.3, 1.3, 0.9], [0, 0, 0], color=body, material="Metal", shape="Cylinder"),
            part("AccentBand", [1.4, 0.2, 1.0], [0, 0.2, 0], color=accent, material="Neon"),
            part("Lid", [1.1, 0.2, 0.75], [0, 0.7, 0], color=dark, material="Metal"),
        ]
    return kids


def build_cpu(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.25)
    accent = lighten(base, 0.35)
    if style == "scrap":
        kids += [
            part("Board", [0.9, 0.12, 0.9], [0, 0, 0], color=body, material="Plastic"),
            part("Die", [0.4, 0.2, 0.4], [0, 0.15, 0], color=dark, material="Metal"),
            part("AccentPin", [0.12, 0.12, 0.12], [0.3, 0.12, 0.3], color=accent, material="Neon"),
            part("AccentPin2", [0.12, 0.12, 0.12], [-0.3, 0.12, -0.3], color=accent, material="Neon"),
        ]
    elif style == "bay":
        kids += [
            part("Board", [1.0, 0.12, 1.0], [0, 0, 0], color=body, material="Plastic"),
            part("Heatsink", [0.7, 0.35, 0.7], [0, 0.25, 0], color=dark, material="Metal"),
            part("AccentLED", [0.2, 0.1, 0.2], [0.35, 0.15, 0.35], color=accent, material="Neon"),
            part("Cap", [0.15, 0.25, 0.15], [-0.35, 0.2, 0.3], color=rgb(40, 80, 50), material="SmoothPlastic"),
        ]
    else:  # crystal / optic
        kids += [
            part("Board", [0.95, 0.12, 0.95], [0, 0, 0], color=dark, material="Plastic"),
            part("Crystal", [0.5, 0.55, 0.5], [0, 0.35, 0], color=accent, material="Glass", transparency=0.25),
            part("Frame", [0.7, 0.15, 0.7], [0, 0.1, 0], color=body, material="Metal"),
        ]
    return kids


def build_drone(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.2)
    accent = lighten(base, 0.35)
    if style == "floor":
        kids += [
            part("Chassis", [1.1, 0.4, 1.2], [0, 0, 0], color=body, material="Metal"),
            part("WheelL", [0.35, 0.55, 0.55], [-0.55, -0.15, 0.3], color=dark, material="SmoothPlastic", shape="Cylinder"),
            part("WheelR", [0.35, 0.55, 0.55], [0.55, -0.15, 0.3], color=dark, material="SmoothPlastic", shape="Cylinder"),
            part("WheelB", [0.3, 0.45, 0.45], [0, -0.1, -0.5], color=dark, material="SmoothPlastic", shape="Cylinder"),
            part("AccentEye", [0.35, 0.25, 0.2], [0, 0.25, 0.55], color=accent, material="Neon"),
        ]
    elif style == "moth":
        kids += [
            part("Body", [0.5, 0.4, 0.9], [0, 0, 0], color=body, material="SmoothPlastic"),
            part("WingL", [0.9, 0.1, 0.6], [-0.55, 0.15, 0], color=lighten(body, 0.2), material="Glass", transparency=0.3),
            part("WingR", [0.9, 0.1, 0.6], [0.55, 0.15, 0], color=lighten(body, 0.2), material="Glass", transparency=0.3),
            part("AccentSpark", [0.25, 0.25, 0.25], [0, 0.2, 0.4], color=accent, material="Neon"),
            part("Tail", [0.2, 0.2, 0.5], [0, 0, -0.6], color=dark, material="Metal"),
        ]
    elif style == "beep":
        kids += [
            part("Dome", [0.9, 0.7, 0.9], [0, 0.1, 0], color=body, material="SmoothPlastic", shape="Ball"),
            part("Base", [1.0, 0.25, 1.0], [0, -0.3, 0], color=dark, material="Metal"),
            part("AccentCross", [0.7, 0.12, 0.12], [0, 0.35, 0.35], color=accent, material="Neon"),
            part("AccentCross2", [0.12, 0.12, 0.7], [0, 0.35, 0.35], color=accent, material="Neon"),
        ]
    elif style == "orb":
        kids += [
            part("Sphere", [0.95, 0.95, 0.95], [0, 0, 0], color=body, material="Glass", transparency=0.2, shape="Ball"),
            part("Core", [0.4, 0.4, 0.4], [0, 0, 0], color=accent, material="Neon", shape="Ball"),
            part("Ring", [1.15, 0.12, 1.15], [0, 0, 0], color=dark, material="Metal"),
        ]
    else:  # spider
        kids += [
            part("Body", [0.8, 0.45, 0.9], [0, 0, 0], color=body, material="Metal"),
            part("LegFL", [0.15, 0.15, 0.7], [-0.5, -0.1, 0.4], color=dark, material="Metal"),
            part("LegFR", [0.15, 0.15, 0.7], [0.5, -0.1, 0.4], color=dark, material="Metal"),
            part("LegBL", [0.15, 0.15, 0.7], [-0.5, -0.1, -0.4], color=dark, material="Metal"),
            part("LegBR", [0.15, 0.15, 0.7], [0.5, -0.1, -0.4], color=dark, material="Metal"),
            part("AccentEye", [0.3, 0.2, 0.15], [0, 0.2, 0.45], color=accent, material="Neon"),
        ]
    return kids


def build_chip(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    body = base
    accent = lighten(base, 0.3)
    dark = darken(base, 0.25)
    kids += [
        part("Card", [0.55, 0.12, 0.4], [0, 0, 0], color=body, material="Plastic"),
        part("AccentDie", [0.22, 0.1, 0.22], [0, 0.1, 0], color=accent, material="Neon"),
    ]
    if style == "heat":
        kids.append(part("Fin", [0.45, 0.2, 0.15], [0, 0.2, 0.05], color=dark, material="Metal"))
    elif style == "wire":
        kids.append(part("Trace", [0.4, 0.05, 0.08], [0, 0.08, 0.12], color=accent, material="Neon"))
    elif style == "grease":
        kids.append(part("Blob", [0.25, 0.15, 0.25], [0.1, 0.12, 0.05], color=lighten(body, 0.15), material="SmoothPlastic"))
    elif style == "shield":
        kids.append(part("Shield", [0.35, 0.25, 0.1], [0, 0.18, 0.05], color=dark, material="Metal"))
    else:
        kids.append(part("Pad", [0.15, 0.08, 0.15], [-0.15, 0.08, 0.1], color=dark, material="Metal"))
    return kids


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
