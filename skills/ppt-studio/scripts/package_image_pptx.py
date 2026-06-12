#!/usr/bin/env python3
"""Package full-slide images into a 16:9 PPTX."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from pptx import Presentation
from pptx.util import Inches


LAYOUTS = {
    "16:9": (13.333333, 7.5),
    "4:3": (10.0, 7.5),
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


def package(run_dir: Path, manifest: dict, out_path: Path, aspect_ratio: str) -> None:
    width, height = LAYOUTS.get(aspect_ratio, LAYOUTS["16:9"])
    prs = Presentation()
    prs.slide_width = Inches(width)
    prs.slide_height = Inches(height)
    blank_layout = prs.slide_layouts[6]

    for index, slide_info in enumerate(manifest["slides"], start=1):
        if not isinstance(slide_info, dict):
            raise ValueError(f"slide {index} is not an object")
        image_rel = slide_info.get("image")
        if not isinstance(image_rel, str) or not image_rel:
            raise ValueError(f"slide {index} missing image path")
        image_path = run_dir / image_rel
        if not image_path.exists():
            raise FileNotFoundError(f"slide {index} image not found: {image_rel}")
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(str(image_path), 0, 0, width=prs.slide_width, height=prs.slide_height)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package PPT Studio slide images into PPTX.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", default="review_manifest.json")
    parser.add_argument("--out", default="exports/presentation.pptx")
    parser.add_argument("--aspect-ratio", default=None, choices=["16:9", "4:3"])
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    manifest = load_manifest(run_dir / args.manifest)
    aspect_ratio = args.aspect_ratio or str(manifest.get("aspect_ratio", "16:9"))
    out_path = run_dir / args.out
    package(run_dir, manifest, out_path, aspect_ratio)

    delivery = {
        "run_id": manifest.get("run_id", run_dir.name),
        "pptx": str(out_path.relative_to(run_dir)),
        "review_html": "review/review.html",
        "slide_count": len(manifest["slides"]),
        "status": "draft",
    }
    (run_dir / "delivery_manifest.json").write_text(
        json.dumps(delivery, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "pptx": str(out_path), "slide_count": len(manifest["slides"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
