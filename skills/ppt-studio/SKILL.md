---
name: ppt-studio
description: Create, redesign, beautify, review, or export PPT presentations, slide decks, pitch decks, reports-to-slides, 答辩稿, 汇报 PPT, 路演 deck, 产品介绍 PPT, 培训课件, or other multi-slide presentation materials. Use when Codex needs a structure-first presentation workflow with staged confirmations, template selection, Roil-generated visuals when appropriate, and editable PowerPoint text by default.
---

# PPT Studio

Use this skill as the default workflow for presentation production.

Default contract:
- build a deck, not isolated pages;
- keep PPT text editable by default;
- keep Chinese PPT text WPS-safe by writing East Asian font slots, not only `font.name`;
- decide slide logic and structure before visuals;
- decide explicitly whether each slide uses Roil, native PPT structure, or both;
- ask only for missing high-impact inputs before heavy work;
- show reviewable previews before batch export.

## User-Facing Behavior

Behave like a presentation partner, not a factory log.

- Ask for missing high-impact inputs in one compact turn.
- Do not narrate every internal artifact you are about to write.
- Report progress in plain language: what was decided, what is being produced now, and what review or decision is needed next.
- If earlier conversation already establishes topic, audience, duration, and source basis, treat those as confirmed and continue.
- Mention internal files only when the user asks for process detail or a stage is blocked.

## Modes

- `default`: normal presentation work.
- `fast`: small or urgent decks; still keep one compact confirmation, preview, sample slides, and review.
- `full`: high-stakes or research-heavy decks; read `references/workflow.md`.
- `html-backed`: only when the user explicitly wants HTML/web-PPT/intermediate HTML production; read `references/workflow.md` and `references/template-systems.md` first.

## Minimum Confirmation

Before creating templates, previews, or slides, confirm the minimum brief:
- presentation goal;
- audience;
- page count or time limit;
- source material or whether research is allowed.

If any of these are missing and materially affect the deck, ask directly in one short message.
If they are already known, summarize assumptions in one compact paragraph and proceed.

## Run Order

Follow this order. Do not skip confirmation gates silently.

1. Confirm the brief and missing constraints.
2. Decide the content basis: user material, research, or thin-topic synthesis.
3. Define the deck arc and one main line per slide.
4. Choose production strategy: template/background system, text strategy, image strategy, export lane, and Roil usage.
5. Show template/style previews before committing.
6. Build representative sample slides first.
7. Finish the deck, review it, and export only after approval or explicit draft request.

## Non-Negotiable Rules

- Structure first: decide deck type and slide jobs before generating visuals.
- One slide, one main line: every slide needs a clear claim and audience takeaway.
- Template first for structured decks: for reports, 答辩, cases, product decks, and evidence-heavy work, reuse PPT template frameworks before drawing from scratch.
- Preview first: do not ask the user to approve final style from text alone when previews are possible.
- Editable text by default: for Chinese teaching, business, and report decks, keep titles and body text in native PPT text boxes unless the user explicitly wants a locked-image deck.
- WPS-safe Chinese fonts: for editable Chinese PPTX, write `a:latin`, `a:ea`, and `a:cs` font declarations and patch theme fonts before delivery. Do not rely on `python-pptx` `font.name` alone.
- Evidence integrity: do not invent facts or silently compress delivery images.
- Role clarity: evidence images prove; core information figures explain; decorative images do neither.
- Teaching clarity: for classroom/courseware decks, visible text and images must support a student action such as look, judge, discuss, build, test, or summarize.
- Gate discipline: if a required stage artifact is missing or invalid, fix that stage before moving forward.

## Roil Decision

For each slide or slide type, classify it as `roil-required`, `roil-optional`, or `no-roil`.

Use Roil by default when a slide needs:
- hero atmosphere or thematic scene;
- custom illustration or character scene;
- screenshot/reference redraw;
- complete information figure, not just a decorative background;
- richer visual density than native PPT layout can reasonably provide.

Do not default to Roil when the slide is mainly:
- evidence screenshots, tables, charts, KPI panels, or text-led reporting;
- a template-reuse page where structure is the main value and native PPT elements are sufficient.

If a slide is `roil-required`, include at least one real Roil-generated sample before `样张确认`.
Do not silently downgrade a `roil-required` slide to PPT-native drawing without stating the fallback and reason.

Call the existing Roil toolchain. Do not duplicate Roil internals.

```bash
python3 /Users/apple/.codex/skills/roil-drawing/scripts/roil_draw.py \
  --prompt "..." \
  --out "ppt-output/runs/<RUN_ID>/images/slide-01.png" \
  --json
```

If Roil returns `needs_platform_login`, stop the drawing step and say only:
`请先登录 Roil 平台：https://image.roil.top/`

Keep slide IDs and batch labels out of the image prompt body.

## Artifacts And Scripts

Maintain a run directory:

```text
ppt-output/runs/<YYYYMMDD-HHMMSS-topic>/
```

Keep stage artifacts for:
- brief and assumptions;
- content basis;
- narrative and page logic;
- strategy, template choice, and Roil classification;
- previews and sample-slide review;
- export manifest.

Primary scripts:
- `scripts/validate_artifacts.py`: validate required files and JSON artifacts.
- `scripts/render_review_page.py`: build review HTML from generated outputs.
- `scripts/package_editable_text_pptx.py`: default PPTX export.
- `scripts/package_image_pptx.py`: locked-image export when explicitly requested.
- `scripts/patch_pptx_fonts.py`: patch existing PPTX files so Chinese text uses WPS-safe East Asian font declarations.
- `scripts/build_template_profiles.py`: rebuild template/page framework profiles.
- `scripts/frame_screenshot.py`: prepare screenshots for template image slots.

Run `scripts/validate_artifacts.py` before review/export. Also run `scripts/check_slide_images.py` when slide images exist. For editable Chinese PPTX, run or apply the equivalent of `scripts/patch_pptx_fonts.py` before delivery.

## Read References On Demand

Read only what the current job needs:
- `references/intake.md`: concise intake wording.
- `references/workflow.md`: full staged workflow and rollback rules.
- `references/artifacts.md`: artifact definitions and validation expectations.
- `references/checkpoints.md`: confirmation checkpoints and batching rules.
- `references/strategy-and-layouts.md`: deck diagnosis, layout vocabulary, and image/text role strategy.
- `references/page-logic-and-image-roles.md`: slide claim rules and image-role decisions.
- `references/template-systems.md`: when to use Guizang or template-driven structure.
- `references/template-fidelity.md`: real-template preview requirement.
- `references/style-directions.md`: non-generic style directions.
- `references/teaching-courseware.md`: classroom/courseware text, image-role, and student-action rules.
- `references/prompt-contracts.md`: preview, generation, and retouch prompt contracts.
- `references/text-safe-generation.md`: readable Chinese text handling around visuals.
- `references/editable-text-layer.md`: editable PPT text layer contract.
- `references/qa-checklist.md`: final review checklist.
- `references/defaults.md`: default export assumptions.
- `references/roil-integration.md`: Roil handoff details.

Template-library inputs:
- `assets/template-library/template-library-tag-index.md`: quick template browsing.
- `assets/template-library/template-library-tag-index.json`: tag-based template matching.
- `assets/template-library/template-library-frame-index.json`: aggregate framework index.
- `assets/template-library/profiles/*.json`: per-template framework and slot details.
