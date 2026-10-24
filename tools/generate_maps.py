#!/usr/bin/env python3
"""Generate Rojo .model.json maps for Assembler lobby + arenas."""

from __future__ import annotations

import json
from pathlib import Path

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
            "Size": size,
            "CFrame": cframe,
            "Color": color,
            "Material": material,
            "TopSurface": "Smooth",
            "BottomSurface": "Smooth",
        },
    }


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


def surface_gui_label(name: str, text: str, *, face: str = "Top") -> dict:
    return {
        "Name": name,
        "ClassName": "SurfaceGui",
        "Properties": {
            "Face": face,
            "LightInfluence": 0.2,
            "PixelsPerStud": 20,
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
                    "Font": "SourceSansBold",
                    "TextColor3": [1.0, 1.0, 1.0],
                    "TextStrokeTransparency": 0.4,
                },
            }
        ],
    }


def model(name: str, children: list[dict], *, primary: str | None = None) -> dict:
    node: dict = {"Name": name, "ClassName": "Model", "Children": children}
    # PrimaryPart is a Ref — not settable in model.json; scripts can Resolve later.
    _ = primary
    return node


def crate(name: str, pos: list[float], size: list[float] | None = None) -> dict:
    s = size or [4, 3, 4]
    return part(name, s, [pos[0], pos[1] + s[1] / 2, pos[2]], color=rgb(120, 88, 52), material="Wood")


def railing_segment(name: str, x: float, z: float, length: float, along_x: bool) -> list[dict]:
    """Low railing: posts + top rail."""
    kids: list[dict] = []
    height = 3.0
    if along_x:
        kids.append(
            part(
                f"{name}_Rail",
                [length, 0.4, 0.4],
                [x, height, z],
                color=rgb(70, 74, 80),
                material="Metal",
            )
        )
        for i, ox in enumerate((-length / 2 + 1, 0.0, length / 2 - 1)):
            kids.append(
                part(
                    f"{name}_Post{i}",
                    [0.35, height, 0.35],
                    [x + ox, height / 2, z],
                    color=rgb(55, 58, 64),
                    material="Metal",
                )
            )
    else:
        kids.append(
            part(
                f"{name}_Rail",
                [0.4, 0.4, length],
                [x, height, z],
                color=rgb(70, 74, 80),
                material="Metal",
            )
        )
        for i, oz in enumerate((-length / 2 + 1, 0.0, length / 2 - 1)):
            kids.append(
                part(
                    f"{name}_Post{i}",
                    [0.35, height, 0.35],
                    [x, height / 2, z + oz],
                    color=rgb(55, 58, 64),
                    material="Metal",
                )
            )
    return kids


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


# ---------------------------------------------------------------------------
# Lobby — Mech Bay Hub at world origin
# ---------------------------------------------------------------------------

STEEL = rgb(78, 84, 92)
STEEL_DARK = rgb(48, 52, 58)
FLOOR = rgb(92, 96, 102)
ACCENT = rgb(210, 140, 40)
WALL = rgb(64, 70, 78)
WARN = rgb(220, 160, 30)


