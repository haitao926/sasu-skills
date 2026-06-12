#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


RATIOS = {
    "21:9": (2100, 900),
    "16:10": (1600, 1000),
    "16:9": (1600, 900),
    "4:3": (1200, 900),
    "1:1": (1200, 1200),
}

STYLE_PRESETS = {
    "swiss-ikb": ("style-b/ikb-dot-gradient.webp", "square", "none"),
    "swiss-lemon": ("style-b/lemon-grid.webp", "square", "none"),
    "swiss-green": ("style-b/lemon-green-dot-shadow.webp", "square", "none"),
    "swiss-orange": ("style-b/safety-orange-halftone.webp", "square", "none"),
    "magazine-classic": ("style-a/monocle-classic.webp", "small", "editorial"),
    "magazine-indigo": ("style-a/indigo-porcelain.webp", "small", "editorial"),
    "magazine-forest": ("style-a/forest-ink.webp", "small", "editorial"),
    "magazine-kraft": ("style-a/kraft-paper.webp", "small", "editorial"),
    "magazine-dune": ("style-a/dune.webp", "small", "editorial"),
}


def cover_resize(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    src_w, src_h = img.size
    dst_w, dst_h = size
    scale = max(dst_w / src_w, dst_h / src_h)
    resized = img.resize((round(src_w * scale), round(src_h * scale)), Image.LANCZOS)
    left = (resized.width - dst_w) // 2
    top = (resized.height - dst_h) // 2
    return resized.crop((left, top, left + dst_w, top + dst_h))


def fit_size(src: tuple[int, int], dst: tuple[int, int]) -> tuple[int, int]:
    src_w, src_h = src
    dst_w, dst_h = dst
    scale = min(dst_w / src_w, dst_h / src_h)
    return max(1, round(src_w * scale)), max(1, round(src_h * scale))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def paste_shadow(canvas: Image.Image, rect: tuple[int, int, int, int], radius: int, strength: str) -> None:
    if strength == "none":
        return
    x, y, w, h = rect
    pad = 42 if strength == "editorial" else 28
    alpha = 80 if strength == "editorial" else 52
    shadow = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    mask = rounded_mask((w, h), radius)
    shadow_alpha = Image.new("L", (w + pad * 2, h + pad * 2), 0)
    shadow_alpha.paste(mask, (pad, pad))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(18 if strength == "editorial" else 10))
    shadow.putalpha(shadow_alpha.point(lambda v: min(alpha, v)))
    canvas.alpha_composite(shadow, (x - pad, y - pad + (18 if strength == "editorial" else 10)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Frame a screenshot on a PPT template-compatible background.")
    parser.add_argument("--input", required=True, help="Screenshot or image to frame")
    parser.add_argument("--out", required=True, help="Output image path")
    parser.add_argument("--ratio", default="16:10", choices=sorted(RATIOS))
    parser.add_argument("--style", default="swiss-ikb", choices=sorted(STYLE_PRESETS))
    parser.add_argument("--padding", default="standard", choices=["compact", "standard", "spacious"])
    parser.add_argument("--background-root", default=str(Path(__file__).resolve().parents[1] / "assets/guizang/screenshot-backgrounds"))
    args = parser.parse_args()

    out_size = RATIOS[args.ratio]
    bg_rel, corner_mode, shadow = STYLE_PRESETS[args.style]
    bg_path = Path(args.background_root) / bg_rel

    if bg_path.exists():
        bg = cover_resize(Image.open(bg_path).convert("RGB"), out_size)
    else:
        bg = Image.new("RGB", out_size, (250, 250, 248))

    canvas = bg.convert("RGBA")
    shot = Image.open(args.input).convert("RGBA")

    pad_fraction = {"compact": 0.08, "standard": 0.12, "spacious": 0.17}[args.padding]
    max_w = round(out_size[0] * (1 - pad_fraction * 2))
    max_h = round(out_size[1] * (1 - pad_fraction * 2))
    fit_w, fit_h = fit_size(shot.size, (max_w, max_h))
    shot = shot.resize((fit_w, fit_h), Image.LANCZOS)

    x = (out_size[0] - fit_w) // 2
    y = (out_size[1] - fit_h) // 2
    radius = 0 if corner_mode == "square" else round(min(out_size) * 0.018)

    paste_shadow(canvas, (x, y, fit_w, fit_h), radius, shadow)
    if radius:
        mask = rounded_mask((fit_w, fit_h), radius)
        clipped = Image.new("RGBA", (fit_w, fit_h), (0, 0, 0, 0))
        clipped.paste(shot, (0, 0), mask)
        canvas.alpha_composite(clipped, (x, y))
    else:
        canvas.alpha_composite(shot, (x, y))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(args.out, quality=94)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
