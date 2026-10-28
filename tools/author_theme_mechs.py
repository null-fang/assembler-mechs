#!/usr/bin/env python3
"""Author dense themed mech lines + front 3/4 previews.

Themes: scrap (Yardbone), arctic (Rimevault), desert (Duneplate), neon (Voltframe).
Writes hand kits (quality bar), Showcase models, assets/previews, and Context media.

  python3 tools/generate_part_models.py
  python3 tools/author_hero_mech.py
  python3 tools/author_theme_mechs.py
  python3 tools/emit_catalog_bay.py
  python3 tools/verify_part_coverage.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from theme_palettes import THEMES, darken, lighten, rgb

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src" / "AssemblerAssets" / "Parts"
SHOWCASE = ROOT / "src" / "AssemblerAssets" / "Showcase"
PREVIEW_DIR = ROOT / "assets" / "previews"
MEDIA = Path("/cursor/stores/bc-48ea8082-48b2-43e8-bfa6-d6d6d8d5a5a0/media")

TORSO_Y = 3.85

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


def bolt(name: str, pos: list[float], color: list[float], r: float = 0.11) -> dict:
    return part(name, [r, r, r], pos, color=color, material="DiamondPlate", role="scratched_steel")


def vent(name: str, pos: list[float], color: list[float], size: list[float] | None = None) -> dict:
    return part(name, size or [0.12, 0.5, 0.14], pos, color=color, material="Metal", role="carbon_dark")


# ---------------------------------------------------------------------------
# Dense theme kits — combat crouch, front-readable, panels/vents/barrels/joints
# ---------------------------------------------------------------------------


def kit_torso(t: dict) -> list[dict]:
    P, Pl, Pd = t["paint"], t["paint_light"], t["paint_dark"]
    A, V, S, Sd, C = t["accent"], t["visor"], t["steel"], t["steel_dark"], t["char"]
    tid = t["id"]
    kids = [
        part("CoreFrame", [2.45, 2.05, 1.55], [0, 0.05, -0.12], color=C, material="Metal", role="carbon_dark"),
        part("Hull", [3.45, 2.45, 2.2], [0, 0.08, 0.08], color=P, material="Metal"),
        part("HullSeam", [3.55, 0.1, 2.25], [0, 0.18, 0.08], color=Pd, material="Metal"),
        part("HullBelt", [3.5, 0.14, 2.2], [0, -0.55, 0.1], color=Sd, material="Metal"),
        # Layered +Z chest
        part("ChestPlateA", [2.55, 1.4, 0.34], [0, 0.28, 1.22], color=Pd, material="DiamondPlate", role="scratched_steel"),
        part("ChestPlateB", [2.1, 1.0, 0.3], [0, 0.38, 1.42], color=darken(P, 0.08), material="Metal"),
        part("ChestPlateC", [1.55, 0.6, 0.24], [0, 0.42, 1.58], color=C, material="Metal", role="carbon_dark"),
        part("BreastLower", [2.35, 0.72, 0.32], [0, -0.48, 1.28], color=Pd, material="Metal"),
        part("BreastSplit", [0.12, 1.6, 0.2], [0, 0.1, 1.55], color=S, material="Metal"),
        part("VentF", [0.95, 0.38, 0.16], [0, -0.12, 1.55], color=C, material="Metal", role="carbon_dark"),
        part("VentFL", [0.18, 0.6, 0.14], [-0.58, -0.12, 1.52], color=darken(C, 0.1), material="Metal"),
        part("VentFR", [0.18, 0.6, 0.14], [0.58, -0.12, 1.52], color=darken(C, 0.1), material="Metal"),
        part("AccentHazard", [1.95, 0.16, 0.14], [0, -0.88, 1.42], color=A, material="Neon", role="hazard_stripe"),
        # Head / visor
        part("HeadDome", [1.95, 1.18, 1.65], [0, 1.58, 0.22], color=Pl, material="Metal"),
        part("HeadCap", [1.58, 0.34, 1.28], [0, 2.25, 0.16], color=Pd, material="Metal"),
        part("VisorRecess", [1.9, 0.88, 0.38], [0, 1.42, 1.08], color=C, material="Metal", role="carbon_dark"),
        part("GlowVisor", [1.7, 0.6, 0.3], [0, 1.42, 1.38], color=V, material="Neon", role="emissive_strip"),
        part("GlowVisorCore", [0.58, 0.72, 0.22], [0, 1.42, 1.58], color=lighten(V, 0.25), material="Neon"),
        part("VisorBrow", [1.95, 0.18, 0.48], [0, 1.95, 1.02], color=S, material="Metal"),
        part("VisorChin", [1.45, 0.14, 0.32], [0, 1.05, 1.25], color=Sd, material="Metal"),
        part("GlowSlitL", [0.22, 0.42, 0.14], [-1.02, 1.38, 1.22], color=V, material="Neon"),
        part("GlowSlitR", [0.22, 0.42, 0.14], [1.02, 1.38, 1.22], color=V, material="Neon"),
        # Cheeks / pauldrons
        part("CheekL", [0.72, 1.45, 1.25], [-1.95, 0.42, 0.42], color=Pd, material="Metal"),
        part("CheekR", [0.72, 1.45, 1.25], [1.95, 0.42, 0.42], color=Pd, material="Metal"),
        part("CheekVentL", [0.18, 0.75, 0.75], [-2.3, 0.38, 0.52], color=C, material="Metal"),
        part("CheekVentR", [0.18, 0.75, 0.75], [2.3, 0.38, 0.52], color=C, material="Metal"),
        part("PauldronL", [1.25, 0.9, 1.4], [-2.25, 1.18, 0.05], color=P, material="Metal"),
        part("PauldronR", [1.25, 0.9, 1.4], [2.25, 1.18, 0.05], color=P, material="Metal"),
        part("PauldronCapL", [1.0, 0.3, 1.1], [-2.3, 1.65, 0.05], color=Pd, material="DiamondPlate", role="scratched_steel"),
        part("PauldronCapR", [1.0, 0.3, 1.1], [2.3, 1.65, 0.05], color=Pd, material="DiamondPlate", role="scratched_steel"),
        part("ShoulderPivotL", [0.68, 0.52, 0.68], [-2.0, 0.88, 0], color=S, material="Metal", shape="Cylinder"),
        part("ShoulderPivotR", [0.68, 0.52, 0.68], [2.0, 0.88, 0], color=S, material="Metal", shape="Cylinder"),
        # Hip
        part("HipDisk", [1.0, 0.42, 1.0], [0, -1.22, 0.05], color=S, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("HipYoke", [2.95, 0.48, 1.6], [0, -1.52, 0.12], color=S, material="Metal"),
        part("PelvisPlate", [2.35, 0.3, 1.2], [0, -1.85, 0.28], color=C, material="Metal"),
        part("SkirtL", [0.58, 0.8, 1.1], [-1.65, -1.42, 0.32], color=Pd, material="Metal"),
        part("SkirtR", [0.58, 0.8, 1.1], [1.65, -1.42, 0.32], color=Pd, material="Metal"),
        # Back
        part("BackPack", [2.25, 1.55, 0.75], [0, 0.32, -1.4], color=C, material="Metal", role="carbon_dark"),
        part("BackPackLid", [1.95, 0.22, 0.58], [0, 1.15, -1.4], color=Sd, material="Metal"),
        part("ThrusterL", [0.58, 0.58, 0.8], [-0.58, 0.18, -1.9], color=S, material="Metal", shape="Cylinder"),
        part("ThrusterR", [0.58, 0.58, 0.8], [0.58, 0.18, -1.9], color=S, material="Metal", shape="Cylinder"),
        part("GlowExhaustL", [0.34, 0.34, 0.22], [-0.58, 0.18, -2.35], color=V, material="Neon"),
        part("GlowExhaustR", [0.34, 0.34, 0.22], [0.58, 0.18, -2.35], color=V, material="Neon"),
        part("Antenna", [0.14, 1.1, 0.14], [1.18, 2.3, -0.38], color=S, material="Metal"),
        part("AntennaTip", [0.2, 0.2, 0.2], [1.18, 2.88, -0.38], color=A, material="Neon"),
        part("SensorPod", [0.38, 0.38, 0.38], [-1.05, 2.05, 0.42], color=S, material="Metal", shape="Ball"),
        part("GlowSensor", [0.2, 0.2, 0.14], [-1.05, 2.05, 0.65], color=V, material="Neon"),
    ]
    # Theme-specific silhouette accents
    if tid == "scrap":
        kids += [
            part("RustPatchL", [0.85, 0.55, 0.18], [-1.1, 0.55, 1.35], color=rgb(140, 90, 55), material="CorrodedMetal"),
            part("RustPatchR", [0.7, 0.4, 0.16], [1.2, -0.2, 1.35], color=rgb(150, 85, 50), material="CorrodedMetal"),
            part("CageRibL", [0.2, 2.1, 1.9], [-1.85, 0.1, 0], color=Sd, material="Metal"),
            part("CageRibR", [0.2, 2.1, 1.9], [1.85, 0.1, 0], color=Sd, material="Metal"),
            part("CageCross", [3.1, 0.16, 0.16], [0, 0.6, 0.95], color=S, material="Metal"),
        ]
    elif tid == "arctic":
        kids += [
            part("IceFinL", [0.16, 1.35, 0.85], [-1.75, 0.7, -0.55], color=Pl, material="Glass", transparency=0.25),
            part("IceFinR", [0.16, 1.35, 0.85], [1.75, 0.7, -0.55], color=Pl, material="Glass", transparency=0.25),
            part("FrostCrest", [0.22, 1.2, 0.55], [0, 1.9, 0.85], color=lighten(V, 0.2), material="Glass", transparency=0.3),
            part("IceSkirt", [2.6, 0.2, 1.3], [0, -1.95, 0.45], color=Pl, material="Metal"),
            part("RimePlate", [1.8, 0.55, 0.2], [0, 0.7, 1.55], color=lighten(P, 0.15), material="Metal"),
        ]
    elif tid == "desert":
        kids += [
            part("SandSkirtL", [0.7, 0.95, 1.2], [-1.8, -1.35, 0.4], color=Pd, material="Metal"),
            part("SandSkirtR", [0.7, 0.95, 1.2], [1.8, -1.35, 0.4], color=Pd, material="Metal"),
            part("DuneNose", [1.5, 0.75, 0.7], [0, 0.05, 1.45], color=Pl, material="Metal"),
            part("HeatSinkL", [0.2, 0.9, 0.7], [-2.05, 0.2, 0.9], color=Sd, material="Metal"),
            part("HeatSinkR", [0.2, 0.9, 0.7], [2.05, 0.2, 0.9], color=Sd, material="Metal"),
            part("OchreBand", [3.4, 0.18, 2.1], [0, -0.2, 0.1], color=A, material="Neon"),
        ]
    else:  # neon
        kids += [
            part("NeonTubeL", [0.12, 2.0, 0.12], [-1.55, 0.2, 1.15], color=V, material="Neon"),
            part("NeonTubeR", [0.12, 2.0, 0.12], [1.55, 0.2, 1.15], color=A, material="Neon"),
            part("NeonRing", [2.4, 0.12, 2.4], [0, 0.9, 0.1], color=V, material="Neon"),
            part("MagPlate", [2.0, 0.85, 0.22], [0, 0.25, 1.5], color=t["paint_light"], material="Metal"),
            part("GlowMagCore", [0.55, 0.55, 0.2], [0, 0.25, 1.7], color=A, material="Neon"),
            part("NightFin", [0.18, 1.4, 1.0], [0, 0.8, -1.55], color=Pd, material="Metal"),
        ]
    for i, y in enumerate((-0.25, 0.15, 0.55, 0.95)):
        kids.append(vent(f"SideVentL{i}", [-1.85, y, 0.98], C, [0.14, 0.32, 0.12]))
        kids.append(vent(f"SideVentR{i}", [1.85, y, 0.98], C, [0.14, 0.32, 0.12]))
    for i, y in enumerate((0.05, 0.4, 0.75, 1.05)):
        kids.append(vent(f"BackVent{i}", [-0.55 + i * 0.35, 0.55, -1.75], C, [0.14, 0.55, 0.12]))
    for i, p in enumerate(
        [
            [-1.25, 0.95, 1.18],
            [1.25, 0.95, 1.18],
            [-1.05, -0.45, 1.25],
            [1.05, -0.45, 1.25],
            [-0.75, 1.95, 0.8],
            [0.75, 1.95, 0.8],
            [-2.25, 1.2, 0.75],
            [2.25, 1.2, 0.75],
            [-0.9, 0.55, 1.5],
            [0.9, 0.55, 1.5],
        ]
    ):
        kids.append(bolt(f"HullBolt{i}", p, Sd))
    return kids


def kit_leg(t: dict, side: str) -> list[dict]:
    P, Pd, A, V, S, Sd, C, R = (
        t["paint"],
        t["paint_dark"],
        t["accent"],
        t["visor"],
        t["steel"],
        t["steel_dark"],
        t["char"],
        t["rubber"],
    )
    s = -1.0 if side == "l" else 1.0
    kids = [
        part("HipBall", [0.98, 0.72, 0.98], [0.05 * s, 1.05, 0.05], color=C, material="Metal", shape="Ball", role="scratched_steel"),
        part("HipPin", [0.26, 0.58, 0.26], [0.52 * s, 1.05, 0.05], color=S, material="Metal", shape="Cylinder"),
        part("Thigh", [1.18, 1.08, 1.28], [0.12 * s, 0.45, 0.32], color=P, material="Metal"),
        part("ThighArmor", [1.02, 0.58, 1.02], [0.14 * s, 0.62, 0.58], color=Pd, material="DiamondPlate", role="scratched_steel"),
        part("ThighPlate", [0.26, 0.9, 1.0], [0.78 * s, 0.45, 0.38], color=Pd, material="Metal"),
        part("ThighSeam", [1.08, 0.08, 1.18], [0.12 * s, 0.18, 0.38], color=C, material="Metal"),
        part("ThighPanel", [0.85, 0.55, 0.28], [0.12 * s, 0.5, 0.9], color=darken(P, 0.1), material="Metal"),
        part("KneeDisk", [1.12, 0.4, 1.12], [0.15 * s, -0.25, 0.62], color=S, material="Metal", shape="Cylinder", role="scratched_steel"),
        part("KneeCap", [0.72, 0.48, 0.38], [0.15 * s, -0.15, 1.08], color=Sd, material="Metal"),
        part("KneePin", [0.28, 0.68, 0.28], [0.72 * s, -0.25, 0.62], color=A, material="Neon"),
        part("Shin", [1.08, 1.25, 1.18], [0.1 * s, -1.02, 0.38], color=P, material="Metal"),
        part("ShinGuard", [0.95, 0.8, 0.38], [0.1 * s, -0.92, 0.88], color=Pd, material="Metal"),
        part("ShinBrace", [0.22, 1.0, 0.55], [0.68 * s, -0.98, 0.42], color=C, material="Metal"),
        part("PistonRod", [0.18, 0.9, 0.18], [0.38 * s, -0.72, 0.05], color=S, material="Metal", shape="Cylinder"),
        part("Ankle", [1.18, 0.38, 1.12], [0.05 * s, -1.62, 0.48], color=S, material="Metal"),
        part("Boot", [1.55, 0.45, 1.85], [0.05 * s, -1.98, 0.62], color=R, material="SmoothPlastic", role="matte_rubber"),
        part("SolePlate", [1.4, 0.12, 1.6], [0.05 * s, -2.22, 0.58], color=C, material="Metal"),
        part("ToeLip", [1.35, 0.28, 0.42], [0.05 * s, -1.82, 1.42], color=Pd, material="Metal"),
        part("Heel", [1.08, 0.3, 0.42], [0.05 * s, -1.92, -0.22], color=Sd, material="Metal"),
        part("AccentShin", [0.16, 0.7, 0.12], [0.58 * s, -1.08, 0.98], color=V, material="Neon"),
        part("GlowAnkle", [0.24, 0.14, 0.14], [0.48 * s, -1.55, 0.95], color=A, material="Neon"),
    ]
    if t["id"] == "arctic":
        kids += [
            part("IceToe", [1.2, 0.22, 0.55], [0.05 * s, -1.85, 1.55], color=t["paint_light"], material="Glass", transparency=0.3),
            part("SkiBlade", [0.35, 0.12, 1.6], [0.55 * s, -2.15, 0.5], color=S, material="Metal"),
        ]
    elif t["id"] == "desert":
        kids += [
            part("SandPad", [1.6, 0.18, 1.7], [0.05 * s, -2.25, 0.55], color=Pd, material="Metal"),
            part("DustGuard", [1.0, 0.45, 0.25], [0.1 * s, -0.7, 1.05], color=t["paint_light"], material="Metal"),
        ]
    elif t["id"] == "neon":
        kids += [
            part("NeonKnee", [0.9, 0.12, 0.9], [0.15 * s, -0.25, 0.62], color=V, material="Neon"),
            part("NeonShin", [0.12, 0.9, 0.12], [0.55 * s, -1.05, 0.95], color=A, material="Neon"),
        ]
    else:
        kids += [
            part("RustShin", [0.55, 0.4, 0.2], [0.1 * s, -1.15, 1.05], color=rgb(130, 80, 50), material="CorrodedMetal"),
        ]
    for i, y in enumerate((-0.8, -1.0, -1.2, -1.4)):
        kids.append(vent(f"ShinVent{i}", [0.1 * s, y, 1.05], C, [0.55, 0.1, 0.1]))
    for i, p in enumerate(
        [
            [0.52 * s, 0.72, 0.95],
            [0.48 * s, -0.92, 1.0],
            [-0.38 * s, 0.32, 0.9],
            [0.42 * s, -1.72, 1.25],
            [0.35 * s, 0.2, 0.85],
        ]
    ):
        kids.append(bolt(f"LegBolt{i}", p, Sd))
    return kids


def kit_gatling(t: dict) -> list[dict]:
    P, Pd, A, V, S, Sd, C, R = (
        t["paint"],
        t["paint_dark"],
        t["accent"],
        t["visor"],
        t["steel"],
        t["steel_dark"],
        t["char"],
        t["rubber"],
    )
    kids = [
        part("Mount", [0.92, 0.72, 0.72], [0, 0, -0.9], color=C, material="Metal"),
        part("MountCollar", [1.02, 0.22, 1.02], [0, 0, -0.55], color=S, material="Metal", shape="Cylinder"),
        part("Forearm", [1.02, 0.88, 1.45], [0, -0.05, 0.05], color=S, material="Metal"),
        part("ForearmPlate", [0.88, 0.58, 0.95], [0, 0.28, 0.22], color=Sd, material="DiamondPlate", role="scratched_steel"),
        part("Receiver", [1.18, 1.05, 1.2], [0, 0.05, 1.02], color=darken(S, 0.1), material="Metal"),
        part("ReceiverTop", [0.95, 0.38, 0.9], [0, 0.58, 1.08], color=Pd, material="Metal"),
        part("CoolingJacket", [0.98, 0.98, 0.95], [0, 0.05, 1.65], color=Sd, material="Metal", shape="Cylinder"),
        part("BarrelA", [0.28, 0.28, 1.7], [-0.3, 0.24, 2.2], color=C, material="Metal", shape="Cylinder"),
        part("BarrelB", [0.28, 0.28, 1.7], [0.3, 0.24, 2.2], color=C, material="Metal", shape="Cylinder"),
        part("BarrelC", [0.28, 0.28, 1.7], [0, -0.2, 2.2], color=C, material="Metal", shape="Cylinder"),
        part("BarrelD", [0.22, 0.22, 1.4], [0, 0.38, 2.05], color=Sd, material="Metal", shape="Cylinder"),
        part("GlowMuzzleA", [0.22, 0.22, 0.14], [-0.3, 0.24, 3.1], color=A, material="Neon"),
        part("GlowMuzzleB", [0.22, 0.22, 0.14], [0.3, 0.24, 3.1], color=A, material="Neon"),
        part("GlowMuzzleC", [0.22, 0.22, 0.14], [0, -0.2, 3.1], color=A, material="Neon"),
        part("BeltBox", [0.72, 0.58, 0.65], [0.78, -0.15, 0.78], color=P, material="Metal"),
        part("BeltFeed", [0.2, 0.2, 0.8], [0.48, 0.15, 1.18], color=V, material="Neon"),
        part("Mag", [0.48, 0.68, 0.42], [-0.72, -0.25, 0.88], color=C, material="Metal"),
        part("Grip", [0.4, 0.58, 0.4], [0, -0.72, 0.15], color=R, material="SmoothPlastic", role="matte_rubber"),
        part("Sight", [0.14, 0.38, 0.48], [0, 0.72, 0.58], color=S, material="Metal"),
        part("GlowSight", [0.1, 0.1, 0.12], [0, 0.92, 0.72], color=V, material="Neon"),
    ]
    for i, z in enumerate((0.35, 0.65, 0.95, 1.25, 1.5)):
        kids.append(vent(f"CoolVent{i}", [0, 0.58, z], C, [0.72, 0.1, 0.1]))
    for i, p in enumerate([[-0.42, 0.38, 0.55], [0.42, 0.38, 0.55], [0, -0.38, 1.45], [0.58, 0.38, 1.35], [-0.5, -0.1, 1.2]]):
        kids.append(bolt(f"GunBolt{i}", p, Sd))
    return kids


def kit_sidearm(t: dict) -> list[dict]:
    P, Pd, A, V, S, Sd, C, R = (
        t["paint"],
        t["paint_dark"],
        t["accent"],
        t["visor"],
        t["steel"],
        t["steel_dark"],
        t["char"],
        t["rubber"],
    )
    lower_r = t["kits"]["lower_r"]
    if "aegis" in lower_r:
        return [
            part("Mount", [0.85, 0.65, 0.65], [0, 0, -0.95], color=C, material="Metal"),
            part("MountCollar", [0.95, 0.2, 0.95], [0, 0, -0.6], color=S, material="Metal", shape="Cylinder"),
            part("Brace", [0.7, 0.55, 0.95], [0, 0, -0.25], color=S, material="Metal"),
            part("Face", [1.7, 2.15, 0.28], [0, 0.15, 0.85], color=P, material="DiamondPlate", role="scratched_steel"),
            part("FaceRimT", [1.85, 0.14, 0.14], [0, 1.25, 1.0], color=S, material="Metal"),
            part("FaceRimB", [1.85, 0.14, 0.14], [0, -0.95, 1.0], color=S, material="Metal"),
            part("FaceRimL", [0.14, 2.0, 0.14], [-0.9, 0.15, 1.0], color=Sd, material="Metal"),
            part("FaceRimR", [0.14, 2.0, 0.14], [0.9, 0.15, 1.0], color=Sd, material="Metal"),
            part("Boss", [0.55, 0.55, 0.28], [0, 0.2, 1.1], color=Sd, material="Metal"),
            part("GlowBoss", [0.35, 0.35, 0.14], [0, 0.2, 1.28], color=V, material="Neon"),
            part("LipTop", [1.5, 0.22, 0.32], [0, 1.15, 0.85], color=Pd, material="Metal"),
            part("LipBot", [1.4, 0.18, 0.28], [0, -0.85, 0.85], color=Pd, material="Metal"),
            part("IceEdge", [1.55, 0.12, 0.12], [0, 0.9, 1.15], color=V, material="Neon"),
            part("IcePane", [1.3, 1.5, 0.1], [0, 0.15, 1.05], color=lighten(P, 0.2), material="Glass", transparency=0.35),
            part("SideBraceL", [0.18, 1.4, 0.4], [-0.75, 0.1, 0.55], color=S, material="Metal"),
            part("SideBraceR", [0.18, 1.4, 0.4], [0.75, 0.1, 0.55], color=S, material="Metal"),
            bolt("ShieldBolt0", [-0.55, 0.85, 1.05], Sd),
            bolt("ShieldBolt1", [0.55, 0.85, 1.05], Sd),
            bolt("ShieldBolt2", [-0.55, -0.55, 1.05], Sd),
            bolt("ShieldBolt3", [0.55, -0.55, 1.05], Sd),
            bolt("ShieldBolt4", [0, 0.55, 1.15], Sd),
            vent("ShieldVent0", [0, 0.55, 1.15], C, [0.7, 0.12, 0.1]),
            vent("ShieldVent1", [0, -0.2, 1.15], C, [0.7, 0.12, 0.1]),
            vent("ShieldVent2", [0, -0.55, 1.15], C, [0.7, 0.12, 0.1]),
        ]
    if "lance" in lower_r:
        return [
            part("Mount", [0.85, 0.65, 0.65], [0, 0, -0.95], color=C, material="Metal"),
            part("MountCollar", [0.95, 0.2, 0.95], [0, 0, -0.6], color=S, material="Metal", shape="Cylinder"),
            part("Housing", [0.85, 0.75, 1.2], [0, 0.1, 0], color=P, material="Metal"),
            part("HousingPlate", [0.7, 0.5, 0.85], [0, 0.3, 0.25], color=Pd, material="DiamondPlate", role="scratched_steel"),
            part("Crystal", [0.42, 0.42, 0.65], [0, 0.15, 0.85], color=V, material="Glass", transparency=0.2),
            part("Emitter", [0.35, 0.35, 1.8], [0, 0.15, 1.85], color=S, material="Metal", shape="Cylinder"),
            part("GlowBeam", [0.14, 0.14, 1.7], [0, 0.15, 1.85], color=V, material="Neon"),
            part("FocusRing", [0.7, 0.14, 0.7], [0, 0.15, 0.5], color=S, material="Metal", shape="Cylinder"),
            part("FocusRing2", [0.58, 0.12, 0.58], [0, 0.15, 1.15], color=lighten(S, 0.1), material="Metal", shape="Cylinder"),
            part("Muzzle", [0.48, 0.48, 0.22], [0, 0.15, 2.85], color=A, material="Neon"),
            part("BatteryPack", [0.48, 0.58, 0.42], [0.55, -0.15, -0.1], color=Sd, material="Metal"),
            part("MagTrace", [0.1, 0.1, 0.9], [0.35, 0.45, 0.4], color=A, material="Neon"),
            part("SideRail", [0.14, 0.28, 1.1], [-0.45, 0.05, 0.7], color=Sd, material="Metal"),
            part("CoilRing", [0.85, 0.12, 0.85], [0, 0.15, 2.2], color=A, material="Neon"),
            bolt("LanceBolt0", [-0.32, 0.35, 0.4], Sd),
            bolt("LanceBolt1", [0.32, 0.35, 0.4], Sd),
            bolt("LanceBolt2", [0, -0.25, 0.5], Sd),
            vent("LanceVent0", [0, 0.55, 0.2], C, [0.55, 0.1, 0.1]),
            vent("LanceVent1", [0, 0.55, 0.5], C, [0.55, 0.1, 0.1]),
            vent("LanceVent2", [0, 0.55, 0.8], C, [0.55, 0.1, 0.1]),
        ]
    if "cleaver" in lower_r:
        return [
            part("Mount", [0.85, 0.65, 0.65], [0, 0, -0.95], color=C, material="Metal"),
            part("MountCollar", [0.95, 0.2, 0.95], [0, 0, -0.6], color=S, material="Metal", shape="Cylinder"),
            part("Haft", [0.42, 0.42, 1.35], [0, 0, -0.1], color=S, material="Metal"),
            part("HaftWrap", [0.48, 0.48, 0.55], [0, 0, -0.5], color=R, material="SmoothPlastic", role="matte_rubber"),
            part("Guard", [1.15, 0.24, 0.85], [0, 0.38, 0.55], color=P, material="Metal"),
            part("GuardSpikeL", [0.2, 0.38, 0.35], [-0.55, 0.5, 0.6], color=Sd, material="Metal"),
            part("GuardSpikeR", [0.2, 0.38, 0.35], [0.55, 0.5, 0.6], color=Sd, material="Metal"),
            part("Blade", [0.18, 0.7, 2.1], [0, 0.12, 1.55], color=lighten(P, 0.12), material="Metal"),
            part("BladeSpine", [0.24, 0.28, 2.0], [0, 0.38, 1.55], color=Sd, material="Metal"),
            part("BladePlate", [0.12, 0.45, 1.4], [-0.12, 0.05, 1.5], color=Pd, material="Metal"),
            part("GlowEdge", [0.08, 0.55, 1.95], [0.14, 0.12, 1.55], color=A, material="Neon"),
            part("Pommel", [0.48, 0.48, 0.32], [0, 0, -1.0], color=S, material="Metal"),
            part("PommelRing", [0.55, 0.12, 0.55], [0, 0, -0.85], color=A, material="Neon"),
            bolt("BladeBolt0", [0, 0.38, 0.95], Sd),
            bolt("BladeBolt1", [0, 0.38, 1.65], Sd),
            bolt("BladeBolt2", [0, 0.2, 1.2], Sd),
            vent("BladeVent0", [0, 0.55, 0.7], C, [0.5, 0.1, 0.1]),
            vent("BladeVent1", [0, 0.55, 1.1], C, [0.5, 0.1, 0.1]),
            vent("BladeVent2", [0, 0.55, 1.5], C, [0.5, 0.1, 0.1]),
        ]
    kids = [
        part("Mount", [0.88, 0.68, 0.68], [0, 0, -0.95], color=C, material="Metal"),
        part("MountCollar", [0.98, 0.2, 0.98], [0, 0, -0.6], color=S, material="Metal", shape="Cylinder"),
        part("Receiver", [0.98, 0.85, 1.55], [0, 0, 0.05], color=S, material="Metal"),
        part("ReceiverPlate", [0.82, 0.52, 1.05], [0, 0.32, 0.22], color=Sd, material="DiamondPlate", role="scratched_steel"),
        part("Breech", [0.78, 0.68, 0.58], [0, 0.05, -0.55], color=C, material="Metal"),
        part("Barrel", [0.4, 0.4, 1.75], [0, 0.12, 1.6], color=C, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.58, 0.58, 0.75], [0, 0.12, 0.98], color=Sd, material="Metal", shape="Cylinder"),
        part("BarrelRing", [0.52, 0.12, 0.52], [0, 0.12, 1.95], color=S, material="Metal", shape="Cylinder"),
        part("Mag", [0.52, 0.72, 0.42], [0, -0.62, 0.22], color=P, material="Metal"),
        part("MagLip", [0.58, 0.12, 0.48], [0, -0.98, 0.22], color=Pd, material="Metal"),
        part("Sight", [0.16, 0.42, 0.52], [0, 0.58, 0.58], color=V, material="Neon"),
        part("Muzzle", [0.5, 0.5, 0.3], [0, 0.12, 2.55], color=A, material="Neon"),
        part("UnderRail", [0.34, 0.18, 1.05], [0, -0.38, 0.98], color=Sd, material="Metal"),
        part("Grip", [0.32, 0.48, 0.32], [0, -0.58, -0.25], color=R, material="SmoothPlastic", role="matte_rubber"),
        part("AccentHazard", [0.75, 0.12, 0.12], [0, -0.38, 0.42], color=A, material="Neon", role="hazard_stripe"),
    ]
    for i, z in enumerate((0.0, 0.35, 0.7, 1.0)):
        kids.append(vent(f"RecvVent{i}", [0, 0.52, z], C, [0.58, 0.1, 0.1]))
    for i, p in enumerate([[-0.42, 0.32, 0.42], [0.42, 0.32, 0.42], [0, -0.22, 1.35]]):
        kids.append(bolt(f"SideBolt{i}", p, Sd))
    return kids


def kit_shoulder(t: dict) -> list[dict]:
    P, Pd, A, V, S, Sd, C = t["paint"], t["paint_dark"], t["accent"], t["visor"], t["steel"], t["steel_dark"], t["char"]
    kids = [
        part("ShoulderMount", [1.28, 0.58, 1.08], [0, -0.2, -0.6], color=C, material="Metal"),
        part("MountBrace", [1.05, 0.28, 0.85], [0, 0.18, -0.45], color=Sd, material="Metal"),
        part("Breech", [1.45, 1.15, 1.5], [0, 0.32, 0.22], color=P, material="Metal"),
        part("BreechPlate", [1.2, 0.75, 0.95], [0, 0.48, 0.55], color=Pd, material="DiamondPlate", role="scratched_steel"),
        part("Collar", [1.55, 0.34, 1.55], [0, 0.32, 0.95], color=S, material="Metal", shape="Cylinder"),
        part("Barrel", [0.68, 0.68, 2.4], [0, 0.38, 2.15], color=Sd, material="Metal", shape="Cylinder"),
        part("BarrelSleeve", [0.95, 0.95, 1.0], [0, 0.38, 1.58], color=darken(S, 0.15), material="Metal", shape="Cylinder"),
        part("BarrelRing", [0.85, 0.16, 0.85], [0, 0.38, 2.75], color=S, material="Metal", shape="Cylinder"),
        part("GlowBore", [0.45, 0.45, 0.3], [0, 0.38, 3.4], color=V, material="Neon"),
        part("FinL", [0.18, 0.75, 1.2], [-0.85, 0.65, 0.48], color=Pd, material="Metal"),
        part("FinR", [0.18, 0.75, 1.2], [0.85, 0.65, 0.48], color=Pd, material="Metal"),
        part("FinTipL", [0.14, 0.42, 0.58], [-0.9, 0.9, 0.95], color=C, material="Metal"),
        part("FinTipR", [0.14, 0.42, 0.58], [0.9, 0.9, 0.95], color=C, material="Metal"),
        part("AccentHazard", [1.2, 0.16, 0.16], [0, -0.38, 0.58], color=A, material="Neon", role="hazard_stripe"),
        part("AmmoDrum", [0.85, 0.85, 0.85], [1.0, -0.1, -0.05], color=C, material="Metal", shape="Cylinder"),
        part("AmmoCap", [0.58, 0.22, 0.58], [1.0, 0.38, -0.05], color=S, material="Metal", shape="Cylinder"),
        part("SideRail", [0.22, 0.38, 1.35], [-0.78, 0.18, 0.75], color=Sd, material="Metal"),
    ]
    if t["id"] == "neon":
        kids += [
            part("PodTubeA", [0.35, 0.35, 1.3], [-0.4, 0.85, 1.0], color=V, material="Metal", shape="Cylinder"),
            part("PodTubeB", [0.35, 0.35, 1.3], [0.4, 0.85, 1.0], color=A, material="Metal", shape="Cylinder"),
            part("GlowPodA", [0.22, 0.22, 0.12], [-0.4, 0.85, 1.7], color=V, material="Neon"),
            part("GlowPodB", [0.22, 0.22, 0.12], [0.4, 0.85, 1.7], color=A, material="Neon"),
        ]
    for i, z in enumerate((0.05, 0.4, 0.75, 1.05)):
        kids.append(vent(f"BreechVent{i}", [0, 0.95, z], C, [0.95, 0.1, 0.1]))
    for i, p in enumerate([[-0.55, 0.75, 0.85], [0.55, 0.75, 0.85], [-0.58, 0.12, 1.25], [0.58, 0.12, 1.25], [0, 0.7, 1.1]]):
        kids.append(bolt(f"CannonBolt{i}", p, Sd))
    return kids


def kit_battery(t: dict) -> list[dict]:
    P, A, V, S, Sd, C = t["paint"], t["accent"], t["visor"], t["steel"], t["steel_dark"], t["char"]
    kids = [
        part("Cell", [1.5, 0.9, 0.65], [0, 0, 0], color=C, material="Metal", role="carbon_dark"),
        part("CellCap", [1.35, 0.2, 0.55], [0, 0.55, 0], color=Sd, material="Metal"),
        part("Terminal", [0.32, 0.32, 0.24], [0.48, 0.42, 0.38], color=A, material="Neon"),
        part("TerminalNeg", [0.32, 0.32, 0.24], [-0.48, 0.42, 0.38], color=S, material="Metal"),
        part("Stripe", [1.2, 0.12, 0.1], [0, 0.15, 0.38], color=V, material="Neon"),
        part("ClampL", [0.18, 0.7, 0.48], [-0.78, 0, 0], color=S, material="Metal"),
        part("ClampR", [0.18, 0.7, 0.48], [0.78, 0, 0], color=S, material="Metal"),
        part("CellBand", [1.55, 0.12, 0.7], [0, -0.2, 0], color=P, material="Metal"),
    ]
    for i, x in enumerate((-0.4, 0.0, 0.4)):
        kids.append(vent(f"BatVent{i}", [x, -0.15, 0.38], C, [0.12, 0.42, 0.08]))
    kids += [bolt("BatBolt0", [-0.52, 0.32, 0.32], Sd), bolt("BatBolt1", [0.52, 0.32, 0.32], Sd)]
    return kids


def kit_cpu(t: dict) -> list[dict]:
    Pd, V, S, Sd, C = t["paint_dark"], t["visor"], t["steel"], t["steel_dark"], t["char"]
    return [
        part("Board", [0.75, 0.12, 0.75], [0, 0, 0], color=Pd, material="Metal"),
        part("Die", [0.38, 0.24, 0.38], [0, 0.2, 0], color=C, material="Metal"),
        part("GlowPin", [0.15, 0.15, 0.15], [0.24, 0.15, 0.24], color=V, material="Neon"),
        part("HeatSink", [0.55, 0.24, 0.24], [0, 0.38, -0.15], color=S, material="Metal"),
        part("TraceA", [0.42, 0.04, 0.06], [-0.1, 0.08, 0.28], color=V, material="Neon"),
        part("TraceB", [0.06, 0.04, 0.38], [0.28, 0.08, -0.05], color=V, material="Neon"),
        part("TraceC", [0.35, 0.04, 0.06], [0.05, 0.08, -0.28], color=t["accent"], material="Neon"),
        bolt("CpuBolt0", [-0.3, 0.08, -0.3], Sd, r=0.08),
        bolt("CpuBolt1", [0.3, 0.08, -0.3], Sd, r=0.08),
        bolt("CpuBolt2", [-0.3, 0.08, 0.3], Sd, r=0.08),
    ]


def kit_drone(t: dict) -> list[dict]:
    P, V, S, Sd, C, R = t["paint"], t["visor"], t["steel"], t["steel_dark"], t["char"], t["rubber"]
    return [
        part("Body", [1.0, 0.42, 1.1], [0, 0, 0], color=S, material="Metal"),
        part("BodyCap", [0.8, 0.16, 0.85], [0, 0.28, 0], color=Sd, material="Metal"),
        part("Eye", [0.38, 0.22, 0.2], [0, 0.22, 0.58], color=V, material="Neon"),
        part("Rotor", [0.7, 0.1, 0.7], [0, 0.42, -0.22], color=C, material="Metal"),
        part("SkidL", [0.14, 0.18, 0.75], [-0.42, -0.32, 0], color=R, material="SmoothPlastic", role="matte_rubber"),
        part("SkidR", [0.14, 0.18, 0.75], [0.42, -0.32, 0], color=R, material="SmoothPlastic", role="matte_rubber"),
        part("Accent", [0.7, 0.08, 0.08], [0, 0.1, 0.5], color=t["accent"], material="Neon"),
        bolt("DroneBolt0", [-0.32, 0.15, 0.32], Sd, r=0.08),
        bolt("DroneBolt1", [0.32, 0.15, 0.32], Sd, r=0.08),
        vent("DroneVent0", [0, 0.05, -0.5], C, [0.5, 0.2, 0.1]),
    ]


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


def build_showcase(t: dict) -> dict:
    kids: list[dict] = []
    kids += offset_parts(kit_torso(t), *SOCK["torso"], "Torso")
    kids += offset_parts(kit_leg(t, "l"), *SOCK["hip_l"], "LegL")
    kids += offset_parts(kit_leg(t, "r"), *SOCK["hip_r"], "LegR")
    kids += offset_parts(kit_gatling(t), *SOCK["lower_l"], "ArmL")
    kids += offset_parts(kit_sidearm(t), *SOCK["lower_r"], "ArmR")
    kids += offset_parts(kit_shoulder(t), *SOCK["shoulder_r"], "ShoulderR")
    kids += offset_parts(kit_battery(t), *SOCK["battery"], "Battery")
    kids += offset_parts(kit_cpu(t), *SOCK["cpu"], "CPU")
    kids += offset_parts(kit_drone(t), *SOCK["drone"], "Drone")
    kids.append(
        part(
            "ShowcasePad",
            [6.5, 0.35, 4.5],
            [0, -TORSO_Y - 0.15, 0.4],
            color=list(c / 255 for c in t["floor"]),
            material="Metal",
            role="metal_plate",
        )
    )
    kids.append(
        part(
            "ShowcaseStripe",
            [5.5, 0.12, 0.25],
            [0, -TORSO_Y + 0.05, 2.4],
            color=t["accent"],
            material="Neon",
            role="hazard_stripe",
        )
    )
    model = pack(kids)
    model["Name"] = t["showcase"]
    model["Attributes"] = {
        "AssemblerShowcase": True,
        "ThemeLine": t["line"],
        "ThemeId": t["id"],
        "Pose": "CombatReady",
        "Camera": "FrontThreeQuarter",
    }
    return model


def write_theme_kits(t: dict) -> None:
    kits = t["kits"]
    mapping = {
        kits["torso"]: kit_torso(t),
        kits["leg_l"]: kit_leg(t, "l"),
        kits["leg_r"]: kit_leg(t, "r"),
        kits["lower_l"]: kit_gatling(t),
        kits["lower_r"]: kit_sidearm(t),
        kits["shoulder"]: kit_shoulder(t),
        kits["battery"]: kit_battery(t),
        kits["cpu"]: kit_cpu(t),
        kits["drone"]: kit_drone(t),
    }
    PARTS.mkdir(parents=True, exist_ok=True)
    for pid, kids in mapping.items():
        write_model(PARTS / f"{pid}.model.json", pack(kids))
        print(f"  [{t['id']}] kit {pid}: {len(kids)} parts")


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------


def project_front_3q(x: float, y: float, z: float) -> tuple[float, float, float]:
    az = math.radians(28)
    el = math.radians(16)
    cx = math.sin(az) * math.cos(el)
    cy = math.sin(el)
    cz = math.cos(az) * math.cos(el)
    fx, fy, fz = -cx, -cy, -cz
    rx, rz = fz, -fx
    rlen = math.hypot(rx, rz) or 1.0
    rx, rz = rx / rlen, rz / rlen
    ry = 0.0
    ux = fy * rz - fz * ry
    uy = fz * rx - fx * rz
    uz = fx * ry - fy * rx
    sx = x * rx + y * ry + z * rz
    sy = x * ux + y * uy + z * uz
    depth = -(x * cx + y * cy + z * cz)
    return sx, sy, depth


def render_preview(model: dict, out_path: Path, t: dict) -> None:
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
            (((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)), 1.12),
            (((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), 0.68),
            (((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)), 1.2),
            (((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), 0.58),
            (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), 0.92),
            (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), 0.8),
        ]
        glow = ("Glow" in name) or ("Visor" in name) or ("Accent" in name) or ("Muzzle" in name) or ("Neon" in name)
        for idxs, shade in face_defs:
            proj = [project_front_3q(*corner(*i)) for i in idxs]
            depth = sum(p[2] for p in proj) / 4.0
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

    faces.sort(key=lambda x: x[0])
    W, H = 1200, 960
    bg = t["bg"]
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    # Atmosphere wash
    for i in range(H):
        tt = i / H
        r = int(bg[0] + (t["floor"][0] - bg[0]) * tt * 0.55)
        g = int(bg[1] + (t["floor"][1] - bg[1]) * tt * 0.55)
        b = int(bg[2] + (t["floor"][2] - bg[2]) * tt * 0.55)
        draw.line([(0, i), (W, i)], fill=(r, g, b))
    draw.rectangle([0, int(H * 0.68), W, H], fill=t["floor"])
    draw.ellipse([W * 0.15, H * 0.72, W * 0.85, H * 0.92], fill=tuple(min(255, c + 12) for c in t["floor"]))

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

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 26)
        font_sm = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font

    title = f"Assembler · {t['line']} ({t['id']}) · front 3/4 combat"
    draw.rectangle([24, 20, 920, 78], fill=(10, 12, 16))
    draw.text((36, 28), title, fill=(235, 240, 245), font=font)
    draw.text((36, 56), t["tagline"] + " · dense panels/vents/barrels · combat crouch", fill=(160, 200, 210), font=font_sm)
    draw.text((36, H - 48), f"Showcase/{t['showcase']}  ·  themed kit line", fill=(140, 145, 155), font=font_sm)
    draw.text((36, H - 28), "Original shapes · SM structure only", fill=(110, 115, 125), font=font_sm)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    try:
        print(f"  wrote {out_path.relative_to(ROOT)}")
    except ValueError:
        print(f"  wrote {out_path}")


def main() -> None:
    SHOWCASE.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    scrap_showcase: dict | None = None
    for tid, t in THEMES.items():
        print(f"authoring {t['line']} ({tid})…")
        write_theme_kits(t)
        showcase = build_showcase(t)
        write_model(SHOWCASE / f"{t['showcase']}.model.json", showcase)
        n = len([c for c in showcase["Children"] if c.get("ClassName") == "Part"]) - 1
        print(f"  showcase {t['showcase']}: {n} visible parts")
        render_preview(showcase, PREVIEW_DIR / t["preview"], t)
        render_preview(showcase, MEDIA / t["preview"], t)
        if tid == "scrap":
            scrap_showcase = showcase
    # Keep hero art bar in sync with Yardbone scrap refine
    if scrap_showcase is not None:
        hero = json.loads(json.dumps(scrap_showcase))
        hero["Name"] = "HeroStarterMech"
        attrs = dict(hero.get("Attributes") or {})
        attrs["ArtBar"] = "SuperMechs3D"
        attrs["ThemeLine"] = "Yardbone"
        hero["Attributes"] = attrs
        write_model(SHOWCASE / "HeroStarterMech.model.json", hero)
        render_preview(scrap_showcase, PREVIEW_DIR / "supermechs-3d-preview.png", THEMES["scrap"])
        render_preview(scrap_showcase, MEDIA / "supermechs-3d-preview.png", THEMES["scrap"])
        print("  synced HeroStarterMech + supermechs-3d-preview to Yardbone scrap")
    print("done — themed lines authored")


if __name__ == "__main__":
    main()
