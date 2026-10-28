"""SuperMechs-inspired dense kit geometry (structure only — original Assembler parts).

Every volume must read as armor, joint, barrel, visor, vent, tread, or bolt —
no hollow/senseless slabs. High part counts with intentional layered paneling.
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


# ---------------------------------------------------------------------------
# Dense greeble helpers — break every large face into intentional mech detail
# ---------------------------------------------------------------------------


def bolts(prefix: str, positions: list[list[float]], *, color: list[float] | None = None, r: float = 0.12) -> list[dict]:
    c = color or GUNMETAL
    out = []
    for i, p in enumerate(positions):
        out.append(part(f"{prefix}Bolt{i}", [r, r, r], p, color=c, material="DiamondPlate"))
    return out


def vent_row(
    prefix: str,
    origin: list[float],
    *,
    count: int = 4,
    spacing: float = 0.22,
    size: list[float] | None = None,
    axis: str = "x",
    color: list[float] | None = None,
) -> list[dict]:
    """Cooling slits / radiator fins along X or Y."""
    sz = size or [0.12, 0.55, 0.14]
    c = color or darken(GUNMETAL, 0.2)
    kids = []
    ox, oy, oz = origin
    for i in range(count):
        if axis == "x":
            pos = [ox + (i - (count - 1) / 2) * spacing, oy, oz]
        elif axis == "y":
            pos = [ox, oy + (i - (count - 1) / 2) * spacing, oz]
        else:
            pos = [ox, oy, oz + (i - (count - 1) / 2) * spacing]
        kids.append(part(f"{prefix}Vent{i}", sz, pos, color=c, material="Metal"))
    return kids


def panel_stack(
    prefix: str,
    base_size: list[float],
    base_pos: list[float],
    *,
    paint: list[float],
    layers: int = 2,
    shrink: float = 0.18,
    push_z: float = 0.08,
) -> list[dict]:
    """Overlapping armor plates on +Z — intentional paneling, not one slab."""
    kids = []
    sx, sy, sz = base_size
    x, y, z = base_pos
    for i in range(layers):
        k = shrink * (i + 1)
        kids.append(
            part(
                f"{prefix}Plate{i}",
                [max(0.25, sx - k * 2), max(0.25, sy - k * 2), max(0.12, sz * 0.35)],
                [x, y - i * 0.05, z + sz / 2 + push_z * (i + 1)],
                color=darken(paint, 0.08 * (i + 1)),
                material="Metal" if i == 0 else "DiamondPlate",
            )
        )
    return kids


def barrel_cluster(
    prefix: str,
    center: list[float],
    *,
    n: int = 3,
    length: float = 1.6,
    radius: float = 0.22,
    spread: float = 0.28,
    color: list[float] | None = None,
    muzzle_glow: bool = True,
) -> list[dict]:
    """Readable multi-barrel gun cluster with optional muzzle emissives."""
    c = color or GUNMETAL
    cx, cy, cz = center
    kids = []
    offsets = [(0.0, 0.0)]
    if n >= 2:
        offsets = [(-spread, 0.08), (spread, 0.08)]
    if n >= 3:
        offsets.append((0.0, -spread * 0.7))
    if n >= 4:
        offsets.append((0.0, spread * 0.85))
    if n >= 5:
        offsets += [(-spread * 0.7, -spread * 0.35), (spread * 0.7, -spread * 0.35)]
    for i, (ox, oy) in enumerate(offsets[:n]):
        kids.append(joint_cyl(f"{prefix}Barrel{i}", [radius, radius, length], [cx + ox, cy + oy, cz], color=c))
        if muzzle_glow:
            kids.append(
                visor(
                    f"{prefix}Muzzle{i}",
                    [radius * 0.85, radius * 0.85, 0.14],
                    [cx + ox, cy + oy, cz + length / 2 + 0.08],
                    VISOR_ORANGE,
                )
            )
    return kids


def joint_assembly(prefix: str, pos: list[float], *, scale: float = 1.0, color: list[float] | None = None) -> list[dict]:
    """Visible mechanical hinge: disk + pin + housing — reads as a joint, not a blob."""
    gm = color or GUNMETAL
    s = scale
    x, y, z = pos
    return [
        joint_cyl(f"{prefix}Disk", [0.95 * s, 0.38 * s, 0.95 * s], [x, y, z], color=gm),
        joint_cyl(f"{prefix}Pin", [0.28 * s, 0.7 * s, 0.28 * s], [x + 0.45 * s, y, z], color=lighten(gm, 0.15)),
        part(f"{prefix}Cap", [0.35 * s, 0.35 * s, 0.22 * s], [x - 0.4 * s, y, z], color=darken(gm, 0.1), material="Metal"),
        visor(f"{prefix}Glow", [0.18 * s, 0.18 * s, 0.12 * s], [x, y, z + 0.45 * s], VISOR_ORANGE),
    ]


# ---------------------------------------------------------------------------
# Torso — dense layered chassis
# ---------------------------------------------------------------------------


def build_torso(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    panel = darken(base, 0.12)
    gm = GUNMETAL
    vent = darken(gm, 0.15)

    # Core is intentionally smaller than outer armor — outer plates carry the silhouette.
    core = [2.6, 2.0, 1.7]
    kids += [
        part("CoreFrame", core, [0, 0.05, -0.05], color=gm, material="Metal"),
        part("Hull", [3.35, 2.35, 2.15], [0, 0.08, 0.05], color=paint, material="Metal"),
        *rim_front("Hull", [3.35, 2.35, 2.15], [0, 0.08, 0.05], color=panel, thickness=0.09),
        *panel_stack("Chest", [2.4, 1.4, 0.5], [0, 0.15, 0.95], paint=panel, layers=3, shrink=0.22, push_z=0.1),
        inset_front("ChestWell", [3.35, 2.35, 2.15], [0, 0.08, 0.05], color=darken(panel, 0.15), material="DiamondPlate", depth=0.1),
        # Head / visor cluster (front silhouette)
        part("HeadDome", [1.85, 1.05, 1.55], [0, 1.55, 0.2], color=lighten(paint, 0.08), material="Metal"),
        part("HeadCap", [1.55, 0.35, 1.25], [0, 2.15, 0.15], color=panel, material="Metal"),
        part("VisorRecess", [1.65, 0.65, 0.28], [0, 1.4, 0.95], color=darken(gm, 0.25), material="Metal"),
        visor("GlowVisor", [1.45, 0.42, 0.18], [0, 1.4, 1.12]),
        part("VisorBrow", [1.7, 0.16, 0.4], [0, 1.75, 0.9], color=gm, material="Metal"),
        visor("GlowSlitL", [0.18, 0.35, 0.12], [-0.85, 1.35, 1.05], VISOR_CYAN),
        visor("GlowSlitR", [0.18, 0.35, 0.12], [0.85, 1.35, 1.05], VISOR_CYAN),
        *bolts("Head", [[-0.7, 1.9, 0.7], [0.7, 1.9, 0.7], [-0.55, 1.55, 0.85], [0.55, 1.55, 0.85]], r=0.1),
        # Shoulders / hips
        joint_cyl("ShoulderPivotL", [0.65, 0.5, 0.65], [-1.95, 0.9, 0], color=gm),
        joint_cyl("ShoulderPivotR", [0.65, 0.5, 0.65], [1.95, 0.9, 0], color=gm),
        part("PauldronL", [1.05, 0.7, 1.2], [-2.15, 1.1, 0.05], color=panel, material="Metal"),
        part("PauldronR", [1.05, 0.7, 1.2], [2.15, 1.1, 0.05], color=panel, material="Metal"),
        part("PauldronCapL", [0.85, 0.28, 0.95], [-2.2, 1.5, 0.05], color=darken(panel, 0.1), material="DiamondPlate"),
        part("PauldronCapR", [0.85, 0.28, 0.95], [2.2, 1.5, 0.05], color=darken(panel, 0.1), material="DiamondPlate"),
        *joint_assembly("Hip", [0, -1.2, 0.05], scale=0.95),
        part("HipYoke", [2.7, 0.4, 1.45], [0, -1.5, 0.1], color=panel, material="Metal"),
        part("PelvisPlate", [2.2, 0.28, 1.1], [0, -1.75, 0.2], color=gm, material="Metal"),
        part("SkirtL", [0.55, 0.7, 1.0], [-1.55, -1.35, 0.25], color=panel, material="Metal"),
        part("SkirtR", [0.55, 0.7, 1.0], [1.55, -1.35, 0.25], color=panel, material="Metal"),
        *vent_row("SideL", [-1.75, 0.2, 0.85], count=3, spacing=0.28, size=[0.14, 0.45, 0.12], axis="y", color=vent),
        *vent_row("SideR", [1.75, 0.2, 0.85], count=3, spacing=0.28, size=[0.14, 0.45, 0.12], axis="y", color=vent),
        *bolts("Hull", [[-1.2, 0.9, 1.1], [1.2, 0.9, 1.1], [-1.0, -0.5, 1.15], [1.0, -0.5, 1.15]], r=0.11),
    ]

    if style == "cage":
        kids += [
            part("RibL", [0.22, 2.05, 1.85], [-1.8, 0.1, 0], color=gm, material="Metal"),
            part("RibR", [0.22, 2.05, 1.85], [1.8, 0.1, 0], color=gm, material="Metal"),
            part("RibCross", [3.0, 0.18, 0.18], [0, 0.55, 0.9], color=gm, material="Metal"),
            part("BackPack", [1.9, 1.15, 0.55], [0, 0.35, -1.3], color=panel, material="Metal"),
            *vent_row("Back", [0, 0.55, -1.55], count=5, spacing=0.28, size=[0.14, 0.55, 0.12], color=vent),
            joint_cyl("ExhaustL", [0.38, 0.38, 0.7], [-0.55, 0.75, -1.55], color=vent),
            joint_cyl("ExhaustR", [0.38, 0.38, 0.7], [0.55, 0.75, -1.55], color=vent),
            visor("GlowExhaustL", [0.22, 0.22, 0.12], [-0.55, 0.75, -1.95]),
            visor("GlowExhaustR", [0.22, 0.22, 0.12], [0.55, 0.75, -1.95]),
            part("AccentHazard", [1.2, 0.16, 0.14], [0, -0.55, 1.25], color=VISOR_ORANGE, material="Neon"),
        ]
    elif style == "plate":
        kids += [
            part("BreastPlate", [2.5, 1.25, 0.32], [0, 0.15, 1.25], color=panel, material="DiamondPlate"),
            *rim_front("Breast", [2.5, 1.25, 0.32], [0, 0.15, 1.25], color=gm, thickness=0.06),
            *panel_stack("BreastLayer", [2.1, 0.9, 0.25], [0, 0.2, 1.3], paint=paint, layers=2),
            wedge("SlopeL", [0.8, 0.35, 0.6], cf([-1.95, 1.45, 0.3]), color=panel),
            wedge("SlopeR", [0.8, 0.35, 0.6], cf([1.95, 1.45, 0.3]), color=panel),
            part("BackRadiator", [1.9, 0.75, 0.35], [0, 0.55, -1.25], color=vent, material="Metal"),
            *vent_row("Rad", [0, 0.55, -1.45], count=4, spacing=0.32, size=[0.12, 0.5, 0.1], color=gm),
            part("Collar", [2.4, 0.22, 1.5], [0, 1.25, 0.1], color=gm, material="Metal"),
        ]
    elif style == "tin":
        kids += [
            part("RingTop", [3.05, 0.45, 1.85], [0, 0.9, 0], color=lighten(paint, 0.1), material="Metal"),
            part("RingMid", [3.15, 0.28, 1.95], [0, 0.25, 0], color=panel, material="Metal"),
            part("RingBot", [3.1, 0.45, 1.9], [0, -0.55, 0], color=darken(paint, 0.1), material="Metal"),
            part("AccentBand", [3.3, 0.14, 2.05], [0, 0.2, 0], color=VISOR_ORANGE, material="Neon"),
            part("FrontBadge", [0.85, 0.65, 0.16], [0, 0.1, 1.25], color=gm, material="DiamondPlate"),
            *bolts("Ring", [[-1.3, 0.9, 0.95], [1.3, 0.9, 0.95], [-1.35, -0.55, 0.95], [1.35, -0.55, 0.95]]),
            joint_cyl("Intake", [0.5, 0.5, 0.6], [0, -0.35, -1.2], color=vent),
            *vent_row("Can", [0, 0.55, 1.2], count=3, spacing=0.35, size=[0.2, 0.35, 0.1], color=vent),
        ]
    elif style == "wedge":
        kids += [
            wedge("ArmorSlope", [3.05, 0.7, 1.85], cf([0, 0.95, 0.3]), color=panel, material="DiamondPlate"),
            part("Nose", [1.4, 0.7, 0.65], [0, 0.1, 1.3], color=lighten(paint, 0.1), material="Metal"),
            part("NoseLip", [1.55, 0.14, 0.25], [0, -0.25, 1.5], color=gm, material="Metal"),
            part("Keel", [1.9, 0.45, 1.5], [0, -1.2, 0.25], color=gm, material="Metal"),
            part("BackFin", [0.22, 1.15, 0.85], [0, 0.7, -1.25], color=vent, material="Metal"),
            part("SideFinL", [0.18, 0.9, 0.7], [-1.7, 0.4, -0.4], color=panel, material="Metal"),
            part("SideFinR", [0.18, 0.9, 0.7], [1.7, 0.4, -0.4], color=panel, material="Metal"),
            visor("GlowCrest", [0.2, 1.0, 0.16], [0, 0.35, 1.35], VISOR_ORANGE),
            *bolts("Wedge", [[-0.9, 0.5, 1.35], [0.9, 0.5, 1.35], [0, -0.6, 1.4]]),
        ]
    elif style == "rib":
        kids += [
            part("Spine", [1.05, 2.15, 1.15], [0, 0.1, -0.2], color=gm, material="Metal"),
            part("Rib1", [3.1, 0.22, 1.85], [0, 0.75, 0], color=panel, material="Metal"),
            part("Rib2", [3.2, 0.22, 1.95], [0, 0.15, 0], color=panel, material="Metal"),
            part("Rib3", [3.05, 0.22, 1.8], [0, -0.45, 0], color=panel, material="Metal"),
            part("Rib4", [2.85, 0.2, 1.65], [0, -0.95, 0], color=panel, material="Metal"),
            visor("GlowWireL", [0.1, 1.7, 0.1], [-0.5, 0.2, 1.0]),
            visor("GlowWireR", [0.1, 1.7, 0.1], [0.5, 0.2, 1.0]),
            part("BackCage", [1.55, 1.2, 0.35], [0, 0.2, -1.2], color=vent, material="Metal"),
            *vent_row("Cage", [0, 0.25, -1.4], count=4, spacing=0.28, size=[0.12, 0.7, 0.1], color=gm),
        ]
    elif style == "rivet":
        kids += [
            part("PlateA", [1.3, 1.05, 0.22], [-0.85, 0.25, 1.25], color=panel, material="DiamondPlate"),
            part("PlateB", [1.3, 1.05, 0.22], [0.85, 0.25, 1.25], color=panel, material="DiamondPlate"),
            *rim_front("PlateA", [1.3, 1.05, 0.22], [-0.85, 0.25, 1.25], color=gm, thickness=0.05),
            *rim_front("PlateB", [1.3, 1.05, 0.22], [0.85, 0.25, 1.25], color=gm, thickness=0.05),
            *bolts(
                "Rivet",
                [
                    [-1.3, 0.65, 1.4],
                    [-0.4, 0.65, 1.4],
                    [-1.3, -0.15, 1.4],
                    [-0.4, -0.15, 1.4],
                    [0.4, 0.65, 1.4],
                    [1.3, 0.65, 1.4],
                    [0.4, -0.15, 1.4],
                    [1.3, -0.15, 1.4],
                ],
                r=0.1,
            ),
            joint_cyl("Exhaust", [0.42, 0.42, 0.85], [0.7, 0.8, -1.4], color=vent),
            joint_cyl("Exhaust2", [0.42, 0.42, 0.85], [-0.7, 0.8, -1.4], color=vent),
            part("SideCageL", [0.28, 1.85, 1.6], [-1.95, 0.1, 0], color=gm, material="Metal"),
            part("SideCageR", [0.28, 1.85, 1.6], [1.95, 0.1, 0], color=gm, material="Metal"),
        ]
    elif style == "vault":
        face = [2.1, 1.4, 0.28]
        kids += [
            part("FacePlate", face, [0, 0.15, 1.3], color=panel, material="DiamondPlate"),
            *rim_front("Face", face, [0, 0.15, 1.3], color=gm, thickness=0.07),
            inset_front("FaceInset", face, [0, 0.15, 1.3], color=darken(panel, 0.12), material="Metal", depth=0.08),
            *panel_stack("VaultDoor", [1.7, 1.0, 0.2], [0, 0.15, 1.35], paint=paint, layers=2, shrink=0.15),
            visor("GlowLock", [0.3, 0.3, 0.18], [0.5, 0.15, 1.55], VISOR_ORANGE),
            joint_cyl("HingeL", [0.16, 1.3, 0.16], [-1.1, 0.15, 1.25], color=gm),
            joint_cyl("HingeR", [0.16, 1.3, 0.16], [1.1, 0.15, 1.25], color=gm),
            part("BackSafe", [2.0, 1.4, 0.45], [0, 0.15, -1.3], color=darken(paint, 0.15), material="Metal"),
            part("RoofLip", [3.15, 0.24, 1.85], [0, 1.35, 0], color=panel, material="Metal"),
            *bolts("Vault", [[-0.8, 0.7, 1.5], [0.8, 0.7, 1.5], [-0.8, -0.4, 1.5], [0.8, -0.4, 1.5]]),
        ]
    elif style == "lattice":
        kids += [
            part("FrameTL", [0.18, 2.2, 0.18], [-1.5, 0.1, -0.85], color=gm, material="Metal"),
            part("FrameTR", [0.18, 2.2, 0.18], [1.5, 0.1, -0.85], color=gm, material="Metal"),
            part("FrameBL", [0.18, 2.2, 0.18], [-1.5, 0.1, 0.85], color=gm, material="Metal"),
            part("FrameBR", [0.18, 2.2, 0.18], [1.5, 0.1, 0.85], color=gm, material="Metal"),
            part("CrossH", [2.8, 0.14, 0.14], [0, 0.5, 0.85], color=gm, material="Metal"),
            part("CrossV", [0.14, 1.8, 0.14], [0, 0.2, 0.85], color=gm, material="Metal"),
            visor("GlowCross", [2.7, 0.12, 0.12], [0, 0.5, 1.0]),
            part("MeshPanel", [2.5, 0.7, 0.1], [0, 0.75, 1.1], color=vent, material="Metal"),
            *vent_row("Mesh", [0, 0.75, 1.2], count=5, spacing=0.35, size=[0.12, 0.45, 0.08], color=gm),
        ]
    elif style == "bunker":
        kids += [
            part("HullArmor", [3.55, 2.15, 2.25], [0, 0.05, 0], color=paint, material="Concrete"),
            *rim_front("HullArmor", [3.55, 2.15, 2.25], [0, 0.05, 0], color=gm, thickness=0.1),
            *panel_stack("BunkerFace", [2.6, 1.5, 0.4], [0, 0.1, 1.05], paint=panel, layers=3, shrink=0.2),
            wedge("CrestSlope", [3.15, 0.45, 1.6], cf([0, 1.25, 0.2]), color=panel),
            visor("GlowSlit", [1.5, 0.22, 0.16], [0, 0.55, 1.4], VISOR_ORANGE),
            part("SideArmorL", [0.4, 1.85, 2.05], [-2.0, 0.05, 0], color=panel, material="Metal"),
            part("SideArmorR", [0.4, 1.85, 2.05], [2.0, 0.05, 0], color=panel, material="Metal"),
            joint_cyl("Antenna", [0.12, 1.05, 0.12], [1.0, 1.95, -0.45], color=gm),
            *bolts("Bunker", [[-1.4, 0.8, 1.2], [1.4, 0.8, 1.2], [-1.2, -0.6, 1.2], [1.2, -0.6, 1.2]]),
            *vent_row("BunkerSide", [-1.85, 0.1, 0.9], count=4, spacing=0.32, size=[0.12, 0.4, 0.1], axis="y"),
        ]
    elif style == "frost":
        ice = lighten(paint, 0.35)
        kids += [
            part("IceFinL", [0.16, 1.3, 0.8], [-1.7, 0.65, -0.5], color=ice, material="Glass", transparency=0.28),
            part("IceFinR", [0.16, 1.3, 0.8], [1.7, 0.65, -0.5], color=ice, material="Glass", transparency=0.28),
            part("FrostCrest", [0.2, 1.1, 0.5], [0, 1.85, 0.8], color=VISOR_CYAN, material="Glass", transparency=0.3),
            part("RimePlate", [1.85, 0.55, 0.22], [0, 0.65, 1.4], color=ice, material="Metal"),
            *panel_stack("FrostFace", [2.2, 1.2, 0.35], [0, 0.2, 1.15], paint=panel, layers=3, shrink=0.18),
            part("IceSkirt", [2.5, 0.18, 1.25], [0, -1.9, 0.4], color=ice, material="Metal"),
            visor("GlowRime", [1.4, 0.14, 0.14], [0, 0.5, 1.5], VISOR_CYAN),
            *bolts("Frost", [[-1.0, 0.8, 1.35], [1.0, 0.8, 1.35], [-0.8, -0.4, 1.35], [0.8, -0.4, 1.35]]),
            *vent_row("FrostSide", [-1.7, 0.15, 0.9], count=4, spacing=0.28, size=[0.12, 0.4, 0.1], axis="y"),
        ]
    elif style == "dune":
        kids += [
            part("DuneNose", [1.45, 0.7, 0.7], [0, 0.05, 1.35], color=lighten(paint, 0.12), material="Metal"),
            *panel_stack("DuneFace", [2.3, 1.3, 0.4], [0, 0.15, 1.05], paint=panel, layers=3, shrink=0.2),
            part("SandSkirtL", [0.65, 0.9, 1.15], [-1.75, -1.3, 0.35], color=panel, material="Metal"),
            part("SandSkirtR", [0.65, 0.9, 1.15], [1.75, -1.3, 0.35], color=panel, material="Metal"),
            part("HeatSinkL", [0.2, 0.85, 0.7], [-2.0, 0.2, 0.85], color=vent, material="Metal"),
            part("HeatSinkR", [0.2, 0.85, 0.7], [2.0, 0.2, 0.85], color=vent, material="Metal"),
            part("OchreBand", [3.35, 0.16, 2.05], [0, -0.2, 0.1], color=VISOR_ORANGE, material="Neon"),
            wedge("DuneSlope", [3.0, 0.45, 1.5], cf([0, 1.2, 0.25]), color=panel),
            *bolts("Dune", [[-1.1, 0.7, 1.3], [1.1, 0.7, 1.3], [-0.9, -0.5, 1.3], [0.9, -0.5, 1.3]]),
            *vent_row("Dune", [0, 0.55, 1.35], count=4, spacing=0.32, size=[0.14, 0.4, 0.1]),
        ]
    elif style == "neon":
        kids += [
            part("NeonTubeL", [0.12, 1.95, 0.12], [-1.5, 0.2, 1.1], color=VISOR_CYAN, material="Neon"),
            part("NeonTubeR", [0.12, 1.95, 0.12], [1.5, 0.2, 1.1], color=VISOR_RED, material="Neon"),
            part("NeonRing", [2.35, 0.12, 2.35], [0, 0.85, 0.1], color=VISOR_CYAN, material="Neon"),
            part("MagPlate", [2.05, 0.9, 0.24], [0, 0.25, 1.4], color=panel, material="Metal"),
            *panel_stack("VoltFace", [1.7, 0.7, 0.25], [0, 0.3, 1.5], paint=paint, layers=2, shrink=0.14),
            visor("GlowMagCore", [0.55, 0.55, 0.2], [0, 0.25, 1.65], VISOR_RED),
            part("NightFin", [0.18, 1.35, 0.95], [0, 0.75, -1.5], color=darken(paint, 0.15), material="Metal"),
            part("BackGlow", [1.6, 0.14, 0.14], [0, 0.4, -1.7], color=VISOR_CYAN, material="Neon"),
            *bolts("Neon", [[-1.0, 0.75, 1.3], [1.0, 0.75, 1.3], [-0.85, -0.4, 1.3], [0.85, -0.4, 1.3]]),
            *vent_row("NeonSide", [-1.65, 0.1, 0.85], count=4, spacing=0.28, size=[0.12, 0.35, 0.1], axis="y"),
        ]
    else:  # glass
        kids += [
            part("Canopy", [1.75, 0.95, 1.25], [0, 1.35, 0.5], color=lighten(paint, 0.35), material="Glass", transparency=0.35),
            part("CanopyFrame", [1.95, 0.12, 1.4], [0, 0.9, 0.5], color=gm, material="Metal"),
            part("AccentRim", [2.0, 0.12, 1.45], [0, 0.85, 0.5], color=VISOR_CYAN, material="Neon"),
            part("CheekL", [0.45, 0.8, 0.85], [-1.75, 0.55, 0.4], color=panel, material="Metal"),
            part("CheekR", [0.45, 0.8, 0.85], [1.75, 0.55, 0.4], color=panel, material="Metal"),
            part("BackFin", [0.18, 1.2, 0.95], [0, 0.85, -1.25], color=gm, material="Metal"),
            *vent_row("GlassSide", [-1.6, 0.15, 0.9], count=3, spacing=0.25, size=[0.1, 0.35, 0.1], axis="y"),
            *bolts("Glass", [[-1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]),
        ]
    return kids


# ---------------------------------------------------------------------------
# Legs — articulated plantigrade / digitigrade / tread with dense armor
# ---------------------------------------------------------------------------


def build_leg(base: list[float], *, style: str, side: str) -> list[dict]:
    """Short thick chibi legs. Root = hip pivot. Baked knee-forward combat crouch."""
    s = -1.0 if side == "l" else 1.0
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    sole = rgb(36, 34, 32)
    panel = panel_safe(paint)

    kids += joint_assembly("Hip", [0, 0, 0], scale=0.9)

    if style in ("workboot", "stump", "hoof", "claw", "digit", "hinge", "frostleg"):
        # Combat crouch: thigh pitched forward, knee disk proud, shin down, fat boot
        kids += [
            part("Thigh", [1.05, 0.95, 1.15], [0.1 * s, -0.55, 0.35], color=paint, material="Metal"),
            part("ThighArmor", [0.95, 0.55, 0.95], [0.12 * s, -0.35, 0.55], color=panel, material="DiamondPlate"),
            *rim_front("Thigh", [1.05, 0.95, 1.15], [0.1 * s, -0.55, 0.35], color=gm, thickness=0.06),
            *panel_stack("ThighFace", [0.85, 0.7, 0.3], [0.1 * s, -0.5, 0.7], paint=panel, layers=2, shrink=0.12),
            *joint_assembly("Knee", [0.12 * s, -1.15, 0.55], scale=0.85),
            part("Shin", [0.95, 0.9, 1.0], [0.08 * s, -1.75, 0.2], color=paint, material="Metal"),
            part("ShinGuard", [0.85, 0.7, 0.35], [0.08 * s, -1.65, 0.65], color=panel, material="Metal"),
            inset_front("ShinInset", [0.95, 0.9, 1.0], [0.08 * s, -1.75, 0.2], color=panel),
            *vent_row("Shin", [0.08 * s, -1.7, 0.75], count=3, spacing=0.22, size=[0.5, 0.12, 0.1], axis="y", color=gm),
            joint_cyl("Ankle", [0.7, 0.32, 0.7], [0.05 * s, -2.2, 0.35], color=gm),
            part("Foot", [1.4, 0.35, 1.65], [0, -2.45, 0.45], color=sole, material="SmoothPlastic"),
            part("SolePlate", [1.25, 0.12, 1.4], [0, -2.65, 0.4], color=darken(sole, 0.2), material="Metal"),
            part("ToeLip", [1.2, 0.25, 0.35], [0, -2.3, 1.15], color=gm, material="Metal"),
            part("Heel", [1.0, 0.28, 0.4], [0, -2.4, -0.25], color=gm, material="Metal"),
            visor("GlowAnkle", [0.28, 0.16, 0.16], [0.4 * s, -2.15, 0.7], VISOR_ORANGE),
            *bolts("Leg", [[0.45 * s, -0.4, 0.85], [0.4 * s, -1.7, 0.7], [-0.35 * s, -1.0, 0.7]], r=0.1),
        ]
        if style == "stump":
            kids += [
                part("ThighPlate", [0.2, 0.75, 0.85], [0.7 * s, -0.5, 0.35], color=panel, material="DiamondPlate"),
                part("ShinPlate", [0.18, 0.7, 0.7], [0.65 * s, -1.7, 0.25], color=panel, material="Metal"),
            ]
        if style == "claw":
            kids += [
                part("ClawL", [0.25, 0.22, 0.85], [-0.35, -2.4, 1.1], color=gm, material="Metal"),
                part("ClawMid", [0.25, 0.22, 0.95], [0, -2.4, 1.2], color=gm, material="Metal"),
                part("ClawR", [0.25, 0.22, 0.85], [0.35, -2.4, 1.1], color=gm, material="Metal"),
            ]
        if style == "digit":
            kids += [
                part("ToeMid", [0.35, 0.22, 0.8], [0, -2.4, 1.05], color=sole, material="Metal"),
                part("ToeL", [0.28, 0.2, 0.7], [-0.4, -2.35, 0.95], color=sole, material="Metal"),
                part("ToeR", [0.28, 0.2, 0.7], [0.4, -2.35, 0.95], color=sole, material="Metal"),
            ]
        if style == "hoof":
            kids += [
                part("HoofBlock", [1.15, 0.4, 1.0], [0, -2.5, 0.55], color=darken(paint, 0.15), material="Metal"),
                wedge("HoofTip", [0.9, 0.3, 0.45], cf([0, -2.35, 1.15]), color=gm),
            ]
        if style == "hinge":
            kids += [
                part("HingeBrace", [0.2, 1.1, 0.35], [0.55 * s, -1.4, 0.15], color=gm, material="Metal"),
                joint_cyl("HingeRod", [0.18, 0.9, 0.18], [0.35 * s, -1.4, -0.1], color=lighten(gm, 0.1)),
            ]
        if style == "frostleg":
            ice = lighten(paint, 0.3)
            kids += [
                part("IceToe", [1.15, 0.2, 0.5], [0, -2.35, 1.35], color=ice, material="Glass", transparency=0.3),
                part("SkiBlade", [0.32, 0.12, 1.5], [0.5 * s, -2.55, 0.45], color=gm, material="Metal"),
                visor("GlowShinIce", [0.5, 0.12, 0.12], [0.08 * s, -1.55, 0.85], VISOR_CYAN),
            ]
    elif style in ("sprint", "piston", "strut"):
        kids += [
            part("Thigh", [0.8, 0.9, 0.85], [0.12 * s, -0.5, 0.4], color=paint, material="Metal"),
            part("ThighFairing", [0.55, 0.4, 0.7], [0.12 * s, -0.35, 0.65], color=panel, material="Metal"),
            *joint_assembly("Knee", [0.14 * s, -1.05, 0.65], scale=0.7),
            part("Shin", [0.7, 1.0, 0.7], [0.1 * s, -1.7, 0.2], color=paint, material="Metal"),
            *vent_row("RunShin", [0.1 * s, -1.65, 0.55], count=3, spacing=0.22, size=[0.4, 0.1, 0.08], axis="y"),
            joint_cyl("Ankle", [0.5, 0.28, 0.5], [0, -2.25, 0.1], color=gm),
            part("Foot", [0.95, 0.28, 1.3], [0, -2.5, 0.45], color=sole, material="SmoothPlastic"),
            part("ToeSpike", [0.35, 0.18, 0.55], [0, -2.4, 1.0], color=gm, material="Metal"),
            wedge("ShinFairing", [0.3, 0.45, 0.55], cf([0.35 * s, -1.45, 0.45]), color=panel),
            visor("GlowKnee", [0.2, 0.2, 0.14], [0.4 * s, -1.05, 0.9]),
            *bolts("Run", [[0.35 * s, -0.4, 0.7], [0.3 * s, -1.7, 0.5]], r=0.09),
        ]
        if style == "piston":
            kids += [
                joint_cyl("PistonRod", [0.26, 1.05, 0.26], [0, -1.45, 0.25], color=gm),
                part("PistonHead", [0.4, 0.22, 0.4], [0, -0.9, 0.25], color=panel, material="Metal"),
            ]
    elif style == "tread":
        kids += [
            part("Upper", [1.2, 0.6, 1.15], [0, -0.3, 0.15], color=paint, material="Metal"),
            part("TrackBox", [1.5, 1.1, 1.85], [0, -1.3, 0.2], color=darken(paint, 0.1), material="DiamondPlate"),
            *rim_front("Track", [1.5, 1.1, 1.85], [0, -1.3, 0.2], color=gm, thickness=0.07),
            joint_cyl("WheelF", [0.4, 0.8, 0.8], [0.55 * s, -1.65, 0.75], color=gm),
            joint_cyl("WheelM", [0.35, 0.7, 0.7], [0.55 * s, -1.7, 0.1], color=darken(gm, 0.1)),
            joint_cyl("WheelB", [0.4, 0.8, 0.8], [0.55 * s, -1.65, -0.55], color=gm),
            part("TrackPad1", [1.55, 0.18, 0.35], [0, -1.95, 0.7], color=sole, material="SmoothPlastic"),
            part("TrackPad2", [1.55, 0.18, 0.35], [0, -1.95, 0.15], color=sole, material="SmoothPlastic"),
            part("TrackPad3", [1.55, 0.18, 0.35], [0, -1.95, -0.4], color=sole, material="SmoothPlastic"),
            visor("GlowLight", [0.28, 0.22, 0.14], [0, -0.1, 0.8], VISOR_ORANGE),
            *vent_row("Tread", [0, -0.85, 1.1], count=3, spacing=0.3, size=[0.7, 0.12, 0.1], axis="x"),
            *bolts("Tread", [[0.5 * s, -0.9, 1.0], [-0.4 * s, -1.4, 1.0]]),
        ]
    else:
        kids += [
            part("Thigh", [0.95, 0.95, 1.0], [0.1 * s, -0.55, 0.25], color=paint, material="Metal"),
            *joint_assembly("Knee", [0.12 * s, -1.15, 0.35], scale=0.8),
            part("Shin", [0.85, 0.9, 0.9], [0.08 * s, -1.75, 0.1], color=paint, material="Metal"),
            part("Foot", [1.25, 0.32, 1.45], [0, -2.4, 0.35], color=sole, material="SmoothPlastic"),
            *bolts("Basic", [[0.4 * s, -0.5, 0.7], [0.35 * s, -1.7, 0.5]], r=0.1),
        ]
    return kids


# ---------------------------------------------------------------------------
# Lower weapons — dense receivers, barrels, grips, magazines
# ---------------------------------------------------------------------------


def build_lower_weapon(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    panel = panel_safe(paint)
    kids.append(joint_cyl("Mount", [0.65, 0.5, 0.65], [0, 0, -0.9], color=gm))
    kids.append(part("MountCollar", [0.85, 0.22, 0.85], [0, 0, -0.55], color=panel, material="Metal"))

    if style == "snap":
        kids += [
            part("Forearm", [0.85, 0.7, 1.2], [0, 0, -0.05], color=paint, material="Metal"),
            *rim_front("Forearm", [0.85, 0.7, 1.2], [0, 0, -0.05], color=gm, thickness=0.05),
            *panel_stack("ArmPlate", [0.7, 0.5, 0.25], [0, 0.1, 0.4], paint=panel, layers=2, shrink=0.1),
            part("Fist", [1.15, 1.0, 0.95], [0, 0, 1.1], color=darken(paint, 0.1), material="Metal"),
            part("Knuckle", [1.2, 0.28, 0.3], [0, 0.4, 1.4], color=gm, material="Metal"),
            part("Knuckle2", [1.1, 0.2, 0.22], [0, 0.15, 1.5], color=gm, material="Metal"),
            visor("GlowKnuckle", [0.85, 0.12, 0.12], [0, 0.45, 1.5], VISOR_ORANGE),
            *bolts("Snap", [[-0.35, 0.25, 0.5], [0.35, 0.25, 0.5], [0, -0.3, 1.4]], r=0.1),
            *vent_row("Fist", [0, 0.15, 1.55], count=3, spacing=0.28, size=[0.12, 0.45, 0.1]),
        ]
    elif style in ("rivet", "mg"):
        kids += [
            part("Receiver", [0.9, 0.75, 1.3], [0, 0.05, 0], color=paint, material="Metal"),
            *rim_front("Receiver", [0.9, 0.75, 1.3], [0, 0.05, 0], color=gm, thickness=0.05),
            *panel_stack("RecvFace", [0.7, 0.5, 0.25], [0, 0.15, 0.5], paint=panel, layers=2, shrink=0.1),
            joint_cyl("CoolingJacket", [0.48, 0.48, 0.9], [0, 0.15, 0.85], color=darken(gm, 0.1)),
            *barrel_cluster("Gun", [0, 0.15, 1.55], n=3 if style == "mg" else 2, length=1.55, radius=0.2, spread=0.26),
            *vent_row("Cool", [0, 0.55, 0.6], count=4, spacing=0.18, size=[0.55, 0.1, 0.1], axis="z", color=gm),
            part("Mag", [0.5, 0.65, 0.4], [0.55, -0.2, 0.15], color=gm, material="Metal"),
            part("MagLip", [0.55, 0.12, 0.45], [0.55, -0.5, 0.15], color=panel, material="Metal"),
            part("Grip", [0.32, 0.5, 0.32], [0, -0.55, -0.2], color=rgb(40, 40, 44), material="SmoothPlastic"),
            part("Sight", [0.14, 0.35, 0.4], [0, 0.55, 0.35], color=gm, material="Metal"),
            visor("GlowSight", [0.1, 0.1, 0.12], [0, 0.7, 0.5]),
            *bolts("MG", [[-0.4, 0.3, 0.5], [0.4, 0.3, 0.5]], r=0.09),
        ]
    elif style == "ember":
        kids += [
            part("Gauntlet", [1.1, 1.0, 1.2], [0, 0, 0], color=paint, material="CorrodedMetal"),
            *panel_stack("EmberFace", [0.9, 0.75, 0.3], [0, 0.1, 0.5], paint=darken(paint, 0.1), layers=2),
            visor("GlowCore", [0.55, 0.55, 0.55], [0, 0.15, 0.6], VISOR_ORANGE),
            part("VentL", [0.2, 0.45, 0.7], [-0.55, 0.2, 0.3], color=gm, material="Metal"),
            part("VentR", [0.2, 0.45, 0.7], [0.55, 0.2, 0.3], color=gm, material="Metal"),
            *vent_row("Ember", [0, 0.55, 0.4], count=3, spacing=0.25, size=[0.7, 0.1, 0.1]),
            part("PunchPlate", [1.2, 1.05, 0.3], [0, 0, 1.1], color=gm, material="Metal"),
            *bolts("Ember", [[-0.4, 0.4, 1.2], [0.4, 0.4, 1.2], [0, -0.4, 1.2]]),
        ]
    elif style in ("needle", "beam"):
        kids += [
            part("Housing", [0.8, 0.7, 1.1], [0, 0.1, 0], color=paint, material="Metal"),
            *rim_front("Housing", [0.8, 0.7, 1.1], [0, 0.1, 0], color=gm, thickness=0.05),
            part("Crystal", [0.4, 0.4, 0.6], [0, 0.15, 0.8], color=VISOR_CYAN, material="Glass", transparency=0.25),
            joint_cyl("Emitter", [0.32, 0.32, 1.05], [0, 0.15, 1.55], color=gm),
            visor("GlowBeam", [0.12, 0.12, 1.4], [0, 0.15, 1.4]),
            joint_cyl("FocusRing", [0.65, 0.12, 0.65], [0, 0.15, 0.45], color=gm),
            joint_cyl("FocusRing2", [0.55, 0.1, 0.55], [0, 0.15, 1.0], color=lighten(gm, 0.1)),
            *vent_row("Beam", [0, 0.5, 0.2], count=3, spacing=0.22, size=[0.5, 0.1, 0.1]),
            part("BatteryPack", [0.45, 0.55, 0.4], [0.5, -0.15, -0.1], color=gm, material="Metal"),
            *bolts("Beam", [[-0.3, 0.35, 0.4], [0.3, 0.35, 0.4]]),
        ]
    elif style in ("cleaver", "melee"):
        kids += [
            part("Haft", [0.4, 0.4, 1.3], [0, 0, -0.15], color=gm, material="Metal"),
            part("HaftWrap", [0.45, 0.45, 0.5], [0, 0, -0.5], color=rgb(40, 40, 44), material="SmoothPlastic"),
            part("Guard", [1.1, 0.22, 0.8], [0, 0.35, 0.5], color=paint, material="Metal"),
            part("GuardSpikeL", [0.2, 0.35, 0.35], [-0.55, 0.45, 0.55], color=gm, material="Metal"),
            part("GuardSpikeR", [0.2, 0.35, 0.35], [0.55, 0.45, 0.55], color=gm, material="Metal"),
            part("Blade", [0.16, 0.65, 2.0], [0, 0.1, 1.5], color=lighten(paint, 0.12), material="Metal"),
            part("BladeSpine", [0.22, 0.25, 1.9], [0, 0.35, 1.5], color=gm, material="Metal"),
            visor("GlowEdge", [0.06, 0.5, 1.85], [0.12, 0.1, 1.5], VISOR_RED),
            part("Pommel", [0.45, 0.45, 0.3], [0, 0, -1.0], color=gm, material="Metal"),
            *bolts("Blade", [[0, 0.35, 0.9], [0, 0.35, 1.6]], r=0.09),
        ]
    elif style == "drill":
        kids += [
            part("Motor", [0.95, 0.85, 1.0], [0, 0, -0.2], color=paint, material="Metal"),
            *rim_front("Motor", [0.95, 0.85, 1.0], [0, 0, -0.2], color=gm, thickness=0.05),
            joint_cyl("Bit", [0.45, 0.45, 1.55], [0, 0, 1.2], color=gm),
            joint_cyl("BitTip", [0.28, 0.28, 0.55], [0, 0, 2.1], color=lighten(gm, 0.15)),
            visor("GlowRing", [0.95, 0.16, 0.95], [0, 0, 0.45], VISOR_ORANGE),
            *vent_row("Drill", [0, 0.5, -0.1], count=3, spacing=0.25, size=[0.6, 0.1, 0.1]),
            part("Handle", [0.35, 0.6, 0.35], [0, -0.7, -0.3], color=rgb(40, 40, 44), material="SmoothPlastic"),
            *bolts("Drill", [[-0.4, 0.3, 0.2], [0.4, 0.3, 0.2]]),
        ]
    elif style == "spray":
        kids += [
            part("Tank", [0.9, 0.9, 1.1], [0, 0.1, -0.2], color=paint, material="Metal"),
            *panel_stack("TankFace", [0.7, 0.65, 0.25], [0, 0.15, 0.25], paint=panel, layers=2),
            joint_cyl("Nozzle", [0.35, 0.35, 1.0], [0, 0.15, 1.1], color=gm),
            joint_cyl("NozzleTip", [0.45, 0.2, 0.45], [0, 0.15, 1.6], color=panel),
            visor("GlowValve", [0.3, 0.3, 0.25], [0.4, 0.5, 0], VISOR_ORANGE),
            part("Hose", [0.16, 0.16, 0.7], [0.5, -0.2, -0.55], color=rgb(40, 40, 44), material="SmoothPlastic"),
            *bolts("Spray", [[-0.35, 0.4, 0.3], [0.35, -0.2, 0.3]]),
        ]
    elif style == "shield":
        kids += [
            part("Brace", [0.65, 0.5, 0.9], [0, 0, -0.3], color=gm, material="Metal"),
            part("Face", [1.6, 2.05, 0.25], [0, 0.15, 0.8], color=paint, material="DiamondPlate"),
            *rim_front("Face", [1.6, 2.05, 0.25], [0, 0.15, 0.8], color=gm, thickness=0.07),
            *panel_stack("ShieldFace", [1.3, 1.5, 0.2], [0, 0.2, 0.9], paint=panel, layers=2, shrink=0.15),
            part("Boss", [0.5, 0.5, 0.25], [0, 0.2, 1.0], color=gm, material="Metal"),
            visor("GlowBoss", [0.3, 0.3, 0.1], [0, 0.2, 1.15]),
            part("LipL", [0.2, 1.65, 0.3], [-0.85, 0.15, 0.8], color=panel, material="Metal"),
            part("LipR", [0.2, 1.65, 0.3], [0.85, 0.15, 0.8], color=panel, material="Metal"),
            part("LipTop", [1.4, 0.2, 0.3], [0, 1.15, 0.8], color=panel, material="Metal"),
            *bolts("Shield", [[-0.55, 0.8, 1.0], [0.55, 0.8, 1.0], [-0.55, -0.5, 1.0], [0.55, -0.5, 1.0]]),
        ]
    else:  # hook
        kids += [
            part("Arm", [0.65, 0.5, 1.4], [0, 0, 0], color=paint, material="Metal"),
            *panel_stack("HookArm", [0.5, 0.35, 0.25], [0, 0.15, 0.4], paint=panel, layers=2, shrink=0.08),
            part("HookCurve", [0.4, 0.85, 0.4], [0, 0.35, 1.15], color=gm, material="Metal"),
            part("HookTip", [0.28, 0.28, 0.75], [0, 0.7, 1.55], color=gm, material="Metal"),
            part("HookBarb", [0.2, 0.35, 0.25], [0, 0.9, 1.85], color=lighten(gm, 0.1), material="Metal"),
            part("Winch", [0.45, 0.45, 0.45], [0, -0.35, -0.35], color=gm, material="Metal", shape="Cylinder"),
            visor("GlowChain", [0.14, 0.14, 0.8], [0, -0.3, 0.4], VISOR_ORANGE),
            *bolts("Hook", [[0, 0.25, 0.5], [0, 0.5, 1.3]], r=0.09),
            *vent_row("Hook", [0, 0.35, 0.2], count=2, spacing=0.3, size=[0.4, 0.1, 0.1]),
        ]
    return kids


# ---------------------------------------------------------------------------
# Shoulder weapons — pods, cannons, rails with dense detail
# ---------------------------------------------------------------------------


def build_shoulder_weapon(base: list[float], *, style: str) -> list[dict]:
    kids: list[dict] = []
    paint = base
    gm = GUNMETAL
    panel = panel_safe(paint)
    kids += [
        part("ShoulderMount", [1.1, 0.45, 0.9], [0, -0.15, -0.7], color=gm, material="Metal"),
        part("MountBrace", [0.9, 0.25, 0.7], [0, 0.15, -0.55], color=panel, material="Metal"),
        *bolts("Mount", [[-0.4, -0.15, -0.4], [0.4, -0.15, -0.4]], r=0.1),
    ]

    if style in ("box", "rocket"):
        kids += [
            part("PodBox", [1.45, 1.05, 1.4], [0, 0.45, 0.3], color=paint, material="Metal"),
            *rim_front("Pod", [1.45, 1.05, 1.4], [0, 0.45, 0.3], color=gm, thickness=0.07),
            *panel_stack("PodFace", [1.2, 0.85, 0.3], [0, 0.5, 0.85], paint=panel, layers=2, shrink=0.12),
            joint_cyl("TubeTL", [0.36, 0.36, 1.25], [-0.35, 0.7, 0.9], color=gm),
            joint_cyl("TubeTR", [0.36, 0.36, 1.25], [0.35, 0.7, 0.9], color=gm),
            joint_cyl("TubeBL", [0.36, 0.36, 1.25], [-0.35, 0.25, 0.9], color=gm),
            joint_cyl("TubeBR", [0.36, 0.36, 1.25], [0.35, 0.25, 0.9], color=gm),
            visor("GlowTubeTL", [0.24, 0.24, 0.1], [-0.35, 0.7, 1.55]),
            visor("GlowTubeTR", [0.24, 0.24, 0.1], [0.35, 0.7, 1.55]),
            visor("GlowTubeBL", [0.24, 0.24, 0.1], [-0.35, 0.25, 1.55]),
            visor("GlowTubeBR", [0.24, 0.24, 0.1], [0.35, 0.25, 1.55]),
            part("Hatch", [1.15, 0.14, 0.85], [0, 1.05, 0.15], color=gm, material="Metal"),
            *vent_row("PodSide", [-0.8, 0.45, 0.3], count=3, spacing=0.25, size=[0.1, 0.35, 0.5], axis="y"),
            *bolts("Pod", [[-0.55, 0.9, 0.9], [0.55, 0.9, 0.9]]),
        ]
        if style == "rocket":
            kids += [
                joint_cyl("TubeMid", [0.32, 0.32, 1.1], [0, 1.05, 0.6], color=darken(gm, 0.1)),
                visor("GlowTubeMid", [0.2, 0.2, 0.1], [0, 1.05, 1.2], VISOR_ORANGE),
            ]
    elif style in ("brick", "mg", "bite"):
        kids += [
            part("Breech", [1.2, 0.75, 0.8], [0, 0.15, -0.3], color=gm, material="Metal"),
            part("Receiver", [1.1, 0.65, 1.1], [0, 0.25, 0.6], color=paint, material="Metal"),
            *rim_front("Receiver", [1.1, 0.65, 1.1], [0, 0.25, 0.6], color=gm, thickness=0.05),
            *panel_stack("CannonFace", [0.9, 0.45, 0.25], [0, 0.35, 1.0], paint=panel, layers=2, shrink=0.1),
            joint_cyl("Collar", [0.8, 0.2, 0.8], [0, 0.3, 1.0], color=panel),
            *barrel_cluster("Shoulder", [0, 0.3, 1.7], n=3 if style == "mg" else 2, length=1.5, radius=0.22, spread=0.3),
            part("SidePlateL", [0.14, 0.6, 0.95], [-0.7, 0.2, 0.35], color=panel, material="Metal"),
            part("SidePlateR", [0.14, 0.6, 0.95], [0.7, 0.2, 0.35], color=panel, material="Metal"),
            *vent_row("Cannon", [0, 0.65, 0.4], count=3, spacing=0.22, size=[0.7, 0.1, 0.1]),
            part("AmmoDrum", [0.7, 0.7, 0.7], [0.85, -0.1, -0.15], color=gm, material="Metal", shape="Cylinder"),
            *bolts("Cannon", [[-0.45, 0.5, 0.9], [0.45, 0.5, 0.9]]),
        ]
    elif style in ("arc", "beam", "spear"):
        kids += [
            part("RailBody", [0.95, 0.65, 1.9], [0, 0.2, 0.5], color=paint, material="Metal"),
            *rim_front("Rail", [0.95, 0.65, 1.9], [0, 0.2, 0.5], color=gm, thickness=0.05),
            visor("GlowRail", [0.16, 0.16, 2.05], [0, 0.45, 0.55]),
            joint_cyl("CoilL", [0.28, 0.45, 0.45], [-0.5, 0.2, 0.2], color=gm),
            joint_cyl("CoilR", [0.28, 0.45, 0.45], [0.5, 0.2, 0.2], color=gm),
            joint_cyl("CoilL2", [0.28, 0.45, 0.45], [-0.5, 0.2, 0.9], color=gm),
            joint_cyl("CoilR2", [0.28, 0.45, 0.45], [0.5, 0.2, 0.9], color=gm),
            visor("GlowEmitter", [0.4, 0.4, 0.3], [0, 0.25, 1.75]),
            *vent_row("Rail", [0, 0.55, 0.3], count=4, spacing=0.28, size=[0.55, 0.1, 0.1], axis="z"),
            *bolts("Rail", [[-0.35, 0.45, 1.2], [0.35, 0.45, 1.2]]),
        ]
    elif style == "slag":
        kids += [
            part("Drum", [1.3, 1.05, 1.3], [0, 0.25, 0], color=paint, material="CorrodedMetal"),
            *panel_stack("SlagFace", [1.0, 0.75, 0.3], [0, 0.3, 0.55], paint=darken(paint, 0.1), layers=2),
            joint_cyl("Spout", [0.6, 0.6, 1.15], [0, 0.15, 1.2], color=gm),
            visor("GlowCrust", [0.8, 0.3, 0.3], [0.35, 0.65, 0.35], VISOR_ORANGE),
            part("Support", [0.35, 0.8, 0.35], [0, -0.45, -0.2], color=gm, material="Metal"),
            *vent_row("Slag", [0, 0.7, -0.2], count=3, spacing=0.28, size=[0.8, 0.1, 0.1]),
            *bolts("Slag", [[-0.5, 0.5, 0.6], [0.5, 0.5, 0.6]]),
        ]
    elif style == "twin":
        kids += [
            part("Cradle", [1.4, 0.5, 1.1], [0, 0.05, 0], color=gm, material="Metal"),
            joint_cyl("GunL", [0.35, 0.35, 2.05], [-0.4, 0.35, 0.8], color=paint),
            joint_cyl("GunR", [0.35, 0.35, 2.05], [0.4, 0.35, 0.8], color=paint),
            joint_cyl("SleeveL", [0.48, 0.48, 0.7], [-0.4, 0.35, 0.35], color=panel),
            joint_cyl("SleeveR", [0.48, 0.48, 0.7], [0.4, 0.35, 0.35], color=panel),
            visor("GlowMuzzleL", [0.28, 0.28, 0.12], [-0.4, 0.35, 1.9], VISOR_ORANGE),
            visor("GlowMuzzleR", [0.28, 0.28, 0.12], [0.4, 0.35, 1.9], VISOR_ORANGE),
            visor("GlowBridge", [0.85, 0.14, 0.14], [0, 0.6, 0.4]),
            *bolts("Twin", [[-0.55, 0.1, 0.3], [0.55, 0.1, 0.3]]),
        ]
    elif style == "mortar":
        kids += [
            part("Base", [1.3, 0.4, 1.3], [0, -0.05, 0], color=gm, material="Metal"),
            joint_cyl("Tube", [0.8, 0.8, 1.8], [0, 0.55, 0.55], color=paint),
            joint_cyl("TubeLip", [0.95, 0.18, 0.95], [0, 0.55, -0.2], color=panel),
            visor("GlowRing", [0.95, 0.16, 0.95], [0, 0.55, 0.05], VISOR_ORANGE),
            part("Bipod", [1.1, 0.6, 0.22], [0, -0.15, 0.65], color=gm, material="Metal"),
            *vent_row("Mortar", [0, 1.0, 0.4], count=3, spacing=0.3, size=[0.7, 0.1, 0.1]),
            *bolts("Mortar", [[-0.5, 0.15, 0.5], [0.5, 0.15, 0.5]]),
        ]
    else:
        kids += [
            part("Receiver", [1.05, 0.65, 1.15], [0, 0.2, 0.35], color=paint, material="Metal"),
            *rim_front("Recv", [1.05, 0.65, 1.15], [0, 0.2, 0.35], color=gm, thickness=0.05),
            joint_cyl("Barrel", [0.38, 0.38, 1.55], [0, 0.25, 1.5], color=gm),
            visor("GlowMuzzle", [0.32, 0.32, 0.18], [0, 0.25, 2.3], VISOR_ORANGE),
            *vent_row("Gen", [0, 0.55, 0.3], count=3, spacing=0.25, size=[0.6, 0.1, 0.1]),
            *bolts("Gen", [[-0.4, 0.4, 0.7], [0.4, 0.4, 0.7]]),
        ]
    return kids


def build_battery(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    paint = base
    kids = [
        part("Pack", [1.45, 0.9, 0.65], [0, 0, 0], color=paint, material="Metal"),
        *rim_front("Pack", [1.45, 0.9, 0.65], [0, 0, 0], color=gm, thickness=0.05),
        *bolts("Bat", [[-0.55, 0.35, 0.35], [0.55, 0.35, 0.35]], r=0.09),
    ]
    if style == "desk":
        kids += [
            visor("GlowTerminal", [0.22, 0.22, 0.16], [-0.4, 0.5, 0], VISOR_RED),
            part("Terminal-", [0.22, 0.22, 0.16], [0.4, 0.5, 0], color=gm, material="Metal"),
            part("AccentLabel", [0.8, 0.28, 0.08], [0, 0.1, 0.4], color=VISOR_CYAN, material="Neon"),
            *vent_row("Desk", [0, -0.2, 0.4], count=3, spacing=0.28, size=[0.12, 0.35, 0.08]),
        ]
    elif style == "bay":
        kids += [
            part("CellA", [0.35, 0.6, 0.4], [-0.4, 0, 0.15], color=darken(paint, 0.2), material="Glass", transparency=0.3),
            part("CellB", [0.35, 0.6, 0.4], [0.4, 0, 0.15], color=darken(paint, 0.2), material="Glass", transparency=0.3),
            visor("GlowBus", [1.3, 0.12, 0.12], [0, 0.55, 0]),
            part("ClampL", [0.14, 0.7, 0.45], [-0.75, 0, 0], color=gm, material="Metal"),
            part("ClampR", [0.14, 0.7, 0.45], [0.75, 0, 0], color=gm, material="Metal"),
        ]
    elif style == "deep":
        kids += [
            visor("GlowRing", [1.6, 0.16, 0.8], [0, 0.3, 0]),
            part("CapTop", [1.3, 0.22, 0.55], [0, 0.65, 0], color=gm, material="Metal"),
            part("Port", [0.3, 0.3, 0.22], [0, 0, 0.5], color=VISOR_CYAN, material="Neon"),
            *vent_row("Deep", [0, 0, 0.4], count=3, spacing=0.3, size=[0.12, 0.5, 0.08]),
        ]
    elif style == "stack":
        kids += [
            part("Layer2", [1.35, 0.28, 0.6], [0, 0, 0], color=darken(paint, 0.15), material="Metal"),
            part("Layer3", [1.35, 0.28, 0.6], [0, 0.35, 0], color=paint, material="Metal"),
            visor("GlowStripe", [0.12, 0.95, 0.12], [0.65, 0, 0.3]),
            *bolts("Stack", [[-0.5, 0.35, 0.3], [0.5, -0.15, 0.3]], r=0.08),
        ]
    else:
        kids += [
            joint_cyl("Drum", [1.1, 1.1, 0.75], [0, 0, 0], color=paint),
            visor("GlowBand", [1.2, 0.14, 0.85], [0, 0.2, 0]),
            *vent_row("Drum", [0, 0.55, 0], count=4, spacing=0.35, size=[0.12, 0.2, 0.4], axis="x"),
        ]
    return kids


def build_cpu(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    kids = [
        part("Board", [1.0, 0.1, 1.0], [0, 0, 0], color=darken(base, 0.2), material="Plastic"),
        part("Die", [0.42, 0.2, 0.42], [0, 0.16, 0], color=gm, material="Metal"),
        visor("GlowLED", [0.16, 0.08, 0.16], [0.35, 0.12, 0.35]),
        part("TraceA", [0.5, 0.04, 0.06], [-0.2, 0.08, 0.3], color=VISOR_CYAN, material="Neon"),
        part("TraceB", [0.06, 0.04, 0.4], [0.3, 0.08, -0.1], color=VISOR_CYAN, material="Neon"),
        *bolts("CPU", [[-0.4, 0.08, -0.4], [0.4, 0.08, -0.4], [-0.4, 0.08, 0.4]], r=0.07),
    ]
    if style == "bay":
        kids.append(part("Heatsink", [0.65, 0.3, 0.65], [0, 0.28, 0], color=gm, material="Metal"))
        kids += vent_row("Sink", [0, 0.4, 0], count=4, spacing=0.14, size=[0.5, 0.2, 0.06], axis="z")
    elif style != "scrap":
        kids.append(part("Crystal", [0.4, 0.45, 0.4], [0, 0.4, 0], color=VISOR_CYAN, material="Glass", transparency=0.25))
    return kids


def build_drone(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    paint = base
    if style == "floor":
        return [
            part("Chassis", [1.0, 0.35, 1.1], [0, 0, 0], color=paint, material="Metal"),
            *rim_front("Chassis", [1.0, 0.35, 1.1], [0, 0, 0], color=gm, thickness=0.04),
            joint_cyl("WheelL", [0.28, 0.45, 0.45], [-0.55, -0.15, 0.3], color=gm),
            joint_cyl("WheelR", [0.28, 0.45, 0.45], [0.55, -0.15, 0.3], color=gm),
            joint_cyl("WheelB", [0.24, 0.35, 0.35], [0, -0.15, -0.4], color=gm),
            visor("GlowEye", [0.3, 0.2, 0.16], [0, 0.25, 0.55]),
            *bolts("Floor", [[-0.3, 0.2, 0.3], [0.3, 0.2, 0.3]], r=0.08),
        ]
    if style == "moth":
        return [
            part("Body", [0.45, 0.35, 0.8], [0, 0, 0], color=paint, material="SmoothPlastic"),
            part("WingL", [0.8, 0.08, 0.5], [-0.55, 0.15, 0], color=lighten(paint, 0.2), material="Glass", transparency=0.3),
            part("WingR", [0.8, 0.08, 0.5], [0.55, 0.15, 0], color=lighten(paint, 0.2), material="Glass", transparency=0.3),
            visor("GlowSpark", [0.2, 0.2, 0.2], [0, 0.2, 0.4]),
            part("AntennaL", [0.06, 0.35, 0.06], [-0.15, 0.35, 0.3], color=gm, material="Metal"),
            part("AntennaR", [0.06, 0.35, 0.06], [0.15, 0.35, 0.3], color=gm, material="Metal"),
        ]
    if style == "beep":
        return [
            part("Dome", [0.8, 0.6, 0.8], [0, 0.1, 0], color=paint, material="SmoothPlastic", shape="Ball"),
            part("Base", [0.9, 0.18, 0.9], [0, -0.3, 0], color=gm, material="Metal"),
            visor("GlowCross", [0.6, 0.1, 0.1], [0, 0.35, 0.35]),
            *bolts("Beep", [[-0.3, -0.2, 0.3], [0.3, -0.2, 0.3]], r=0.07),
        ]
    if style == "orb":
        return [
            part("Sphere", [0.85, 0.85, 0.85], [0, 0, 0], color=paint, material="Glass", transparency=0.2, shape="Ball"),
            visor("GlowCore", [0.35, 0.35, 0.35], [0, 0, 0]),
            joint_cyl("Ring", [1.05, 0.1, 1.05], [0, 0, 0], color=gm),
            joint_cyl("Ring2", [1.05, 0.1, 1.05], [0, 0.2, 0], color=darken(gm, 0.1)),
            part("Antenna", [0.08, 0.4, 0.08], [0, 0.55, 0], color=gm, material="Metal"),
        ]
    return [
        part("Body", [0.7, 0.35, 0.8], [0, 0, 0], color=paint, material="Metal"),
        part("LegFL", [0.12, 0.12, 0.6], [-0.4, -0.1, 0.35], color=gm, material="Metal"),
        part("LegFR", [0.12, 0.12, 0.6], [0.4, -0.1, 0.35], color=gm, material="Metal"),
        part("LegBL", [0.12, 0.12, 0.6], [-0.4, -0.1, -0.35], color=gm, material="Metal"),
        part("LegBR", [0.12, 0.12, 0.6], [0.4, -0.1, -0.35], color=gm, material="Metal"),
        visor("GlowEye", [0.28, 0.18, 0.12], [0, 0.2, 0.45]),
        *bolts("Spider", [[0, 0.2, 0], [0.25, 0.15, -0.2]], r=0.07),
    ]


def build_chip(base: list[float], *, style: str) -> list[dict]:
    gm = GUNMETAL
    kids = [
        part("Card", [0.55, 0.1, 0.4], [0, 0, 0], color=base, material="Plastic"),
        visor("GlowDie", [0.2, 0.08, 0.2], [0, 0.1, 0]),
        part("PadL", [0.1, 0.06, 0.12], [-0.2, 0.06, 0.12], color=gm, material="Metal"),
        part("PadR", [0.1, 0.06, 0.12], [0.2, 0.06, 0.12], color=gm, material="Metal"),
    ]
    if style == "heat":
        kids += [
            part("Fin1", [0.4, 0.18, 0.08], [0, 0.18, 0.05], color=gm, material="Metal"),
            part("Fin2", [0.4, 0.18, 0.08], [0, 0.18, -0.05], color=gm, material="Metal"),
        ]
    elif style == "wire":
        kids.append(visor("GlowTrace", [0.4, 0.04, 0.06], [0, 0.08, 0.12]))
    elif style == "grease":
        kids.append(part("Blob", [0.22, 0.12, 0.22], [0.1, 0.1, 0.05], color=lighten(base, 0.15), material="SmoothPlastic"))
    elif style == "shield":
        kids.append(part("Shield", [0.32, 0.22, 0.08], [0, 0.16, 0.05], color=gm, material="Metal"))
    else:
        kids.append(part("Pad", [0.12, 0.06, 0.12], [-0.15, 0.08, 0.1], color=gm, material="Metal"))
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
