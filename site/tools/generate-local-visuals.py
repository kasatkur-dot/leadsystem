#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"


PALETTES = {
    "blue": {
        "bg1": (236, 242, 246),
        "bg2": (194, 214, 228),
        "ink": (28, 54, 78),
        "soft": (80, 124, 154),
        "accent": (173, 120, 70),
        "line": (255, 255, 255),
    },
    "stone": {
        "bg1": (241, 235, 222),
        "bg2": (202, 214, 211),
        "ink": (39, 52, 58),
        "soft": (92, 118, 125),
        "accent": (151, 91, 62),
        "line": (255, 255, 255),
    },
    "green": {
        "bg1": (232, 238, 227),
        "bg2": (183, 211, 202),
        "ink": (35, 68, 69),
        "soft": (73, 125, 116),
        "accent": (170, 113, 63),
        "line": (255, 255, 255),
    },
}


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient(size: tuple[int, int], p: dict[str, tuple[int, int, int]]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, p["bg1"])
    px = img.load()
    for y in range(h):
        ty = y / max(1, h - 1)
        for x in range(w):
            tx = x / max(1, w - 1)
            t = 0.68 * ty + 0.32 * tx
            c = tuple(lerp(p["bg1"][i], p["bg2"][i], t) for i in range(3))
            px[x, y] = c
    return img


def overlay_grid(draw: ImageDraw.ImageDraw, w: int, h: int, p: dict[str, tuple[int, int, int]], step: int) -> None:
    line = (*p["line"], 44)
    for x in range(0, w + step, step):
        draw.line((x, 0, x, h), fill=line, width=1)
    for y in range(0, h + step, step):
        draw.line((0, y, w, y), fill=line, width=1)
    for x in range(-h, w, step * 3):
        draw.line((x, h, x + h, 0), fill=(*p["line"], 24), width=1)


def add_glow(base: Image.Image, boxes: list[tuple[int, int, int, int]], color: tuple[int, int, int]) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for box in boxes:
        gd.rounded_rectangle(box, radius=32, fill=(*color, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    base.alpha_composite(glow)


def facade(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, p: dict[str, tuple[int, int, int]], floors: int, bays: int, roof: bool = True) -> None:
    body = (*p["ink"], 222)
    shade = (*p["soft"], 185)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=10, fill=body)
    draw.rectangle((x + width * 0.08, y + height * 0.06, x + width * 0.36, y + height), fill=shade)
    if roof:
        draw.polygon(
            [(x - width * 0.04, y + height * 0.02), (x + width * 0.52, y - height * 0.10), (x + width * 1.04, y + height * 0.02)],
            fill=(*p["accent"], 215),
        )
    gap_x = width / (bays + 1)
    gap_y = height / (floors + 1)
    win_w = max(10, int(gap_x * 0.38))
    win_h = max(8, int(gap_y * 0.28))
    for row in range(1, floors + 1):
        for col in range(1, bays + 1):
            wx = int(x + gap_x * col - win_w / 2)
            wy = int(y + gap_y * row - win_h / 2)
            fill = (232, 240, 237, 185) if (row + col) % 3 else (194, 215, 222, 165)
            draw.rounded_rectangle((wx, wy, wx + win_w, wy + win_h), radius=3, fill=fill)


def structural_frame(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, p: dict[str, tuple[int, int, int]], levels: int = 5, bays: int = 6) -> None:
    line = (*p["ink"], 210)
    accent = (*p["accent"], 210)
    for i in range(levels + 1):
        yy = y + int(h * i / levels)
        draw.line((x, yy, x + w, yy), fill=line, width=5 if i in (0, levels) else 3)
    for i in range(bays + 1):
        xx = x + int(w * i / bays)
        draw.line((xx, y, xx, y + h), fill=line, width=5 if i in (0, bays) else 3)
    for i in range(bays):
        x1 = x + int(w * i / bays)
        x2 = x + int(w * (i + 1) / bays)
        draw.line((x1, y + h, x2, y), fill=accent if i % 2 == 0 else (*p["soft"], 170), width=3)


def floor_plan(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, p: dict[str, tuple[int, int, int]]) -> None:
    wall = (*p["ink"], 230)
    thin = (*p["soft"], 190)
    fill = (255, 255, 255, 105)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=wall, width=7)
    splits = [
        ((x + int(w * 0.43), y), (x + int(w * 0.43), y + h)),
        ((x, y + int(h * 0.48)), (x + int(w * 0.43), y + int(h * 0.48))),
        ((x + int(w * 0.43), y + int(h * 0.34)), (x + w, y + int(h * 0.34))),
        ((x + int(w * 0.68), y + int(h * 0.34)), (x + int(w * 0.68), y + h)),
        ((x + int(w * 0.43), y + int(h * 0.68)), (x + w, y + int(h * 0.68))),
    ]
    for a, b in splits:
        draw.line((*a, *b), fill=wall, width=5)
    for i in range(8):
        xx = x + 35 + i * int(w / 9)
        draw.arc((xx, y + h - 80, xx + 68, y + h - 12), 180, 270, fill=thin, width=3)
    for i in range(5):
        draw.rounded_rectangle(
            (x + 34 + i * int(w * 0.16), y + 32, x + 80 + i * int(w * 0.16), y + 64),
            radius=4,
            outline=thin,
            width=2,
        )


