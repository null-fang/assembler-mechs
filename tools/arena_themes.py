"""Arena theme contract — moods aligned to Yardbone / Rimevault / Duneplate / Voltframe.

Used by generate_maps.py. Mirrored in Shared/Themes/ThemeIds + ArenaMood (Luau).
"""

from __future__ import annotations

from typing import Any


def rgb(r: int, g: int, b: int) -> list[float]:
    return [r / 255.0, g / 255.0, b / 255.0]


# CollectionService tag (Shared/World/Tags.ArenaTheme)
TAG_ARENA = "AssemblerArena"
TAG_ARENA_THEME = "AssemblerArenaTheme"
ATTR_THEME_ID = "ThemeId"
ATTR_THEME_LINE = "ThemeLine"
ATTR_ARENA_ID = "ArenaId"

# Model name → theme set
ARENAS: dict[str, dict[str, Any]] = {
    "ScrapPit": {
        "theme_id": "ScrapPit",
        "mech_line": "Yardbone",
        "mood": "scrap",
        "origin": [0.0, 0.0, 400.0],
        "label": "SCRAP PIT",
        "tagline": "Yardbone scrap bowl",
        "floor": rgb(118, 78, 52),
        "accent": rgb(255, 140, 60),
        "haze": rgb(180, 110, 60),
        "lamp": rgb(255, 170, 100),
    },
    "DryDock": {
        "theme_id": "DryDock",
        "mech_line": "Rimevault",
        "mood": "arctic",
        "origin": [400.0, 0.0, 0.0],
        "label": "DRY DOCK",
        "tagline": "Rimevault ice pier",
        "floor": rgb(170, 190, 210),
        "accent": rgb(120, 210, 245),
        "haze": rgb(140, 190, 230),
        "lamp": rgb(200, 230, 255),
    },
    "NightYard": {
        "theme_id": "NightYard",
        "mech_line": "Voltframe",
        "mood": "neon",
        "origin": [-400.0, 0.0, 0.0],
        "label": "NIGHT YARD",
        "tagline": "Voltframe neon yard",
        "floor": rgb(28, 30, 38),
        "accent": rgb(210, 70, 180),
        "haze": rgb(40, 30, 80),
        "lamp": rgb(180, 160, 255),
    },
    "SandQuarry": {
        "theme_id": "SandQuarry",
        "mech_line": "Duneplate",
        "mood": "desert",
        "origin": [0.0, 0.0, -400.0],
        "label": "SAND QUARRY",
        "tagline": "Duneplate heat yard",
        "floor": rgb(198, 160, 95),
        "accent": rgb(220, 140, 50),
        "haze": rgb(210, 170, 100),
        "lamp": rgb(255, 210, 140),
    },
}

# Lobby landmark booths (shop / crate plaza) — order matches mech lines.
LOBBY_THEME_LANDMARKS = [
    {
        "key": "Scrap",
        "line": "Yardbone",
        "mood": "scrap",
        "label": "YARDBONE SHOP",
        "crate_label": "SCRAP CRATE",
        "pos": [-55.0, 0.0, -78.0],
        "board": rgb(120, 70, 40),
        "neon": rgb(255, 150, 60),
        "crate": rgb(130, 90, 50),
    },
    {
        "key": "Arctic",
        "line": "Rimevault",
        "mood": "arctic",
        "label": "RIMEVAULT SHOP",
        "crate_label": "ICE CRATE",
        "pos": [-20.0, 0.0, -78.0],
        "board": rgb(70, 110, 140),
        "neon": rgb(140, 220, 255),
        "crate": rgb(180, 200, 220),
    },
    {
        "key": "Desert",
        "line": "Duneplate",
        "mood": "desert",
        "label": "DUNEPLATE SHOP",
        "crate_label": "DUNE CRATE",
        "pos": [20.0, 0.0, -78.0],
        "board": rgb(160, 120, 55),
        "neon": rgb(230, 170, 70),
        "crate": rgb(190, 150, 80),
    },
    {
        "key": "Neon",
        "line": "Voltframe",
        "mood": "neon",
        "label": "VOLTFRAME SHOP",
        "crate_label": "VOLT CRATE",
        "pos": [55.0, 0.0, -78.0],
        "board": rgb(40, 35, 70),
        "neon": rgb(80, 230, 255),
        "crate": rgb(60, 50, 100),
    },
]


def arena_model_meta(arena_name: str) -> dict[str, Any]:
    """Attributes + Tags baked into Rojo arena Models."""
    info = ARENAS[arena_name]
    return {
        "Attributes": {
            ATTR_THEME_ID: info["theme_id"],
            ATTR_THEME_LINE: info["mech_line"],
            ATTR_ARENA_ID: arena_name,
            "Mood": info["mood"],
        },
        "Tags": [TAG_ARENA, TAG_ARENA_THEME],
    }
