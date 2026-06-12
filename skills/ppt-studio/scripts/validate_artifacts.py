#!/usr/bin/env python3
"""Validate PPT Studio run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


STAGE_REQUIREMENTS = {
    "requirements": ["requirements.md"],
    "content": ["requirements.md", "content_report.md"],
    "planning": [
        "requirements.md",
        "content_report.md",
        "outline.md",
        "deck_strategy.md",
        "template_candidates.md",
        "template_selection.json",
        "template_fidelity.md",
        "style_options.md",
        "design_spec.md",
        "slide_blueprint.md",
        "spec_lock.md",
    ],
    "review": ["review_manifest.json"],
    "delivery": ["delivery_manifest.json"],
}


def nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and bool(path.read_text(encoding="utf-8").strip())


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def text_contains_all(path: Path, markers: list[str]) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8").lower()
    return all(marker.lower() in text for marker in markers)


def validate_required(run_dir: Path, stage: str, errors: list[str]) -> None:
    for rel in STAGE_REQUIREMENTS[stage]:
        path = run_dir / rel
        if path.suffix == ".json":
            if not path.exists():
                errors.append(f"missing {rel}")
                continue
            try:
                load_json(path)
            except Exception as exc:  # noqa: BLE001 - surface concise validation errors.
                errors.append(f"invalid {rel}: {exc}")
        elif not nonempty(path):
            errors.append(f"missing or empty {rel}")


def validate_branch_brief(run_dir: Path, errors: list[str]) -> None:
    if not nonempty(run_dir / "research_brief.md") and not nonempty(run_dir / "source_brief.md"):
        errors.append("missing research_brief.md or source_brief.md")


def validate_page_logic(run_dir: Path, errors: list[str]) -> None:
    markers = [
        "slide_claim",
        "audience_takeaway",
        "main_line",
        "content_job",
        "evidence_needed",
        "visual_carrier",
        "editable_text_policy",
    ]
    if text_contains_all(run_dir / "page_logic.md", markers):
        return
    if text_contains_all(run_dir / "slide_blueprint.md", markers):
        return
    errors.append(
        "missing page logic: add page_logic.md or include "
        "slide_claim/audience_takeaway/main_line/content_job/"
        "evidence_needed/visual_carrier/editable_text_policy in slide_blueprint.md"
    )


def validate_review_manifest(run_dir: Path, errors: list[str]) -> None:
    manifest_path = run_dir / "review_manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return
    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("review_manifest.json must contain a non-empty slides array")
        return
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            errors.append(f"slide {index} in review_manifest.json is not an object")
            continue
        image = slide.get("image")
        if not isinstance(image, str) or not image:
            errors.append(f"slide {index} missing image path")
            continue
        if not (run_dir / image).exists():
            errors.append(f"slide {index} image not found: {image}")


def validate_delivery_manifest(run_dir: Path, errors: list[str]) -> None:
    manifest_path = run_dir / "delivery_manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return
    pptx = manifest.get("pptx")
    if not isinstance(pptx, str) or not pptx:
        errors.append("delivery_manifest.json missing pptx path")
    elif not (run_dir / pptx).exists():
        errors.append(f"pptx not found: {pptx}")


def stages_for(stage: str) -> list[str]:
    if stage == "all":
        return ["requirements", "content", "planning", "review", "delivery"]
    return [stage]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PPT Studio artifacts.")
    parser.add_argument("--run-dir", required=True, help="PPT Studio run directory")
    parser.add_argument(
        "--stage",
        choices=["requirements", "content", "planning", "review", "delivery", "all"],
        default="all",
    )
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    errors: list[str] = []
    if not run_dir.exists() or not run_dir.is_dir():
        errors.append(f"run directory not found: {run_dir}")
    else:
        for stage in stages_for(args.stage):
            validate_required(run_dir, stage, errors)
        if args.stage in {"content", "planning", "all"}:
            validate_branch_brief(run_dir, errors)
        if args.stage in {"planning", "all"}:
            validate_page_logic(run_dir, errors)
        if args.stage in {"review", "all"}:
            validate_review_manifest(run_dir, errors)
        if args.stage in {"delivery", "all"}:
            validate_delivery_manifest(run_dir, errors)

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
