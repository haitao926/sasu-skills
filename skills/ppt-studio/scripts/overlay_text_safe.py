#!/usr/bin/env python3
"""Overlay exact text onto Roil-generated visual plates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


FONT_REGULAR_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


ROLE_SIZES = {
    "title": 76,
    "subtitle": 38,
    "heading": 42,
    "body": 30,
    "label": 26,
    "page": 22,
}

TARGET_SIZE = (1600, 900)


def choose_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    raise RuntimeError("no usable CJK font found")


def fit_font(text: str, role: str, max_width: int, max_height: int, bold: bool) -> ImageFont.FreeTypeFont:
    base_size = int(ROLE_SIZES.get(role, 30))
    candidates = FONT_BOLD_CANDIDATES if bold or role in {"title", "heading"} else FONT_REGULAR_CANDIDATES
    dummy = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(dummy)
    for size in range(base_size, 15, -2):
        font = choose_font(candidates, size)
        lines = wrap_text(draw, text, font, max_width)
        line_height = int(size * 1.18)
        height = len(lines) * line_height
        widest = max((draw.textbbox((0, 0), line, font=font)[2] for line in lines), default=0)
        if widest <= max_width and height <= max_height:
            return font
    return choose_font(candidates, 16)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    normalized = str(text).replace("\\n", "\n")
    for paragraph in normalized.splitlines() or [normalized]:
        current = ""
        for char in paragraph:
            candidate = current + char
            width = draw.textbbox((0, 0), candidate, font=font)[2]
            if width <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = char
        if current:
            lines.append(current)
    return lines or [""]


def parse_color(raw: str | None, default: str) -> tuple[int, int, int, int]:
    value = (raw or default).strip().lstrip("#")
    if len(value) == 6:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
    if len(value) == 8:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4, 6))
    raise ValueError(f"invalid color: {raw}")


def rounded_rectangle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline, width: int) -> None:
    try:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    except AttributeError:
        draw.rectangle(box, fill=fill, outline=outline, width=width)


def draw_container(draw: ImageDraw.ImageDraw, image_size: tuple[int, int], block: dict) -> None:
    if not block.get("container"):
        return
    width, height = image_size
    x = int(float(block["x"]) * width)
    y = int(float(block["y"]) * height)
    w = int(float(block["w"]) * width)
    h = int(float(block["h"]) * height)
    fill = parse_color(block.get("container_fill"), "#FFFFFF")
    outline = parse_color(block.get("container_line"), "#A9C7E8")
    line_width = max(1, int(float(block.get("container_line_width", 1.5)) * 2))
    radius = int(min(w, h) * 0.1) if block.get("container_shape", "rounded") != "rect" else 0
    box = (x, y, x + w, y + h)
    if radius > 0:
        rounded_rectangle(draw, box, radius, fill, outline, line_width)
    else:
        draw.rectangle(box, fill=fill, outline=outline, width=line_width)


def draw_block(draw: ImageDraw.ImageDraw, image_size: tuple[int, int], block: dict) -> None:
    width, height = image_size
    x = int(float(block["x"]) * width)
    y = int(float(block["y"]) * height)
    w = int(float(block["w"]) * width)
    h = int(float(block["h"]) * height)
    margin_left = int(float(block.get("margin_left", 0)) * width)
    margin_right = int(float(block.get("margin_right", 0)) * width)
    margin_top = int(float(block.get("margin_top", 0)) * height)
    margin_bottom = int(float(block.get("margin_bottom", 0)) * height)
    role = str(block.get("role", "body"))
    text = str(block.get("text", ""))
    align = str(block.get("align", "left"))
    vertical_anchor = str(block.get("vertical_anchor", "middle"))
    fill = parse_color(block.get("color"), "#293241")
    stroke_fill = parse_color(block.get("stroke_color"), "#FFFFFF")
    stroke_width = int(block.get("stroke_width", 0))
    bold = bool(block.get("bold", role in {"title", "heading"}))
    inner_w = max(1, w - margin_left - margin_right)
    inner_h = max(1, h - margin_top - margin_bottom)
    font = fit_font(text, role, inner_w, inner_h, bold)
    lines = wrap_text(draw, text, font, inner_w)
    line_spacing = float(block.get("line_spacing", 1.28))
    line_height = int(font.size * line_spacing)
    total_height = len(lines) * line_height
    if vertical_anchor == "top":
        cy = y + margin_top
    elif vertical_anchor == "bottom":
        cy = y + h - margin_bottom - total_height
    else:
        cy = y + margin_top + max(0, (inner_h - total_height) // 2)
    for line in lines:
        text_width = draw.textbbox((0, 0), line, font=font)[2]
        if align == "center":
            cx = x + margin_left + (inner_w - text_width) // 2
        elif align == "right":
            cx = x + w - margin_right - text_width
        else:
            cx = x + margin_left
        draw.text((cx, cy), line, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        cy += line_height


def process_slide(run_dir: Path, slide: dict) -> dict:
    plate = run_dir / str(slide["visual_plate"])
    output = run_dir / str(slide["output"])
    if not plate.exists():
        raise FileNotFoundError(f"visual plate not found: {slide['visual_plate']}")
    image = fit_to_canvas(Image.open(plate).convert("RGBA"), TARGET_SIZE)
    draw = ImageDraw.Draw(image)
    for block in slide.get("text_blocks", []):
        draw_container(draw, image.size, block)
    for block in slide.get("text_blocks", []):
        draw_block(draw, image.size, block)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, quality=95)
    return {"output": str(output.relative_to(run_dir)), "size": image.size}


def fit_to_canvas(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Center-crop an image to the target slide ratio, then resize."""
    target_w, target_h = size
    target_ratio = target_w / target_h
    width, height = image.size
    ratio = width / height
    if abs(ratio - target_ratio) < 0.01:
        return image.resize(size, Image.Resampling.LANCZOS)
    if ratio > target_ratio:
        new_w = int(height * target_ratio)
        left = max(0, (width - new_w) // 2)
        crop = image.crop((left, 0, left + new_w, height))
    else:
        new_h = int(width / target_ratio)
        top = max(0, (height - new_h) // 2)
        crop = image.crop((0, top, width, top + new_h))
    return crop.resize(size, Image.Resampling.LANCZOS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Overlay exact text onto Roil visual plates.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--spec", required=True, help="JSON overlay spec path relative to run-dir or absolute")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = run_dir / spec_path
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slides = spec.get("slides")
    if not isinstance(slides, list) or not slides:
        raise SystemExit("overlay spec must contain a non-empty slides array")
    outputs = [process_slide(run_dir, slide) for slide in slides]
    print(json.dumps({"ok": True, "outputs": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