def build_lobby() -> dict:
    kids: list[dict] = []

    # Main hangar floor
    kids.append(part("Floor", [160, 2, 120], [0, -1, 0], color=FLOOR, material="Concrete"))
    # Slightly raised center strip
    kids.append(part("CenterBay", [40, 0.4, 36], [0, 0.2, 0], color=rgb(70, 74, 82), material="Metal"))

    # Hangar shell — open front (negative Z), closed back/sides
    kids.append(part("WallBack", [160, 28, 2], [0, 13, 59], color=WALL, material="Concrete"))
    kids.append(part("WallLeft", [2, 28, 120], [-79, 13, 0], color=WALL, material="Concrete"))
    kids.append(part("WallRight", [2, 28, 120], [79, 13, 0], color=WALL, material="Concrete"))
    # Partial front framing (open bay doors)
    kids.append(part("FrontLeftPillar", [6, 28, 4], [-55, 13, -58], color=STEEL, material="Metal"))
    kids.append(part("FrontRightPillar", [6, 28, 4], [55, 13, -58], color=STEEL, material="Metal"))
    kids.append(part("FrontLintels", [116, 4, 4], [0, 26, -58], color=STEEL_DARK, material="Metal"))

    # Roof beams (open hangar feel)
    for i, x in enumerate((-50, -25, 0, 25, 50)):
        kids.append(
            part(f"RoofBeam{i}", [3, 2, 118], [x, 27, 0], color=STEEL_DARK, material="Metal")
        )
    kids.append(part("RoofSlab", [160, 1, 120], [0, 28.5, 0], color=rgb(55, 58, 65), material="Metal"))

    # Columns along sides
    for i, z in enumerate((-40, -15, 15, 40)):
        kids.append(part(f"ColL{i}", [4, 26, 4], [-70, 12, z], color=STEEL, material="Metal"))
        kids.append(part(f"ColR{i}", [4, 26, 4], [70, 12, z], color=STEEL, material="Metal"))

    # Railings around center bay
    kids.extend(railing_segment("RailN", 0, -20, 36, True))
    kids.extend(railing_segment("RailS", 0, 20, 36, True))
    kids.extend(railing_segment("RailW", -22, 0, 36, False))
    kids.extend(railing_segment("RailE", 22, 0, 36, False))

    # Crates / props
    for i, (x, z) in enumerate(
        [(-60, -35), (-55, -40), (-62, -42), (58, -38), (62, -42), (55, 40), (-58, 42)]
    ):
        kids.append(crate(f"Crate{i}", [x, 0, z], [3 + (i % 2), 2.5 + (i % 3) * 0.4, 3]))

    # Tool benches
    kids.append(part("WorkbenchL", [12, 3, 4], [-40, 1.5, 30], color=rgb(95, 70, 45), material="Wood"))
    kids.append(part("WorkbenchR", [12, 3, 4], [40, 1.5, 30], color=rgb(95, 70, 45), material="Wood"))

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

    # Lighting fixtures (hanging)
    for i, (x, z) in enumerate([(-30, -20), (30, -20), (-30, 20), (30, 20), (0, 0)]):
        lamp = part(
            f"LampHousing{i}",
            [6, 1, 6],
            [x, 24, z],
            color=rgb(40, 42, 48),
            material="Metal",
            can_collide=False,
        )
        lamp["Children"] = [
            spot_light("Spot", 2.5 if i == 4 else 1.8, 60, 70, rgb(255, 235, 200), face="Bottom")
        ]
        kids.append(lamp)

    # Ambient fill light in bay
    fill = part(
        "BayFillLight",
        [2, 2, 2],
        [0, 18, 0],
        color=rgb(255, 240, 200),
        material="Neon",
        transparency=0.6,
        can_collide=False,
    )
    fill["Children"] = [point_light("Fill", 1.2, 80, rgb(255, 230, 190))]
    kids.append(fill)

    # Spawn
    kids.append(
        {
            "Name": "SpawnLocation",
            "ClassName": "SpawnLocation",
            "Properties": {
                "Anchored": True,
                "Size": [12, 1, 12],
                "Position": [0, 0.5, -30],
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

    # Garage pedestal — view assembled mech
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

    # Campaign terminal (screen as sibling so world Position is unambiguous)
    terminal = part(
        "CampaignTerminal",
        [8, 6, 4],
        [35, 3, -20],
        color=rgb(45, 50, 58),
        material="Metal",
    )
    terminal["Children"] = [
        attachment("Interact", [0, 0, -2.5]),
        point_light("TerminalGlow", 1.5, 24, rgb(40, 180, 220)),
    ]
    kids.append(terminal)
    screen = part(
        "CampaignTerminalScreen",
        [6, 4, 0.4],
        [35, 5, -22.2],
        color=rgb(40, 180, 220),
        material="Neon",
        can_collide=False,
    )
    screen["Children"] = [surface_gui_label("CampaignLabel", "CAMPAIGN", face="Front")]
    kids.append(screen)

    # Arena directory signs (props pointing at far arenas)
    kids.append(
        part("SignScrapPit", [10, 4, 0.6], [-50, 6, -55], color=rgb(160, 90, 50), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "SCRAP PIT →", face="Front")]
    kids.append(
        part("SignDryDock", [10, 4, 0.6], [0, 6, -55], color=rgb(70, 110, 140), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "DRY DOCK →", face="Front")]
    kids.append(
        part("SignNightYard", [10, 4, 0.6], [50, 6, -55], color=rgb(50, 55, 90), material="Metal")
    )
    kids[-1]["Children"] = [surface_gui_label("T", "NIGHT YARD →", face="Front")]

    return model("Lobby", kids)


# ---------------------------------------------------------------------------
# Arenas
# ---------------------------------------------------------------------------


def build_scrap_pit(origin: list[float]) -> dict:
    """Circular scrapyard bowl — rust tones, debris piles, open pit feel."""
    ox, oy, oz = origin
    kids: list[dict] = []
    floor_c = rgb(110, 75, 55)
    wall_c = rgb(90, 60, 45)

    kids.append(part("Floor", [90, 2, 90], [ox, oy - 1, oz], color=floor_c, material="Ground"))
    # Inner pit depression ring
    kids.append(
        part("PitRing", [50, 1, 50], [ox, oy + 0.1, oz], color=rgb(85, 55, 40), material="Slate")
    )

    # Low perimeter walls (broken scrap barriers)
    for i, (dx, dz, sx, sz) in enumerate(
        [
            (0, -44, 80, 4),
            (0, 44, 80, 4),
            (-44, 0, 4, 72),
            (44, 0, 4, 72),
        ]
    ):
        kids.append(
            part(f"Barrier{i}", [sx, 6, sz], [ox + dx, oy + 3, oz + dz], color=wall_c, material="CorrodedMetal")
        )

    # Corner scrap piles
    for i, (dx, dz) in enumerate([(-30, -30), (28, -28), (-28, 30), (30, 28)]):
        kids.append(crate(f"ScrapPile{i}", [ox + dx, oy, oz + dz], [8, 5, 7]))
        kids.append(
            part(
                f"ScrapChunk{i}",
                [5, 3, 4],
                [ox + dx + 4, oy + 1.5, oz + dz - 3],
                color=rgb(100, 70, 50),
                material="CorrodedMetal",
            )
        )

    # Crane boom silhouette
    kids.append(
        part("CraneTower", [4, 28, 4], [ox + 38, oy + 14, oz - 38], color=STEEL, material="Metal")
    )
    kids.append(
        part("CraneArm", [36, 2, 3], [ox + 20, oy + 26, oz - 38], color=rgb(200, 140, 40), material="Metal")
    )

    kids.append(pad("PadA", [ox - 22, oy, oz], rgb(180, 90, 50), "P1"))
    kids.append(pad("PadB", [ox + 22, oy, oz], rgb(80, 120, 160), "P2"))
    kids.append(arena_origin([ox, oy, oz]))

    lamp = part(
        "ArenaLamp",
        [4, 1, 4],
        [ox, oy + 22, oz],
        color=rgb(40, 40, 40),
        material="Metal",
        can_collide=False,
    )
    lamp["Children"] = [point_light("Light", 2.0, 70, rgb(255, 200, 140))]
    kids.append(lamp)

    return model("ScrapPit", kids)


def build_dry_dock(origin: list[float]) -> dict:
    """Rectangular shipyard dock — concrete piers, water channel between pads."""
    ox, oy, oz = origin
    kids: list[dict] = []

    kids.append(
        part("Floor", [100, 2, 70], [ox, oy - 1, oz], color=rgb(130, 132, 138), material="Concrete")
    )
    # Water channel down the middle
    kids.append(
        part(
            "Channel",
            [18, 1.5, 70],
            [ox, oy - 0.4, oz],
            color=rgb(40, 90, 120),
            material="Glass",
            transparency=0.25,
        )
    )
    # Dock piers
    kids.append(
        part("PierWest", [36, 2.5, 60], [ox - 28, oy + 0.5, oz], color=rgb(110, 112, 118), material="Concrete")
    )
    kids.append(
        part("PierEast", [36, 2.5, 60], [ox + 28, oy + 0.5, oz], color=rgb(110, 112, 118), material="Concrete")
    )

    # Mooring posts
    for i, x in enumerate((-40, -20, 20, 40)):
        for j, z in enumerate((-28, 28)):
            kids.append(
                part(
                    f"Bollard{i}_{j}",
                    [2, 4, 2],
                    [ox + x, oy + 3.5, oz + z],
                    color=rgb(60, 65, 70),
                    material="Metal",
                )
            )

    # Side warehouses
    kids.append(
        part("ShedLeft", [8, 16, 40], [ox - 48, oy + 8, oz], color=rgb(70, 90, 105), material="Metal")
    )
    kids.append(
        part("ShedRight", [8, 16, 40], [ox + 48, oy + 8, oz], color=rgb(70, 90, 105), material="Metal")
    )

    # Catwalk over channel + raised rail
    kids.append(
        part("Catwalk", [20, 0.6, 6], [ox, oy + 8, oz], color=STEEL, material="DiamondPlate")
    )
    kids.append(
        part(
            "CatRail",
            [18, 0.4, 0.4],
            [ox, oy + 10, oz - 3.2],
            color=rgb(70, 74, 80),
            material="Metal",
        )
    )
    for i, ox_off in enumerate((-7.0, 0.0, 7.0)):
        kids.append(
            part(
                f"CatPost{i}",
                [0.35, 2.2, 0.35],
                [ox + ox_off, oy + 9.1, oz - 3.2],
                color=rgb(55, 58, 64),
                material="Metal",
            )
        )

    kids.append(pad("PadA", [ox - 28, oy + 1.5, oz], rgb(70, 140, 170), "P1"))
    kids.append(pad("PadB", [ox + 28, oy + 1.5, oz], rgb(170, 100, 60), "P2"))
    kids.append(arena_origin([ox, oy + 1.5, oz]))

    for i, (x, z) in enumerate([(-28, -20), (28, -20), (-28, 20), (28, 20)]):
        lamp = part(
            f"DockLamp{i}",
            [2, 8, 2],
            [ox + x, oy + 6, oz + z],
            color=STEEL,
            material="Metal",
            can_collide=False,
        )
        lamp["Children"] = [point_light("Light", 1.4, 40, rgb(200, 220, 255))]
        kids.append(lamp)

    return model("DryDock", kids)


def build_night_yard(origin: list[float]) -> dict:
    """Night outdoor yard — dark asphalt, floodlights, fence, cargo containers."""
    ox, oy, oz = origin
    kids: list[dict] = []

    kids.append(
        part("Floor", [100, 2, 100], [ox, oy - 1, oz], color=rgb(35, 38, 45), material="Asphalt")
    )
    # Center painted mark
    kids.append(
        part(
            "CenterMark",
            [28, 0.2, 28],
            [ox, oy + 0.1, oz],
            color=rgb(55, 60, 80),
            material="SmoothPlastic",
        )
    )

    # Chain-link style fence (solid low-poly stand-in)
    for i, (dx, dz, sx, sz) in enumerate(
        [(0, -48, 96, 1), (0, 48, 96, 1), (-48, 0, 1, 96), (48, 0, 1, 96)]
    ):
        kids.append(
            part(
                f"Fence{i}",
                [sx, 10, sz],
                [ox + dx, oy + 5, oz + dz],
                color=rgb(50, 55, 65),
                material="Metal",
                transparency=0.35,
            )
        )

    # Cargo containers as cover
    containers = [
        (-35, -25, 0),
        (-35, 20, 90),
        (32, -22, 0),
        (30, 25, 45),
    ]
    for i, (dx, dz, _rot) in enumerate(containers):
        kids.append(
            part(
                f"Container{i}",
                [20, 8, 8],
                [ox + dx, oy + 4, oz + dz],
                color=rgb(40, 90, 70) if i % 2 == 0 else rgb(90, 50, 45),
                material="Metal",
            )
        )

    # Floodlight poles
    for i, (dx, dz) in enumerate([(-40, -40), (40, -40), (-40, 40), (40, 40)]):
        pole = part(
            f"FloodPole{i}",
            [1.5, 22, 1.5],
            [ox + dx, oy + 11, oz + dz],
            color=STEEL_DARK,
            material="Metal",
        )
        head = {
            "Name": f"FloodHead{i}",
            "ClassName": "Part",
            "Properties": {
                "Anchored": True,
                "Size": [4, 1.5, 3],
                "Position": [ox + dx, oy + 22, oz + dz],
                "Color": rgb(30, 30, 35),
                "Material": "Metal",
                "CanCollide": False,
                "TopSurface": "Smooth",
                "BottomSurface": "Smooth",
            },
            "Children": [
                spot_light("Flood", 3.0, 80, 55, rgb(220, 230, 255), face="Bottom"),
            ],
        }
        kids.append(pole)
        kids.append(head)

    kids.append(pad("PadA", [ox, oy, oz - 26], rgb(90, 100, 180), "P1"))
    kids.append(pad("PadB", [ox, oy, oz + 26], rgb(180, 90, 100), "P2"))
    kids.append(arena_origin([ox, oy, oz]))

    return model("NightYard", kids)


def wrap_root(name: str, children: list[dict]) -> dict:
    return {"ClassName": "Model", "Children": children}


def write_model(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # model.json root uses ClassName/Children; Name comes from filename
    payload = {"ClassName": data.get("ClassName", "Model"), "Children": data.get("Children", [])}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(payload['Children'])} children)")


def main() -> None:
    # Clean previous generated maps (keep folder)
    if OUT.exists():
        for p in OUT.rglob("*.model.json"):
            p.unlink()

    arenas = OUT / "Arenas"
    write_model(OUT / "Lobby.model.json", build_lobby())
    write_model(arenas / "ScrapPit.model.json", build_scrap_pit([0, 0, 400]))
    write_model(arenas / "DryDock.model.json", build_dry_dock([400, 0, 0]))
    write_model(arenas / "NightYard.model.json", build_night_yard([-400, 0, 0]))

    # Folder marker for Arenas via init.meta not needed — directory = Folder
    print("done")


if __name__ == "__main__":
    main()
