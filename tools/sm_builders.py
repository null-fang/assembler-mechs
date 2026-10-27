"""SuperMechs-inspired chibi kit geometry (structure only — original Assembler parts).

Proportions: big torso + visor, short thick legs, readable guns/pods/blades.
Color language: bold paint hull, gunmetal joints/barrels, Neon visor/muzzle emissives.
"""

from __future__ import annotations

from typing import Callable

# Imported from generate_part_models after helpers exist — set by bind().
part: Callable
wedge: Callable
cf: Callable
rim_front: Callable
inset_front: Callable
joint_cyl: Callable
rgb: Callable
darken: Callable
lighten: Callable
panel_safe: Callable
CAUTION: list[float]

GUNMETAL = None  # set in bind
VISOR_CYAN = None
VISOR_ORANGE = None
VISOR_RED = None


def bind(ns: dict) -> None:
    global part, wedge, cf, rim_front, inset_front, joint_cyl, rgb, darken, lighten, panel_safe, CAUTION
    global GUNMETAL, VISOR_CYAN, VISOR_ORANGE, VISOR_RED
    part = ns["part"]
    wedge = ns["wedge"]
    cf = ns["cf"]
    rim_front = ns["rim_front"]
    inset_front = ns["inset_front"]
    joint_cyl = ns["joint_cyl"]
    rgb = ns["rgb"]
    darken = ns["darken"]
    lighten = ns["lighten"]
    panel_safe = ns["panel_safe"]
    CAUTION = ns["CAUTION"]
    GUNMETAL = rgb(52, 56, 62)
    VISOR_CYAN = rgb(56, 196, 255)
    VISOR_ORANGE = rgb(255, 140, 40)
    VISOR_RED = rgb(255, 70, 55)


def visor(name: str, size: list[float], pos: list[float], color: list[float] | None = None) -> dict:
    return part(name, size, pos, color=color or VISOR_CYAN, material="Neon")


