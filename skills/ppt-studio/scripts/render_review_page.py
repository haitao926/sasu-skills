#!/usr/bin/env python3
"""Render a local HTML review page for PPT Studio slide images."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import sys


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PPT Studio Review</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #161616;
      --muted: #666;
      --line: #d8d8d8;
      --paper: #f6f4ef;
      --panel: #ffffff;
      --accent: #2f6f62;
      --warn: #a33b20;
    }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
    }}
    header {{
      padding: 24px clamp(18px, 4vw, 48px);
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    h1 {{
      margin: 0;
      font-size: 22px;
      letter-spacing: 0;
    }}
    .meta {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
    }}
    main {{
      padding: 28px clamp(18px, 4vw, 48px) 48px;
      display: grid;
      gap: 24px;
    }}
    article {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .slide-head {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
    }}
    .slide-title {{
      font-weight: 700;
      font-size: 15px;
    }}
    .status {{
      color: var(--accent);
      font-size: 13px;
      white-space: nowrap;
    }}
    img {{
      display: block;
      width: 100%;
      height: auto;
      background: #eee;
    }}
    .notes {{
      padding: 12px 16px 16px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}
    .review-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, 360px);
      gap: 0;
      align-items: stretch;
    }}
    .review-side {{
      border-left: 1px solid var(--line);
      padding: 16px;
      background: #fbfaf7;
    }}
    .field {{
      margin-bottom: 14px;
    }}
    .label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .02em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    textarea {{
      box-sizing: border-box;
      width: 100%;
      min-height: 108px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      color: var(--ink);
      background: #fff;
      font: inherit;
      resize: vertical;
    }}
    .checks {{
      display: grid;
      gap: 8px;
      color: var(--ink);
      font-size: 14px;
    }}
    .checks label {{
      display: flex;
      gap: 8px;
      align-items: flex-start;
    }}
    .missing {{
      color: var(--warn);
      font-weight: 700;
    }}
    @media (max-width: 900px) {{
      .review-grid {{
        grid-template-columns: 1fr;
      }}
      .review-side {{
        border-left: 0;
        border-top: 1px solid var(--line);
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>PPT Studio Review</h1>
    <div class="meta">Run: {run_id} · Aspect: {aspect_ratio} · Slides: {slide_count} · Layout authority: editable PPTX</div>
  </header>
  <main>
    {slides}
  </main>
</body>
</html>
"""


def render_slide(run_dir: Path, slide: dict, index: int) -> str:
    number = html.escape(str(slide.get("number", index)))
    title = html.escape(str(slide.get("title", f"Slide {index}")))
    status = html.escape(str(slide.get("status", "pending")))
    notes = html.escape(str(slide.get("notes", "")))
    image = str(slide.get("image", ""))
    src = html.escape("../" + image if not image.startswith(("/", "file:", "http")) else image)
    missing_html = "" if (run_dir / image).exists() else '<span class="missing">Image missing:</span> '
    return f"""
    <article>
      <div class="slide-head">
        <div class="slide-title">Slide {number}: {title}</div>
        <div class="status">{status}</div>
      </div>
      <div class="review-grid">
        <div>
          <img src="{src}" alt="Slide {number}">
          <div class="notes">{missing_html}{notes}</div>
        </div>
        <aside class="review-side">
          <div class="field">
            <span class="label">QA checks</span>
            <div class="checks">
              <label><input type="checkbox"> Content is accurate</label>
              <label><input type="checkbox"> Text is legible</label>
              <label><input type="checkbox"> Layout is clean</label>
              <label><input type="checkbox"> Style matches deck</label>
            </div>
          </div>
          <div class="field">
            <label class="label" for="notes-{number}">Retouch notes</label>
            <textarea id="notes-{number}" placeholder="Write exact changes for this slide..."></textarea>
          </div>
        </aside>
      </div>
    </article>
    """


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render PPT Studio review HTML.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", default="review_manifest.json")
    parser.add_argument("--out", default="review/review.html")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    manifest_path = run_dir / args.manifest
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    slides = manifest.get("slides", [])
    if not isinstance(slides, list) or not slides:
        raise SystemExit("review manifest must contain a non-empty slides array")

    out_path = run_dir / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    slide_html = "\n".join(render_slide(run_dir, slide, index) for index, slide in enumerate(slides, start=1))
    page = HTML_TEMPLATE.format(
        run_id=html.escape(str(manifest.get("run_id", run_dir.name))),
        aspect_ratio=html.escape(str(manifest.get("aspect_ratio", "16:9"))),
        slide_count=len(slides),
        slides=slide_html,
    )
    out_path.write_text(page, encoding="utf-8")
    print(json.dumps({"ok": True, "review_html": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