def document_stack(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, p: dict[str, tuple[int, int, int]]) -> None:
    for i in range(4):
        ox = i * 24
        oy = i * 18
        draw.rounded_rectangle((x + ox, y + oy, x + w + ox, y + h + oy), radius=18, fill=(255, 255, 255, 160), outline=(*p["ink"], 80), width=2)
    for i in range(8):
        yy = y + 62 + i * 38
        draw.line((x + 62, yy, x + w - 62, yy), fill=(*p["soft"], 135), width=3)
    draw.rounded_rectangle((x + 62, y + 58, x + 180, y + 94), radius=8, fill=(*p["accent"], 155))


def skyline(draw: ImageDraw.ImageDraw, w: int, h: int, p: dict[str, tuple[int, int, int]], rng: random.Random) -> None:
    ground = int(h * 0.72)
    draw.polygon([(0, h), (0, ground), (w, int(h * 0.62)), (w, h)], fill=(*p["ink"], 42))
    x = int(w * 0.05)
    while x < w * 0.94:
        bw = rng.randint(int(w * 0.05), int(w * 0.11))
        bh = rng.randint(int(h * 0.16), int(h * 0.46))
        facade(draw, x, ground - bh, bw, bh, p, rng.randint(3, 8), rng.randint(3, 6), roof=rng.random() > 0.55)
        x += bw + rng.randint(14, 34)


