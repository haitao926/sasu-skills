# Template Fidelity

Use this after `模板候选确认` and before `风格确认`.

Core rule: confirmed PPTX templates are reusable production frameworks, not mood references.

## Fidelity Gate

After a template is confirmed, create `template_fidelity.md` with:

- selected `template_id`;
- original PPTX path;
- profile JSON path;
- real template preview path, or a clear note if rendering is unavailable;
- 3-5 reusable source slide/framework IDs;
- what will be preserved: grid, image slots, title zones, typography direction, colors, decorations;
- what will be replaced: source text, stock photos, domain-specific placeholders;
- fidelity risk: where adaptation may drift from the original template.

Do not proceed to style previews or page generation until this gate exists.

## Real Preview Requirement

For a confirmed PPTX template, show one of these before generating custom pages:

- real rendered template screenshots;
- a real PPTX-derived thumbnail;
- or a template-adapted sample created by modifying/copying the original PPTX framework.

Do not use hand-drawn PNG, HTML, PIL, SVG, or generic layout mockups as "template previews" unless explicitly labeled as non-template style sketches.

## Source Framework Reuse

When adapting a template page:

- start from a real source slide or a profile framework whose slot positions came from the PPTX;
- preserve the original dominant structure: image side, title side, diagram area, card rhythm, chapter marker, or decorative system;
- keep the source template's visual grammar unless the user asks to redesign;
- replace content inside slots instead of inventing a new layout with the same name.

If exact PPTX editing is unavailable, say so and create a best-effort adaptation, but do not claim it is a faithful template reuse.

## Rejection Rules

Reject or redo a preview if:

- it does not visually resemble the confirmed template;
- it only copies the template's topic category while changing the layout system;
- it ignores source slide image/text slot proportions;
- it uses a different color/typography system without user approval;
- it was rendered from scratch but described as template-derived.
