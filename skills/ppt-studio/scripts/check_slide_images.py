#!/usr/bin/env python3
"""Check PPT Studio slide image files before review/export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image


EXPECTED_RATIOS = {
    "16:9": 16 / 9,
    "4:3": 4 / 3,
}


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("manifest must contain a non-empty slides array")
    return data


def check_image(path: Path, expected_ratio: float, tolerance: float, min_width: int, min_height: int) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing image: {path}"]
    if path.stat().st_size <= 0:
        return [f"empty image: {path}"]
    try:
        with Image.open(path) as image:
            width, height = image.size
    except Exception as exc:  # noqa: BLE001 - report image parsing failures concisely.
        return [f"cannot open image {path}: {exc}"]
    if width < min_width or height < min_height:
        errors.append(f"image too small: {path} ({width}x{height})")
    ratio = width / height
    if abs(ratio - expected_ratio) > tolerance:
        errors.append(f"aspect ratio mismatch: {path} ({width}x{height})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PPT Studio slide images.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", default="review_manifest.json")
    parser.add_argument("--min-width", type=int, default=1200)
    parser.add_argument("--min-height", type=int, default=675)
    parser.add_argument("--ratio-tolerance", type=float, default=0.08)
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    manifest = load_manifest(run_dir / args.manifest)
    ratio_name = str(manifest.get("aspect_ratio", "16:9"))
    expected_ratio = EXPECTED_RATIOS.get(ratio_name, EXPECTED_RATIOS["16:9"])

    errors: list[str] = []
    for index, slide in enumerate(manifest["slides"], start=1):
        if not isinstance(slide, dict):
            errors.append(f"slide {index} is not an object")
            continue
        image_rel = slide.get("image")
        if not isinstance(image_rel, str) or not image_rel:
            errors.append(f"slide {index} missing image path")
            continue
        errors.extend(
            check_image(
                run_dir / image_rel,
                expected_ratio,
                args.ratio_tolerance,
                args.min_width,
                args.min_height,
            )
        )

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "slides": len(manifest["slides"]), "aspect_ratio": ratio_name}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
