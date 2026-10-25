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
            part("Hull", [4.0, 2.8, 2.4], [0, 0, 0], color=hull, material="Metal"),
            part("BreastPlate", [3.4, 1.8, 0.4], [0, 0.2, 1.3], color=panel, material="DiamondPlate"),
            part("AccentStripe", [0.35, 2.4, 0.2], [0, 0.1, 1.45], color=accent, material="Neon"),
            part("PauldronL", [1.2, 1.0, 1.4], [-2.2, 1.0, 0], color=panel, material="Metal"),
            part("PauldronR", [1.2, 1.0, 1.4], [2.2, 1.0, 0], color=panel, material="Metal"),
            part("Skirt", [3.6, 0.6, 2.0], [0, -1.5, 0.1], color=darken(hull, 0.12), material="Metal"),
            part("BackRadiator", [2.8, 1.2, 0.5], [0, 0.6, -1.4], color=vent, material="Metal"),
            part("NeckRing", [1.4, 0.35, 1.4], [0, 1.55, 0.1], color=panel, material="Metal"),
        ]
    elif style == "tin":
        kids += [
            part("Hull", [3.4, 2.4, 2.0], [0, 0, 0], color=hull, material="Metal"),
            part("Cap", [3.0, 0.5, 1.8], [0, 1.35, 0], color=lighten(hull, 0.15), material="Metal"),
            part("AccentBand", [3.5, 0.3, 2.1], [0, 0.2, 0], color=accent, material="Neon"),
            part("CanSeamL", [0.15, 2.2, 1.9], [-1.65, 0, 0], color=panel, material="Metal"),
            part("CanSeamR", [0.15, 2.2, 1.9], [1.65, 0, 0], color=panel, material="Metal"),
            part("FrontLogo", [1.0, 1.0, 0.2], [0, 0.3, 1.1], color=vent, material="SmoothPlastic"),
            part("HipRing", [2.8, 0.4, 1.6], [0, -1.3, 0], color=panel, material="Metal"),
            part("Intake", [1.6, 0.7, 0.5], [0, -0.5, -1.2], color=vent, material="Metal"),
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
        kids += [
            part("Hull", [4.2, 3.0, 2.6], [0, 0, 0], color=hull, material="DiamondPlate"),
            part("Door", [2.2, 2.0, 0.35], [0, 0.1, 1.4], color=panel, material="Metal"),
            part("AccentLock", [0.5, 0.5, 0.3], [0.6, 0.1, 1.55], color=accent, material="Neon"),
            part("HingeL", [0.3, 2.0, 0.3], [-1.2, 0.1, 1.4], color=vent, material="Metal"),
            part("HingeR", [0.3, 2.0, 0.3], [1.2, 0.1, 1.4], color=vent, material="Metal"),
            part("CornerL", [0.8, 0.8, 0.8], [-1.9, 1.2, 1.0], color=panel, material="Metal"),
            part("CornerR", [0.8, 0.8, 0.8], [1.9, 1.2, 1.0], color=panel, material="Metal"),
            part("BackSafe", [3.0, 2.2, 0.8], [0, 0, -1.5], color=darken(hull, 0.15), material="Metal"),
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
        kids += [
            part("ThighBlock", [1.5, 1.1, 1.5], [0, 0.4, 0], color=armor, material="CorrodedMetal"),
            part("KneeCap", [1.4, 0.5, 1.4], [0, -0.3, 0], color=joint, material="Metal"),
            part("ShinBlock", [1.55, 1.0, 1.55], [0, -1.0, 0], color=armor, material="CorrodedMetal"),
            part("FootPad", [1.9, 0.4, 1.9], [0, -1.65, 0.1], color=sole, material="SmoothPlastic"),
            part("AccentStud", [0.4, 0.4, 0.4], [0.5 * s, -0.3, 0.7], color=accent, material="Neon"),
            part("ToeLip", [1.7, 0.35, 0.5], [0, -1.55, 0.9], color=panel_safe(armor), material="Metal"),
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


def build_lower_weapon(base: list[float], *, style: str) -> list[dict]:
    """Lower/arm weapons: snap, rivet, ember, needle, cleaver, drill, spray, hook."""
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
    else:  # hook
        kids += [
            part("Arm", [0.7, 0.55, 1.5], [0, 0, 0], color=body, material="Metal"),
            part("HookCurve", [0.45, 0.9, 0.45], [0, 0.35, 1.1], color=dark, material="Metal"),
            part("HookTip", [0.3, 0.3, 0.8], [0, 0.7, 1.5], color=muzzle, material="Metal"),
            part("AccentChain", [0.2, 0.2, 0.9], [0, -0.35, 0.4], color=accent, material="Neon"),
        ]
    return kids


def build_shoulder_weapon(base: list[float], *, style: str) -> list[dict]:
    """Shoulder weapons: brick, arc, bite, slag, box, twin, mortar, spear."""
    kids: list[dict] = []
    body = base
    dark = darken(base, 0.22)
    accent = lighten(base, 0.32)
    tip = rgb(28, 30, 34)

    kids.append(part("ShoulderMount", [1.2, 0.55, 1.0], [0, -0.15, -0.7], color=dark, material="Metal"))

    if style == "brick":
        kids += [
            part("Block", [1.6, 1.0, 1.8], [0, 0.15, 0.2], color=body, material="Concrete"),
            part("Barrel", [0.55, 0.55, 1.4], [0, 0.2, 1.4], color=dark, material="Metal"),
            part("AccentBand", [1.65, 0.2, 0.2], [0, 0.55, 0.3], color=accent, material="Neon"),
            part("Breech", [1.3, 0.8, 0.6], [0, 0.1, -0.9], color=tip, material="Metal"),
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
        kids += [
            part("Magazine", [1.7, 1.1, 1.4], [0, 0.2, 0], color=body, material="Metal"),
            part("Barrels", [1.2, 0.45, 1.6], [0, 0.15, 1.2], color=dark, material="Metal"),
            part("AccentPanel", [0.3, 0.8, 1.0], [0.85, 0.2, 0], color=accent, material="Neon"),
            part("Hatch", [1.2, 0.2, 1.0], [0, 0.8, 0], color=tip, material="Metal"),
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
    else:  # spear
        kids += [
            part("Shaft", [0.35, 0.35, 2.8], [0, 0.15, 0.6], color=body, material="Metal"),
            part("Head", [0.7, 0.5, 0.9], [0, 0.2, 2.1], color=dark, material="Metal"),
            part("AccentCore", [0.25, 0.25, 1.2], [0, 0.35, 0.8], color=accent, material="Neon"),
            part("Counter", [0.6, 0.6, 0.6], [0, 0.1, -0.9], color=tip, material="Metal"),
        ]
    return kids


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
reg("saw_arm", "lower", rgb(130, 130, 135), style="cleaver")
reg("ram_fist", "lower", rgb(100, 95, 90), style="snap")
reg("plasma_dab", "lower", rgb(90, 180, 210), style="needle")
reg("coal_mitt", "lower", rgb(160, 80, 40), style="ember")
reg("auger_bit", "lower", rgb(95, 100, 85), style="drill")
reg("grapple_hook", "lower", rgb(80, 85, 95), style="hook")
reg("foam_sprayer", "lower", rgb(160, 160, 150), style="spray")
reg("hammer_hand", "lower", rgb(120, 110, 100), style="snap")
reg("crate_mortar", "shoulder", rgb(110, 95, 70), style="mortar")
reg("coil_spear", "shoulder", rgb(60, 120, 170), style="spear")
reg("junk_box", "shoulder", rgb(90, 85, 75), style="box")
reg("flare_twin", "shoulder", rgb(200, 100, 50), style="twin")
reg("slag_brick", "shoulder", rgb(130, 70, 45), style="brick")
reg("arc_fork", "shoulder", rgb(70, 160, 210), style="arc")
reg("heat_lance", "shoulder", rgb(210, 90, 40), style="bite")
reg("pitch_pot", "shoulder", rgb(55, 45, 40), style="slag")
reg("cell_strip", "battery", rgb(40, 55, 65), style="stack")
reg("wet_cell", "battery", rgb(45, 90, 100), style="drum")
reg("junk_brick", "battery", rgb(60, 58, 55), style="desk")
reg("surge_pack", "battery", rgb(25, 80, 110), style="bay")
reg("core_cell", "battery", rgb(30, 100, 120), style="deep")
reg("fried_cpu", "cpu", rgb(90, 60, 50), style="scrap")
reg("lab_cpu", "cpu", rgb(70, 130, 110), style="bay")
reg("prism_cpu", "cpu", rgb(50, 100, 140), style="optic")
reg("buzz_drone", "drone", rgb(170, 160, 70), style="moth")
reg("crate_mite", "drone", rgb(100, 85, 65), style="floor")
reg("cross_beep", "drone", rgb(90, 170, 130), style="beep")
reg("glass_orb", "drone", rgb(120, 160, 190), style="orb")
reg("crawl_bit", "drone", rgb(85, 75, 65), style="spider")
reg("chip_foam", "chip", rgb(120, 130, 140), style="heat")
reg("chip_braid", "chip", rgb(50, 130, 140), style="wire")
reg("chip_oil", "chip", rgb(140, 120, 50), style="grease")
reg("chip_bulk", "chip", rgb(100, 105, 95), style="shield")
reg("chip_scab", "chip", rgb(120, 85, 70), style="skin")

for side in ("l", "r"):
    reg(f"cargo_{side}", "leg", rgb(90, 85, 70), style="workboot", side=side)
    reg(f"blade_{side}", "leg", rgb(140, 145, 150), style="sprint", side=side)
    reg(f"block_{side}", "leg", rgb(70, 68, 65), style="stump", side=side)
    reg(f"grip_{side}", "leg", rgb(100, 90, 80), style="claw", side=side)
    reg(f"hydro_{side}", "leg", rgb(85, 100, 110), style="piston", side=side)


def build_children(kind: str, color: list[float], kwargs: dict) -> list[dict]:
    style = kwargs.get("style", "cage")
    if kind == "torso":
        return build_torso(color, style=style)
    if kind == "leg":
        return build_leg(color, style=style, side=kwargs.get("side", "r"))
    if kind == "lower":
        return build_lower_weapon(color, style=style)
    if kind == "shoulder":
        return build_shoulder_weapon(color, style=style)
    if kind == "battery":
        return build_battery(color, style=style)
    if kind == "cpu":
        return build_cpu(color, style=style)
    if kind == "drone":
        return build_drone(color, style=style)
    if kind == "chip":
        return build_chip(color, style=style)
    raise ValueError(f"unknown kind {kind}")


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        for p in OUT.glob("*.model.json"):
            p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    for pid, (kind, color, kwargs) in sorted(PART_RECIPES.items()):
        children = build_children(kind, color, kwargs)
        assert len(children) >= 3, f"{pid} too few parts ({len(children)})"
        write_model(OUT / f"{pid}.model.json", pack_model(children))
        counts[kind] = counts.get(kind, 0) + 1

    # Manifest lives outside RS so Rojo does not sync it as an Instance
    manifest = {
        "count": len(PART_RECIPES),
        "byKind": counts,
        "ids": sorted(PART_RECIPES.keys()),
    }
    man_path = ROOT / "tools" / "part_models_manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(PART_RECIPES)} part models -> {OUT.relative_to(ROOT)}")
    print(f"manifest -> {man_path.relative_to(ROOT)}")
    for k, n in sorted(counts.items()):
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
