# Page Logic And Image Roles

Use this before `deck_strategy.md`, `slide_blueprint.md`, Roil prompts, and export review.

Core rule: template controls framework, Roil controls core figures, PPT controls editable text and evidence.

## Page Logic Gate

Before layout, drawing, or template reuse, write this for every slide:

```yaml
slide:
title:
slide_claim:
audience_takeaway:
main_line:
content_job:
evidence_needed:
visual_carrier:
editable_text_policy:
template_framework_need:
```

If `main_line` cannot be written in one sentence, split the slide or simplify the argument. One slide should have one dominant claim.

## Structure Decision

Choose structure from the slide's job, not from decoration:

- `claim-evidence`: use when real screenshots/photos/documents prove a claim.
- `architecture-diagram`: use when system components and interfaces are the message.
- `flow-diagram`: use when sequence, causality, or closed-loop logic is the message.
- `process-steps`: use when the audience must remember stages.
- `comparison`: use when change, contrast, or options are the message.
- `image-hero`: use only when one visual evidence or scene can carry the page.

For template-backed work, map every slide to `template_id`, `template_profile_path`, and `framework_id`. Reuse the framework first; then replace content.

## Image Role Decision

Every image must be one of these roles:

- `evidence`: real screenshot/photo/document. It proves existence, usage, classroom reality, or source basis. Do not compress or redraw it.
- `core-information-figure`: generated or drawn figure that explains mechanism, architecture, workflow, method, or value chain. It can be a complete Roil image block.
- `visual-layer`: atmosphere, background, texture, or icon layer. PPT-native text carries the meaning.
- `diagram-support`: simple deterministic shapes, arrows, or icons that stay editable.
- `decorative-texture`: non-essential; remove if it competes with content.

Evidence images prove. Core information figures explain. Do not ask screenshots/photos to explain abstract platform logic.

## Roil Complete Figure Contract

Use a complete Roil information figure when the user asks for "Roil 画完整图", "图片本身信息更充实", "核心展示图", or when a page section needs a visually integrated mechanism/workflow explanation.

Call Roil directly:

```bash
python3 /Users/apple/.codex/skills/roil-drawing/scripts/roil_draw.py \
  --prompt "..." \
  --out "ppt-output/runs/<RUN_ID>/images/<figure-name>.png" \
  --json
```

Prompt requirements:

- state what the figure explains in one sentence;
- define fixed composition and reading order;
- list exact allowed labels if text is burned in;
- cap module count and label count;
- specify the main visual flow and the output/result area;
- forbid extra text, fake UI, garbled labels, and unrelated decoration;
- require readability at the final slide size.

Do not replace this with SVG, HTML, PIL, or PowerPoint shapes unless explicitly choosing a deterministic fallback and saying so in the artifact. If the chosen contract is `complete Roil information figure`, do not create a weak background image and overlay dense PPT labels afterward.

## Editable Text Policy

Default: slide title, conclusion sentence, body bullets, captions, page numbers, and citations remain editable PPT text.

Burn text into a generated image only when:

- the image itself is the selected `core-information-figure`;
- labels are few, exact, and must be spatially integrated into the figure;
- the final review confirms labels are accurate and readable.

If burned-in text is wrong, blurry, overlapped, or too small, regenerate the image or move the text back into PPT-native editable text.

## Density And Readability

Use these gates before review/export:

- The main line is understandable within 3 seconds.
- The viewer can tell what is evidence and what is explanation.
- Core figures are richer than empty decorative diagrams but not module inventories.
- No text overlaps image details or important screenshot regions.
- All figure labels are readable at projected slide size.
- Screenshots/photos keep original quality in delivery PPTX.

## Review Questions

Ask these before moving from sample slides to full production:

- Does the slide have one clear claim?
- Is the template framework helping the argument, or only adding decoration?
- Is each image doing the right job: evidence, core figure, visual layer, or support?
- If Roil was requested, was Roil actually used for the core figure?
- Are editable text and burned-in labels assigned deliberately?
