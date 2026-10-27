#!/usr/bin/env python3
"""Hand-author SuperMechs-inspired hero starter kits + AssemblerAssets showcase.

Dense multi-cube kits (panels / vents / barrels / joints) — SM structure only,
never pasted SM art. Preview is front 3/4 (visor + weapons toward camera).

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


OLIVE = rgb(86, 124, 64)
OLIVE_LIGHT = rgb(120, 158, 90)
OLIVE_DARK = rgb(58, 88, 48)
CHAR = rgb(42, 44, 48)
STEEL = rgb(110, 118, 128)
STEEL_DK = rgb(72, 78, 86)
VISOR = rgb(40, 220, 255)
ORANGE = rgb(255, 140, 48)
RUBBER = rgb(28, 28, 30)
CANNON = rgb(72, 78, 88)
GUNMETAL = rgb(58, 62, 70)


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
    elif "Boot" in name or "Sole" in name or "Grip" in name or "Skid" in name:
        attrs["TextureRole"] = "matte_rubber"
    elif "Hazard" in name:
        attrs["TextureRole"] = "hazard_stripe"
    else:
        attrs["TextureRole"] = "metal_plate"
    node: dict = {"Name": name, "ClassName": "Part", "Properties": props}
    if attrs:
        node["Attributes"] = attrs
    return node


def root_marker() -> dict:
    return part(
        "Root",
        [0.2, 0.2, 0.2],
        [0, 0, 0],
        color=rgb(255, 255, 255),
        transparency=1.0,
        role="matte_rubber",
    )


def pack(children: list[dict]) -> dict:
    return {"ClassName": "Model", "Children": [root_marker()] + children}


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def vent_row(prefix: str, origin: list[float], n: int, step: float, size: list[float], color: list[float]) -> list[dict]:
    kids = []
    for i in range(n):
        kids.append(
            part(
                f"{prefix}{i}",
                size,
                [origin[0] + i * step, origin[1], origin[2]],
                color=color,
                material="Metal",
                role="carbon_dark",
            )
        )
    return kids


def rivet_line(prefix: str, origin: list[float], n: int, step: float, axis: str = "x") -> list[dict]:
    kids = []
    for i in range(n):
        pos = list(origin)
        if axis == "x":
            pos[0] += i * step
        elif axis == "y":
            pos[1] += i * step
        else:
            pos[2] += i * step
        kids.append(
            part(
                f"{prefix}{i}",
                [0.14, 0.14, 0.14],
                pos,
                color=STEEL,
                material="Metal",
                role="scratched_steel",
            )
        )
    return kids


# ---------------------------------------------------------------------------
# Dense hand kits — many designed cubes per piece
# ---------------------------------------------------------------------------


def kit_visor_torso() -> list[dict]:
    """Top-heavy chassis: layered panels, visor stack, vents, pauldrons, backpack."""
    kids: list[dict] = [
        # Core volume
        part("HullCore", [3.4, 2.35, 2.1], [0, 0.05, 0], color=OLIVE, material="Metal"),
        part("HullShell", [3.9, 2.75, 2.45], [0, 0.05, 0], color=OLIVE_DARK, material="Metal"),
        part("HullInset", [3.1, 2.0, 0.25], [0, 0.1, 1.15], color=CHAR, material="Metal", role="carbon_dark"),
        # Dome / head block
        part("Dome", [3.15, 1.05, 1.95], [0, 1.4, 0.08], color=OLIVE_LIGHT, material="Metal"),
        part("DomeCap", [2.4, 0.35, 1.5], [0, 2.0, 0.05], color=OLIVE, material="Metal"),
        part("DomeRidge", [0.35, 0.55, 1.7], [0, 1.65, 0.1], color=STEEL, material="Metal"),
        # Visor stack (front)
        part("VisorBrow", [2.55, 0.28, 0.4], [0, 0.95, 1.3], color=GUNMETAL, material="Metal"),
        part("VisorRecess", [2.35, 0.75, 0.38], [0, 0.55, 1.28], color=CHAR, material="Metal", role="carbon_dark"),
        part("GlowVisor", [2.05, 0.48, 0.2], [0, 0.58, 1.48], color=VISOR, material="Neon", role="emissive_strip"),
        part("VisorLip", [2.2, 0.12, 0.25], [0, 0.28, 1.4], color=STEEL_DK, material="Metal"),
        part("VisorCheekL", [0.35, 0.55, 0.35], [-1.15, 0.55, 1.35], color=OLIVE_DARK, material="Metal"),
        part("VisorCheekR", [0.35, 0.55, 0.35], [1.15, 0.55, 1.35], color=OLIVE_DARK, material="Metal"),
        # Breast / abdomen panels
        part("BreastPlate", [2.7, 1.15, 0.38], [0, -0.25, 1.22], color=darken(OLIVE, 0.12), material="DiamondPlate", role="scratched_steel"),
        part("BreastBoltL", [0.22, 0.22, 0.18], [-0.9, -0.1, 1.42], color=STEEL, material="Metal"),
        part("BreastBoltR", [0.22, 0.22, 0.18], [0.9, -0.1, 1.42], color=STEEL, material="Metal"),
        part("AbPanel", [2.2, 0.7, 0.32], [0, -0.95, 1.15], color=OLIVE_DARK, material="Metal"),
        part("AccentHazard", [2.0, 0.16, 0.16], [0, -0.7, 1.38], color=ORANGE, material="Neon", role="hazard_stripe"),
        part("GlowChestPip", [0.2, 0.2, 0.15], [0, -0.35, 1.45], color=VISOR, material="Neon"),
        # Side cheeks / skirts
        part("CheekL", [0.7, 1.55, 1.35], [-1.95, 0.35, 0.3], color=OLIVE_DARK, material="Metal"),
        part("CheekR", [0.7, 1.55, 1.35], [1.95, 0.35, 0.3], color=OLIVE_DARK, material="Metal"),
        part("SideSkirtL", [0.4, 1.2, 1.5], [-2.05, -0.55, 0.1], color=STEEL_DK, material="Metal"),
        part("SideSkirtR", [0.4, 1.2, 1.5], [2.05, -0.55, 0.1], color=STEEL_DK, material="Metal"),
        # Hip yoke
        part("HipYoke", [3.35, 0.5, 1.95], [0, -1.5, 0.05], color=STEEL, material="Metal"),
        part("HipSocketL", [0.55, 0.45, 0.55], [-1.1, -1.55, 0.15], color=CHAR, material="Metal", shape="Ball"),
        part("HipSocketR", [0.55, 0.45, 0.55], [1.1, -1.55, 0.15], color=CHAR, material="Metal", shape="Ball"),
        # Pauldrons (layered)
        part("PauldronL", [1.35, 0.85, 1.5], [-2.2, 1.15, 0], color=OLIVE, material="Metal"),
        part("PauldronLTrim", [1.15, 0.25, 1.35], [-2.25, 1.55, 0.05], color=STEEL, material="Metal"),
        part("PauldronLVent", [0.35, 0.55, 0.9], [-2.55, 1.1, 0.15], color=CHAR, material="Metal", role="carbon_dark"),
        part("PauldronR", [1.35, 0.85, 1.5], [2.2, 1.15, 0], color=OLIVE, material="Metal"),
        part("PauldronRTrim", [1.15, 0.25, 1.35], [2.25, 1.55, 0.05], color=STEEL, material="Metal"),
        part("PauldronRStub", [0.55, 0.45, 0.7], [2.55, 1.05, -0.15], color=GUNMETAL, material="Metal"),
        # Backpack / thruster cluster
        part("BackPack", [2.7, 1.75, 0.9], [0, 0.3, -1.5], color=CHAR, material="Metal", role="carbon_dark"),
        part("BackPlate", [2.3, 1.2, 0.25], [0, 0.35, -1.95], color=STEEL_DK, material="Metal"),
        part("ThrusterL", [0.55, 0.55, 0.85], [-0.55, 0.05, -2.15], color=STEEL, material="Metal", shape="Cylinder"),
        part("ThrusterR", [0.55, 0.55, 0.85], [0.55, 0.05, -2.15], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowExhaustL", [0.32, 0.32, 0.28], [-0.55, 0.05, -2.55], color=VISOR, material="Neon"),
        part("GlowExhaustR", [0.32, 0.32, 0.28], [0.55, 0.05, -2.55], color=VISOR, material="Neon"),
        part("Antenna", [0.16, 1.15, 0.16], [1.15, 2.2, -0.35], color=STEEL, material="Metal"),
        part("AntennaTip", [0.2, 0.2, 0.2], [1.15, 2.8, -0.35], color=ORANGE, material="Neon"),
        part("SensorStub", [0.25, 0.35, 0.25], [-1.0, 2.0, 0.4], color=GUNMETAL, material="Metal"),
    ]
    kids += vent_row("VentF", [-0.9, -0.55, 1.42], 5, 0.45, [0.28, 0.45, 0.12], CHAR)
    kids += vent_row("VentSideL", [-2.15, 0.1, -0.4], 3, 0.4, [0.12, 0.35, 0.28], GUNMETAL)
    kids += rivet_line("RivetTop", [-1.2, 1.85, 0.85], 5, 0.6, "x")
    kids += rivet_line("RivetHip", [-1.4, -1.35, 0.9], 6, 0.55, "x")
    return kids


def kit_plant_leg(side: str) -> list[dict]:
    """Crouched biped: armor plates, piston, knee joint stack, planted boot."""
    s = -1.0 if side == "l" else 1.0
    kids: list[dict] = [
        part("HipBall", [0.95, 0.7, 0.95], [0.05 * s, 1.05, 0.05], color=CHAR, material="Metal", shape="Ball", role="scratched_steel"),
        part("HipCollar", [1.15, 0.28, 1.15], [0.08 * s, 0.85, 0.08], color=STEEL, material="Metal"),
        part("Thigh", [1.2, 1.05, 1.3], [0.12 * s, 0.4, 0.22], color=OLIVE, material="Metal"),
        part("ThighPlateOut", [0.28, 0.9, 1.05], [0.78 * s, 0.4, 0.28], color=OLIVE_DARK, material="Metal"),
        part("ThighPlateIn", [0.22, 0.75, 0.9], [-0.55 * s, 0.4, 0.2], color=STEEL_DK, material="Metal"),
        part("ThighRidge", [0.2, 0.85, 0.2], [0.2 * s, 0.45, 0.85], color=STEEL, material="Metal"),
        part("PistonRod", [0.18, 0.9, 0.18], [0.45 * s, 0.15, -0.35], color=STEEL, material="Metal"),
        part("PistonSleeve", [0.32, 0.4, 0.32], [0.45 * s, 0.55, -0.35], color=GUNMETAL, material="Metal"),
        # Knee cluster
        part("KneeDisk", [1.1, 0.38, 1.1], [0.15 * s, -0.28, 0.55], color=STEEL, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("KneeDiskB", [0.85, 0.28, 0.85], [0.15 * s, -0.28, 0.55], color=CHAR, material="Metal", shape="Cylinder"),
        part("KneePin", [0.26, 0.65, 0.26], [0.72 * s, -0.28, 0.55], color=ORANGE, material="Neon"),
        part("KneeGuard", [0.95, 0.35, 0.45], [0.12 * s, -0.05, 0.95], color=OLIVE_DARK, material="Metal"),
        # Shin
        part("Shin", [1.05, 1.15, 1.15], [0.1 * s, -1.0, 0.32], color=OLIVE, material="Metal"),
        part("ShinPlate", [0.28, 0.95, 0.95], [0.68 * s, -1.0, 0.38], color=OLIVE_DARK, material="Metal"),
        part("ShinBrace", [0.22, 0.95, 0.5], [0.55 * s, -1.0, -0.15], color=CHAR, material="Metal"),
        part("ShinVentA", [0.7, 0.18, 0.12], [0.05 * s, -0.75, 0.9], color=CHAR, material="Metal", role="carbon_dark"),
        part("ShinVentB", [0.7, 0.18, 0.12], [0.05 * s, -1.05, 0.9], color=CHAR, material="Metal", role="carbon_dark"),
        part("AccentShin", [0.18, 0.65, 0.14], [0.5 * s, -1.05, 0.88], color=VISOR, material="Neon"),
        # Ankle + boot
        part("Ankle", [1.15, 0.38, 1.1], [0.05 * s, -1.55, 0.42], color=STEEL, material="Metal"),
        part("AnkleBall", [0.55, 0.4, 0.55], [0.05 * s, -1.55, 0.35], color=CHAR, material="Metal", shape="Ball"),
        part("Boot", [1.6, 0.42, 1.9], [0.05 * s, -1.95, 0.58], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("BootArmor", [1.4, 0.28, 1.1], [0.05 * s, -1.72, 0.55], color=OLIVE_DARK, material="Metal"),
        part("ToeLip", [1.3, 0.26, 0.42], [0.05 * s, -1.78, 1.4], color=STEEL_DK, material="Metal"),
        part("HeelBlock", [1.0, 0.35, 0.45], [0.05 * s, -1.95, -0.25], color=CHAR, material="Metal"),
        part("SoleGrip", [1.45, 0.12, 1.6], [0.05 * s, -2.12, 0.55], color=darken(RUBBER, 0.15), material="SmoothPlastic", role="matte_rubber"),
    ]
    kids += rivet_line("ThighRivet", [-0.35, 0.7, 0.7], 3, 0.35, "x")
    return kids


def kit_gatling_arm() -> list[dict]:
    """Triple-barrel mitt with cooling vanes, belt, mounts, glow muzzles."""
    kids: list[dict] = [
        part("Mount", [1.0, 0.8, 0.8], [0, 0, -0.9], color=CHAR, material="Metal"),
        part("MountPin", [0.35, 0.35, 0.55], [0, 0, -1.25], color=STEEL, material="Metal", shape="Cylinder"),
        part("ElbowJoint", [0.7, 0.7, 0.7], [0, 0, -0.45], color=GUNMETAL, material="Metal", shape="Ball"),
        part("Forearm", [1.05, 0.85, 1.45], [0, -0.02, 0.1], color=STEEL, material="Metal"),
        part("ForearmPlate", [1.15, 0.25, 1.2], [0, 0.45, 0.15], color=OLIVE_DARK, material="Metal"),
        part("ForearmRail", [0.2, 0.2, 1.3], [0.55, 0.15, 0.2], color=CHAR, material="Metal"),
        part("Receiver", [1.2, 1.05, 1.15], [0, 0.05, 1.0], color=STEEL_DK, material="Metal"),
        part("ReceiverLid", [1.0, 0.2, 0.9], [0, 0.6, 1.0], color=OLIVE, material="Metal"),
        part("CoolingJacket", [1.0, 1.0, 0.9], [0, 0.05, 1.6], color=CANNON, material="Metal", shape="Cylinder"),
        # Triple barrels + sleeves
        part("BarrelA", [0.26, 0.26, 1.75], [-0.3, 0.22, 2.05], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelB", [0.26, 0.26, 1.75], [0.3, 0.22, 2.05], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelC", [0.26, 0.26, 1.75], [0, -0.18, 2.05], color=CHAR, material="Metal", shape="Cylinder"),
        part("SleeveA", [0.38, 0.38, 0.55], [-0.3, 0.22, 1.45], color=STEEL, material="Metal", shape="Cylinder"),
        part("SleeveB", [0.38, 0.38, 0.55], [0.3, 0.22, 1.45], color=STEEL, material="Metal", shape="Cylinder"),
        part("SleeveC", [0.38, 0.38, 0.55], [0, -0.18, 1.45], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowMuzzleA", [0.32, 0.32, 0.18], [-0.3, 0.22, 2.95], color=ORANGE, material="Neon"),
        part("GlowMuzzleB", [0.32, 0.32, 0.18], [0.3, 0.22, 2.95], color=ORANGE, material="Neon"),
        part("GlowMuzzleC", [0.32, 0.32, 0.18], [0, -0.18, 2.95], color=ORANGE, material="Neon"),
        part("MuzzleBrake", [0.85, 0.55, 0.35], [0, 0.05, 2.75], color=GUNMETAL, material="Metal"),
        # Belt / feed
        part("BeltBox", [0.75, 0.6, 0.65], [0.75, -0.2, 0.75], color=OLIVE, material="Metal"),
        part("BeltLid", [0.7, 0.12, 0.55], [0.75, 0.15, 0.75], color=OLIVE_LIGHT, material="Metal"),
        part("AccentFeed", [0.16, 0.16, 0.75], [0.42, 0.2, 1.05], color=VISOR, material="Neon"),
        part("BeltLink", [0.35, 0.2, 0.2], [0.55, 0.05, 0.45], color=STEEL, material="Metal"),
        part("Grip", [0.4, 0.55, 0.4], [0, -0.7, 0.15], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("GripGuard", [0.55, 0.15, 0.55], [0, -0.4, 0.15], color=CHAR, material="Metal"),
    ]
    kids += vent_row("CoolVent", [-0.45, 0.55, 1.55], 4, 0.3, [0.22, 0.12, 0.4], CHAR)
    return kids


def kit_rivet_ready() -> list[dict]:
    """Sidearm cannon with mag, rails, sight, muzzle stack."""
    kids: list[dict] = [
        part("Mount", [0.95, 0.75, 0.75], [0, 0, -0.95], color=CHAR, material="Metal"),
        part("MountBolt", [0.3, 0.3, 0.3], [0, 0.35, -0.95], color=STEEL, material="Metal"),
        part("Receiver", [1.05, 0.9, 1.6], [0, 0.02, 0.1], color=STEEL, material="Metal"),
        part("ReceiverTop", [0.9, 0.22, 1.3], [0, 0.5, 0.15], color=OLIVE_DARK, material="Metal"),
        part("ReceiverSide", [0.2, 0.65, 1.2], [0.55, 0.05, 0.15], color=STEEL_DK, material="Metal"),
        part("Barrel", [0.38, 0.38, 1.7], [0, 0.12, 1.5], color=CHAR, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.55, 0.55, 0.7], [0, 0.12, 0.95], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelRing", [0.5, 0.12, 0.5], [0, 0.12, 1.85], color=STEEL, material="Metal", shape="Cylinder"),
        part("Mag", [0.55, 0.8, 0.5], [0, -0.65, 0.2], color=OLIVE, material="Metal"),
        part("MagCatch", [0.25, 0.25, 0.25], [0.35, -0.35, 0.2], color=ORANGE, material="Neon"),
        part("Sight", [0.16, 0.4, 0.55], [0, 0.6, 0.55], color=VISOR, material="Neon"),
        part("SightBase", [0.28, 0.15, 0.45], [0, 0.45, 0.5], color=GUNMETAL, material="Metal"),
        part("UnderRail", [0.35, 0.18, 1.1], [0, -0.35, 0.95], color=CANNON, material="Metal"),
        part("Muzzle", [0.48, 0.48, 0.32], [0, 0.12, 2.35], color=ORANGE, material="Neon"),
        part("MuzzleCollar", [0.6, 0.2, 0.6], [0, 0.12, 2.15], color=STEEL_DK, material="Metal"),
        part("EjectPort", [0.35, 0.25, 0.35], [0.45, 0.25, 0.55], color=CHAR, material="Metal", role="carbon_dark"),
    ]
    kids += rivet_line("RecvRivet", [-0.4, 0.35, 0.7], 3, 0.4, "x")
    return kids


def kit_ridge_cannon() -> list[dict]:
    """Shoulder ridge cannon: breech plates, fins, drum, long barrel, glow bore."""
    kids: list[dict] = [
        part("ShoulderMount", [1.35, 0.55, 1.15], [0, -0.25, -0.55], color=CHAR, material="Metal"),
        part("MountClampL", [0.25, 0.55, 0.7], [-0.7, -0.15, -0.4], color=STEEL, material="Metal"),
        part("MountClampR", [0.25, 0.55, 0.7], [0.7, -0.15, -0.4], color=STEEL, material="Metal"),
        part("Breech", [1.5, 1.2, 1.55], [0, 0.3, 0.15], color=OLIVE, material="Metal"),
        part("BreechLid", [1.25, 0.22, 1.2], [0, 0.95, 0.2], color=OLIVE_LIGHT, material="Metal"),
        part("BreechInset", [1.1, 0.7, 0.25], [0, 0.3, 0.95], color=CHAR, material="Metal", role="carbon_dark"),
        part("Collar", [1.5, 0.32, 1.5], [0, 0.3, 0.9], color=STEEL, material="Metal", shape="Cylinder"),
        part("CollarRing", [1.65, 0.18, 1.65], [0, 0.3, 0.9], color=GUNMETAL, material="Metal", shape="Cylinder"),
        part("Barrel", [0.65, 0.65, 2.5], [0, 0.32, 2.05], color=CANNON, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.95, 0.95, 1.05], [0, 0.32, 1.5], color=STEEL_DK, material="Metal", shape="Cylinder"),
        part("BarrelBand", [0.8, 0.18, 0.8], [0, 0.32, 2.55], color=STEEL, material="Metal", shape="Cylinder"),
        part("GlowBore", [0.42, 0.42, 0.28], [0, 0.32, 3.3], color=VISOR, material="Neon"),
        part("BoreRing", [0.7, 0.15, 0.7], [0, 0.32, 3.1], color=ORANGE, material="Neon"),
        part("FinL", [0.18, 0.75, 1.25], [-0.8, 0.6, 0.35], color=OLIVE_DARK, material="Metal"),
        part("FinR", [0.18, 0.75, 1.25], [0.8, 0.6, 0.35], color=OLIVE_DARK, material="Metal"),
        part("FinLTip", [0.14, 0.4, 0.55], [-0.85, 0.85, 0.7], color=STEEL, material="Metal"),
        part("FinRTip", [0.14, 0.4, 0.55], [0.85, 0.85, 0.7], color=STEEL, material="Metal"),
        part("AccentHazard", [1.25, 0.16, 0.16], [0, -0.35, 0.55], color=ORANGE, material="Neon", role="hazard_stripe"),
        part("AmmoDrum", [0.9, 0.9, 0.9], [0.95, -0.1, -0.05], color=CHAR, material="Metal", shape="Cylinder"),
        part("DrumCap", [0.7, 0.2, 0.7], [0.95, 0.4, -0.05], color=STEEL, material="Metal", shape="Cylinder"),
        part("DrumFeed", [0.35, 0.35, 0.55], [0.55, 0.05, 0.35], color=GUNMETAL, material="Metal"),
        part("ScopeRail", [0.2, 0.15, 1.0], [0, 0.95, 0.8], color=CHAR, material="Metal"),
        part("GlowScope", [0.18, 0.18, 0.25], [0, 1.05, 1.2], color=VISOR, material="Neon"),
    ]
    kids += vent_row("BreechVent", [-0.55, 0.55, 0.85], 4, 0.35, [0.25, 0.4, 0.12], CHAR)
    return kids


def kit_desk_battery() -> list[dict]:
    return [
        part("Cell", [1.55, 0.95, 0.7], [0, 0, 0], color=CHAR, material="Metal", role="carbon_dark"),
        part("CellBand", [1.6, 0.15, 0.75], [0, 0.15, 0], color=STEEL, material="Metal"),
        part("TerminalP", [0.32, 0.32, 0.22], [0.45, 0.4, 0.38], color=ORANGE, material="Neon"),
        part("TerminalN", [0.32, 0.32, 0.22], [-0.45, 0.4, 0.38], color=STEEL, material="Metal"),
        part("Stripe", [1.25, 0.12, 0.12], [0, 0.2, 0.38], color=VISOR, material="Neon"),
        part("ClampL", [0.2, 0.75, 0.55], [-0.8, 0, 0], color=STEEL, material="Metal"),
        part("ClampR", [0.2, 0.75, 0.55], [0.8, 0, 0], color=STEEL, material="Metal"),
        part("VentSlot", [0.9, 0.35, 0.12], [0, -0.2, 0.38], color=GUNMETAL, material="Metal", role="carbon_dark"),
        part("WarningPip", [0.15, 0.15, 0.12], [0.65, -0.25, 0.38], color=ORANGE, material="Neon"),
    ]


def kit_scrap_cpu() -> list[dict]:
    return [
        part("Board", [0.7, 0.18, 0.7], [0, 0, 0], color=OLIVE, material="Metal"),
        part("BoardEdge", [0.75, 0.08, 0.75], [0, -0.05, 0], color=STEEL_DK, material="Metal"),
        part("Die", [0.35, 0.22, 0.35], [0, 0.2, 0], color=CHAR, material="Metal"),
        part("GlowPin", [0.14, 0.14, 0.14], [0.22, 0.18, 0.22], color=VISOR, material="Neon"),
        part("GlowPin2", [0.12, 0.12, 0.12], [-0.22, 0.16, -0.18], color=ORANGE, material="Neon"),
        part("HeatSink", [0.55, 0.22, 0.2], [0, 0.38, -0.15], color=STEEL, material="Metal"),
        part("HeatFinA", [0.5, 0.28, 0.08], [0, 0.42, -0.28], color=STEEL_DK, material="Metal"),
        part("HeatFinB", [0.5, 0.28, 0.08], [0, 0.42, -0.05], color=STEEL_DK, material="Metal"),
        part("Trace", [0.45, 0.05, 0.08], [-0.05, 0.12, 0.28], color=VISOR, material="Neon"),
    ]


def kit_floor_drone() -> list[dict]:
    return [
        part("Body", [1.0, 0.45, 1.1], [0, 0, 0], color=STEEL, material="Metal"),
        part("BodyArmor", [0.85, 0.2, 0.9], [0, 0.25, 0.05], color=OLIVE_DARK, material="Metal"),
        part("Eye", [0.35, 0.18, 0.18], [0, 0.18, 0.55], color=VISOR, material="Neon"),
        part("EyeRing", [0.45, 0.1, 0.12], [0, 0.18, 0.5], color=CHAR, material="Metal"),
        part("Rotor", [0.75, 0.1, 0.75], [0, 0.4, -0.2], color=CHAR, material="Metal"),
        part("RotorHub", [0.28, 0.18, 0.28], [0, 0.45, -0.2], color=STEEL, material="Metal"),
        part("SkidL", [0.14, 0.2, 0.75], [-0.42, -0.32, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("SkidR", [0.14, 0.2, 0.75], [0.42, -0.32, 0], color=RUBBER, material="SmoothPlastic", role="matte_rubber"),
        part("Antenna", [0.1, 0.45, 0.1], [0.3, 0.45, 0.25], color=STEEL, material="Metal"),
        part("AccentPip", [0.12, 0.12, 0.12], [-0.35, 0.15, 0.4], color=ORANGE, material="Neon"),
    ]


def kit_chip(color: list[float], glow: list[float]) -> list[dict]:
    return [
        part("Plate", [0.48, 0.12, 0.38], [0, 0, 0], color=color, material="Metal"),
        part("Frame", [0.52, 0.06, 0.42], [0, -0.02, 0], color=STEEL_DK, material="Metal"),
        part("GlowDot", [0.12, 0.08, 0.12], [0.14, 0.1, 0.08], color=glow, material="Neon"),
        part("PinA", [0.07, 0.07, 0.18], [-0.14, -0.02, 0.05], color=STEEL, material="Metal"),
        part("PinB", [0.07, 0.07, 0.18], [-0.14, -0.02, -0.1], color=STEEL, material="Metal"),
        part("Cap", [0.1, 0.1, 0.1], [0.05, 0.1, -0.1], color=CHAR, material="Metal"),
    ]


# ---------------------------------------------------------------------------
# Showcase assembly (torso-local; feet near y=-TORSO_Y)
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
            [6.8, 0.32, 4.8],
            [0, -TORSO_Y - 0.15, 0.5],
            color=rgb(55, 58, 62),
            material="Metal",
            role="metal_plate",
        )
    )
    kids.append(
        part(
            "ShowcaseStripe",
            [5.8, 0.12, 0.25],
            [0, -TORSO_Y + 0.05, 2.6],
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
        "View": "FrontThreeQuarter",
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
# Front 3/4 preview (visor / weapons toward camera)
# ---------------------------------------------------------------------------


def render_preview(model: dict, out_path: Path) -> None:
    """Front-right 3/4: mech faces +Z; camera from front-right-up."""

    az = math.radians(34)  # yaw from pure front toward +X (right)

    def project(x: float, y: float, z: float) -> tuple[float, float, float]:
        # Camera in front (+Z) and right (+X), looking at origin.
        # depth increases toward camera so front draws last.
        along = z * math.cos(az) + x * math.sin(az)
        across = x * math.cos(az) - z * math.sin(az)
        sx = across * 0.95
        sy = y * 0.98 + along * 0.22
        depth = along
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

        def corner(ix: int, iy: int, iz: int) -> tuple[float, float, float]:
            return (
                pos[0] + (-hx if ix == 0 else hx),
                pos[1] + (-hy if iy == 0 else hy),
                pos[2] + (-hz if iz == 0 else hz),
            )

        face_defs = [
            (((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), 1.12),  # +Z front (bright)
            (((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), 0.68),  # -Z back
            (((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)), 1.2),  # +Y top
            (((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), 0.58),  # -Y bottom
            (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), 0.95),  # +X
            (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), 0.8),  # -X
        ]
        glow = ("Glow" in name) or ("Visor" in name) or ("Accent" in name)
        for idxs, shade in face_defs:
            proj = [project(*corner(*i)) for i in idxs]
            # back-face cull: skip faces pointing away from camera (avg depth normal approx)
            depth = sum(p[2] for p in proj) / 4.0
            # rough facing: if the face center is behind part center along view, still draw;
            # painter sort handles occlusion.
            poly = [(p[0], p[1]) for p in proj]
            for px, py in poly:
                pts_x.append(px)
                pts_y.append(py)
            fill = tuple(
                int(max(0, min(255, c * 255 * shade * (1.18 if glow else 1.0)))) for c in color
            )
            faces.append((depth, poly, fill, glow))

    faces.sort(key=lambda t: t[0])  # far → near (front last)

    W, H = 1200, 960
    img = Image.new("RGB", (W, H), (24, 26, 32))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, int(H * 0.62), W, H], fill=(32, 34, 40))

    min_x, max_x = min(pts_x), max(pts_x)
    min_y, max_y = min(pts_y), max(pts_y)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    margin = 90
    scale = (min(W, H) - 2 * margin) / span
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    def to_screen(x: float, y: float) -> tuple[float, float]:
        return W / 2 + (x - cx) * scale, H / 2 - (y - cy) * scale * 0.98 + 16

    for _d, poly, fill, glow in faces:
        screen = [to_screen(x, y) for x, y in poly]
        draw.polygon(screen, fill=fill, outline=(14, 14, 18))
        if glow:
            draw.line(screen + [screen[0]], fill=tuple(min(255, c + 40) for c in fill), width=2)

    title = "Assembler · Hero starter (front 3/4)"
    draw.rectangle([24, 20, 820, 78], fill=(18, 20, 24))
    try:
        font = ImageFont.truetype("arial.ttf", 26)
        font_sm = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font
    draw.text((36, 28), title, fill=(235, 240, 245), font=font)
    draw.text(
        (36, 56),
        "Dense kits · panels/vents/barrels/joints · combat ready · emissive visor",
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
    print("authoring dense hero starter kits + showcase…")
    write_starter_kits()
    showcase = build_showcase()
    write_model(SHOWCASE / "HeroStarterMech.model.json", showcase)
    n = len([c for c in showcase["Children"] if c.get("ClassName") == "Part"]) - 1
    print(f"  showcase HeroStarterMech: {n} visible parts")
    if n < 160:
        raise SystemExit(f"showcase too sparse ({n} parts); expected denser build")
    preview = PREVIEW_DIR / "supermechs-3d-preview.png"
    render_preview(showcase, preview)
    render_preview(showcase, ROOT / "assets" / "textures" / "supermechs-3d-preview.png")
    print("done")


if __name__ == "__main__":
    main()