def build_torso(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    panel = darken(base, 0.12)
    gm = GUNMETAL
    vent = darken(gm, 0.15)

    # Shared chibi chassis: fat core + head dome + glowing visor + hip yoke.
    core = [3.4, 2.4, 2.2]
    kids += [
        part("Hull", core, [0, 0.1, 0], color=paint, material="Metal"),
        *rim_front("Hull", core, [0, 0.1, 0], color=panel, thickness=0.1),
        inset_front("ChestInset", core, [0, 0.1, 0], color=panel, material="DiamondPlate", depth=0.14),
        part("HeadDome", [2.0, 1.2, 1.7], [0, 1.55, 0.15], color=lighten(paint, 0.08), material="Metal"),
        visor("GlowVisor", [1.55, 0.55, 0.22], [0, 1.45, 1.05]),
        part("VisorBrow", [1.7, 0.18, 0.35], [0, 1.8, 0.85], color=gm, material="Metal"),
        joint_cyl("HipJoint", [0.9, 0.45, 0.9], [0, -1.25, 0.05], color=gm),
        part("HipYoke", [2.6, 0.45, 1.4], [0, -1.45, 0.1], color=panel, material="Metal"),
        joint_cyl("ShoulderPivotL", [0.7, 0.55, 0.7], [-1.95, 0.85, 0], color=gm),
        joint_cyl("ShoulderPivotR", [0.7, 0.55, 0.7], [1.95, 0.85, 0], color=gm),
    ]

    if style == "cage":
        kids += [
            part("RibL", [0.28, 2.0, 2.0], [-1.75, 0.1, 0], color=gm, material="Metal"),
            part("RibR", [0.28, 2.0, 2.0], [1.75, 0.1, 0], color=gm, material="Metal"),
            part("BackPack", [2.0, 1.2, 0.55], [0, 0.3, -1.25], color=panel, material="Metal"),
            joint_cyl("ExhaustL", [0.4, 0.4, 0.75], [-0.55, 0.7, -1.5], color=vent),
            joint_cyl("ExhaustR", [0.4, 0.4, 0.75], [0.55, 0.7, -1.5], color=vent),
            part("AccentVent", [1.1, 0.55, 0.18], [0, -0.2, 1.25], color=vent, material="Metal"),
        ]
    elif style == "plate":
        kids += [
            part("BreastPlate", [2.6, 1.35, 0.35], [0, 0.2, 1.2], color=panel, material="DiamondPlate"),
            *rim_front("Breast", [2.6, 1.35, 0.35], [0, 0.2, 1.2], color=gm, thickness=0.07),
            part("PauldronL", [1.1, 0.75, 1.15], [-2.05, 1.05, 0], color=panel, material="Metal"),
            part("PauldronR", [1.1, 0.75, 1.15], [2.05, 1.05, 0], color=panel, material="Metal"),
            wedge("SlopeL", [0.85, 0.4, 0.65], cf([-1.95, 1.4, 0.25]), color=panel),
            wedge("SlopeR", [0.85, 0.4, 0.65], cf([1.95, 1.4, 0.25]), color=panel),
            part("BackRadiator", [2.0, 0.8, 0.4], [0, 0.55, -1.2], color=vent, material="Metal"),
        ]
    elif style == "tin":
        kids += [
            part("RingTop", [3.0, 0.55, 1.9], [0, 0.85, 0], color=lighten(paint, 0.1), material="Metal"),
            part("RingBot", [3.1, 0.5, 1.95], [0, -0.55, 0], color=darken(paint, 0.1), material="Metal"),
            part("AccentBand", [3.25, 0.16, 2.05], [0, 0.2, 0], color=VISOR_ORANGE, material="Neon"),
            part("FrontBadge", [0.9, 0.7, 0.18], [0, 0.15, 1.2], color=gm, material="DiamondPlate"),
            joint_cyl("Intake", [0.55, 0.55, 0.65], [0, -0.4, -1.15], color=vent),
        ]
    elif style == "wedge":
        kids += [
            wedge("ArmorSlope", [3.1, 0.75, 1.9], cf([0, 0.95, 0.25]), color=panel, material="DiamondPlate"),
            part("Nose", [1.5, 0.8, 0.7], [0, 0.15, 1.25], color=lighten(paint, 0.1), material="Metal"),
            part("Keel", [2.0, 0.5, 1.6], [0, -1.15, 0.2], color=gm, material="Metal"),
            part("BackFin", [0.28, 1.2, 0.9], [0, 0.7, -1.2], color=vent, material="Metal"),
            visor("GlowCrest", [0.25, 1.1, 0.2], [0, 0.4, 1.2], VISOR_ORANGE),
        ]
    elif style == "rib":
        kids += [
            part("Spine", [1.2, 2.2, 1.3], [0, 0.1, -0.15], color=gm, material="Metal"),
            part("Rib1", [3.15, 0.28, 1.9], [0, 0.7, 0], color=panel, material="Metal"),
            part("Rib2", [3.25, 0.28, 2.0], [0, 0.05, 0], color=panel, material="Metal"),
            part("Rib3", [3.0, 0.28, 1.8], [0, -0.55, 0], color=panel, material="Metal"),
            visor("GlowWireL", [0.12, 1.6, 0.12], [-0.45, 0.2, 0.95]),
            visor("GlowWireR", [0.12, 1.6, 0.12], [0.45, 0.2, 0.95]),
            part("BackCage", [1.7, 1.3, 0.4], [0, 0.2, -1.15], color=vent, material="Metal"),
        ]
    elif style == "rivet":
        kids += [
            part("PlateA", [1.4, 1.15, 0.25], [-0.9, 0.25, 1.2], color=panel, material="DiamondPlate"),
            part("PlateB", [1.4, 1.15, 0.25], [0.9, 0.25, 1.2], color=panel, material="DiamondPlate"),
            *rim_front("PlateA", [1.4, 1.15, 0.25], [-0.9, 0.25, 1.2], color=gm, thickness=0.06),
            *rim_front("PlateB", [1.4, 1.15, 0.25], [0.9, 0.25, 1.2], color=gm, thickness=0.06),
            joint_cyl("Exhaust", [0.45, 0.45, 0.9], [0.7, 0.75, -1.4], color=vent),
            joint_cyl("Exhaust2", [0.45, 0.45, 0.9], [-0.7, 0.75, -1.4], color=vent),
            part("SideCageL", [0.35, 1.9, 1.7], [-1.9, 0.1, 0], color=gm, material="Metal"),
            part("SideCageR", [0.35, 1.9, 1.7], [1.9, 0.1, 0], color=gm, material="Metal"),
        ]
    elif style == "vault":
        face = [2.2, 1.5, 0.3]
        kids += [
            part("FacePlate", face, [0, 0.15, 1.25], color=panel, material="DiamondPlate"),
            *rim_front("Face", face, [0, 0.15, 1.25], color=gm, thickness=0.08),
            inset_front("FaceInset", face, [0, 0.15, 1.25], color=darken(panel, 0.12), material="Metal", depth=0.08),
            visor("GlowLock", [0.35, 0.35, 0.22], [0.45, 0.15, 1.5], VISOR_ORANGE),
            joint_cyl("HingeL", [0.2, 1.4, 0.2], [-1.15, 0.15, 1.2], color=gm),
            joint_cyl("HingeR", [0.2, 1.4, 0.2], [1.15, 0.15, 1.2], color=gm),
            part("BackSafe", [2.2, 1.5, 0.5], [0, 0.15, -1.25], color=darken(paint, 0.15), material="Metal"),
            part("RoofLip", [3.2, 0.28, 1.9], [0, 1.35, 0], color=panel, material="Metal"),
        ]
    elif style == "lattice":
        kids += [
            part("FrameTL", [0.22, 2.3, 0.22], [-1.55, 0.1, -0.85], color=gm, material="Metal"),
            part("FrameTR", [0.22, 2.3, 0.22], [1.55, 0.1, -0.85], color=gm, material="Metal"),
            part("FrameBL", [0.22, 2.3, 0.22], [-1.55, 0.1, 0.85], color=gm, material="Metal"),
            part("FrameBR", [0.22, 2.3, 0.22], [1.55, 0.1, 0.85], color=gm, material="Metal"),
            visor("GlowCross", [2.9, 0.14, 0.14], [0, 0.45, 0.9]),
            part("MeshPanel", [2.7, 0.75, 0.12], [0, 0.7, 1.05], color=vent, material="Metal"),
        ]
    elif style == "bunker":
        kids += [
            part("HullArmor", [3.8, 2.2, 2.4], [0, 0.05, 0], color=paint, material="Concrete"),
            *rim_front("HullArmor", [3.8, 2.2, 2.4], [0, 0.05, 0], color=gm, thickness=0.12),
            wedge("CrestSlope", [3.3, 0.5, 1.7], cf([0, 1.25, 0.15]), color=panel),
            visor("GlowSlit", [1.6, 0.28, 0.2], [0, 0.55, 1.35], VISOR_ORANGE),
            part("SideArmorL", [0.5, 1.9, 2.2], [-2.05, 0.05, 0], color=panel, material="Metal"),
            part("SideArmorR", [0.5, 1.9, 2.2], [2.05, 0.05, 0], color=panel, material="Metal"),
            joint_cyl("Antenna", [0.14, 1.1, 0.14], [1.0, 1.9, -0.5], color=gm),
        ]
    else:  # glass
        kids += [
            part("Canopy", [1.9, 1.0, 1.35], [0, 1.35, 0.45], color=lighten(paint, 0.35), material="Glass", transparency=0.35),
            part("AccentRim", [2.1, 0.14, 1.5], [0, 0.85, 0.45], color=VISOR_CYAN, material="Neon"),
            part("CheekL", [0.5, 0.85, 0.9], [-1.75, 0.55, 0.35], color=panel, material="Metal"),
            part("CheekR", [0.5, 0.85, 0.9], [1.75, 0.55, 0.35], color=panel, material="Metal"),
            part("BackFin", [0.22, 1.25, 1.0], [0, 0.85, -1.2], color=gm, material="Metal"),
        ]
    return kids


def build_leg(base: list[float], *, style: str, side: str) -> list[dict]:
    """Short thick chibi legs. Root = hip pivot. Baked knee bend in local geometry."""
    s = -1.0 if side == "l" else 1.0
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    sole = rgb(36, 34, 32)

    # Hip pivot at origin (socket)
    kids.append(joint_cyl("HipJoint", [0.85, 0.55, 0.85], [0, 0, 0], color=gm))

    if style in ("workboot", "stump", "hoof", "claw", "digit", "hinge"):
        # Plantigrade / armored biped — thigh forward, shin down, fat boot
        kids += [
            part("Thigh", [1.15, 1.05, 1.2], [0.08 * s, -0.65, 0.2], color=paint, material="Metal"),
            *rim_front("Thigh", [1.15, 1.05, 1.2], [0.08 * s, -0.65, 0.2], color=gm, thickness=0.07),
            joint_cyl("Knee", [0.95, 0.4, 0.95], [0.1 * s, -1.25, 0.25], color=gm),
            part("Shin", [1.05, 0.95, 1.1], [0.05 * s, -1.85, 0.05], color=paint, material="Metal"),
            inset_front("ShinInset", [1.05, 0.95, 1.1], [0.05 * s, -1.85, 0.05], color=panel_safe(paint)),
            part("Foot", [1.45, 0.4, 1.7], [0, -2.4, 0.35], color=sole, material="SmoothPlastic"),
            part("ToeLip", [1.25, 0.28, 0.4], [0, -2.25, 1.05], color=gm, material="Metal"),
            visor("GlowAnkle", [0.35, 0.2, 0.2], [0.35 * s, -2.05, 0.55], VISOR_ORANGE),
        ]
        if style == "stump":
            kids.append(part("ThighPlate", [0.22, 0.8, 0.9], [0.7 * s, -0.6, 0.25], color=panel_safe(paint), material="DiamondPlate"))
        if style == "claw":
            kids += [
                part("ClawL", [0.28, 0.25, 0.9], [-0.35, -2.35, 1.0], color=gm, material="Metal"),
                part("ClawR", [0.28, 0.25, 0.9], [0.35, -2.35, 1.0], color=gm, material="Metal"),
            ]
        if style == "digit":
            kids += [
                part("ToeMid", [0.4, 0.25, 0.85], [0, -2.35, 0.95], color=sole, material="Metal"),
                part("ToeL", [0.3, 0.22, 0.75], [-0.4, -2.3, 0.85], color=sole, material="Metal"),
                part("ToeR", [0.3, 0.22, 0.75], [0.4, -2.3, 0.85], color=sole, material="Metal"),
            ]
    elif style in ("sprint", "piston", "strut"):
        # Digitigrade / runner — Z-bend
        kids += [
            part("Thigh", [0.85, 1.0, 0.9], [0.1 * s, -0.55, 0.35], color=paint, material="Metal"),
            joint_cyl("Knee", [0.75, 0.35, 0.75], [0.12 * s, -1.15, 0.55], color=gm),
            part("Shin", [0.75, 1.05, 0.75], [0.08 * s, -1.75, 0.15], color=paint, material="Metal"),
            joint_cyl("Ankle", [0.55, 0.3, 0.55], [0, -2.25, 0.05], color=gm),
            part("Foot", [1.0, 0.3, 1.35], [0, -2.45, 0.4], color=sole, material="SmoothPlastic"),
            wedge("ShinFairing", [0.35, 0.5, 0.65], cf([0.35 * s, -1.5, 0.4]), color=panel_safe(paint)),
            visor("GlowKnee", [0.25, 0.25, 0.2], [0.4 * s, -1.15, 0.75]),
        ]
        if style == "piston":
            kids.append(joint_cyl("PistonRod", [0.3, 1.1, 0.3], [0, -1.5, 0.2], color=gm))
    elif style == "tread":
        kids += [
            part("Upper", [1.25, 0.7, 1.2], [0, -0.35, 0.1], color=paint, material="Metal"),
            part("TrackBox", [1.55, 1.2, 1.9], [0, -1.35, 0.15], color=darken(paint, 0.1), material="DiamondPlate"),
            joint_cyl("WheelF", [0.45, 0.85, 0.85], [0.55 * s, -1.7, 0.7], color=gm),
            joint_cyl("WheelB", [0.45, 0.85, 0.85], [0.55 * s, -1.7, -0.55], color=gm),
            visor("GlowLight", [0.3, 0.25, 0.18], [0, -0.15, 0.75], VISOR_ORANGE),
        ]
    else:
        kids += [
            part("Thigh", [1.0, 1.0, 1.05], [0.08 * s, -0.6, 0.15], color=paint, material="Metal"),
            joint_cyl("Knee", [0.85, 0.35, 0.85], [0.1 * s, -1.2, 0.2], color=gm),
            part("Shin", [0.9, 0.95, 0.95], [0.05 * s, -1.8, 0], color=paint, material="Metal"),
            part("Foot", [1.3, 0.35, 1.5], [0, -2.35, 0.3], color=sole, material="SmoothPlastic"),
        ]
    return kids


def build_lower_weapon(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    kids.append(joint_cyl("Mount", [0.7, 0.55, 0.7], [0, 0, -0.85], color=gm))

    if style == "snap":
        kids += [
            part("Forearm", [0.9, 0.75, 1.25], [0, 0, -0.05], color=paint, material="Metal"),
            *rim_front("Forearm", [0.9, 0.75, 1.25], [0, 0, -0.05], color=gm, thickness=0.06),
            part("Fist", [1.2, 1.05, 1.0], [0, 0, 1.05], color=darken(paint, 0.1), material="Metal"),
            part("Knuckle", [1.25, 0.3, 0.35], [0, 0.4, 1.35], color=gm, material="Metal"),
            visor("GlowKnuckle", [0.9, 0.15, 0.15], [0, 0.45, 1.45], VISOR_ORANGE),
        ]
    elif style in ("rivet", "mg"):
        # Readable multi-barrel gun
        kids += [
            part("Receiver", [0.95, 0.8, 1.35], [0, 0.05, 0], color=paint, material="Metal"),
            *rim_front("Receiver", [0.95, 0.8, 1.35], [0, 0.05, 0], color=gm, thickness=0.06),
            joint_cyl("Barrel", [0.32, 0.32, 1.9], [0, 0.15, 1.45], color=gm),
            joint_cyl("BarrelL", [0.22, 0.22, 1.5], [-0.28, 0.05, 1.2], color=gm),
            joint_cyl("BarrelR", [0.22, 0.22, 1.5], [0.28, 0.05, 1.2], color=gm),
            joint_cyl("CoolingJacket", [0.5, 0.5, 0.95], [0, 0.15, 0.85], color=darken(gm, 0.1)),
            part("Mag", [0.55, 0.7, 0.45], [0.55, -0.2, 0.1], color=gm, material="Metal"),
            part("Grip", [0.35, 0.55, 0.35], [0, -0.55, -0.15], color=rgb(40, 40, 44), material="SmoothPlastic"),
            visor("GlowMuzzle", [0.35, 0.35, 0.25], [0, 0.15, 2.35], VISOR_ORANGE),
        ]
    elif style == "ember":
        kids += [
            part("Gauntlet", [1.15, 1.05, 1.25], [0, 0, 0], color=paint, material="CorrodedMetal"),
            visor("GlowCore", [0.65, 0.65, 0.65], [0, 0.15, 0.55], VISOR_ORANGE),
            part("VentL", [0.25, 0.5, 0.75], [-0.55, 0.2, 0.25], color=gm, material="Metal"),
            part("VentR", [0.25, 0.5, 0.75], [0.55, 0.2, 0.25], color=gm, material="Metal"),
            part("PunchPlate", [1.25, 1.1, 0.35], [0, 0, 1.05], color=gm, material="Metal"),
        ]
    elif style in ("needle", "beam"):
        kids += [
            part("Housing", [0.85, 0.75, 1.15], [0, 0.1, 0], color=paint, material="Metal"),
            part("Crystal", [0.45, 0.45, 0.65], [0, 0.15, 0.75], color=VISOR_CYAN, material="Glass", transparency=0.25),
            joint_cyl("Emitter", [0.35, 0.35, 1.0], [0, 0.15, 1.55], color=gm),
            visor("GlowBeam", [0.14, 0.14, 1.5], [0, 0.15, 1.35]),
            joint_cyl("FocusRing", [0.7, 0.14, 0.7], [0, 0.15, 0.4], color=gm),
        ]
    elif style in ("cleaver", "melee"):
        kids += [
            part("Haft", [0.45, 0.45, 1.4], [0, 0, -0.1], color=gm, material="Metal"),
            part("Guard", [1.15, 0.25, 0.85], [0, 0.35, 0.45], color=paint, material="Metal"),
            part("Blade", [0.18, 0.7, 2.1], [0, 0.1, 1.45], color=lighten(paint, 0.12), material="Metal"),
            visor("GlowEdge", [0.08, 0.55, 1.9], [0.12, 0.1, 1.45], VISOR_RED),
            part("Pommel", [0.5, 0.5, 0.35], [0, 0, -0.95], color=gm, material="Metal"),
        ]
    elif style == "drill":
        kids += [
            part("Motor", [1.0, 0.9, 1.05], [0, 0, -0.15], color=paint, material="Metal"),
            joint_cyl("Bit", [0.5, 0.5, 1.65], [0, 0, 1.15], color=gm),
            visor("GlowRing", [1.0, 0.18, 1.0], [0, 0, 0.4], VISOR_ORANGE),
            part("Handle", [0.4, 0.65, 0.4], [0, -0.7, -0.25], color=rgb(40, 40, 44), material="SmoothPlastic"),
        ]
    elif style == "spray":
        kids += [
            part("Tank", [0.95, 0.95, 1.15], [0, 0.1, -0.15], color=paint, material="Metal"),
            joint_cyl("Nozzle", [0.4, 0.4, 1.05], [0, 0.15, 1.05], color=gm),
            visor("GlowValve", [0.35, 0.35, 0.3], [0.4, 0.5, 0], VISOR_ORANGE),
            part("Hose", [0.2, 0.2, 0.75], [0.5, -0.2, -0.55], color=rgb(40, 40, 44), material="SmoothPlastic"),
        ]
    elif style == "shield":
        kids += [
            part("Brace", [0.7, 0.55, 0.95], [0, 0, -0.25], color=gm, material="Metal"),
            part("Face", [1.7, 2.15, 0.28], [0, 0.15, 0.75], color=paint, material="DiamondPlate"),
            *rim_front("Face", [1.7, 2.15, 0.28], [0, 0.15, 0.75], color=gm, thickness=0.08),
            part("Boss", [0.55, 0.55, 0.28], [0, 0.2, 0.95], color=gm, material="Metal"),
            visor("GlowBoss", [0.35, 0.35, 0.12], [0, 0.2, 1.1]),
            part("LipL", [0.25, 1.7, 0.35], [-0.9, 0.15, 0.75], color=panel_safe(paint), material="Metal"),
            part("LipR", [0.25, 1.7, 0.35], [0.9, 0.15, 0.75], color=panel_safe(paint), material="Metal"),
        ]
    else:  # hook
        kids += [
            part("Arm", [0.7, 0.55, 1.45], [0, 0, 0], color=paint, material="Metal"),
            part("HookCurve", [0.45, 0.9, 0.45], [0, 0.35, 1.1], color=gm, material="Metal"),
            part("HookTip", [0.3, 0.3, 0.8], [0, 0.7, 1.5], color=gm, material="Metal"),
            visor("GlowChain", [0.18, 0.18, 0.85], [0, -0.3, 0.4], VISOR_ORANGE),
        ]
    return kids


def build_shoulder_weapon(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    kids.append(part("ShoulderMount", [1.15, 0.5, 0.95], [0, -0.1, -0.65], color=gm, material="Metal"))

    if style in ("box", "rocket"):
        # Readable missile pod grid (2x2 tubes)
        kids += [
            part("PodBox", [1.55, 1.15, 1.5], [0, 0.45, 0.25], color=paint, material="Metal"),
            *rim_front("Pod", [1.55, 1.15, 1.5], [0, 0.45, 0.25], color=gm, thickness=0.08),
            joint_cyl("TubeTL", [0.4, 0.4, 1.35], [-0.35, 0.7, 0.85], color=gm),
            joint_cyl("TubeTR", [0.4, 0.4, 1.35], [0.35, 0.7, 0.85], color=gm),
            joint_cyl("TubeBL", [0.4, 0.4, 1.35], [-0.35, 0.25, 0.85], color=gm),
            joint_cyl("TubeBR", [0.4, 0.4, 1.35], [0.35, 0.25, 0.85], color=gm),
            visor("GlowTubeTL", [0.28, 0.28, 0.12], [-0.35, 0.7, 1.55]),
            visor("GlowTubeTR", [0.28, 0.28, 0.12], [0.35, 0.7, 1.55]),
            visor("GlowTubeBL", [0.28, 0.28, 0.12], [-0.35, 0.25, 1.55]),
            visor("GlowTubeBR", [0.28, 0.28, 0.12], [0.35, 0.25, 1.55]),
            part("Hatch", [1.2, 0.15, 0.9], [0, 1.1, 0.1], color=gm, material="Metal"),
        ]
        if style == "rocket":
            kids.append(joint_cyl("TubeMid", [0.35, 0.35, 1.2], [0, 1.05, 0.55], color=darken(gm, 0.1)))
    elif style in ("brick", "mg", "bite"):
        # Heavy cannon / gatling shoulder
        kids += [
            part("Breech", [1.25, 0.8, 0.85], [0, 0.15, -0.25], color=gm, material="Metal"),
            part("Receiver", [1.15, 0.7, 1.15], [0, 0.25, 0.6], color=paint, material="Metal"),
            *rim_front("Receiver", [1.15, 0.7, 1.15], [0, 0.25, 0.6], color=gm, thickness=0.06),
            joint_cyl("Barrel", [0.45, 0.45, 1.7], [0, 0.3, 1.65], color=gm),
            joint_cyl("BarrelL", [0.28, 0.28, 1.3], [-0.35, 0.2, 1.35], color=gm),
            joint_cyl("BarrelR", [0.28, 0.28, 1.3], [0.35, 0.2, 1.35], color=gm),
            joint_cyl("Collar", [0.85, 0.22, 0.85], [0, 0.3, 0.95], color=panel_safe(paint)),
            visor("GlowMuzzle", [0.4, 0.4, 0.25], [0, 0.3, 2.5], VISOR_ORANGE),
            part("SidePlateL", [0.18, 0.65, 1.0], [-0.7, 0.2, 0.3], color=panel_safe(paint), material="Metal"),
            part("SidePlateR", [0.18, 0.65, 1.0], [0.7, 0.2, 0.3], color=panel_safe(paint), material="Metal"),
        ]
    elif style in ("arc", "beam", "spear"):
        kids += [
            part("RailBody", [1.0, 0.7, 2.0], [0, 0.2, 0.45], color=paint, material="Metal"),
            *rim_front("Rail", [1.0, 0.7, 2.0], [0, 0.2, 0.45], color=gm, thickness=0.06),
            visor("GlowRail", [0.2, 0.2, 2.2], [0, 0.45, 0.55]),
            joint_cyl("CoilL", [0.3, 0.5, 0.5], [-0.5, 0.2, 0.15], color=gm),
            joint_cyl("CoilR", [0.3, 0.5, 0.5], [0.5, 0.2, 0.15], color=gm),
            visor("GlowEmitter", [0.45, 0.45, 0.35], [0, 0.25, 1.75]),
        ]
    elif style == "slag":
        kids += [
            part("Drum", [1.4, 1.15, 1.4], [0, 0.25, 0], color=paint, material="CorrodedMetal"),
            joint_cyl("Spout", [0.65, 0.65, 1.25], [0, 0.15, 1.2], color=gm),
            visor("GlowCrust", [0.9, 0.35, 0.35], [0.35, 0.65, 0.3], VISOR_ORANGE),
            part("Support", [0.4, 0.85, 0.4], [0, -0.45, -0.2], color=gm, material="Metal"),
        ]
    elif style == "twin":
        kids += [
            part("Cradle", [1.45, 0.55, 1.15], [0, 0.05, 0], color=gm, material="Metal"),
            joint_cyl("GunL", [0.38, 0.38, 2.15], [-0.4, 0.35, 0.75], color=paint),
            joint_cyl("GunR", [0.38, 0.38, 2.15], [0.4, 0.35, 0.75], color=paint),
            visor("GlowBridge", [0.9, 0.16, 0.16], [0, 0.6, 0.35]),
        ]
    elif style == "mortar":
        kids += [
            part("Base", [1.35, 0.45, 1.35], [0, -0.05, 0], color=gm, material="Metal"),
            joint_cyl("Tube", [0.85, 0.85, 1.9], [0, 0.55, 0.55], color=paint),
            visor("GlowRing", [1.0, 0.18, 1.0], [0, 0.55, 0.05], VISOR_ORANGE),
            part("Bipod", [1.15, 0.65, 0.25], [0, -0.15, 0.6], color=gm, material="Metal"),
        ]
    else:
        kids += [
            part("Receiver", [1.1, 0.7, 1.2], [0, 0.2, 0.3], color=paint, material="Metal"),
            joint_cyl("Barrel", [0.4, 0.4, 1.6], [0, 0.25, 1.5], color=gm),
            visor("GlowMuzzle", [0.35, 0.35, 0.22], [0, 0.25, 2.3], VISOR_ORANGE),
        ]
    return kids


def build_battery(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    paint = base
    kids = [part("Pack", [1.5, 0.95, 0.7], [0, 0, 0], color=paint, material="Metal")]
    if style == "desk":
        kids += [
            visor("GlowTerminal", [0.25, 0.25, 0.18], [-0.4, 0.5, 0], VISOR_RED),
            part("Terminal-", [0.25, 0.25, 0.18], [0.4, 0.5, 0], color=gm, material="Metal"),
            part("AccentLabel", [0.85, 0.3, 0.1], [0, 0.1, 0.4], color=VISOR_CYAN, material="Neon"),
        ]
    elif style == "bay":
        kids += [
            part("CellA", [0.4, 0.65, 0.45], [-0.4, 0, 0.15], color=darken(paint, 0.2), material="Glass", transparency=0.3),
            part("CellB", [0.4, 0.65, 0.45], [0.4, 0, 0.15], color=darken(paint, 0.2), material="Glass", transparency=0.3),
            visor("GlowBus", [1.4, 0.14, 0.14], [0, 0.55, 0]),
        ]
    elif style == "deep":
        kids += [
            visor("GlowRing", [1.7, 0.2, 0.85], [0, 0.3, 0]),
            part("CapTop", [1.35, 0.25, 0.6], [0, 0.65, 0], color=gm, material="Metal"),
            part("Port", [0.35, 0.35, 0.25], [0, 0, 0.5], color=VISOR_CYAN, material="Neon"),
        ]
    elif style == "stack":
        kids += [
            part("Layer2", [1.4, 0.3, 0.65], [0, 0, 0], color=darken(paint, 0.15), material="Metal"),
            part("Layer3", [1.4, 0.3, 0.65], [0, 0.35, 0], color=paint, material="Metal"),
            visor("GlowStripe", [0.14, 1.0, 0.14], [0.65, 0, 0.3]),
        ]
    else:
        kids += [
            joint_cyl("Drum", [1.15, 1.15, 0.8], [0, 0, 0], color=paint),
            visor("GlowBand", [1.25, 0.18, 0.9], [0, 0.2, 0]),
        ]
    return kids


def build_cpu(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    kids = [
        part("Board", [1.0, 0.12, 1.0], [0, 0, 0], color=darken(base, 0.2), material="Plastic"),
        part("Die", [0.45, 0.22, 0.45], [0, 0.18, 0], color=gm, material="Metal"),
        visor("GlowLED", [0.2, 0.1, 0.2], [0.35, 0.15, 0.35]),
    ]
    if style == "bay":
        kids.append(part("Heatsink", [0.7, 0.35, 0.7], [0, 0.3, 0], color=gm, material="Metal"))
    elif style != "scrap":
        kids.append(part("Crystal", [0.45, 0.5, 0.45], [0, 0.4, 0], color=VISOR_CYAN, material="Glass", transparency=0.25))
    return kids


def build_drone(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    paint = base
    if style == "floor":
        return [
            part("Chassis", [1.05, 0.4, 1.15], [0, 0, 0], color=paint, material="Metal"),
            joint_cyl("WheelL", [0.32, 0.5, 0.5], [-0.55, -0.15, 0.3], color=gm),
            joint_cyl("WheelR", [0.32, 0.5, 0.5], [0.55, -0.15, 0.3], color=gm),
            visor("GlowEye", [0.35, 0.25, 0.2], [0, 0.25, 0.55]),
        ]
    if style == "moth":
        return [
            part("Body", [0.5, 0.4, 0.85], [0, 0, 0], color=paint, material="SmoothPlastic"),
            part("WingL", [0.85, 0.1, 0.55], [-0.55, 0.15, 0], color=lighten(paint, 0.2), material="Glass", transparency=0.3),
            part("WingR", [0.85, 0.1, 0.55], [0.55, 0.15, 0], color=lighten(paint, 0.2), material="Glass", transparency=0.3),
            visor("GlowSpark", [0.25, 0.25, 0.25], [0, 0.2, 0.4]),
        ]
    if style == "beep":
        return [
            part("Dome", [0.85, 0.65, 0.85], [0, 0.1, 0], color=paint, material="SmoothPlastic", shape="Ball"),
            part("Base", [0.95, 0.22, 0.95], [0, -0.3, 0], color=gm, material="Metal"),
            visor("GlowCross", [0.65, 0.12, 0.12], [0, 0.35, 0.35]),
        ]
    if style == "orb":
        return [
            part("Sphere", [0.9, 0.9, 0.9], [0, 0, 0], color=paint, material="Glass", transparency=0.2, shape="Ball"),
            visor("GlowCore", [0.4, 0.4, 0.4], [0, 0, 0]),
            joint_cyl("Ring", [1.1, 0.12, 1.1], [0, 0, 0], color=gm),
        ]
    return [
        part("Body", [0.75, 0.4, 0.85], [0, 0, 0], color=paint, material="Metal"),
        part("LegFL", [0.14, 0.14, 0.65], [-0.45, -0.1, 0.35], color=gm, material="Metal"),
        part("LegFR", [0.14, 0.14, 0.65], [0.45, -0.1, 0.35], color=gm, material="Metal"),
        part("LegBL", [0.14, 0.14, 0.65], [-0.45, -0.1, -0.35], color=gm, material="Metal"),
        part("LegBR", [0.14, 0.14, 0.65], [0.45, -0.1, -0.35], color=gm, material="Metal"),
        visor("GlowEye", [0.3, 0.2, 0.15], [0, 0.2, 0.45]),
    ]


def build_chip(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    kids = [
        part("Card", [0.55, 0.12, 0.4], [0, 0, 0], color=base, material="Plastic"),
        visor("GlowDie", [0.22, 0.1, 0.22], [0, 0.1, 0]),
    ]
    if style == "heat":
        kids.append(part("Fin", [0.45, 0.2, 0.15], [0, 0.2, 0.05], color=gm, material="Metal"))
    elif style == "wire":
        kids.append(visor("GlowTrace", [0.4, 0.05, 0.08], [0, 0.08, 0.12]))
    elif style == "grease":
        kids.append(part("Blob", [0.25, 0.15, 0.25], [0.1, 0.12, 0.05], color=lighten(base, 0.15), material="SmoothPlastic"))
    elif style == "shield":
        kids.append(part("Shield", [0.35, 0.25, 0.1], [0, 0.18, 0.05], color=gm, material="Metal"))
    else:
        kids.append(part("Pad", [0.15, 0.08, 0.15], [-0.15, 0.08, 0.1], color=gm, material="Metal"))
    return kids


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
    rank = RARITY_RANK.get(rarity, 0)
    if rank <= 0:
        return []
    s = scale
    gm = GUNMETAL
    kids = [
        part("AccentTrimA", [0.5 * s, 0.1 * s, 0.1 * s], [0.35 * s, 0.3 * s, 0.45 * s], color=lighten(base, 0.25), material="Metal"),
        visor("GlowPip", [0.22 * s, 0.22 * s, 0.12 * s], [0, 0.4 * s, 0.5 * s], VISOR_CYAN if rank < 3 else VISOR_ORANGE),
    ]
    if rank >= 2:
        kids += [
            part("TrimStud", [0.18 * s, 0.18 * s, 0.18 * s], [0.45 * s, -0.15 * s, 0.3 * s], color=gm, material="DiamondPlate"),
            part("TrimStud2", [0.18 * s, 0.18 * s, 0.18 * s], [-0.45 * s, -0.15 * s, 0.3 * s], color=gm, material="DiamondPlate"),
        ]
    if rank >= 3:
        kids += [
            part("GlowCore", [0.32 * s, 0.32 * s, 0.32 * s], [0, 0.35 * s, 0.55 * s], color=VISOR_CYAN, material="Neon", transparency=0.12),
            part("GlowHalo", [0.65 * s, 0.08 * s, 0.65 * s], [0, 0.45 * s, 0.2 * s], color=VISOR_ORANGE, material="Neon", transparency=0.3),
        ]
    if rank >= 4:
        kids += [
            part("GlowVein", [0.1 * s, 0.75 * s, 0.1 * s], [0.4 * s, 0.1 * s, 0.2 * s], color=VISOR_ORANGE, material="Neon", transparency=0.2),
            part("GlowVein2", [0.1 * s, 0.75 * s, 0.1 * s], [-0.4 * s, 0.1 * s, 0.2 * s], color=VISOR_CYAN, material="Neon", transparency=0.25),
        ]
    return kids