def draw_asset(name: str, size: tuple[int, int], palette: str, mode: str, seed: int) -> None:
    rng = random.Random(seed)
    p = PALETTES[palette]
    base = gradient(size, p).convert("RGBA")
    w, h = size
    add_glow(base, [(int(w * 0.56), int(h * 0.08), int(w * 1.05), int(h * 0.52)), (-80, int(h * 0.52), int(w * 0.32), int(h * 1.08))], p["accent"])
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    overlay_grid(d, w, h, p, max(46, int(w / 24)))

    if mode == "hero":
        skyline(d, w, h, p, rng)
        structural_frame(d, int(w * 0.54), int(h * 0.17), int(w * 0.30), int(h * 0.46), p, 6, 5)
        floor_plan(d, int(w * 0.08), int(h * 0.18), int(w * 0.31), int(h * 0.36), p)
    elif mode == "docs":
        document_stack(d, int(w * 0.12), int(h * 0.15), int(w * 0.36), int(h * 0.62), p)
        facade(d, int(w * 0.58), int(h * 0.26), int(w * 0.24), int(h * 0.42), p, 6, 4)
    elif mode == "blueprint":
        floor_plan(d, int(w * 0.12), int(h * 0.14), int(w * 0.70), int(h * 0.58), p)
        structural_frame(d, int(w * 0.50), int(h * 0.42), int(w * 0.30), int(h * 0.30), p, 3, 4)
    elif mode == "frame":
        structural_frame(d, int(w * 0.13), int(h * 0.18), int(w * 0.70), int(h * 0.56), p, 6, 7)
        facade(d, int(w * 0.61), int(h * 0.29), int(w * 0.20), int(h * 0.34), p, 5, 3, False)
    elif mode == "plan":
        floor_plan(d, int(w * 0.10), int(h * 0.11), int(w * 0.78), int(h * 0.70), p)
        d.rounded_rectangle((int(w * 0.18), int(h * 0.23), int(w * 0.33), int(h * 0.36)), radius=14, fill=(*p["accent"], 72))
    elif mode == "renovation":
        facade(d, int(w * 0.18), int(h * 0.22), int(w * 0.44), int(h * 0.46), p, 5, 6)
        for i in range(5):
            xx = int(w * (0.14 + i * 0.11))
            d.line((xx, int(h * 0.18), xx + int(w * 0.22), int(h * 0.75)), fill=(*p["accent"], 165), width=4)
        document_stack(d, int(w * 0.62), int(h * 0.30), int(w * 0.20), int(h * 0.35), p)
    elif mode == "warehouse":
        d.polygon([(int(w * 0.12), int(h * 0.62)), (int(w * 0.28), int(h * 0.28)), (int(w * 0.86), int(h * 0.30)), (int(w * 0.92), int(h * 0.64))], fill=(*p["ink"], 210))
        d.polygon([(int(w * 0.16), int(h * 0.61)), (int(w * 0.30), int(h * 0.35)), (int(w * 0.82), int(h * 0.37)), (int(w * 0.88), int(h * 0.62))], fill=(*p["soft"], 178))
        for i in range(7):
            xx = int(w * (0.24 + i * 0.08))
            d.line((xx, int(h * 0.38), xx + int(w * 0.04), int(h * 0.62)), fill=(255, 255, 255, 105), width=3)
        structural_frame(d, int(w * 0.18), int(h * 0.64), int(w * 0.68), int(h * 0.12), p, 1, 8)
    elif mode == "campus":
        facade(d, int(w * 0.14), int(h * 0.34), int(w * 0.28), int(h * 0.34), p, 4, 5)
        facade(d, int(w * 0.55), int(h * 0.27), int(w * 0.26), int(h * 0.42), p, 5, 4)
        d.rounded_rectangle((int(w * 0.38), int(h * 0.49), int(w * 0.58), int(h * 0.57)), radius=18, fill=(*p["accent"], 175))
    elif mode == "tower":
        facade(d, int(w * 0.42), int(h * 0.12), int(w * 0.22), int(h * 0.66), p, 11, 4)
        structural_frame(d, int(w * 0.20), int(h * 0.24), int(w * 0.28), int(h * 0.44), p, 6, 4)
        structural_frame(d, int(w * 0.62), int(h * 0.34), int(w * 0.18), int(h * 0.34), p, 5, 3)
    elif mode == "media":
        floor_plan(d, int(w * 0.11), int(h * 0.18), int(w * 0.34), int(h * 0.46), p)
        document_stack(d, int(w * 0.49), int(h * 0.16), int(w * 0.30), int(h * 0.54), p)
        structural_frame(d, int(w * 0.32), int(h * 0.62), int(w * 0.40), int(h * 0.16), p, 2, 5)
    else:
        skyline(d, w, h, p, rng)
        floor_plan(d, int(w * 0.10), int(h * 0.16), int(w * 0.34), int(h * 0.38), p)

    for _ in range(12):
        cx = rng.randint(0, w)
        cy = rng.randint(0, h)
        r = rng.randint(max(18, w // 80), max(42, w // 28))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*p["line"], rng.randint(28, 70)), width=2)

    base.alpha_composite(layer)
    vignette = Image.new("RGBA", size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, w, h), outline=(22, 43, 62, 34), width=max(10, w // 70))
    base.alpha_composite(vignette.filter(ImageFilter.GaussianBlur(max(10, w // 80))))
    base = base.convert("RGB")
    base.save(OUT / name, "WEBP", quality=82, method=6)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assets = [
        ("hero-building.webp", (1600, 1000), "blue", "hero"),
        ("service-project-docs.webp", (1200, 800), "stone", "docs"),
        ("service-working-docs.webp", (1200, 800), "blue", "blueprint"),
        ("service-architecture-structure.webp", (1200, 800), "green", "frame"),
        ("service-replanning.webp", (1200, 800), "stone", "plan"),
        ("service-reconstruction.webp", (1200, 800), "blue", "renovation"),
        ("service-commercial.webp", (1200, 800), "green", "warehouse"),
        ("case-education-campus.webp", (1400, 900), "green", "campus"),
        ("case-school-renovation.webp", (1200, 800), "blue", "renovation"),
        ("case-warehouse.webp", (1200, 800), "stone", "warehouse"),
        ("case-office-replanning.webp", (1000, 750), "green", "plan"),
        ("case-structural-tower.webp", (1000, 750), "blue", "tower"),
        ("media-video-cover.webp", (1400, 900), "stone", "media"),
        ("media-diagram.webp", (1200, 800), "blue", "blueprint"),
        ("about-engineering-office.webp", (1400, 900), "green", "docs"),
        ("contacts-building-bg.webp", (1800, 950), "blue", "hero"),
    ]
    for idx, item in enumerate(assets, start=1):
        draw_asset(*item, seed=20260511 + idx)


if __name__ == "__main__":
    main()
