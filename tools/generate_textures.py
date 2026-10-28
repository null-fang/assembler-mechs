#!/usr/bin/env python3
"""Generate industrial mech texture pack PNGs + embed Luau pixel modules.

Regen:
  python tools/generate_textures.py
  # then fill tools/texture_ids.json rbxassetid after Studio upload
"""

from __future__ import annotations

import base64
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "textures"
PIXELS = ROOT / "src" / "Shared" / "Assembler" / "TexturePixels"
SIZE = 256
EMBED = 128
KEYS = [
    "metal_plate",
    "scratched_steel",
    "hazard_stripe",
    "matte_rubber",
    "carbon_dark",
    "emissive_strip",
]


def metal_plate(seed: int = 1) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE))
    px = img.load()
    base = (92, 98, 108)
    for y in range(SIZE):
        for x in range(SIZE):
            n = (math.sin(x * 0.07) + math.cos(y * 0.09)) * 6
            rivet = 18 if ((x + 16) % 64 < 6 and (y + 16) % 64 < 6) else 0
            seam = 12 if (x % 64 < 2) or (y % 64 < 2) else 0
            grit = rng.randint(-10, 10)
            px[x, y] = tuple(
                max(0, min(255, int(base[i] + n + rivet - seam + grit))) for i in range(3)
            )
    d = ImageDraw.Draw(img)
    for gy in range(32, SIZE, 64):
        for gx in range(32, SIZE, 64):
            d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(70, 74, 82), outline=(140, 146, 156))
    return img.filter(ImageFilter.SMOOTH_MORE)


def scratched_steel(seed: int = 2) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE), (120, 124, 130))
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            band = int(8 * math.sin((x + y) * 0.15))
            px[x, y] = (
                120 + band + rng.randint(-8, 8),
                124 + band + rng.randint(-8, 8),
                130 + band + rng.randint(-6, 6),
            )
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(90):
        y0 = rng.randint(0, SIZE - 1)
        length = rng.randint(20, 90)
        x0 = rng.randint(0, SIZE - 1)
        shade = rng.randint(40, 90)
        alpha = rng.randint(60, 140)
        d.line(
            [(x0, y0), ((x0 + length) % SIZE, (y0 + rng.randint(-4, 4)) % SIZE)],
            fill=(shade, shade, shade + 5, alpha),
            width=1,
        )
    return img.convert("RGB")


def hazard_stripe(seed: int = 3) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE))
    px = img.load()
    yellow, black, stripe = (230, 180, 40), (28, 28, 30), 28
    for y in range(SIZE):
        for x in range(SIZE):
            v = (x + y) % (stripe * 2)
            px[x, y] = yellow if v < stripe else black
    rng = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(40):
        x, y = rng.randint(0, SIZE - 1), rng.randint(0, SIZE - 1)
        d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=(80, 80, 80, 90))
    return img.convert("RGB")


def matte_rubber(seed: int = 4) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (SIZE, SIZE))
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            bump = 6 if ((x // 8) + (y // 8)) % 2 == 0 else 0
            g = 36 + bump + rng.randint(-4, 4)
            px[x, y] = (g, g, g + 2)
    for _ in range(2000):
        x, y = rng.randint(0, SIZE - 1), rng.randint(0, SIZE - 1)
        g = rng.randint(20, 55)
        px[x, y] = (g, g, g + 1)
    return img.filter(ImageFilter.SMOOTH)


def carbon_dark(_seed: int = 5) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE))
    px = img.load()
    a, b, twill = (22, 24, 28), (40, 42, 48), 8
    for y in range(SIZE):
        for x in range(SIZE):
            cell = ((x // twill) + (y // twill)) % 2
            sx = (x % twill) / twill
            sy = (y % twill) / twill
            shade = a if cell == 0 else b
            n = int(8 * (sx + sy - 1))
            px[x, y] = tuple(max(0, min(255, shade[i] + n)) for i in range(3))
    return img


def emissive_strip(_seed: int = 6) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(SIZE):
        dist = min(abs(y - SIZE // 2), abs(y - SIZE // 2 + SIZE), abs(y - SIZE // 2 - SIZE))
        if dist < 28:
            t = 1 - dist / 28
            d.line(
                [(0, y), (SIZE, y)],
                fill=(int(80 + 140 * t), int(180 + 60 * t), 255, int(40 + 200 * t)),
            )
    for x in range(0, SIZE, 16):
        d.line([(x, SIZE // 2 - 20), (x, SIZE // 2 + 20)], fill=(200, 240, 255, 90), width=1)
    rgb = Image.new("RGB", (SIZE, SIZE), (8, 12, 20))
    rgb.paste(img, mask=img.split()[-1])
    return rgb


BUILDERS = {
    "metal_plate": metal_plate,
    "scratched_steel": scratched_steel,
    "hazard_stripe": hazard_stripe,
    "matte_rubber": matte_rubber,
    "carbon_dark": carbon_dark,
    "emissive_strip": emissive_strip,
}


def write_embeds(textures: dict[str, Image.Image]) -> None:
    PIXELS.mkdir(parents=True, exist_ok=True)
    for key in KEYS:
        im = textures[key].convert("RGBA").resize((EMBED, EMBED), Image.Resampling.LANCZOS)
        b64 = base64.b64encode(im.tobytes()).decode("ascii")
        chunk = 180
        parts = [b64[i : i + chunk] for i in range(0, len(b64), chunk)]
        body = "\n".join(f'\t\t"{p}",' for p in parts)
        (PIXELS / f"{key}.luau").write_text(
            f"-- Auto-generated RGBA8 @{EMBED} for {key}. Concat + HttpService:Base64Decode.\n"
            f"return table.concat({{\n{body}\n}})\n",
            encoding="utf-8",
        )
    (PIXELS / "init.luau").write_text(
        "-- Embedded industrial texture payloads (RGBA8 base64 @ 128).\n"
        "local M = {\n"
        f"\tSIZE = {EMBED},\n"
        + "".join(f"\t{k} = require(script.{k}),\n" for k in KEYS)
        + "}\nreturn M\n",
        encoding="utf-8",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    textures = {k: BUILDERS[k]() for k in KEYS}
    for name, im in textures.items():
        path = OUT / f"{name}.png"
        im.save(path, "PNG")
        print(f"wrote {path.relative_to(ROOT)}")

    sheet = Image.new("RGB", (SIZE * 3 + 16, SIZE * 2 + 48), (18, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(KEYS):
        x = 8 + (i % 3) * (SIZE + 4)
        y = 32 + (i // 3) * (SIZE + 8)
        sheet.paste(textures[name], (x, y))
        d.text((x + 4, y - 14), name, fill=(200, 210, 220))
    sheet.save(OUT / "pack_contact_sheet.png")
    print(f"wrote {(OUT / 'pack_contact_sheet.png').relative_to(ROOT)}")

    write_embeds(textures)
    print(f"wrote embeds -> {PIXELS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
