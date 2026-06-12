# Roil Integration

PPT Studio uses the existing `roil-drawing` skill as its visual generation layer. Do not copy Roil scripts or authentication logic into this skill.

## Command

Use this command shape:

```bash
python3 /Users/apple/.codex/skills/roil-drawing/scripts/roil_draw.py \
  --prompt "<image prompt>" \
  --out "<run-dir>/images/slide-01.png" \
  --json
```

For preview images, write to:

```text
<run-dir>/previews/<direction-code>-cover.png
<run-dir>/previews/<direction-code>-agenda.png
<run-dir>/previews/<direction-code>-body.png
```

For final images, write to:

```text
<run-dir>/images/slide-01.png
<run-dir>/images/slide-02.png
...
```

## Login Handoff

If the JSON result reports `needs_platform_login`, stop the drawing stage and say:

```text
请先登录 Roil 平台：https://image.roil.top/
```

Do not inspect auth files, keys, or environment variables unless the user explicitly asks for debugging.

## Prompt Construction

Before building a prompt, read `page_logic.md` or `slide_blueprint.md` and determine the image role:

- `core-information-figure`: Roil generates the complete mechanism/workflow figure.
- `visual-layer`: Roil generates atmosphere, texture, icons, or blank zones; PPT text carries exact meaning.
- `hero-atmosphere` or `reference-redraw`: Roil generates the visual asset according to the selected style.
- `evidence`: do not call Roil; preserve and place the original screenshot/photo/document.

A Roil prompt should contain only audience-facing content and visual direction:

- slide title only when it belongs in the generated asset;
- intended message;
- layout and visual hierarchy;
- style direction from `design_spec.md`;
- required diagrams, charts, or scene elements;
- aspect ratio, usually 16:9.

Keep operational labels out of the prompt body:

- no slide IDs;
- no filenames;
- no candidate codes;
- no internal batch labels.

Those belong in manifests, filenames, and review pages.

## Core Information Figure Pattern

Use this when the visual carrier is `core-information-figure`:

```text
Create a presentation-ready information figure for insertion into a 16:9 slide.
The figure explains: <one-sentence main line>.
Composition: <fixed reading order and structure>.
Modules: <4-7 exact modules>.
Allowed labels: <short exact labels only>.
Main flow: <arrows, loop, layered architecture, or causal chain>.
Output area: <result/report/evidence/outcome>.
Style: <confirmed visual system>.
No extra text, fake UI, random English, decorative filler, watermarks, logos, or QR codes.
Readable at final slide slot size.
```

Do not create a weak decorative background and rely on dense PPT overlays if this contract is selected.

## Visual Layer Pattern

Use this when the visual carrier is `visual-layer`:

```text
Create a presentation visual layer for a 16:9 slide.
Visual intent: <atmosphere/icon language/texture/non-text structure>.
Reserve blank zones: <title/body/label positions>.
Do not render Chinese text, English text, random letters, UI chrome, watermarks, logos, or QR codes.
```

## Preview Prompt Pattern

For each visual direction, generate:

- cover page preview;
- agenda or structure page preview;
- body/content page preview.

All three previews must use the same visual system so the user can judge deck-wide consistency.

## Retouch Prompt Pattern

When the user requests edits, create a concise prompt with:

- the current slide image as reference if the execution path supports references;
- the exact visible text changes;
- composition changes;
- what must remain unchanged;
- style lock reminders from `spec_lock.md`.

If reference editing is not available, regenerate the full slide image from the updated blueprint and note that it is a regeneration.
