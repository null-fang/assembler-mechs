#!/usr/bin/env python3
"""Generate Rojo .model.json maps for Assembler lobby + arenas.

Invented mech-bay hub / arena dressing — neon accents and readable landmarks
inspired by modern Roblox hub energy, without copying any third-party IP.

Theme moods (Shared/Themes + tools/arena_themes.py):
  ScrapPit   → Yardbone scrap
  DryDock    → Rimevault arctic
  NightYard  → Voltframe neon
  SandQuarry → Duneplate desert

Stable script hooks (do not rename):
  Lobby: SpawnLocation, GaragePedestal, CampaignTerminal, CampaignTerminalScreen,
         StarterCrate, ShopTerminal
  Arenas: PadA, PadB, ArenaOrigin
  Arena Models: Attribute ThemeId + Tags AssemblerArenaTheme
"""

from __future__ import annotations

import json
from pathlib import Path

from arena_themes import (
    ARENAS,
    LOBBY_THEME_LANDMARKS,
    arena_model_meta,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "Workspace"


def rgb(r: int, g: int, b: int) -> list[float]:
    return [r / 255.0, g / 255.0, b / 255.0]


def part(
    name: str,
    size: list[float],
    pos: list[float],
    *,
    color: list[float],
    material: str = "SmoothPlastic",
    transparency: float | None = None,
    can_collide: bool | None = None,
    shape: str | None = None,
    orientation: list[float] | None = None,
) -> dict:
    props: dict = {
        "Anchored": True,
        "Size": size,
        "Position": pos,
        "Color": color,
        "Material": material,
        "TopSurface": "Smooth",
        "BottomSurface": "Smooth",
    }
    if transparency is not None:
        props["Transparency"] = transparency
    if can_collide is not None:
        props["CanCollide"] = can_collide
    if shape is not None:
        props["Shape"] = shape
    if orientation is not None:
        props["Orientation"] = orientation
    return {"Name": name, "ClassName": "Part", "Properties": props}


def attachment(name: str, pos: list[float]) -> dict:
    return {
        "Name": name,
        "ClassName": "Attachment",
        "Properties": {"Position": pos},
    }


def point_light(name: str, brightness: float, range_: float, color: list[float]) -> dict:
    return {
        "Name": name,
        "ClassName": "PointLight",
        "Properties": {
            "Brightness": brightness,
            "Range": range_,
            "Color": color,
            "Shadows": True,
        },
    }


def spot_light(
    name: str,
    brightness: float,
    range_: float,
    angle: float,
    color: list[float],
    face: str = "Bottom",
) -> dict:
    return {
        "Name": name,
        "ClassName": "SpotLight",
        "Properties": {
            "Brightness": brightness,
            "Range": range_,
            "Angle": angle,
            "Color": color,
            "Face": face,
            "Shadows": True,
        },
    }


def surface_gui_label(
    name: str,
    text: str,
    *,
    face: str = "Top",
    text_color: list[float] | None = None,
    stroke: float = 0.35,
) -> dict:
    return {
        "Name": name,
        "ClassName": "SurfaceGui",
        "Properties": {
            "Face": face,
            "LightInfluence": 0.15,
            "PixelsPerStud": 22,
        },
        "Children": [
            {
                "Name": "Label",
                "ClassName": "TextLabel",
                "Properties": {
                    "Size": {"UDim2": [[1.0, 0], [1.0, 0]]},
                    "BackgroundTransparency": 1.0,
                    "Text": text,
                    "TextScaled": True,
                    "Font": "GothamBold",
                    "TextColor3": text_color or [1.0, 1.0, 1.0],
                    "TextStrokeTransparency": stroke,
                },
            }
        ],
    }


def particle_emitter(
    name: str,
    *,
    rate: float,
    lifetime: list[float],
    speed: list[float],
    size_start: float,
    size_end: float,
    color: list[float],
    light_emission: float = 0.4,
    drag: float = 2.0,
    texture: str = "rbxasset://textures/particles/smoke_main.dds",
    spread: list[float] | None = None,
) -> dict:
    """Subtle ParticleEmitter — Rojo serializes NumberRange/NumberSequence as arrays."""
    return {
        "Name": name,
        "ClassName": "ParticleEmitter",
        "Properties": {
            "Texture": texture,
            "Rate": rate,
            "Lifetime": lifetime,
            "Speed": speed,
            "SpreadAngle": spread or [25.0, 25.0],
            "Drag": drag,
            "LightEmission": light_emission,
            "LightInfluence": 0.2,
            "Size": [
                {"time": 0.0, "value": size_start},
                {"time": 1.0, "value": size_end},
            ],
            "Transparency": [
                {"time": 0.0, "value": 0.35},
                {"time": 0.7, "value": 0.55},
                {"time": 1.0, "value": 1.0},
            ],
            "Color": [{"time": 0.0, "value": color}, {"time": 1.0, "value": color}],
            "Enabled": True,
            "LockedToPart": False,
        },
    }


def model(
    name: str,
    children: list[dict],
    *,
    primary: str | None = None,
    attributes: dict | None = None,
    tags: list[str] | None = None,
) -> dict:
    node: dict = {"Name": name, "ClassName": "Model", "Children": children}
    _ = primary
    if attributes:
        node["Attributes"] = attributes
    if tags:
        node["Tags"] = tags
    return node


def themed_arena_model(name: str, children: list[dict]) -> dict:
    meta = arena_model_meta(name)
    return model(name, children, attributes=meta["Attributes"], tags=meta["Tags"])


def crate(name: str, pos: list[float], size: list[float] | None = None) -> dict:
    s = size or [4, 3, 4]
    return part(name, s, [pos[0], pos[1] + s[1] / 2, pos[2]], color=rgb(120, 88, 52), material="Wood")


def barrel(name: str, pos: list[float], color: list[float] | None = None) -> dict:
    return part(
        name,
        [2.2, 3.2, 2.2],
        [pos[0], pos[1] + 1.6, pos[2]],
        color=color or rgb(70, 78, 55),
        material="Metal",
        shape="Cylinder",
        orientation=[0, 0, 90],
    )


def cable_spool(name: str, pos: list[float]) -> dict:
    return part(
        name,
        [5, 4, 5],
        [pos[0], pos[1] + 2, pos[2]],
        color=rgb(95, 78, 48),
        material="Wood",
        shape="Cylinder",
        orientation=[0, 0, 90],
    )


def neon_strip(
    name: str,
    size: list[float],
    pos: list[float],
    color: list[float],
    *,
    orientation: list[float] | None = None,
) -> dict:
    return part(
        name,
        size,
        pos,
        color=color,
        material="Neon",
        can_collide=False,
        orientation=orientation,
    )


def sign_board(
    name: str,
    text: str,
    pos: list[float],
    *,
    size: list[float] | None = None,
    board_color: list[float] | None = None,
    neon_color: list[float] | None = None,
    face: str = "Front",
) -> list[dict]:
    """Backed metal sign + optional neon underglow strip."""
    s = size or [10, 3.5, 0.5]
    board = part(
        name,
        s,
        pos,
        color=board_color or rgb(28, 32, 40),
        material="Metal",
    )
    board["Children"] = [
        surface_gui_label("T", text, face=face, text_color=neon_color or rgb(120, 220, 255)),
    ]
    glow = neon_strip(
        f"{name}_Glow",
        [s[0] * 0.92, 0.18, 0.2],
        [pos[0], pos[1] - s[1] / 2 - 0.15, pos[2] - 0.15],
        neon_color or rgb(40, 180, 220),
    )
    return [board, glow]


def railing_segment(
    name: str,
    x: float,
    z: float,
    length: float,
    along_x: bool,
    *,
    y: float = 0.0,
    height: float = 3.0,
    color: list[float] | None = None,
) -> list[dict]:
    """Low railing: posts + top rail."""
    kids: list[dict] = []
    rail_c = color or rgb(70, 74, 80)
    post_c = rgb(55, 58, 64)
    if along_x:
        kids.append(
            part(
                f"{name}_Rail",
                [length, 0.4, 0.4],
                [x, y + height, z],
                color=rail_c,
                material="Metal",
            )
        )
        for i, ox in enumerate((-length / 2 + 1, 0.0, length / 2 - 1)):
            kids.append(
                part(
                    f"{name}_Post{i}",
                    [0.35, height, 0.35],
                    [x + ox, y + height / 2, z],
                    color=post_c,
                    material="Metal",
                )
            )
    else:
        kids.append(
            part(
                f"{name}_Rail",
                [0.4, 0.4, length],
                [x, y + height, z],
                color=rail_c,
                material="Metal",
            )
        )
        for i, oz in enumerate((-length / 2 + 1, 0.0, length / 2 - 1)):
            kids.append(
                part(
                    f"{name}_Post{i}",
                    [0.35, height, 0.35],
                    [x, y + height / 2, z + oz],
                    color=post_c,
                    material="Metal",
                )
            )
    return kids


def pad_ring(name: str, pos: list[float], color: list[float], *, y_off: float = 0.15) -> dict:
    return part(
        name,
        [16.5, 0.25, 16.5],
        [pos[0], pos[1] + y_off, pos[2]],
        color=color,
        material="Neon",
        can_collide=False,
    )


def pad(name: str, pos: list[float], color: list[float], label: str) -> dict:
    """Fighter pad with Attachment child for scripts."""
    return {
        "Name": name,
        "ClassName": "Part",
        "Properties": {
            "Anchored": True,
            "Size": [14, 1.2, 14],
            "Position": [pos[0], pos[1] + 0.6, pos[2]],
            "Color": color,
            "Material": "DiamondPlate",
            "TopSurface": "Smooth",
            "BottomSurface": "Smooth",
        },
        "Children": [
            attachment("Spawn", [0, 2.5, 0]),
            surface_gui_label("PadLabel", label, face="Top"),
        ],
    }


def arena_origin(pos: list[float]) -> dict:
    return {
        "Name": "ArenaOrigin",
        "ClassName": "Part",
        "Properties": {
            "Anchored": True,
            "Size": [2, 2, 2],
            "Position": [pos[0], pos[1] + 1, pos[2]],
            "Color": rgb(255, 200, 40),
            "Material": "Neon",
            "Transparency": 0.35,
            "CanCollide": False,
            "TopSurface": "Smooth",
            "BottomSurface": "Smooth",
        },
        "Children": [attachment("Center", [0, 0, 0])],
    }


def kill_volume(name: str, size: list[float], pos: list[float]) -> dict:
    """Invisible deep kill brick — CanTouch for future scripts; no collide."""
    p = part(
        name,
        size,
        pos,
        color=rgb(20, 8, 8),
        material="SmoothPlastic",
        transparency=1.0,
        can_collide=False,
    )
    p["Properties"]["CanTouch"] = True
    p["Properties"]["CanQuery"] = True
    return p


def lamp_post(
    name: str,
    pos: list[float],
    *,
    height: float = 14.0,
    light_color: list[float] | None = None,
    brightness: float = 1.6,
    range_: float = 42.0,
) -> list[dict]:
    lc = light_color or rgb(255, 230, 190)
    pole = part(
        f"{name}_Pole",
        [1.2, height, 1.2],
        [pos[0], pos[1] + height / 2, pos[2]],
        color=rgb(42, 46, 52),
        material="Metal",
    )
    head = part(
        f"{name}_Head",
        [3.2, 1.0, 3.2],
        [pos[0], pos[1] + height + 0.4, pos[2]],
        color=rgb(30, 32, 38),
        material="Metal",
        can_collide=False,
    )
    head["Children"] = [spot_light("Spot", brightness, range_, 65, lc, face="Bottom")]
    return [pole, head]


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

STEEL = rgb(78, 84, 92)
STEEL_DARK = rgb(48, 52, 58)
FLOOR = rgb(92, 96, 102)
ACCENT = rgb(210, 140, 40)
WALL = rgb(64, 70, 78)
WARN = rgb(220, 160, 30)
NEON_CYAN = rgb(40, 200, 230)
NEON_AMBER = rgb(255, 170, 50)
NEON_MAGENTA = rgb(210, 70, 180)
NEON_LIME = rgb(120, 230, 90)
ICE = rgb(190, 220, 245)
ICE_DEEP = rgb(90, 140, 180)
SAND = rgb(198, 160, 95)
SAND_DARK = rgb(150, 110, 60)
OCHRE = rgb(220, 140, 50)


def prop_cluster(
    prefix: str,
    origin: list[float],
    spots: list[tuple[float, float]],
    *,
    color: list[float],
    material: str = "Metal",
    y: float = 0.0,
) -> list[dict]:
    """Dense scrap/crate/chunk dressing around a mood origin."""
    kids: list[dict] = []
    for i, (dx, dz) in enumerate(spots):
        sx = 3.5 + (i % 3) * 1.2
        sy = 2.2 + (i % 4) * 0.55
        sz = 3.0 + (i % 2) * 1.4
        kids.append(
            part(
                f"{prefix}Heap{i}",
                [sx, sy, sz],
                [origin[0] + dx, origin[1] + y + sy / 2, origin[2] + dz],
                color=color,
                material=material,
            )
        )
        if i % 2 == 0:
            kids.append(
                part(
                    f"{prefix}Chunk{i}",
                    [2.2, 1.4, 1.8],
                    [origin[0] + dx + 2.2, origin[1] + y + 0.7, origin[2] + dz - 1.5],
                    color=[max(0.0, c * 0.75) for c in color],
                    material="CorrodedMetal" if material != "Ice" else "Ice",
                )
            )
    return kids


def rim_lights(
    prefix: str,
    origin: list[float],
    offsets: list[tuple[float, float]],
    *,
    color: list[float],
    height: float = 14.0,
    brightness: float = 1.6,
) -> list[dict]:
    kids: list[dict] = []
    for i, (dx, dz) in enumerate(offsets):
        kids.extend(
            lamp_post(
                f"{prefix}{i}",
                [origin[0] + dx, origin[1], origin[2] + dz],
                height=height,
                light_color=color,
                brightness=brightness,
                range_=46,
            )
        )
    return kids


# ---------------------------------------------------------------------------
# Lobby — Mech Bay Hub at world origin
# ---------------------------------------------------------------------------


def build_lobby() -> dict:
    kids: list[dict] = []

    # --- Shell / seal voids -------------------------------------------------
    kids.append(part("Floor", [160, 2, 120], [0, -1, 0], color=FLOOR, material="Concrete"))
    kids.append(part("CenterBay", [40, 0.4, 36], [0, 0.2, 0], color=rgb(70, 74, 82), material="Metal"))
    # Inner diamond-plate walk lanes
    kids.append(
        part("WalkLaneX", [120, 0.12, 10], [0, 0.08, -28], color=rgb(100, 104, 112), material="DiamondPlate")
    )
    kids.append(
        part("WalkLaneZ", [10, 0.12, 70], [35, 0.08, -5], color=rgb(100, 104, 112), material="DiamondPlate")
    )

    kids.append(part("WallBack", [160, 28, 2], [0, 13, 59], color=WALL, material="Concrete"))
    kids.append(part("WallLeft", [2, 28, 120], [-79, 13, 0], color=WALL, material="Concrete"))
    kids.append(part("WallRight", [2, 28, 120], [79, 13, 0], color=WALL, material="Concrete"))
    kids.append(part("WallFrontLeft", [52, 28, 2], [-54, 13, -59], color=WALL, material="Concrete"))
    kids.append(part("WallFrontRight", [52, 28, 2], [54, 13, -59], color=WALL, material="Concrete"))
    kids.append(part("WallFrontHeader", [56, 8, 2], [0, 23, -59], color=STEEL_DARK, material="Metal"))
    kids.append(part("FrontLeftPillar", [6, 28, 4], [-28, 13, -58], color=STEEL, material="Metal"))
    kids.append(part("FrontRightPillar", [6, 28, 4], [28, 13, -58], color=STEEL, material="Metal"))
    kids.append(part("FrontLintels", [56, 3, 4], [0, 19, -58], color=STEEL, material="Metal"))
    # Corner seals (no sky leaks at wall joints)
    for name, pos in (
        ("CornerSealBL", [-78, 13, 58]),
        ("CornerSealBR", [78, 13, 58]),
        ("CornerSealFL", [-78, 13, -58]),
        ("CornerSealFR", [78, 13, -58]),
    ):
        kids.append(part(name, [4, 28, 4], list(pos), color=STEEL_DARK, material="Metal"))

    kids.append(
        part("ExteriorApron", [160, 2, 48], [0, -1, -84], color=rgb(70, 74, 80), material="Asphalt")
    )
    kids.append(part("ExteriorLip", [160, 1, 2], [0, -0.4, -60], color=STEEL_DARK, material="Metal"))
    kids.append(part("ExteriorWingL", [2, 18, 40], [-79, 8, -80], color=WALL, material="Concrete"))
    kids.append(part("ExteriorWingR", [2, 18, 40], [79, 8, -80], color=WALL, material="Concrete"))
    # Apron side walls + rear fascia so doorframe is fully boxed
    kids.append(part("ApronEndWall", [160, 10, 2], [0, 4, -107], color=STEEL_DARK, material="Concrete"))
    kids.append(part("ApronRoofEdge", [160, 1.5, 6], [0, 27, -61], color=STEEL, material="Metal"))

    for i, x in enumerate((-50, -25, 0, 25, 50)):
        kids.append(part(f"RoofBeam{i}", [3, 2, 118], [x, 27, 0], color=STEEL_DARK, material="Metal"))
    kids.append(part("RoofSlab", [160, 1, 120], [0, 28.5, 0], color=rgb(55, 58, 65), material="Metal"))
    # Cross truss + neon accent rails on ceiling (hub energy)
    for i, z in enumerate((-30, 0, 30)):
        kids.append(part(f"CrossTruss{i}", [156, 1.2, 1.5], [0, 26.5, z], color=STEEL, material="Metal"))
        kids.append(neon_strip(f"CeilingNeon{i}", [140, 0.25, 0.35], [0, 25.8, z], NEON_CYAN))

    for i, z in enumerate((-40, -15, 15, 40)):
        kids.append(part(f"ColL{i}", [4, 26, 4], [-70, 12, z], color=STEEL, material="Metal"))
        kids.append(part(f"ColR{i}", [4, 26, 4], [70, 12, z], color=STEEL, material="Metal"))
        # Column wraps with amber tip lights
        tip = part(
            f"ColTipL{i}",
            [4.4, 0.5, 4.4],
            [-70, 24.5, z],
            color=NEON_AMBER,
            material="Neon",
            can_collide=False,
        )
        tip["Children"] = [point_light("Tip", 0.6, 18, NEON_AMBER)]
        kids.append(tip)
        tip_r = part(
            f"ColTipR{i}",
            [4.4, 0.5, 4.4],
            [70, 24.5, z],
            color=NEON_CYAN,
            material="Neon",
            can_collide=False,
        )
        tip_r["Children"] = [point_light("Tip", 0.55, 18, NEON_CYAN)]
        kids.append(tip_r)

    # Mezzanine balcony (spectator / ops overlook)
    kids.append(
        part("MezzFloor", [50, 1.2, 14], [-45, 12, 48], color=STEEL, material="DiamondPlate")
    )
    kids.extend(railing_segment("MezzRail", -45, 41.5, 46, True, y=12.0, height=2.8))
    kids.append(part("MezzStairs", [8, 1, 18], [-18, 6, 48], color=STEEL_DARK, material="Metal"))
    kids.extend(
        sign_board(
            "SignOpsDeck",
            "OPS DECK",
            [-45, 15.5, 42],
            size=[12, 2.5, 0.4],
            neon_color=NEON_AMBER,
        )
    )

    # Railings around center bay
    kids.extend(railing_segment("RailN", 0, -20, 36, True))
    kids.extend(railing_segment("RailS", 0, 20, 36, True))
    kids.extend(railing_segment("RailW", -22, 0, 36, False))
    kids.extend(railing_segment("RailE", 22, 0, 36, False))
    # Gate gaps marked with neon stubs at bay entrances
    for name, pos in (
        ("BayGateN", [0, 0.3, -20]),
        ("BayGateS", [0, 0.3, 20]),
    ):
        kids.append(neon_strip(name, [8, 0.2, 0.35], list(pos), NEON_AMBER))

    # --- Dense props --------------------------------------------------------
    crate_spots = [
        (-60, -35),
        (-55, -40),
        (-62, -42),
        (-58, -30),
        (58, -38),
        (62, -42),
        (55, 40),
        (-58, 42),
        (50, 35),
        (-48, 38),
        (65, 10),
        (-65, 12),
        (48, -10),
        (-52, -8),
    ]
    for i, (x, z) in enumerate(crate_spots):
        kids.append(crate(f"Crate{i}", [x, 0, z], [3 + (i % 2), 2.5 + (i % 3) * 0.4, 3]))

    for i, (x, z) in enumerate([(-45, -45), (45, -48), (-40, 48), (42, 45), (68, -20), (-68, 22)]):
        kids.append(barrel(f"Barrel{i}", [x, 0, z], rgb(80, 90, 50) if i % 2 == 0 else rgb(90, 55, 40)))

    for i, (x, z) in enumerate([(-62, 30), (60, 28), (-30, 45)]):
        kids.append(cable_spool(f"Spool{i}", [x, 0, z]))

    # Tool benches + racks
    kids.append(part("WorkbenchL", [12, 3, 4], [-40, 1.5, 30], color=rgb(95, 70, 45), material="Wood"))
    kids.append(part("WorkbenchR", [12, 3, 4], [40, 1.5, 30], color=rgb(95, 70, 45), material="Wood"))
    kids.append(part("ToolRackL", [1, 8, 10], [-46, 5, 30], color=STEEL_DARK, material="Metal"))
    kids.append(part("ToolRackR", [1, 8, 10], [46, 5, 30], color=STEEL_DARK, material="Metal"))
    kids.append(neon_strip("BenchGlowL", [10, 0.15, 0.2], [-40, 3.2, 28], NEON_AMBER))
    kids.append(neon_strip("BenchGlowR", [10, 0.15, 0.2], [40, 3.2, 28], NEON_CYAN))

    # Wall tech panels
    for i, z in enumerate((-25, 0, 25)):
        panel = part(
            f"WallPanelL{i}",
            [0.6, 10, 12],
            [-78.2, 10, z],
            color=rgb(35, 40, 48),
            material="Metal",
        )
        panel["Children"] = [point_light("Panel", 0.4, 14, NEON_CYAN)]
        kids.append(panel)
        kids.append(neon_strip(f"WallNeonL{i}", [0.2, 8, 0.25], [-77.7, 10, z - 5], NEON_CYAN))
        kids.append(
            part(
                f"WallPanelR{i}",
                [0.6, 10, 12],
                [78.2, 10, z],
                color=rgb(35, 40, 48),
                material="Metal",
            )
        )
        kids.append(neon_strip(f"WallNeonR{i}", [0.2, 8, 0.25], [77.7, 10, z + 5], NEON_AMBER))

    # Warning stripes near entrance
    for i, x in enumerate(range(-48, 49, 8)):
        kids.append(
            part(
                f"Stripe{i}",
                [4, 0.15, 8],
                [x, 0.1, -50],
                color=WARN if (i % 2 == 0) else STEEL_DARK,
                material="SmoothPlastic",
            )
        )

    # --- Floor path: Spawn → Campaign terminal (readable landmark) ----------
    # Dashed chevrons along diamond-plate lane toward terminal at (35, *, -20)
    path_points = [
        (0, -20),
        (8, -20),
        (16, -20),
        (24, -20),
        (32, -20),
        (35, -16),
        (35, -12),
        (35, -8),
    ]
    for i, (x, z) in enumerate(path_points):
        kids.append(
            neon_strip(
                f"PathMark{i}",
                [2.2, 0.12, 1.1],
                [x, 0.18, z],
                NEON_CYAN if i % 2 == 0 else rgb(80, 200, 180),
            )
        )
    # Arrow heads near terminal
    kids.append(neon_strip("PathArrow", [3.5, 0.14, 2.0], [35, 0.2, -24], NEON_CYAN))
    kids.extend(
        sign_board(
            "SignFloorCampaign",
            "→ CAMPAIGN",
            [22, 0.4, -20],
            size=[8, 0.15, 3],
            board_color=rgb(20, 28, 36),
            neon_color=NEON_CYAN,
            face="Top",
        )
    )

    # Hazard ring around garage bay
    for i, ang_off in enumerate((-10, -5, 5, 10)):
        kids.append(
            part(
                f"HazardRing{i}",
                [3.5, 0.12, 1.2],
                [ang_off * 1.4, 0.15, 8 + (i - 1.5) * 3],
                color=WARN if i % 2 == 0 else STEEL_DARK,
                material="SmoothPlastic",
            )
        )

    # --- Signage (BAY 01, CAMPAIGN, hub identity) ----------------------------
    kids.extend(
        sign_board(
            "SignBay01",
            "BAY 01",
            [-30, 18, -57.2],
            size=[14, 4, 0.5],
            neon_color=NEON_AMBER,
        )
    )
    kids.extend(
        sign_board(
            "SignBay02",
            "BAY 02",
            [30, 18, -57.2],
            size=[14, 4, 0.5],
            neon_color=NEON_CYAN,
        )
    )
    kids.extend(
        sign_board(
            "SignAssembler",
            "ASSEMBLER",
            [0, 21.5, -57.2],
            size=[22, 3.2, 0.5],
            neon_color=rgb(255, 220, 140),
        )
    )
    kids.extend(
        sign_board(
            "SignCampaignWall",
            "CAMPAIGN",
            [35, 10, -22.5],
            size=[10, 2.2, 0.4],
            neon_color=NEON_CYAN,
        )
    )
    kids.extend(
        sign_board(
            "SignGarage",
            "GARAGE DISPLAY",
            [0, 8, 18],
            size=[16, 2.4, 0.4],
            neon_color=NEON_AMBER,
        )
    )
    kids.extend(
        sign_board(
            "SignExit",
            "APRON / YARD",
            [0, 14, -57.2],
            size=[12, 2, 0.4],
            neon_color=rgb(180, 200, 210),
        )
    )

    # Hanging lamps
    for i, (x, z) in enumerate([(-30, -20), (30, -20), (-30, 20), (30, 20), (0, 0), (35, -20), (-50, 0)]):
        lamp = part(
            f"LampHousing{i}",
            [6, 1, 6],
            [x, 24, z],
            color=rgb(40, 42, 48),
            material="Metal",
            can_collide=False,
        )
        bright = 2.8 if i == 4 else 1.9
        lamp["Children"] = [
            spot_light("Spot", bright, 62, 70, rgb(255, 235, 200), face="Bottom")
        ]
        kids.append(lamp)

    fill = part(
        "BayFillLight",
        [2, 2, 2],
        [0, 18, 0],
        color=rgb(255, 240, 200),
        material="Neon",
        transparency=0.6,
        can_collide=False,
    )
    fill["Children"] = [point_light("Fill", 1.35, 85, rgb(255, 230, 190))]
    kids.append(fill)

    # Spawn
    kids.append(
        {
            "Name": "SpawnLocation",
            "ClassName": "SpawnLocation",
            "Properties": {
                "Anchored": True,
                "Size": [12, 1, 12],
                "Position": [0, 0.5, -28],
                "Orientation": [0, 180, 0],
                "Color": rgb(80, 140, 200),
                "Material": "Neon",
                "Duration": 0,
                "Neutral": True,
                "TopSurface": "Smooth",
                "BottomSurface": "Smooth",
            },
            "Children": [surface_gui_label("SpawnLabel", "SPAWN", face="Top")],
        }
    )
    kids.append(pad_ring("SpawnRing", [0, 0, -28], NEON_CYAN, y_off=0.12))

    # Garage pedestal + bay lighting
    pedestal = part(
        "GaragePedestal",
        [16, 2, 16],
        [0, 1, 8],
        color=rgb(55, 60, 70),
        material="DiamondPlate",
    )
    pedestal["Children"] = [
        attachment("MechRoot", [0, 4, 0]),
        surface_gui_label("GarageLabel", "GARAGE", face="Top"),
        point_light("PedestalUnder", 1.1, 22, NEON_AMBER),
    ]
    kids.append(pedestal)
    kids.append(
        part(
            "GaragePedestalRing",
            [18, 0.35, 18],
            [0, 0.2, 8],
            color=ACCENT,
            material="Neon",
            can_collide=False,
        )
    )
    kids.append(
        part(
            "GaragePedestalRingOuter",
            [20.5, 0.2, 20.5],
            [0, 0.12, 8],
            color=NEON_CYAN,
            material="Neon",
            can_collide=False,
            transparency=0.25,
        )
    )
    # Overhead garage bay spots aimed at pedestal
    for i, (x, z) in enumerate([(-8, 8), (8, 8), (0, 0), (0, 16)]):
        bay_lamp = part(
            f"GarageBayLamp{i}",
            [3, 0.8, 3],
            [x, 22, z],
            color=rgb(35, 38, 44),
            material="Metal",
            can_collide=False,
        )
        bay_lamp["Children"] = [
            spot_light("BaySpot", 2.6, 38, 48, rgb(255, 245, 220), face="Bottom")
        ]
        kids.append(bay_lamp)
    # Pedestal corner beacons
    for i, (x, z) in enumerate([(-9, -1), (9, -1), (-9, 17), (9, 17)]):
        beacon = part(
            f"PedestalBeacon{i}",
            [0.8, 3.5, 0.8],
            [x, 2.5, z],
            color=STEEL_DARK,
            material="Metal",
        )
        tip = part(
            f"PedestalBeaconTip{i}",
            [1.0, 0.4, 1.0],
            [x, 4.4, z],
            color=NEON_AMBER if i % 2 == 0 else NEON_CYAN,
            material="Neon",
            can_collide=False,
        )
        tip["Children"] = [
            point_light("Glow", 0.9, 12, NEON_AMBER if i % 2 == 0 else NEON_CYAN)
        ]
        kids.append(beacon)
        kids.append(tip)

    # Campaign terminal
    terminal = part(
        "CampaignTerminal",
        [8, 6, 4],
        [35, 3, -20],
        color=rgb(45, 50, 58),
        material="Metal",
    )
    terminal["Children"] = [
        attachment("Interact", [0, 0, -2.5]),
        point_light("TerminalGlow", 1.7, 28, NEON_CYAN),
    ]
    kids.append(terminal)
    screen = part(
        "CampaignTerminalScreen",
        [6, 4, 0.4],
        [35, 5, -22.2],
        color=NEON_CYAN,
        material="Neon",
        can_collide=False,
    )
    screen["Children"] = [surface_gui_label("CampaignLabel", "CAMPAIGN", face="Front")]
    kids.append(screen)
    # Terminal kiosk frame + floor pad
    kids.append(
        part("TerminalBase", [10, 0.5, 8], [35, 0.25, -20], color=STEEL_DARK, material="Metal")
    )
    kids.append(neon_strip("TerminalHalo", [11, 0.15, 9], [35, 0.4, -20], NEON_CYAN))
    kids.append(
        part("TerminalCanopy", [10, 0.6, 5], [35, 7.5, -20], color=STEEL, material="Metal")
    )

    # Arena directory signs (4 theme sets)
    kids.append(
        part("SignScrapPit", [10, 4, 0.6], [-55, 6, -55], color=rgb(160, 90, 50), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "SCRAP PIT →", face="Front")]
    kids.append(
        part("SignDryDock", [10, 4, 0.6], [-20, 6, -55], color=rgb(90, 140, 180), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "DRY DOCK →", face="Front")]
    kids.append(
        part("SignNightYard", [10, 4, 0.6], [20, 6, -55], color=rgb(50, 55, 90), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "NIGHT YARD →", face="Front")]
    kids.append(
        part("SignSandQuarry", [10, 4, 0.6], [55, 6, -55], color=rgb(180, 130, 55), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "SAND QUARRY →", face="Front")]

    # --- Theme shop / crate plaza (apron landmarks) -------------------------
    kids.extend(
        sign_board(
            "SignThemePlaza",
            "THEME BAYS",
            [0, 8, -72],
            size=[16, 2.4, 0.45],
            neon_color=NEON_AMBER,
        )
    )
    for lm in LOBBY_THEME_LANDMARKS:
        key = lm["key"]
        x, _, z = lm["pos"]
        # Shop booth landmark
        booth = part(
            f"ShopLandmark{key}",
            [8, 6, 5],
            [x, 3, z],
            color=lm["board"],
            material="Metal",
        )
        booth["Children"] = [
            attachment("ShopRoot", [0, 0, -2.8]),
            point_light("BoothGlow", 1.2, 22, lm["neon"]),
            surface_gui_label("ShopLabel", lm["label"], face="Front", text_color=lm["neon"]),
        ]
        kids.append(booth)
        kids.append(
            neon_strip(
                f"ShopHalo{key}",
                [9, 0.18, 6],
                [x, 0.25, z],
                lm["neon"],
            )
        )
        kids.append(
            part(
                f"ShopCanopy{key}",
                [9, 0.5, 6],
                [x, 6.4, z],
                color=STEEL_DARK,
                material="Metal",
            )
        )
        # Themed display crate beside booth
        crate_part = part(
            f"ThemeCrate{key}",
            [3.4, 2.8, 3.4],
            [x + 6.5, 1.4, z + 1.5],
            color=lm["crate"],
            material="Wood" if key != "Neon" else "Metal",
        )
        crate_part["Children"] = [
            surface_gui_label("CrateLabel", lm["crate_label"], face="Top", text_color=lm["neon"]),
            point_light("CrateGlow", 0.7, 12, lm["neon"]),
        ]
        kids.append(crate_part)
        kids.append(
            neon_strip(
                f"CrateRing{key}",
                [4.2, 0.12, 4.2],
                [x + 6.5, 0.2, z + 1.5],
                lm["neon"],
            )
        )
        # Floor path dashes from bay toward each booth
        kids.append(
            neon_strip(
                f"ThemePath{key}",
                [1.6, 0.12, 8],
                [x, 0.18, z + 12],
                lm["neon"],
            )
        )

    # Stable shop + starter crate hooks (LobbyPrompts / WorldBootstrap)
    shop = part(
        "ShopTerminal",
        [7, 5.5, 4],
        [-18, 2.75, 28],
        color=rgb(48, 52, 62),
        material="Metal",
    )
    shop["Children"] = [
        attachment("Interact", [0, 0, -2.4]),
        point_light("ShopGlow", 1.4, 24, NEON_AMBER),
        surface_gui_label("ShopLabel", "SHOP", face="Front", text_color=NEON_AMBER),
    ]
    kids.append(shop)
    kids.append(
        part("ShopTerminalBase", [9, 0.4, 7], [-18, 0.2, 28], color=STEEL_DARK, material="Metal")
    )
    kids.append(neon_strip("ShopTerminalHalo", [10, 0.14, 8], [-18, 0.35, 28], NEON_AMBER))
    kids.extend(
        sign_board(
            "SignShopWall",
            "PART SHOP",
            [-18, 9, 30.5],
            size=[10, 2.2, 0.4],
            neon_color=NEON_AMBER,
        )
    )

    starter = part(
        "StarterCrate",
        [3.4, 2.8, 3.4],
        [-10, 1.5, 2],
        color=rgb(130, 92, 48),
        material="Wood",
    )
    starter["Children"] = [
        attachment("Interact", [0, 0, -2]),
        point_light("CrateGlow", 1.0, 16, NEON_AMBER),
        surface_gui_label("CrateLabel", "STARTER CRATE", face="Top", text_color=NEON_AMBER),
    ]
    kids.append(starter)
    kids.append(neon_strip("StarterCrateRing", [4.4, 0.14, 4.4], [-10, 0.2, 2], NEON_AMBER))
    kids.append(
        part(
            "StarterCrateBeacon",
            [0.7, 4, 0.7],
            [-12.5, 2.2, 0],
            color=STEEL_DARK,
            material="Metal",
        )
    )
    kids.append(
        part(
            "StarterCrateBeaconTip",
            [0.9, 0.35, 0.9],
            [-12.5, 4.4, 0],
            color=NEON_AMBER,
            material="Neon",
            can_collide=False,
        )
    )

    # Subtle steam / spark FX
    steam_a = part(
        "SteamVentA",
        [2, 1, 2],
        [-70, 1, -40],
        color=STEEL,
        material="Metal",
        can_collide=False,
        transparency=0.4,
    )
    steam_a["Children"] = [
        particle_emitter(
            "Steam",
            rate=6,
            lifetime=[1.2, 2.4],
            speed=[1.5, 3.5],
            size_start=1.2,
            size_end=3.5,
            color=rgb(180, 190, 200),
            light_emission=0.05,
            drag=3.0,
        )
    ]
    kids.append(steam_a)
    steam_b = part(
        "SteamVentB",
        [2, 1, 2],
        [68, 1, 35],
        color=STEEL,
        material="Metal",
        can_collide=False,
        transparency=0.4,
    )
    steam_b["Children"] = [
        particle_emitter(
            "Steam",
            rate=5,
            lifetime=[1.0, 2.2],
            speed=[1.2, 3.0],
            size_start=1.0,
            size_end=3.0,
            color=rgb(170, 180, 190),
            light_emission=0.05,
            drag=3.2,
        )
    ]
    kids.append(steam_b)
    sparks = part(
        "WelderSparks",
        [1.5, 1.5, 1.5],
        [-40, 4, 30],
        color=NEON_AMBER,
        material="Neon",
        transparency=0.7,
        can_collide=False,
    )
    sparks["Children"] = [
        particle_emitter(
            "Sparks",
            rate=10,
            lifetime=[0.25, 0.7],
            speed=[4, 10],
            size_start=0.15,
            size_end=0.05,
            color=rgb(255, 200, 80),
            light_emission=0.8,
            drag=1.0,
            texture="rbxasset://textures/particles/sparkles_main.dds",
            spread=[40.0, 40.0],
        )
    ]
    kids.append(sparks)

    return model("Lobby", kids)


# ---------------------------------------------------------------------------
# Arenas — densified theme sets
# ---------------------------------------------------------------------------


def build_scrap_pit(origin: list[float]) -> dict:
    """Yardbone scrap bowl — warm rust, slag, amber lamps, center kill pit."""
    ox, oy, oz = origin
    kids: list[dict] = []
    floor_c = ARENAS["ScrapPit"]["floor"]
    wall_c = rgb(95, 58, 40)
    ember = ARENAS["ScrapPit"]["accent"]
    olive = rgb(86, 110, 55)

    kids.append(part("Floor", [96, 2, 96], [ox, oy - 1, oz], color=floor_c, material="Ground"))
    kids.append(
        part("PitRing", [52, 1, 52], [ox, oy + 0.1, oz], color=rgb(85, 55, 40), material="Slate")
    )
    kids.append(
        part("PitMouth", [22, 1.5, 22], [ox, oy - 2.2, oz], color=rgb(40, 22, 16), material="Slate")
    )
    kids.append(
        part("PitDepth", [18, 18, 18], [ox, oy - 12, oz], color=rgb(25, 12, 10), material="Rock")
    )
    kids.append(kill_volume("KillPit", [16, 6, 16], [ox, oy - 20, oz]))
    kids.append(neon_strip("PitRimNeon", [24, 0.2, 24], [ox, oy + 0.25, oz], ember))
    kids.append(neon_strip("PitInnerNeon", [16, 0.15, 16], [ox, oy + 0.18, oz], olive))

    for i, (dx, dz, sx, sz) in enumerate(
        [(0, -46, 88, 5), (0, 46, 88, 5), (-46, 0, 5, 80), (46, 0, 5, 80)]
    ):
        kids.append(
            part(
                f"Barrier{i}",
                [sx, 7, sz],
                [ox + dx, oy + 3.5, oz + dz],
                color=wall_c,
                material="CorrodedMetal",
            )
        )
        # Barrier rust ribbing
        if sx > sz:
            for j, ox2 in enumerate((-30, -10, 10, 30)):
                kids.append(
                    part(
                        f"BarrierRib{i}_{j}",
                        [2.5, 6.5, 0.6],
                        [ox + ox2, oy + 3.5, oz + dz],
                        color=rgb(110, 70, 40),
                        material="CorrodedMetal",
                    )
                )
        else:
            for j, oz2 in enumerate((-28, -8, 8, 28)):
                kids.append(
                    part(
                        f"BarrierRib{i}_{j}",
                        [0.6, 6.5, 2.5],
                        [ox + dx, oy + 3.5, oz + oz2],
                        color=rgb(110, 70, 40),
                        material="CorrodedMetal",
                    )
                )

    kids.extend(
        railing_segment(
            "SpecRail", ox, oz - 43, 60, True, y=oy + 6.5, height=2.6, color=rgb(120, 80, 45)
        )
    )
    kids.append(
        part("SpecWalk", [50, 1, 6], [ox, oy + 6.8, oz - 43], color=rgb(90, 65, 45), material="DiamondPlate")
    )
    kids.extend(
        sign_board(
            "SignScrap",
            "SCRAP PIT",
            [ox, oy + 12, oz - 45],
            size=[18, 3.2, 0.5],
            board_color=rgb(60, 40, 28),
            neon_color=ember,
        )
    )
    kids.extend(
        sign_board(
            "SignYardbone",
            "YARDBONE",
            [ox + 40, oy + 10, oz],
            size=[12, 2.4, 0.4],
            neon_color=olive,
        )
    )

    scrap_spots = [
        (-32, -32),
        (30, -30),
        (-30, 32),
        (32, 30),
        (-38, 0),
        (38, 5),
        (0, 38),
        (-22, -18),
        (20, -16),
        (-18, 20),
        (18, 22),
        (-40, -18),
        (40, 18),
        (10, -38),
        (-12, 36),
    ]
    kids.extend(prop_cluster("Scrap", [ox, oy, oz], scrap_spots, color=rgb(120, 78, 48), material="CorrodedMetal"))
    for i, (dx, dz) in enumerate(scrap_spots[:8]):
        kids.append(crate(f"ScrapPile{i}", [ox + dx, oy, oz + dz], [7 + i % 3, 4 + (i % 2), 6]))

    for i, (dx, dz) in enumerate(
        [(-20, -38), (22, 36), (-36, 18), (34, -20), (-10, 40), (12, -40), (-42, 12), (42, -8)]
    ):
        kids.append(barrel(f"SlagDrum{i}", [ox + dx, oy, oz + dz], rgb(110, 70, 40) if i % 2 == 0 else olive))

    for i, (dx, dz) in enumerate([(-28, 10), (26, -12), (-8, -34)]):
        kids.append(cable_spool(f"ScrapSpool{i}", [ox + dx, oy, oz + dz]))

    # Dual cranes
    for ci, (tx, tz, arm_dir) in enumerate(((40, -40, -1), (-40, 40, 1))):
        kids.append(
            part(f"CraneTower{ci}", [4, 30, 4], [ox + tx, oy + 15, oz + tz], color=STEEL, material="Metal")
        )
        kids.append(
            part(
                f"CraneArm{ci}",
                [36, 2, 3],
                [ox + tx + arm_dir * 16, oy + 28, oz + tz],
                color=rgb(200, 140, 40),
                material="Metal",
            )
        )
        kids.append(
            neon_strip(
                f"CraneNeon{ci}",
                [32, 0.25, 0.35],
                [ox + tx + arm_dir * 16, oy + 27, oz + tz],
                ember,
            )
        )

    kids.extend(
        rim_lights(
            "RustLamp",
            [ox, oy, oz],
            [(-28, -28), (28, -28), (-28, 28), (28, 28), (0, -40), (0, 40), (-40, 0), (40, 0)],
            color=ARENAS["ScrapPit"]["lamp"],
            height=16,
            brightness=1.85,
        )
    )

    kids.append(pad("PadA", [ox - 24, oy, oz], rgb(180, 90, 50), "P1"))
    kids.append(pad("PadB", [ox + 24, oy, oz], rgb(80, 120, 160), "P2"))
    kids.append(pad_ring("PadARing", [ox - 24, oy, oz], ember, y_off=1.35))
    kids.append(pad_ring("PadBRing", [ox + 24, oy, oz], rgb(80, 160, 200), y_off=1.35))
    for i, x in enumerate(range(-18, 19, 6)):
        kids.append(
            neon_strip(
                f"LaneMark{i}",
                [2, 0.12, 1],
                [ox + x, oy + 0.2, oz],
                rgb(200, 120, 50) if abs(x) > 6 else STEEL_DARK,
            )
        )
    kids.append(arena_origin([ox, oy, oz]))

    lamp = part(
        "ArenaLamp",
        [5, 1.2, 5],
        [ox, oy + 24, oz],
        color=rgb(40, 40, 40),
        material="Metal",
        can_collide=False,
    )
    lamp["Children"] = [point_light("Light", 2.4, 78, rgb(255, 190, 120))]
    kids.append(lamp)

    for fi, (fx, fz) in enumerate(((0, -8), (8, 4), (-6, 6))):
        ember_fx = part(
            f"EmberFx{fi}",
            [2, 2, 2],
            [ox + fx, oy + 2, oz + fz],
            color=ember,
            material="Neon",
            transparency=0.8,
            can_collide=False,
        )
        ember_fx["Children"] = [
            particle_emitter(
                "Embers",
                rate=6,
                lifetime=[0.8, 1.8],
                speed=[1, 3],
                size_start=0.2,
                size_end=0.05,
                color=rgb(255, 150, 50),
                light_emission=0.7,
                texture="rbxasset://textures/particles/sparkles_main.dds",
                spread=[50.0, 50.0],
            )
        ]
        kids.append(ember_fx)

    kids.append(
        part(
            "WarmHaze",
            [90, 40, 90],
            [ox, oy + 18, oz],
            color=ARENAS["ScrapPit"]["haze"],
            material="ForceField",
            transparency=0.92,
            can_collide=False,
        )
    )
    # Local lighting cue bricks (read by ArenaMood via ThemeId; visual wash)
    kids.append(
        part(
            "MoodWash",
            [88, 2, 88],
            [ox, oy + 36, oz],
            color=rgb(255, 160, 80),
            material="Neon",
            transparency=0.94,
            can_collide=False,
        )
    )

    return themed_arena_model("ScrapPit", kids)


def build_dry_dock(origin: list[float]) -> dict:
    """Rimevault arctic pier — frozen channel, ice bollards, cold lamps."""
    ox, oy, oz = origin
    kids: list[dict] = []
    cool = ARENAS["DryDock"]["accent"]
    ice_c = ICE
    frost = rgb(220, 235, 250)

    kids.append(
        part("Floor", [108, 2, 76], [ox, oy - 1, oz], color=rgb(150, 165, 180), material="Concrete")
    )
    kids.append(
        part(
            "FrostSheet",
            [100, 0.2, 68],
            [ox, oy + 0.15, oz],
            color=frost,
            material="Ice",
            transparency=0.35,
            can_collide=False,
        )
    )
    # Frozen channel + kill
    kids.append(
        part(
            "Channel",
            [18, 8, 72],
            [ox, oy - 4, oz],
            color=rgb(40, 90, 130),
            material="Ice",
            transparency=0.2,
        )
    )
    kids.append(
        part(
            "ChannelSurface",
            [17, 0.5, 70],
            [ox, oy - 0.05, oz],
            color=ice_c,
            material="Ice",
            transparency=0.25,
            can_collide=False,
        )
    )
    kids.append(kill_volume("KillChannel", [14, 4, 66], [ox, oy - 10, oz]))
    kids.append(neon_strip("ChannelEdgeW", [0.3, 0.2, 68], [ox - 9.2, oy + 0.3, oz], cool))
    kids.append(neon_strip("ChannelEdgeE", [0.3, 0.2, 68], [ox + 9.2, oy + 0.3, oz], cool))
    kids.append(neon_strip("ChannelCenter", [1.2, 0.12, 60], [ox, oy + 0.35, oz], frost))

    kids.append(
        part("PierWest", [38, 2.5, 64], [ox - 30, oy + 0.5, oz], color=rgb(140, 155, 170), material="Concrete")
    )
    kids.append(
        part("PierEast", [38, 2.5, 64], [ox + 30, oy + 0.5, oz], color=rgb(140, 155, 170), material="Concrete")
    )

    for i, x in enumerate((-42, -22, 22, 42)):
        for j, z in enumerate((-30, -10, 10, 30)):
            kids.append(
                part(
                    f"Bollard{i}_{j}",
                    [2, 4.5, 2],
                    [ox + x, oy + 3.8, oz + z],
                    color=rgb(80, 100, 120),
                    material="Metal",
                )
            )
            kids.append(
                neon_strip(
                    f"BollardCap{i}_{j}",
                    [2.2, 0.25, 2.2],
                    [ox + x, oy + 6.2, oz + z],
                    cool if (i + j) % 2 == 0 else frost,
                )
            )
            # Ice collar
            kids.append(
                part(
                    f"IceCollar{i}_{j}",
                    [2.8, 0.6, 2.8],
                    [ox + x, oy + 2.0, oz + z],
                    color=ice_c,
                    material="Ice",
                    transparency=0.2,
                    can_collide=False,
                )
            )

    kids.append(
        part("ShedLeft", [9, 18, 44], [ox - 50, oy + 9, oz], color=rgb(70, 110, 140), material="Metal")
    )
    kids.append(
        part("ShedRight", [9, 18, 44], [ox + 50, oy + 9, oz], color=rgb(70, 110, 140), material="Metal")
    )
    for si, side in enumerate((-50, 50)):
        kids.append(
            neon_strip(
                f"ShedNeon{si}",
                [0.25, 14, 36],
                [ox + side + (0.6 if side > 0 else -0.6), oy + 10, oz],
                cool,
            )
        )

    kids.extend(
        sign_board(
            "SignDryBay",
            "DRY DOCK",
            [ox, oy + 16, oz - 36],
            size=[18, 3.5, 0.5],
            neon_color=cool,
        )
    )
    kids.extend(
        sign_board(
            "SignRimevault",
            "RIMEVAULT",
            [ox, oy + 12, oz + 36],
            size=[14, 2.6, 0.45],
            neon_color=frost,
        )
    )
    kids.extend(
        sign_board("SignPierA", "PIER A", [ox - 30, oy + 8, oz - 34], size=[10, 2.2, 0.4], neon_color=cool)
    )
    kids.extend(
        sign_board("SignPierB", "PIER B", [ox + 30, oy + 8, oz - 34], size=[10, 2.2, 0.4], neon_color=frost)
    )

    kids.append(part("Catwalk", [22, 0.6, 7], [ox, oy + 9, oz], color=STEEL, material="DiamondPlate"))
    kids.extend(railing_segment("CatRailN", ox, oz - 3.6, 20, True, y=oy + 9, height=2.4, color=ICE_DEEP))
    kids.extend(railing_segment("CatRailS", ox, oz + 3.6, 20, True, y=oy + 9, height=2.4, color=ICE_DEEP))
    kids.append(
        part("BridgeW", [12, 0.5, 5], [ox - 16, oy + 2.2, oz], color=STEEL, material="DiamondPlate")
    )
    kids.append(
        part("BridgeE", [12, 0.5, 5], [ox + 16, oy + 2.2, oz], color=STEEL, material="DiamondPlate")
    )

    ice_spots = [(-38, -18), (-36, 16), (36, -20), (38, 14), (-34, -4), (34, 6), (-40, 24), (40, -26)]
    kids.extend(
        prop_cluster(
            "IceCargo",
            [ox, oy + 1.5, oz],
            ice_spots,
            color=rgb(160, 185, 210),
            material="Ice",
            y=0.0,
        )
    )
    for i, (dx, dz) in enumerate(ice_spots[:5]):
        kids.append(crate(f"DockCrate{i}", [ox + dx, oy + 1.5, oz + dz], [5, 3.5, 4]))
    for i, (dx, dz) in enumerate([(-40, 0), (40, 5), (-28, 28), (28, -28)]):
        kids.append(cable_spool(f"DockSpool{i}", [ox + dx, oy + 1.5, oz + dz]))

    kids.append(
        part("GantryLegs", [3, 22, 3], [ox - 8, oy + 12, oz - 28], color=STEEL, material="Metal")
    )
    kids.append(
        part("GantryBeam", [50, 2, 2.5], [ox, oy + 22, oz - 28], color=rgb(90, 150, 180), material="Metal")
    )
    kids.append(neon_strip("GantryNeon", [46, 0.2, 0.3], [ox, oy + 21.2, oz - 28], cool))
    kids.append(
        part("GantryLegsB", [3, 22, 3], [ox + 8, oy + 12, oz + 28], color=STEEL, material="Metal")
    )
    kids.append(
        part("GantryBeamB", [50, 2, 2.5], [ox, oy + 22, oz + 28], color=rgb(90, 150, 180), material="Metal")
    )
    kids.append(neon_strip("GantryNeonB", [46, 0.2, 0.3], [ox, oy + 21.2, oz + 28], frost))

    kids.append(pad("PadA", [ox - 30, oy + 1.5, oz], rgb(70, 140, 170), "P1"))
    kids.append(pad("PadB", [ox + 30, oy + 1.5, oz], rgb(180, 200, 220), "P2"))
    kids.append(pad_ring("PadARing", [ox - 30, oy + 1.5, oz], cool, y_off=1.4))
    kids.append(pad_ring("PadBRing", [ox + 30, oy + 1.5, oz], frost, y_off=1.4))
    kids.append(arena_origin([ox, oy + 1.5, oz]))

    for i, (x, z) in enumerate(
        [(-30, -22), (30, -22), (-30, 22), (30, 22), (0, -34), (0, 34), (-44, 0), (44, 0)]
    ):
        lamp = part(
            f"DockLamp{i}",
            [2, 10, 2],
            [ox + x, oy + 7, oz + z],
            color=STEEL,
            material="Metal",
            can_collide=False,
        )
        lamp["Children"] = [point_light("Light", 1.65, 46, ARENAS["DryDock"]["lamp"])]
        kids.append(lamp)

    mist = part(
        "ChannelMist",
        [10, 2, 40],
        [ox, oy + 1.5, oz],
        color=cool,
        material="ForceField",
        transparency=0.85,
        can_collide=False,
    )
    mist["Children"] = [
        particle_emitter(
            "Mist",
            rate=10,
            lifetime=[1.5, 3.0],
            speed=[0.5, 1.8],
            size_start=1.5,
            size_end=4.0,
            color=rgb(180, 220, 245),
            light_emission=0.12,
            drag=4.0,
        )
    ]
    kids.append(mist)
    kids.append(
        part(
            "CoolHaze",
            [100, 36, 70],
            [ox, oy + 16, oz],
            color=ARENAS["DryDock"]["haze"],
            material="ForceField",
            transparency=0.93,
            can_collide=False,
        )
    )
    kids.append(
        part(
            "MoodWash",
            [100, 2, 70],
            [ox, oy + 34, oz],
            color=rgb(160, 210, 255),
            material="Neon",
            transparency=0.95,
            can_collide=False,
        )
    )

    return themed_arena_model("DryDock", kids)


def build_night_yard(origin: list[float]) -> dict:
    """Voltframe neon cargo yard — indigo asphalt, magenta/cyan lanes."""
    ox, oy, oz = origin
    kids: list[dict] = []
    asphalt = ARENAS["NightYard"]["floor"]
    violet = rgb(90, 70, 180)

    kids.append(part("Floor", [108, 2, 108], [ox, oy - 1, oz], color=asphalt, material="Asphalt"))
    kids.append(
        part(
            "CenterMark",
            [30, 0.18, 30],
            [ox, oy + 0.12, oz],
            color=rgb(45, 50, 75),
            material="SmoothPlastic",
        )
    )
    kids.append(neon_strip("LaneNS", [2.5, 0.14, 80], [ox, oy + 0.2, oz], NEON_MAGENTA))
    kids.append(neon_strip("LaneEW", [80, 0.14, 2.5], [ox, oy + 0.2, oz], NEON_CYAN))
    kids.append(neon_strip("LaneRing", [36, 0.14, 36], [ox, oy + 0.22, oz], violet))
    kids.append(neon_strip("LaneRingOuter", [52, 0.12, 52], [ox, oy + 0.2, oz], NEON_CYAN))
    # Diagonal accent lanes
    for i, (dx, dz) in enumerate(((-20, -20), (20, 20), (-20, 20), (20, -20))):
        kids.append(
            neon_strip(
                f"DiagLane{i}",
                [18, 0.12, 0.8],
                [ox + dx, oy + 0.18, oz + dz],
                NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
                orientation=[0, 45 if i < 2 else -45, 0],
            )
        )

    for i, (dx, dz, sx, sz) in enumerate(
        [(0, -50, 100, 1.2), (0, 50, 100, 1.2), (-50, 0, 1.2, 100), (50, 0, 1.2, 100)]
    ):
        kids.append(
            part(
                f"Fence{i}",
                [sx, 11, sz],
                [ox + dx, oy + 5.5, oz + dz],
                color=rgb(45, 48, 60),
                material="Metal",
                transparency=0.32,
            )
        )
        if sx > sz:
            kids.append(
                neon_strip(
                    f"FenceNeon{i}",
                    [sx * 0.96, 0.2, 0.25],
                    [ox + dx, oy + 11.2, oz + dz],
                    NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
                )
            )
        else:
            kids.append(
                neon_strip(
                    f"FenceNeon{i}",
                    [0.25, 0.2, sz * 0.96],
                    [ox + dx, oy + 11.2, oz + dz],
                    NEON_CYAN if i % 2 == 0 else NEON_MAGENTA,
                )
            )

    for i, (dx, dz) in enumerate([(-58, -58), (58, -58), (-58, 58), (58, 58)]):
        kids.append(
            part(
                f"OuterVoid{i}",
                [16, 2, 16],
                [ox + dx, oy - 8, oz + dz],
                color=rgb(10, 10, 16),
                material="SmoothPlastic",
            )
        )
        kids.append(kill_volume(f"KillCorner{i}", [14, 5, 14], [ox + dx, oy - 14, oz + dz]))

    containers = [
        (-36, -26, rgb(35, 100, 80)),
        (-34, 22, rgb(100, 45, 50)),
        (34, -24, rgb(40, 55, 110)),
        (32, 26, rgb(90, 50, 100)),
        (-20, -40, rgb(50, 70, 55)),
        (18, 40, rgb(70, 40, 55)),
        (-42, 8, rgb(30, 40, 80)),
        (42, -8, rgb(80, 30, 70)),
        (0, -44, rgb(45, 35, 90)),
        (0, 44, rgb(35, 80, 90)),
    ]
    for i, (dx, dz, col) in enumerate(containers):
        kids.append(
            part(f"Container{i}", [16 if i < 6 else 12, 8, 7], [ox + dx, oy + 4, oz + dz], color=col, material="Metal")
        )
        kids.append(
            neon_strip(
                f"ContainerEdge{i}",
                [16.2 if i < 6 else 12.2, 0.2, 0.25],
                [ox + dx, oy + 8.2, oz + dz - 3.6],
                NEON_CYAN if i % 2 == 0 else NEON_MAGENTA,
            )
        )
        kids.append(
            neon_strip(
                f"ContainerSide{i}",
                [0.2, 6, 0.25],
                [ox + dx + (8 if i % 2 == 0 else -8), oy + 4, oz + dz],
                NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
            )
        )

    kids.extend(
        railing_segment("NightSpec", ox - 44, oz, 70, False, y=oy, height=3.2, color=rgb(80, 70, 120))
    )
    kids.append(
        part("SpecPlatform", [6, 1, 50], [ox - 44, oy + 0.5, oz], color=rgb(40, 42, 55), material="DiamondPlate")
    )
    kids.extend(
        railing_segment("NightSpecE", ox + 44, oz, 70, False, y=oy, height=3.2, color=rgb(70, 100, 120))
    )
    kids.append(
        part("SpecPlatformE", [6, 1, 50], [ox + 44, oy + 0.5, oz], color=rgb(40, 42, 55), material="DiamondPlate")
    )

    for i, (dx, dz) in enumerate([(-42, -42), (42, -42), (-42, 42), (42, 42)]):
        pole = part(
            f"FloodPole{i}",
            [1.5, 24, 1.5],
            [ox + dx, oy + 12, oz + dz],
            color=STEEL_DARK,
            material="Metal",
        )
        head = part(
            f"FloodHead{i}",
            [4.5, 1.5, 3.5],
            [ox + dx, oy + 24, oz + dz],
            color=rgb(28, 28, 35),
            material="Metal",
            can_collide=False,
        )
        head["Children"] = [spot_light("Flood", 3.2, 85, 52, rgb(200, 210, 255), face="Bottom")]
        kids.append(pole)
        kids.append(head)
        kids.append(
            neon_strip(
                f"FloodNeon{i}",
                [1.8, 0.3, 1.8],
                [ox + dx, oy + 22.5, oz + dz],
                NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
            )
        )

    kids.extend(
        rim_lights(
            "YardLamp",
            [ox, oy, oz],
            [(0, -40), (0, 40), (-40, 0), (40, 0), (-24, -24), (24, 24)],
            color=ARENAS["NightYard"]["lamp"],
            height=12,
            brightness=1.55,
        )
    )

    kids.extend(
        sign_board(
            "SignNight",
            "NIGHT YARD",
            [ox, oy + 14, oz - 48],
            size=[20, 3.5, 0.5],
            board_color=rgb(20, 18, 35),
            neon_color=NEON_MAGENTA,
        )
    )
    kids.extend(
        sign_board(
            "SignVoltframe",
            "VOLTFRAME",
            [ox, oy + 10, oz + 48],
            size=[14, 2.6, 0.45],
            board_color=rgb(18, 22, 40),
            neon_color=NEON_CYAN,
        )
    )
    kids.extend(
        sign_board("SignGate", "GATE 3", [ox + 48, oy + 8, oz], size=[8, 2.5, 0.4], neon_color=NEON_CYAN)
    )

    # Dense neon props
    for i, (dx, dz) in enumerate([(-30, 10), (30, -12), (-12, 30), (14, -32), (-28, -14), (26, 18)]):
        kids.append(
            part(
                f"NeonCrate{i}",
                [4, 3, 4],
                [ox + dx, oy + 1.5, oz + dz],
                color=rgb(40, 35, 70) if i % 2 == 0 else rgb(30, 60, 80),
                material="Metal",
            )
        )
        kids.append(
            neon_strip(
                f"NeonCrateGlow{i}",
                [4.2, 0.15, 4.2],
                [ox + dx, oy + 0.2, oz + dz],
                NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
            )
        )

    kids.append(pad("PadA", [ox, oy, oz - 28], rgb(90, 100, 180), "P1"))
    kids.append(pad("PadB", [ox, oy, oz + 28], rgb(180, 90, 100), "P2"))
    kids.append(pad_ring("PadARing", [ox, oy, oz - 28], NEON_CYAN, y_off=1.35))
    kids.append(pad_ring("PadBRing", [ox, oy, oz + 28], NEON_MAGENTA, y_off=1.35))
    kids.append(arena_origin([ox, oy, oz]))

    fog = part(
        "NightFog",
        [40, 2, 40],
        [ox, oy + 1.2, oz],
        color=violet,
        material="ForceField",
        transparency=0.88,
        can_collide=False,
    )
    fog["Children"] = [
        particle_emitter(
            "Fog",
            rate=6,
            lifetime=[2.0, 4.0],
            speed=[0.3, 1.2],
            size_start=2.0,
            size_end=5.0,
            color=rgb(100, 80, 160),
            light_emission=0.15,
            drag=5.0,
        )
    ]
    kids.append(fog)
    kids.append(
        part(
            "NightHaze",
            [100, 45, 100],
            [ox, oy + 20, oz],
            color=ARENAS["NightYard"]["haze"],
            material="ForceField",
            transparency=0.94,
            can_collide=False,
        )
    )
    kids.append(
        part(
            "MoodWash",
            [100, 2, 100],
            [ox, oy + 38, oz],
            color=rgb(120, 60, 200),
            material="Neon",
            transparency=0.95,
            can_collide=False,
        )
    )

    return themed_arena_model("NightYard", kids)


def build_sand_quarry(origin: list[float]) -> dict:
    """Duneplate desert quarry — sand bowl, ochre cliffs, heat haze."""
    ox, oy, oz = origin
    kids: list[dict] = []
    sand = ARENAS["SandQuarry"]["floor"]
    accent = ARENAS["SandQuarry"]["accent"]
    cliff = SAND_DARK

    kids.append(part("Floor", [100, 2, 100], [ox, oy - 1, oz], color=sand, material="Sand"))
    kids.append(
        part(
            "QuarryBowl",
            [56, 1, 56],
            [ox, oy + 0.05, oz],
            color=rgb(180, 140, 80),
            material="Sandstone",
        )
    )
    kids.append(
        part("QuarryMouth", [20, 1.2, 20], [ox, oy - 1.8, oz], color=rgb(120, 85, 45), material="Rock")
    )
    kids.append(
        part("QuarryDepth", [16, 14, 16], [ox, oy - 10, oz], color=rgb(90, 60, 35), material="Rock")
    )
    kids.append(kill_volume("KillQuarry", [14, 5, 14], [ox, oy - 18, oz]))
    kids.append(neon_strip("QuarryRim", [22, 0.18, 22], [ox, oy + 0.22, oz], accent))

    # Mesa cliff walls
    for i, (dx, dz, sx, sz) in enumerate(
        [(0, -48, 90, 8), (0, 48, 90, 8), (-48, 0, 8, 84), (48, 0, 8, 84)]
    ):
        kids.append(
            part(
                f"Cliff{i}",
                [sx, 14, sz],
                [ox + dx, oy + 6, oz + dz],
                color=cliff,
                material="Sandstone",
            )
        )
        kids.append(
            part(
                f"CliffCap{i}",
                [sx * 0.9, 2, sz * 0.9 if sz > sx else sz],
                [ox + dx, oy + 14, oz + dz],
                color=rgb(170, 130, 70),
                material="Sandstone",
            )
        )

    # Mesa pillars
    for i, (dx, dz) in enumerate([(-30, -30), (30, -28), (-28, 30), (32, 28), (0, -36), (0, 36)]):
        kids.append(
            part(
                f"Mesa{i}",
                [8 + i % 3, 10 + (i % 2) * 3, 8],
                [ox + dx, oy + 5, oz + dz],
                color=rgb(160, 120, 65) if i % 2 == 0 else cliff,
                material="Sandstone",
            )
        )
        kids.append(
            neon_strip(
                f"MesaBand{i}",
                [8.4 + i % 3, 0.25, 0.3],
                [ox + dx, oy + 8, oz + dz - 4],
                accent,
            )
        )

    dune_spots = [
        (-34, -18),
        (34, 16),
        (-32, 20),
        (30, -22),
        (-20, 34),
        (18, -34),
        (-40, 4),
        (40, -6),
        (-12, -30),
        (14, 32),
        (-24, 8),
        (22, -10),
        (-16, 16),
        (16, -18),
        (-38, -28),
        (38, 30),
    ]
    kids.extend(prop_cluster("Dune", [ox, oy, oz], dune_spots, color=rgb(170, 130, 70), material="Sandstone"))
    for i, (dx, dz) in enumerate(dune_spots[:8]):
        kids.append(crate(f"SandCrate{i}", [ox + dx, oy, oz + dz], [5, 3.2, 4]))
    for i, (dx, dz) in enumerate([(-36, -8), (36, 10), (-8, 38), (10, -38), (-22, -36), (24, 36)]):
        kids.append(barrel(f"OilDrum{i}", [ox + dx, oy, oz + dz], rgb(140, 90, 40)))
    for i, (dx, dz) in enumerate([(-30, 0), (30, 4), (0, 30)]):
        kids.append(cable_spool(f"SandSpool{i}", [ox + dx, oy, oz + dz]))
    # Shade tents / canopy props
    for i, (dx, dz) in enumerate([(-22, -14), (22, 14)]):
        kids.append(
            part(
                f"ShadePost{i}A",
                [0.6, 8, 0.6],
                [ox + dx - 4, oy + 4, oz + dz],
                color=STEEL,
                material="Metal",
            )
        )
        kids.append(
            part(
                f"ShadePost{i}B",
                [0.6, 8, 0.6],
                [ox + dx + 4, oy + 4, oz + dz],
                color=STEEL,
                material="Metal",
            )
        )
        kids.append(
            part(
                f"ShadeCanopy{i}",
                [10, 0.4, 8],
                [ox + dx, oy + 8.2, oz + dz],
                color=rgb(180, 120, 50),
                material="Fabric",
            )
        )
        kids.append(
            neon_strip(
                f"ShadeNeon{i}",
                [9, 0.15, 0.25],
                [ox + dx, oy + 8.0, oz + dz - 3.8],
                accent,
            )
        )

    kids.extend(
        railing_segment(
            "QuarrySpec", ox, oz - 42, 55, True, y=oy + 7, height=2.8, color=rgb(140, 110, 60)
        )
    )
    kids.append(
        part(
            "SpecWalk",
            [48, 1, 5],
            [ox, oy + 7.2, oz - 42],
            color=rgb(150, 120, 70),
            material="DiamondPlate",
        )
    )

    # Excavator boom landmark
    kids.append(
        part("ExcavTower", [5, 26, 5], [ox + 38, oy + 13, oz - 36], color=STEEL, material="Metal")
    )
    kids.append(
        part(
            "ExcavArm",
            [34, 2.2, 2.8],
            [ox + 20, oy + 24, oz - 36],
            color=OCHRE,
            material="Metal",
        )
    )
    kids.append(neon_strip("ExcavNeon", [30, 0.22, 0.3], [ox + 20, oy + 23.2, oz - 36], accent))

    kids.extend(
        rim_lights(
            "HeatLamp",
            [ox, oy, oz],
            [(-28, -28), (28, -28), (-28, 28), (28, 28), (0, -40), (0, 40), (-40, 0), (40, 0)],
            color=ARENAS["SandQuarry"]["lamp"],
            height=15,
            brightness=1.9,
        )
    )

    kids.extend(
        sign_board(
            "SignSand",
            "SAND QUARRY",
            [ox, oy + 14, oz - 46],
            size=[20, 3.4, 0.5],
            board_color=rgb(80, 55, 30),
            neon_color=accent,
        )
    )
    kids.extend(
        sign_board(
            "SignDuneplate",
            "DUNEPLATE",
            [ox, oy + 10, oz + 46],
            size=[14, 2.6, 0.45],
            board_color=rgb(90, 65, 35),
            neon_color=rgb(255, 200, 120),
        )
    )

    kids.append(pad("PadA", [ox - 24, oy, oz], rgb(200, 140, 70), "P1"))
    kids.append(pad("PadB", [ox + 24, oy, oz], rgb(160, 100, 50), "P2"))
    kids.append(pad_ring("PadARing", [ox - 24, oy, oz], accent, y_off=1.35))
    kids.append(pad_ring("PadBRing", [ox + 24, oy, oz], rgb(255, 200, 120), y_off=1.35))
    for i, x in enumerate(range(-18, 19, 6)):
        kids.append(
            neon_strip(
                f"LaneMark{i}",
                [2, 0.12, 1],
                [ox + x, oy + 0.2, oz],
                accent if abs(x) > 6 else SAND_DARK,
            )
        )
    kids.append(arena_origin([ox, oy, oz]))

    heat = part(
        "HeatFx",
        [3, 3, 3],
        [ox, oy + 3, oz],
        color=accent,
        material="Neon",
        transparency=0.85,
        can_collide=False,
    )
    heat["Children"] = [
        particle_emitter(
            "HeatShimmer",
            rate=8,
            lifetime=[1.2, 2.5],
            speed=[0.4, 1.5],
            size_start=1.5,
            size_end=4.0,
            color=rgb(255, 200, 120),
            light_emission=0.2,
            drag=3.5,
        )
    ]
    kids.append(heat)
    kids.append(
        part(
            "HeatHaze",
            [94, 42, 94],
            [ox, oy + 18, oz],
            color=ARENAS["SandQuarry"]["haze"],
            material="ForceField",
            transparency=0.92,
            can_collide=False,
        )
    )
    kids.append(
        part(
            "MoodWash",
            [94, 2, 94],
            [ox, oy + 36, oz],
            color=rgb(255, 190, 100),
            material="Neon",
            transparency=0.94,
            can_collide=False,
        )
    )

    return themed_arena_model("SandQuarry", kids)


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {
        "ClassName": data.get("ClassName", "Model"),
        "Children": data.get("Children", []),
    }
    if data.get("Attributes"):
        payload["Attributes"] = data["Attributes"]
    if data.get("Tags"):
        payload["Tags"] = data["Tags"]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(payload['Children'])} children)")


def main() -> None:
    if OUT.exists():
        for p in OUT.rglob("*.model.json"):
            p.unlink()

    arenas = OUT / "Arenas"
    write_model(OUT / "Lobby.model.json", build_lobby())
    for name, info in ARENAS.items():
        builder = {
            "ScrapPit": build_scrap_pit,
            "DryDock": build_dry_dock,
            "NightYard": build_night_yard,
            "SandQuarry": build_sand_quarry,
        }[name]
        write_model(arenas / f"{name}.model.json", builder(list(info["origin"])))
    print("done")


if __name__ == "__main__":
    main()
