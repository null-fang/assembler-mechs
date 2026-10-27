#!/usr/bin/env python3
"""Render front 3/4 combat-pose mech preview from AssemblerAssets kits + Sockets.

Properly rotates part corners (not AABB mush). Cylinders → capsules; Neon → glow.
Camera: front three-quarter (visor/+Z faces viewer), slight elevation, combat crouch.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "src" / "AssemblerAssets" / "Parts"

SOCKETS = {
    "Torso": {"offset": (0.0, 0.0, 0.0), "rot": (8.0, 0.0, 0.0)},
    "LeftHip": {"offset": (-1.05, -1.85, 0.15), "rot": (18.0, 6.0, 10.0)},
    "RightHip": {"offset": (1.05, -1.85, 0.15), "rot": (18.0, -6.0, -10.0)},
    "LowerLeft": {"offset": (-2.15, -0.35, 0.95), "rot": (12.0, 28.0, -22.0)},
    "LowerRight": {"offset": (2.15, -0.35, 0.95), "rot": (12.0, -28.0, 22.0)},
    "ShoulderLeft": {"offset": (-1.75, 1.55, -0.35), "rot": (-18.0, 18.0, 6.0)},
    "ShoulderRight": {"offset": (1.75, 1.55, -0.35), "rot": (-18.0, -18.0, -6.0)},
    "Battery": {"offset": (0.0, 0.15, -1.45), "rot": (0.0, 0.0, 0.0)},
    "CPU": {"offset": (0.0, 1.15, 0.35), "rot": (0.0, 0.0, 0.0)},
}

# Hero starter kits (overwritten by author_hero_mech after generate)
SHOWCASE = {
    "Torso": "rusty_cage",
    "LeftHip": "workboot_l",
    "RightHip": "workboot_r",
    "LowerLeft": "snap_arm",
    "LowerRight": "rivet_gun",
    "ShoulderLeft": "rocket_pod",
    "ShoulderRight": "brick_shoulder",
    "Battery": "desk_brick",
    "CPU": "scrap_cpu",
}


def deg_mat(rx: float, ry: float, rz: float):
    ax, ay, az = map(math.radians, (rx, ry, rz))
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    return (
        (cy * cz, cz * sx * sy - cx * sz, sx * sz + cx * cz * sy),
        (cy * sz, cx * cz + sx * sy * sz, cx * sy * sz - cz * sx),
        (-sy, cy * sx, cx * cy),
    )


def mul(m, v):
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def load_parts(pid: str) -> list[dict]:
    data = json.loads((PARTS / f"{pid}.model.json").read_text(encoding="utf-8"))
    out = []
    for ch in data.get("Children") or []:
        if ch.get("ClassName") not in ("Part", "WedgePart"):
            continue
        if ch.get("Name") == "Root":
            continue
        props = ch.get("Properties") or {}
        if float(props.get("Transparency") or 0) >= 0.99:
            continue
        size = list(props.get("Size") or [1, 1, 1])
        pos = list(props.get("Position") or [0, 0, 0])
        if "CFrame" in props:
            pos = list(props["CFrame"][:3])
        color = list(props.get("Color") or [0.5, 0.5, 0.5])
        mat = props.get("Material") or "Metal"
        name = ch["Name"]
        out.append(
            {
                "name": name,
                "size": size,
                "pos": pos,
                "color": color,
                "material": mat,
                "shape": props.get("Shape"),
                "wedge": ch.get("ClassName") == "WedgePart",
                "neon": mat == "Neon" or name.startswith("Glow") or "Visor" in name or "Lens" in name or "Muzzle" in name,
            }
        )
    return out


def collect():
    items = []
    for socket, pid in SHOWCASE.items():
        sock = SOCKETS[socket]
        Rs = deg_mat(*sock["rot"])
        origin = sock["offset"]
        for p in load_parts(pid):
            local = tuple(float(x) for x in p["pos"])
            world_c = (
                origin[0] + mul(Rs, local)[0],
                origin[1] + mul(Rs, local)[1],
                origin[2] + mul(Rs, local)[2],
            )
            sx, sy, sz = (float(x) for x in p["size"])
            corners_w = []
            for dx in (-sx / 2, sx / 2):
                for dy in (-sy / 2, sy / 2):
                    for dz in (-sz / 2, sz / 2):
                        corners_w.append(
                            (
                                world_c[0] + mul(Rs, (dx, dy, dz))[0],
                                world_c[1] + mul(Rs, (dx, dy, dz))[1],
                                world_c[2] + mul(Rs, (dx, dy, dz))[2],
                            )
                        )
            items.append(
                {
                    **p,
                    "world": world_c,
                    "corners": corners_w,
                    "Rs": Rs,
                }
            )
    return items


# Front 3/4 camera basis (shared with author_hero_mech)
_AZ = math.radians(28)
_EL = math.radians(16)
_CAM = (
    math.sin(_AZ) * math.cos(_EL),
    math.sin(_EL),
    math.cos(_AZ) * math.cos(_EL),
)
_FWD = (-_CAM[0], -_CAM[1], -_CAM[2])
_RX, _RZ = _FWD[2], -_FWD[0]
_RLEN = math.hypot(_RX, _RZ) or 1.0
_RIGHT = (_RX / _RLEN, 0.0, _RZ / _RLEN)
_UP = (
    _FWD[1] * _RIGHT[2] - _FWD[2] * _RIGHT[1],
    _FWD[2] * _RIGHT[0] - _FWD[0] * _RIGHT[2],
    _FWD[0] * _RIGHT[1] - _FWD[1] * _RIGHT[0],
)


def project(x, y, z, *, scale, cx, cy):
    sx = (x * _RIGHT[0] + y * _RIGHT[1] + z * _RIGHT[2]) * scale + cx
    sy = -(x * _UP[0] + y * _UP[1] + z * _UP[2]) * scale + cy
    return sx, sy


def depth_key(x, y, z) -> float:
    # Larger = farther from camera (draw first)
    return -(x * _CAM[0] + y * _CAM[1] + z * _CAM[2])


def rgb255(c, shade=1.0, boost=0):
    return tuple(max(0, min(255, int(c[i] * 255 * shade) + boost)) for i in range(3))


def draw_part(draw, glow_layer, part, scale, cx, cy):
    corners = [project(*c, scale=scale, cx=cx, cy=cy) for c in part["corners"]]
    # Corner index from nested loops dx,dy,dz:
    # 0 - - -   1 - - +   2 - + -   3 - + +   4 + - -   5 + - +   6 + + -   7 + + +
    faces = [
        ([1, 5, 7, 3], 1.1 if part["neon"] else 1.05),  # +Z front
        ([2, 3, 7, 6], 0.9),  # +Y
        ([5, 4, 6, 7], 0.78),  # +X
        ([0, 1, 3, 2], 0.72),  # -X
        ([0, 4, 5, 1], 0.62),  # -Y
        ([0, 2, 6, 4], 0.55),  # -Z back
    ]
    for idxs, shade in faces:
        pts = [corners[i] for i in idxs]
        area = (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[2][0] - pts[0][0]) * (
            pts[1][1] - pts[0][1]
        )
        if area <= 0:
            continue
        col = rgb255(part["color"], shade, boost=35 if part["neon"] else 0)
        draw.polygon(pts, fill=col)
        draw.line(pts + [pts[0]], fill=rgb255(part["color"], shade * 0.5), width=1)

    if part["shape"] == "Cylinder":
        for face_idxs in ([4, 5, 7, 6], [0, 1, 3, 2]):
            pts = [corners[i] for i in face_idxs]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            bbox = [min(xs), min(ys), max(xs), max(ys)]
            draw.ellipse(bbox, outline=rgb255(part["color"], 0.5), width=2)

    if part["neon"]:
        xs = [p[0] for p in corners]
        ys = [p[1] for p in corners]
        pad = 10
        glow_layer.ellipse(
            [min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad],
            fill=rgb255(part["color"], 1.0, boost=40),
        )


def render(out: Path, size: int = 1100) -> None:
    parts = collect()
    # Sort by camera depth (far → near)
    parts.sort(key=lambda b: depth_key(*b["world"]))

    img = Image.new("RGB", (size, size), (16, 20, 26))
    draw = ImageDraw.Draw(img)
    for i in range(size):
        t = i / size
        draw.line([(0, i), (size, i)], fill=(int(16 + 28 * t), int(20 + 22 * t), int(26 + 30 * t)))

    floor_y = int(size * 0.82)
    draw.rectangle([0, floor_y, size, size], fill=(24, 28, 34))
    draw.ellipse([size * 0.18, floor_y - 22, size * 0.82, floor_y + 70], fill=(34, 38, 46))
    for gx in range(-40, size + 40, 56):
        draw.line([(gx, floor_y), (gx + 90, size)], fill=(44, 50, 58), width=1)

    # Autofit projected bounds
    all_xy = []
    for p in parts:
        for c in p["corners"]:
            all_xy.append(project(*c, scale=1.0, cx=0, cy=0))
    xs = [p[0] for p in all_xy]
    ys = [p[1] for p in all_xy]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    scale = (size * 0.78) / span
    cx = size * 0.50 - ((min(xs) + max(xs)) / 2) * scale
    cy = size * 0.48 - ((min(ys) + max(ys)) / 2) * scale

    glow = Image.new("RGB", (size, size), (0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for p in parts:
        draw_part(draw, gdraw, p, scale, cx, cy)

    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(img, ImageChops_screen(img, glow), 0.35)

    bar = ImageDraw.Draw(img)
    bar.rectangle([0, size - 58, size, size], fill=(10, 12, 16))
    bar.text(
        (28, size - 40),
        "Assembler  ·  front 3/4 combat pose  ·  dense SM-inspired kits",
        fill=(210, 220, 230),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print(f"wrote {out} ({len(parts)} parts)")


def ImageChops_screen(a: Image.Image, b: Image.Image) -> Image.Image:
    from PIL import ImageChops

    return ImageChops.screen(a, b)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("/cursor/stores/bc-48ea8082-48b2-43e8-bfa6-d6d6d8d5a5a0/media/supermechs-3d-preview.png"),
    )
    args = ap.parse_args()
    render(args.out)


if __name__ == "__main__":
    main()
