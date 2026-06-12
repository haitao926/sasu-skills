#!/usr/bin/env python3
"""Build per-template and per-slide framework profiles for PPT Studio.

The tag index answers "which template family should I use?".
This script answers "what page frameworks does that template already contain?"

It parses each PPTX template in the local template library and emits:

- one JSON profile per template under `assets/template-library/profiles/`
- one aggregate frame index at `assets/template-library/template-library-frame-index.json`
- one markdown summary at `assets/template-library/template-library-frame-index.md`

The generated JSON is intended to be read by the PPT workflow when selecting
templates and when writing run-level PPT metadata JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template-library"
TAG_INDEX_PATH = TEMPLATE_ROOT / "template-library-tag-index.json"
PROFILE_DIR = TEMPLATE_ROOT / "profiles"
FRAME_INDEX_JSON = TEMPLATE_ROOT / "template-library-frame-index.json"
FRAME_INDEX_MD = TEMPLATE_ROOT / "template-library-frame-index.md"

EMU_PER_INCH = 914400
DEFAULT_WIDTH = 13.333
DEFAULT_HEIGHT = 7.5
PPT_NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def safe_slug(value: str) -> str:
    value = normalize_text(value)
    value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-_")
    return value or "template"


def short_hash(value: str, length: int = 8) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def normalize_relpath(relpath: str) -> str:
    return str(Path(relpath).as_posix())


def template_id_for(item: dict[str, Any]) -> str:
    rel = normalize_relpath(str(item.get("path", "")))
    stem = Path(rel).stem
    return f"{safe_slug(stem)}-{short_hash(rel)}"


def xml_text(shape) -> str:
    try:
        if not getattr(shape, "has_text_frame", False):
            return ""
        text = normalize_text(shape.text or "")
        return text
    except Exception:
        return ""


def bbox(shape, slide_w: float, slide_h: float) -> dict[str, float] | None:
    try:
        left = float(shape.left) / EMU_PER_INCH
        top = float(shape.top) / EMU_PER_INCH
        width = float(shape.width) / EMU_PER_INCH
        height = float(shape.height) / EMU_PER_INCH
    except Exception:
        return None
    if width <= 0 or height <= 0:
        return None
    return {
        "x": round(left / slide_w, 4),
        "y": round(top / slide_h, 4),
        "w": round(width / slide_w, 4),
        "h": round(height / slide_h, 4),
    }


def bbox_area(box: dict[str, float] | None) -> float:
    if not box:
        return 0.0
    return max(0.0, box["w"]) * max(0.0, box["h"])


def emu_to_inches(value: int | float | None) -> float | None:
    if value is None:
        return None
    return round(float(value) / EMU_PER_INCH, 4)


def pt_value(value: Any) -> float | None:
    if value is None:
        return None
    pt = getattr(value, "pt", None)
    if pt is not None:
        return round(float(pt), 2)
    if isinstance(value, (int, float)):
        return round(float(value), 3)
    return None


def dominant_string(values: list[str]) -> str | None:
    items = [value for value in values if value]
    if not items:
        return None
    return Counter(items).most_common(1)[0][0]


def dominant_bool(values: list[bool]) -> bool | None:
    items = [value for value in values if value is not None]
    if not items:
        return None
    return Counter(items).most_common(1)[0][0]


def median_number(values: list[float], digits: int = 3) -> float | None:
    items = [float(value) for value in values if value is not None]
    if not items:
        return None
    return round(float(median(items)), digits)


def align_name(value: Any) -> str | None:
    if value == PP_ALIGN.CENTER:
        return "center"
    if value == PP_ALIGN.RIGHT:
        return "right"
    if value == PP_ALIGN.LEFT:
        return "left"
    return None


def anchor_name(value: Any) -> str | None:
    if value == MSO_ANCHOR.TOP:
        return "top"
    if value == MSO_ANCHOR.MIDDLE:
        return "middle"
    if value == MSO_ANCHOR.BOTTOM:
        return "bottom"
    return None


def theme_fonts_for(pptx_path: Path) -> dict[str, str]:
    fonts = {
        "major_latin": "",
        "minor_latin": "",
        "major_east_asian": "",
        "minor_east_asian": "",
        "major_complex_script": "",
        "minor_complex_script": "",
    }
    try:
        with ZipFile(pptx_path) as archive:
            xml = archive.read("ppt/theme/theme1.xml")
    except Exception:
        return fonts

    root = ET.fromstring(xml)
    mappings = {
        "major_latin": ".//a:themeElements/a:fontScheme/a:majorFont/a:latin",
        "minor_latin": ".//a:themeElements/a:fontScheme/a:minorFont/a:latin",
        "major_east_asian": ".//a:themeElements/a:fontScheme/a:majorFont/a:ea",
        "minor_east_asian": ".//a:themeElements/a:fontScheme/a:minorFont/a:ea",
        "major_complex_script": ".//a:themeElements/a:fontScheme/a:majorFont/a:cs",
        "minor_complex_script": ".//a:themeElements/a:fontScheme/a:minorFont/a:cs",
    }
    for key, xpath in mappings.items():
        node = root.find(xpath, PPT_NS)
        if node is not None:
            fonts[key] = (node.attrib.get("typeface") or "").strip()
    return fonts


def normalize_style(style: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in style.items() if value not in (None, "", [])}


def aggregate_text_styles(entries: list[dict[str, Any]], fallback_font: str) -> dict[str, dict[str, Any]]:
    by_role: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        role = str(entry.get("role", ""))
        style = entry.get("text_style")
        if role and isinstance(style, dict):
            by_role.setdefault(role, []).append(style)

    tokens: dict[str, dict[str, Any]] = {}
    for role, styles in by_role.items():
        token = normalize_style(
            {
                "font": dominant_string([str(style.get("font", "")) for style in styles]) or fallback_font,
                "font_size": median_number([style.get("font_size") for style in styles], digits=2),
                "bold": dominant_bool([style.get("bold") for style in styles]),
                "align": dominant_string([str(style.get("align", "")) for style in styles]),
                "line_spacing": median_number([style.get("line_spacing") for style in styles]),
                "space_before": median_number([style.get("space_before") for style in styles], digits=2),
                "space_after": median_number([style.get("space_after") for style in styles], digits=2),
                "margin_left": median_number([style.get("margin_left") for style in styles], digits=4),
                "margin_right": median_number([style.get("margin_right") for style in styles], digits=4),
                "margin_top": median_number([style.get("margin_top") for style in styles], digits=4),
                "margin_bottom": median_number([style.get("margin_bottom") for style in styles], digits=4),
                "vertical_anchor": dominant_string([str(style.get("vertical_anchor", "")) for style in styles]),
            }
        )
        tokens[role] = token
    return tokens


def shape_text_style(shape, text: str, fallback_font: str) -> dict[str, Any]:
    if not getattr(shape, "has_text_frame", False):
        return {}
    frame = shape.text_frame
    paragraph = frame.paragraphs[0] if frame.paragraphs else None
    run = paragraph.runs[0] if paragraph and paragraph.runs else None
    font = run.font if run else paragraph.font if paragraph else None
    preferred_font = getattr(font, "name", None) if font else None
    if not preferred_font:
        preferred_font = fallback_font

    style = normalize_style(
        {
            "font": preferred_font,
            "font_size": pt_value(getattr(font, "size", None)) if font else None,
            "bold": getattr(font, "bold", None) if font else None,
            "align": align_name(getattr(paragraph, "alignment", None)) if paragraph else None,
            "line_spacing": pt_value(getattr(paragraph, "line_spacing", None))
            if hasattr(getattr(paragraph, "line_spacing", None), "pt")
            else getattr(paragraph, "line_spacing", None)
            if paragraph
            else None,
            "space_before": pt_value(getattr(paragraph, "space_before", None)) if paragraph else None,
            "space_after": pt_value(getattr(paragraph, "space_after", None)) if paragraph else None,
            "margin_left": emu_to_inches(getattr(frame, "margin_left", None)),
            "margin_right": emu_to_inches(getattr(frame, "margin_right", None)),
            "margin_top": emu_to_inches(getattr(frame, "margin_top", None)),
            "margin_bottom": emu_to_inches(getattr(frame, "margin_bottom", None)),
            "vertical_anchor": anchor_name(getattr(frame, "vertical_anchor", None)),
        }
    )
    if text and re.search(r"[\u4e00-\u9fff]", text) and not style.get("font"):
        style["font"] = fallback_font
    return style


def box_center(box: dict[str, float] | None) -> tuple[float, float]:
    if not box:
        return (0.0, 0.0)
    return (box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)


def zone_for(box: dict[str, float] | None) -> str:
    if not box:
        return "unknown"
    cx, cy = box_center(box)
    hor = "left" if cx < 0.33 else "center" if cx < 0.66 else "right"
    ver = "top" if cy < 0.33 else "middle" if cy < 0.66 else "bottom"
    return f"{ver}-{hor}"


def text_role(text: str, box: dict[str, float] | None, slide_idx: int, total_slides: int) -> str:
    if not text:
        return "empty"
    area = bbox_area(box)
    y = box["y"] if box else 0.0
    h = box["h"] if box else 0.0
    if slide_idx == 1 and area >= 0.08:
        return "title"
    if y <= 0.14 and area >= 0.05 and len(text) <= 50:
        return "title"
    if any(k in text for k in ["目录", "Agenda", "CONTENTS", "Contents"]):
        return "section_label"
    if any(k in text for k in ["结论", "摘要", "摘要", "提示", "说明"]) and len(text) <= 40:
        return "claim"
    if y >= 0.83 or h <= 0.06:
        return "footer"
    if area <= 0.025 or len(text) <= 20:
        return "label"
    if any(k in text for k in ["问题", "目标", "方法", "结果", "技术路线", "平台介绍", "闭环", "框架", "流程"]):
        return "claim"
    return "body"


def image_role(area: float, box: dict[str, float] | None, category: str, slide_idx: int) -> str:
    if slide_idx == 1 and area >= 0.18:
        return "hero-atmosphere"
    if area >= 0.36:
        return "hero-evidence"
    if area >= 0.18:
        return "evidence"
    if area >= 0.08:
        return "supporting-image"
    if any(k in category for k in ["科研", "毕业答辩", "商务风格", "工作汇报", "技术"]):
        return "evidence"
    return "supporting-image"


def shape_role(shape_type: str, area: float, text: str) -> str:
    if shape_type in {"line", "connector"}:
        return "connector"
    if area >= 0.82 and not text:
        return "background"
    if area >= 0.18:
        return "diagram-block"
    return "decorative-shape"


def classify_layout(metrics: dict[str, Any], profile: dict[str, Any]) -> str:
    slide_idx = metrics["slide_index"]
    total = metrics["total_slides"]
    text_blob = metrics["text_blob"]
    image_count = metrics["image_count"]
    image_area = metrics["image_area"]
    text_count = metrics["text_count"]
    chart_count = metrics["chart_count"]
    table_count = metrics["table_count"]
    connector_count = metrics["connector_count"]
    shape_count = metrics["shape_count"]
    title_like = metrics["title_like"]
    body_like = metrics["body_like"]

    if slide_idx == 1 or any(k in text_blob for k in ["封面", "Cover", "封页"]):
        return "cover-statement"
    if any(k in text_blob for k in ["目录", "Agenda", "Contents", "章节"]):
        return "toc"
    if slide_idx == total and text_count <= 5:
        return "closing-takeaway"
    if any(k in text_blob for k in ["限制", "局限", "后续", "未来", "不足"]):
        return "limitations-future"
    if any(k in text_blob for k in ["问题", "疑问", "研究问题", "RQ"]):
        return "research-question"
    if table_count:
        return "table"
    if chart_count and image_count <= 1:
        return "kpi-grid"
    if image_count >= 4:
        return "matrix-grid"
    if image_count == 3 and image_area >= 0.25:
        return "matrix-grid"
    if image_count == 2 and image_area >= 0.30:
        if any(k in text_blob for k in ["对比", "A/B", "左右", "before", "after"]):
            return "comparison"
        return "duo-compare"
    if image_count == 1 and image_area >= 0.30:
        return "image-hero"
    if any(k in text_blob for k in ["架构", "框架", "系统", "技术栈", "模块", "平台", "部署"]):
        if connector_count >= 2 or shape_count >= max(8, text_count + 4):
            return "architecture-diagram"
        return "claim-evidence"
    if any(k in text_blob for k in ["流程", "闭环", "路径", "步骤", "阶段", "路由", "pipeline"]):
        return "process-strip" if connector_count or shape_count >= 6 else "flow-diagram"
    if connector_count >= 3 or shape_count >= 10:
        return "process-strip" if text_count <= 8 else "flow-diagram"
    if text_count >= 10 and image_count == 0:
        return "table" if body_like >= title_like else "claim-evidence"
    if image_count and text_count <= 4:
        return "claim-evidence"
    return "two-column" if image_count else "claim-evidence"


def area_signature(slots: list[dict[str, Any]]) -> str:
    if not slots:
        return "empty"
    zones = Counter(slot["zone"] for slot in slots)
    dominant = ",".join(f"{zone}:{count}" for zone, count in zones.most_common(3))
    return dominant


def framework_signature(slots: list[dict[str, Any]]) -> str:
    if not slots:
        return "empty"
    image_slots = [slot for slot in slots if slot["role"].startswith("image")]
    text_slots = [slot for slot in slots if slot["role"] in {"title", "body", "claim", "label", "section_label"}]
    if image_slots and text_slots:
        left_text = sum(1 for slot in text_slots if slot["zone"].endswith("left"))
        right_text = sum(1 for slot in text_slots if slot["zone"].endswith("right"))
        left_img = sum(1 for slot in image_slots if slot["zone"].endswith("left"))
        right_img = sum(1 for slot in image_slots if slot["zone"].endswith("right"))
        if left_text > right_text and right_img >= left_img:
            return "left-text_right-visual"
        if right_text > left_text and left_img >= right_img:
            return "right-text_left-visual"
    if len(image_slots) >= 3:
        return "multi-image-grid"
    if len(text_slots) >= 6 and not image_slots:
        return "text-led"
    if len(image_slots) == 1:
        return "single-hero"
    return "mixed"


def primary_carrier(metrics: dict[str, Any]) -> str:
    if metrics["table_count"]:
        return "table"
    if metrics["chart_count"]:
        return "chart"
    if metrics["image_count"] >= 2 and metrics["image_area"] >= 0.25:
        return "image"
    if metrics["connector_count"] >= 2 or metrics["shape_count"] >= 8:
        return "diagram-shapes"
    if metrics["text_count"] >= 8 and metrics["image_count"] == 0:
        return "text"
    if metrics["image_count"] == 1:
        return "image"
    return "mixed"


def slide_density(metrics: dict[str, Any]) -> str:
    score = metrics["text_count"] + metrics["shape_count"] / 2 + metrics["image_count"] * 2
    if score >= 22:
        return "high"
    if score >= 12:
        return "medium-high"
    if score >= 6:
        return "medium"
    return "low"


def parse_slide(
    slide,
    slide_index: int,
    total_slides: int,
    profile: dict[str, Any],
    slide_w: float,
    slide_h: float,
    fallback_font: str,
) -> dict[str, Any]:
    objects: list[dict[str, Any]] = []
    text_entries: list[dict[str, Any]] = []
    image_entries: list[dict[str, Any]] = []
    chart_entries: list[dict[str, Any]] = []
    table_entries: list[dict[str, Any]] = []
    shape_entries: list[dict[str, Any]] = []
    connector_entries: list[dict[str, Any]] = []

    def walk(shapes):
        for shape in shapes:
            if getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.GROUP:
                try:
                    walk(shape.shapes)
                except Exception:
                    pass
                continue

            box = bbox(shape, slide_w, slide_h)
            text = xml_text(shape)
            shape_type = getattr(getattr(shape, "shape_type", None), "name", None) or str(getattr(shape, "shape_type", "unknown"))
            shape_type = shape_type.lower()
            has_image = getattr(shape, "shape_type", None) == MSO_SHAPE_TYPE.PICTURE
            has_table = bool(getattr(shape, "has_table", False))
            has_chart = bool(getattr(shape, "has_chart", False))
            is_placeholder = bool(getattr(shape, "is_placeholder", False))
            role = "shape"
            if has_table:
                role = "table"
            elif has_chart:
                role = "chart"
            elif has_image:
                role = "image"
            elif shape_type in {"line", "connector"}:
                role = "connector"
            elif text:
                role = text_role(text, box, slide_index, total_slides)
            else:
                role = shape_role(shape_type, bbox_area(box), text)
            text_style = shape_text_style(shape, text, fallback_font) if text else {}

            entry = {
                "name": getattr(shape, "name", ""),
                "shape_type": shape_type,
                "role": role,
                "text": text[:200],
                "text_style": text_style,
                "is_placeholder": is_placeholder,
                "box": box,
                "area": round(bbox_area(box), 4),
                "zone": zone_for(box),
            }
            objects.append(entry)
            if role in {"title", "body", "claim", "label", "section_label", "footer"} and text:
                text_entries.append(entry)
            if role == "image":
                image_entries.append(entry)
            if role == "table":
                table_entries.append(entry)
            if role == "chart":
                chart_entries.append(entry)
            if role == "connector":
                connector_entries.append(entry)
            if role == "background" or role == "diagram-block" or role == "decorative-shape":
                shape_entries.append(entry)

    try:
        walk(slide.shapes)
    except Exception as exc:
        raise RuntimeError(f"failed to parse slide {slide_index}: {exc}") from exc

    text_blob = " ".join(entry["text"] for entry in text_entries)
    title_like = sum(1 for entry in text_entries if entry["role"] in {"title", "section_label"})
    body_like = sum(1 for entry in text_entries if entry["role"] in {"body", "claim"})
    text_area = round(sum(entry["area"] for entry in text_entries), 4)
    image_area = round(sum(entry["area"] for entry in image_entries), 4)
    shape_area = round(sum(entry["area"] for entry in shape_entries), 4)
    slots = sorted(
        [
            {
                "index": i + 1,
                "name": entry["name"],
                "role": entry["role"] if entry["role"] != "shape" else "diagram-block",
                "zone": entry["zone"],
                "box": entry["box"],
                "area": entry["area"],
                "text": entry["text"][:120],
                "editable": entry["role"] in {"title", "body", "claim", "label", "section_label", "footer"},
                "text_style": entry["text_style"],
            }
            for i, entry in enumerate(
                sorted(
                    [e for e in objects if e["role"] not in {"background"}],
                    key=lambda e: e["area"],
                    reverse=True,
                )[:10]
            )
        ],
        key=lambda slot: slot["index"],
    )

    metrics = {
        "slide_index": slide_index,
        "total_slides": total_slides,
        "text_count": len(text_entries),
        "image_count": len(image_entries),
        "chart_count": len(chart_entries),
        "table_count": len(table_entries),
        "shape_count": len(shape_entries),
        "connector_count": len(connector_entries),
        "text_area": text_area,
        "image_area": image_area,
        "shape_area": shape_area,
        "text_blob": text_blob,
        "title_like": title_like,
        "body_like": body_like,
    }
    layout_job = classify_layout(metrics, profile)
    carrier = primary_carrier(metrics)
    density = slide_density(metrics)
    signature = framework_signature(slots)
    signature_area = area_signature(slots)
    title_guess = next((entry["text"] for entry in text_entries if entry["role"] in {"title", "section_label"}), "")
    if not title_guess and text_entries:
        title_guess = text_entries[0]["text"]
    if len(title_guess) > 50:
        title_guess = title_guess[:50]
    text_style_tokens = aggregate_text_styles(text_entries, fallback_font)

    return {
        "slide_index": slide_index,
        "slide_id": f"{slide_index:02d}",
        "title_guess": title_guess,
        "layout_job": layout_job,
        "primary_carrier": carrier,
        "density": density,
        "framework_signature": signature,
        "area_signature": signature_area,
        "metrics": metrics,
        "slots": slots,
        "counts": {
            "text": len(text_entries),
            "image": len(image_entries),
            "chart": len(chart_entries),
            "table": len(table_entries),
            "shape": len(shape_entries),
            "connector": len(connector_entries),
        },
        "content_roles": {
            "text": Counter(entry["role"] for entry in text_entries),
            "image": Counter(entry["role"] for entry in image_entries),
        },
        "text_style_tokens": text_style_tokens,
        "recommendations": {
            "preferred_for": [],
            "avoid_for": [],
        },
    }


def build_profile(item: dict[str, Any], tag_item: dict[str, Any], out_path: Path) -> dict[str, Any]:
    rel_path = normalize_relpath(str(item["path"]))
    pptx_path = SKILL_ROOT / rel_path
    if not pptx_path.exists():
        raise FileNotFoundError(f"template not found: {pptx_path}")

    prs = Presentation(str(pptx_path))
    slide_w = float(prs.slide_width) / EMU_PER_INCH if prs.slide_width else DEFAULT_WIDTH
    slide_h = float(prs.slide_height) / EMU_PER_INCH if prs.slide_height else DEFAULT_HEIGHT
    slide_count = len(prs.slides)
    theme_fonts = theme_fonts_for(pptx_path)
    default_cjk_font = (
        theme_fonts.get("minor_east_asian")
        or theme_fonts.get("major_east_asian")
        or theme_fonts.get("minor_latin")
        or theme_fonts.get("major_latin")
        or "微软雅黑"
    )

    slides: list[dict[str, Any]] = []
    for index, slide in enumerate(prs.slides, start=1):
        slides.append(parse_slide(slide, index, slide_count, tag_item["profile"], slide_w, slide_h, default_cjk_font))

    layout_counts = Counter(slide["layout_job"] for slide in slides)
    carrier_counts = Counter(slide["primary_carrier"] for slide in slides)
    density_counts = Counter(slide["density"] for slide in slides)
    dominant_layouts = [name for name, _ in layout_counts.most_common(5)]
    dominant_carriers = [name for name, _ in carrier_counts.most_common(3)]
    dominant_densities = [name for name, _ in density_counts.most_common(3)]
    common_slot_roles = Counter()
    common_zones = Counter()
    deck_text_entries: list[dict[str, Any]] = []
    for slide in slides:
        for slot in slide["slots"]:
            common_slot_roles[slot["role"]] += 1
            common_zones[slot["zone"]] += 1
            if slot["editable"] and isinstance(slot.get("text_style"), dict):
                deck_text_entries.append({"role": slot["role"], "text_style": slot["text_style"]})

    template_id = template_id_for(item)
    profile_path = PROFILE_DIR / f"{template_id}.json"
    all_text = " ".join(slide["title_guess"] for slide in slides if slide["title_guess"])
    tag_profile = tag_item["profile"]

    profile = {
        "schema_version": "ppt-studio/template-profile-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "template_id": template_id,
        "template_profile_path": str(profile_path.relative_to(SKILL_ROOT)),
        "source_template": {
            "name": item.get("name"),
            "category": item.get("category"),
            "path": rel_path,
            "source": item.get("source"),
            "slide_count": item.get("slide_count"),
            "media_count": item.get("media_count"),
            "image_media_count": item.get("image_media_count"),
            "motion_hint": item.get("motion_hint"),
            "tags": item.get("tags", []),
        },
        "template_match": {
            "family": tag_profile.get("family", ""),
            "scenario": tag_profile.get("scenario", []),
            "best_for": tag_profile.get("best_for", []),
            "avoid": tag_profile.get("avoid", []),
            "recommended_page_jobs": tag_profile.get("recommended_page_jobs", []),
            "visual": tag_profile.get("visual", []),
            "image_strategy": tag_profile.get("image_strategy", []),
            "text_strategy": tag_profile.get("text_strategy", []),
            "density": tag_profile.get("density", ""),
        },
        "deck_frame": {
            "aspect_ratio": round(slide_w / slide_h, 4) if slide_h else 1.7778,
            "slide_size_in": {"w": round(slide_w, 3), "h": round(slide_h, 3)},
            "theme_fonts": theme_fonts,
            "default_text_font": default_cjk_font,
            "dominant_layout_jobs": dominant_layouts,
            "dominant_primary_carriers": dominant_carriers,
            "dominant_density": dominant_densities[0] if dominant_densities else "medium",
            "common_text_roles": [role for role, _ in common_slot_roles.most_common(6)],
            "common_zones": [zone for zone, _ in common_zones.most_common(6)],
            "template_text_signature": normalize_text(all_text)[:240],
            "text_style_tokens": aggregate_text_styles(deck_text_entries, default_cjk_font),
            "recommended_reuse_contract": [
                "保留模板的网格、页边距、标题区和证据区关系",
                "只替换模板里的占位内容、截图和图表数据，不破坏原始版式语言",
                "每页先复用模板框架，再在框架内重建编辑文本与证据图",
            ],
        },
        "slides": [
            {
                "slide_index": slide["slide_index"],
                "slide_id": slide["slide_id"],
                "framework_id": f"{template_id}-s{slide['slide_index']:02d}",
                "title_guess": slide["title_guess"],
                "layout_job": slide["layout_job"],
                "primary_carrier": slide["primary_carrier"],
                "density": slide["density"],
                "framework_signature": slide["framework_signature"],
                "area_signature": slide["area_signature"],
                "counts": slide["counts"],
                "metrics": slide["metrics"],
                "slots": slide["slots"],
                "content_roles": {
                    "text": {k: int(v) for k, v in slide["content_roles"]["text"].items()},
                    "image": {k: int(v) for k, v in slide["content_roles"]["image"].items()},
                },
                "text_style_tokens": slide["text_style_tokens"],
                "reusable_for": tag_profile.get("recommended_page_jobs", []),
                "avoid_for": tag_profile.get("avoid", []),
                "editable_text_policy": [
                    "标题、标签、说明句保留为可编辑文本",
                    "截图和照片保留原图，不压缩不转码",
                    "结构信息写入 JSON，便于后续快速定位同类页面",
                ],
            }
            for slide in slides
        ],
        "summary": {
            "slide_count": slide_count,
            "layout_job_counts": {k: int(v) for k, v in layout_counts.most_common()},
            "carrier_counts": {k: int(v) for k, v in carrier_counts.most_common()},
            "density_counts": {k: int(v) for k, v in density_counts.most_common()},
            "dominant_layout_jobs": dominant_layouts,
            "dominant_primary_carriers": dominant_carriers,
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return profile


def build_markdown(profiles: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# PPT Studio Template Frame Index")
    lines.append("")
    lines.append("- Generated: " + datetime.now(timezone.utc).isoformat())
    lines.append(f"- Template profiles: {len(profiles)}")
    lines.append("")
    lines.append("## Quick Match Rules")
    lines.append("")
    lines.append("- 先看 `template_match.family` 和 `deck_frame.dominant_layout_jobs`，再看每页 `framework_id`。")
    lines.append("- 科研、答辩、技术、报告类优先使用 `claim-evidence`、`architecture-diagram`、`process-strip`、`table`、`image-hero`。")
    lines.append("- 模板 JSON 里保留每页的 `layout_job`、`primary_carrier`、`slots` 和 `reusable_for`，方便快速定位可复用页面。")
    lines.append("")
    for profile in profiles:
        src = profile["source_template"]
        summary = profile["summary"]
        lines.append(f"## {src['name']}")
        lines.append("")
        lines.append(f"- template_id: `{profile['template_id']}`")
        lines.append(f"- profile_path: `{profile['template_profile_path']}`")
        lines.append(f"- category: `{src['category']}`")
        lines.append(f"- slide_count: `{summary['slide_count']}`")
        lines.append(f"- dominant_layout_jobs: {', '.join(summary['dominant_layout_jobs'])}")
        lines.append(f"- dominant_primary_carriers: {', '.join(summary['dominant_primary_carriers'])}")
        lines.append(f"- layout_job_counts: {json.dumps(summary['layout_job_counts'], ensure_ascii=False)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_frame_index(tag_index: dict[str, Any], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    profile_map = {profile["source_template"]["path"]: profile for profile in profiles}
    templates: list[dict[str, Any]] = []
    for item in tag_index.get("templates", []):
        if not isinstance(item, dict) or item.get("kind") != "pptx-template":
            continue
        rel = normalize_relpath(str(item.get("path", "")))
        profile = profile_map.get(rel)
        if not profile:
            continue
        enriched = dict(item)
        enriched["template_id"] = profile["template_id"]
        enriched["template_profile_path"] = profile["template_profile_path"]
        enriched["framework_summary"] = {
            "dominant_layout_jobs": profile["summary"]["dominant_layout_jobs"],
            "dominant_primary_carriers": profile["summary"]["dominant_primary_carriers"],
            "slide_count": profile["summary"]["slide_count"],
        }
        enriched["slide_frameworks"] = [
            {
                "slide_index": slide["slide_index"],
                "framework_id": slide["framework_id"],
                "layout_job": slide["layout_job"],
                "primary_carrier": slide["primary_carrier"],
                "density": slide["density"],
                "title_guess": slide["title_guess"],
                "framework_signature": slide["framework_signature"],
            }
            for slide in profile["slides"]
        ]
        templates.append(enriched)

    return {
        "schema_version": "ppt-studio/template-frame-index-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_tag_index": str(TAG_INDEX_PATH.relative_to(SKILL_ROOT)),
        "template_count": len(templates),
        "templates": templates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build PPT Studio template framework profiles.")
    parser.add_argument("--tag-index", default=str(TAG_INDEX_PATH))
    parser.add_argument("--profiles-dir", default=str(PROFILE_DIR))
    parser.add_argument("--out-json", default=str(FRAME_INDEX_JSON))
    parser.add_argument("--out-md", default=str(FRAME_INDEX_MD))
    parser.add_argument(
        "--template-path",
        help="Profile a single PPTX template path (absolute or relative to the skill root).",
    )
    parser.add_argument(
        "--template-name",
        help="Optional human-readable override for single-template profiling.",
    )
    args = parser.parse_args(argv)

    tag_index_path = Path(args.tag_index)
    if not tag_index_path.exists():
        raise FileNotFoundError(f"tag index not found: {tag_index_path}")
    tag_index = load_json(tag_index_path)

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    template_items = [
        item
        for item in tag_index.get("templates", [])
        if isinstance(item, dict) and item.get("kind") == "pptx-template"
    ]
    if not template_items:
        raise ValueError("tag index does not contain any PPTX templates")

    selected_items = template_items
    if args.template_path:
        requested = normalize_relpath(args.template_path)
        selected_items = [item for item in template_items if normalize_relpath(str(item.get("path", ""))) == requested]
        if not selected_items:
            raise ValueError(f"template not found in tag index: {requested}")

    profiles: list[dict[str, Any]] = []
    for item in selected_items:
        profile_id = template_id_for(item)
        out_path = PROFILE_DIR / f"{profile_id}.json"
        profile = build_profile(item, item, out_path)
        profiles.append(profile)

    if args.template_path:
        payload = profiles[0]
        print(
            json.dumps(
                {
                    "ok": True,
                    "template_id": payload["template_id"],
                    "profile": str((PROFILE_DIR / f"{payload['template_id']}.json").relative_to(SKILL_ROOT)),
                },
                ensure_ascii=False,
            )
        )
        return 0

    frame_index = build_frame_index(tag_index, profiles)
    Path(args.out_json).write_text(json.dumps(frame_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.out_md).write_text(build_markdown(profiles), encoding="utf-8")

    enriched_tag_index = dict(tag_index)
    enriched_templates: list[dict[str, Any]] = []
    profile_lookup = {profile["source_template"]["path"]: profile for profile in profiles}
    for item in template_items:
        rel = normalize_relpath(str(item.get("path", "")))
        profile = profile_lookup.get(rel)
        enriched = dict(item)
        if profile:
            enriched["template_id"] = profile["template_id"]
            enriched["template_profile_path"] = profile["template_profile_path"]
            enriched["framework_summary"] = {
                "dominant_layout_jobs": profile["summary"]["dominant_layout_jobs"],
                "dominant_primary_carriers": profile["summary"]["dominant_primary_carriers"],
                "slide_count": profile["summary"]["slide_count"],
            }
            enriched["slide_frameworks"] = [
                {
                    "slide_index": slide["slide_index"],
                    "framework_id": slide["framework_id"],
                    "layout_job": slide["layout_job"],
                    "primary_carrier": slide["primary_carrier"],
                    "density": slide["density"],
                    "title_guess": slide["title_guess"],
                    "framework_signature": slide["framework_signature"],
                }
                for slide in profile["slides"]
            ]
        enriched_templates.append(enriched)
    enriched_tag_index["templates"] = enriched_templates
    tag_index_path.write_text(json.dumps(enriched_tag_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "profiles": len(profiles),
                "json": str(Path(args.out_json).relative_to(SKILL_ROOT)),
                "md": str(Path(args.out_md).relative_to(SKILL_ROOT)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
