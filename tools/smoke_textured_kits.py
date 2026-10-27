#!/usr/bin/env python3
"""Smoke: texture pack + TextureIds contract + TextureRole on kits."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)
    print(f"FAIL: {msg}")


def main() -> int:
    ids_path = ROOT / "tools" / "texture_ids.json"
    if not ids_path.exists():
        fail("tools/texture_ids.json missing")
        return 1
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
    keys = list((ids.get("textures") or {}).keys())
    expected = [
        "metal_plate",
        "scratched_steel",
        "hazard_stripe",
        "matte_rubber",
        "carbon_dark",
        "emissive_strip",
    ]
    for k in expected:
        if k not in keys:
            fail(f"texture key missing: {k}")
        png = ROOT / "assets" / "textures" / f"{k}.png"
        if not png.exists():
            fail(f"png missing: {png.relative_to(ROOT)}")
        tmpl = ROOT / "src" / "AssemblerAssets" / "Textures" / f"{k}.model.json"
        if not tmpl.exists():
            fail(f"template missing: {tmpl.relative_to(ROOT)}")
        embed = ROOT / "src" / "Shared" / "Assembler" / "TexturePixels" / f"{k}.luau"
        if not embed.exists():
            fail(f"embed missing: {embed.relative_to(ROOT)}")

    for rel in (
        "src/Shared/Assembler/TextureIds.luau",
        "src/Shared/Assembler/TextureApply.luau",
        "src/Shared/Assembler/TexturePixels/init.luau",
    ):
        if not (ROOT / rel).exists():
            fail(f"missing {rel}")

    parts = ROOT / "src" / "AssemblerAssets" / "Parts"
    showcase = ["crest_vault", "aegis_door", "pulse_mitt", "rack_salvo", "rusty_cage"]
    for pid in showcase:
        path = parts / f"{pid}.model.json"
        if not path.exists():
            fail(f"showcase kit missing: {pid}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        roles = 0
        for ch in data.get("Children") or []:
            attrs = ch.get("Attributes") or {}
            if attrs.get("TextureRole"):
                roles += 1
        if roles < 2:
            fail(f"{pid}: expected TextureRole on parts, found {roles}")
        else:
            print(f"OK {pid}: {roles} textured parts")

    luau = (ROOT / "src/Shared/Assembler/TextureIds.luau").read_text(encoding="utf-8")
    for k in expected:
        if k not in luau:
            fail(f"TextureIds.luau missing key {k}")

    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        return 1
    print("smoke_textured_kits OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
