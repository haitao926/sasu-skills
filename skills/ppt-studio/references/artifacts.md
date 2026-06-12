# PPT Studio Artifacts

All artifacts live under:

```text
ppt-output/runs/<RUN_ID>/
```

Recommended layout:

```text
briefs/
planning/
previews/
images/
review/
exports/
```

## Required Artifacts

`requirements.md`

The locked user brief. Include topic, goal, audience, page count, aspect ratio, branch, review strictness, confirmation mode, checkpoint plan, source materials, visual constraints, assumptions, and confirmation status.

`content_report.md`

The content basis for the deck. For thin topics, this is the expanded narrative basis. For source decks, it is a normalized digest. For research decks, it is the synthesized story basis.

`research_brief.md` or `source_brief.md`

Research branch uses `research_brief.md` with sources, source summaries, and claim boundaries. Source and thin-topic branches use `source_brief.md`.

`outline.md`

Slide-by-slide narrative sequence. Each slide needs title, job, core message, and content notes.

`page_logic.md` or `slide_blueprint.md` page-logic section

Slide-level logic gate before template matching, Roil prompting, or image placement. Each slide should include `slide_claim`, `audience_takeaway`, `main_line`, `content_job`, `evidence_needed`, `visual_carrier`, and `editable_text_policy`.

`deck_strategy.md`

The strategy gate before visual style and page generation. It decides whether the deck should be image-first, structure-first, academic, corporate, technical, courseware, story-driven, or mixed. Required sections:

- deck diagnosis: scenario, audience, stakes, density, and whether the deck is primarily argument, evidence, story, teaching, sales, or demo;
- background/template system: selected background approach and template family, with 1-2 rejected alternatives;
- structure map: slide -> layout job -> reason;
- image plan: slide -> image role -> source or generation method -> why the image is needed;
- text plan: slide -> text role -> maximum density;
- figure-text contract: how images and text divide labor, especially for evidence-heavy slides;
- export lane: editable PPTX, Roil plates plus editable text, HTML-backed, html-guizang, or locked images.

Do not generate final slides if this file is missing.

`template_candidates.md`

Concrete template choice gate. Must be written before `style_options.md`. Include 2-4 candidate templates with `template_id`, `template_profile_path`, fit reason, reusable framework examples, risks, rejected alternatives, and the question shown to the user for `模板候选确认`.

Do not generate style previews or final slides if this file is missing for template-backed work.

`template_selection.json`

Records the user-confirmed or explicitly agent-chosen template. Include selected `template_id`, `template_profile_path`, confirmation status, rejected alternatives, and the reason for final selection. This file must exist before `slide_framework.json` for template-backed decks.

`template_fidelity.md`

Template fidelity gate after confirmed template selection. Include selected `template_id`, original PPTX path, profile JSON path, real template preview/adapted sample paths, source framework IDs to preserve, slot/layout elements to keep, content to replace, and fidelity risks. If a preview is hand-drawn or not template-derived, label it as a non-template sketch.

Do not generate final slides if this file is missing for template-backed work.

`style_options.md`

The proposed visual directions and preview image paths. Must include enough information for the user to choose a direction from actual previews.

`design_spec.md`

The confirmed deck-wide visual system and rationale.

`slide_blueprint.md`

Page-by-page production plan. Each slide should include visible text, layout intent, page logic, data/diagram needs, image role, visual carrier, visual plate prompt notes, and editable text box planning.

`slide_framework.json` (recommended for template-backed decks)

Machine-readable page framework map. Each slide should include `framework_id`, `layout_job`, `primary_carrier`, image roles, text roles, and slot mapping to the selected template profile.

`template_selection.json` (required for template-backed decks)

Records the selected `template_id`, `template_profile_path`, rejected alternatives, and why the template was chosen. This is the fast lookup layer for later reuse.

`spec_lock.md`

Final generation guardrails. Include aspect ratio, style invariants, typography direction, color direction, forbidden elements, and retouch rules.

`checkpoint_log.md` (optional, recommended)

Concise record of staged confirmations and user decisions. Useful when the deck is generated in batches or when the user asks to review progress between sections.

`editable_text_spec.json`

JSON spec for packaging Roil plates with native editable PPT text boxes. Use normalized 0-1 coordinates.

Minimal shape:

```json
{
  "slides": [
    {
      "visual_plate": "images/plates/slide-01.png",
      "text_blocks": [
        {
          "text": "快乐儿童节",
          "x": 0.25,
          "y": 0.30,
          "w": 0.50,
          "h": 0.12,
          "role": "title",
          "align": "center",
          "color": "#F05A4F"
        }
      ]
    }
  ]
}
```

`review_manifest.json`

JSON manifest for generated final slide images and review status. Required for locked-image preview/review flows and image QA. Editable exports may still create final preview images for review, but the delivered PPT should keep text editable by default.

Minimal shape:

```json
{
  "run_id": "20260530-140000-topic",
  "aspect_ratio": "16:9",
  "slides": [
    {
      "number": 1,
      "title": "Cover",
      "image": "images/slide-01.png",
      "status": "pending",
      "notes": ""
    }
  ]
}
```

`delivery_manifest.json`

JSON manifest for final outputs.

Minimal shape:

```json
{
  "run_id": "20260530-140000-topic",
  "pptx": "exports/presentation-editable.pptx",
  "review_html": "review/review.html",
  "slide_count": 1,
  "status": "draft"
}
```

## Validation

Use `scripts/validate_artifacts.py`:

```bash
python3 /Users/apple/.codex/skills/ppt-studio/scripts/validate_artifacts.py \
  --run-dir ppt-output/runs/<RUN_ID> \
  --stage planning
```

Stages:

- `requirements`
- `content`
- `planning`
- `review`
- `delivery`
- `all`

Validation confirms required files exist, markdown files are non-empty, JSON files parse, and referenced slide images exist for review/delivery stages.
