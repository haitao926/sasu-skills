# Text-Safe Generation

Use this reference when the deck needs readable Chinese or exact instructional text.

## Principle

PPT Studio should be Roil-first for visual quality and text-safe for readability:

- Roil draws atmosphere, illustration, character style, backgrounds, symbolic objects, texture, composition, and complete core information figures when the image itself carries the explanation.
- The default text-safe layer is native PowerPoint text boxes, so teachers or presenters can edit text later.
- A deterministic image overlay is allowed only for locked visual exports or when the user explicitly accepts non-editable text.
- Text handling must be planned, not hidden. Record it in `requirements.md`, `slide_blueprint.md`, and `spec_lock.md`.

This is different from a silent fallback. The visual system still comes from generated images; code only handles exact text and packaging.

## When To Use

Use text-safe mode by default for:

- Chinese education decks;
- class meetings, school events, and training materials;
- pages with activity rules or exact slogans;
- any slide where a typo would make the deck unusable.

Do not use text-safe mode to replace Roil with hard-coded illustrations.

## Roil Plate Prompt

Ask Roil for a visual plate with intentional blank text zones:

```text
Create a 16:9 presentation slide visual plate for <topic>.
Draw only the illustrated background, characters, decorative motifs, layout atmosphere, and blank content panels.
Leave clean blank areas for later Chinese text overlay:
- title zone: <position/size>
- body zone: <position/size>
- optional labels: <position/size>
Do not render Chinese text, English text, random letters, watermarks, UI chrome, or logos.
Style: <confirmed visual system>.
The result should look like a polished classroom presentation slide, with soft natural linework and coherent illustration style.
```

Use this only when the selected contract is `visual-layer + editable PPT labels`. If the selected contract is `core-information-figure + editable page context`, use the core figure prompt contract instead and do not leave the explanation to PPT labels alone.

## Text Layer Spec

Each slide in `slide_blueprint.md` should include:

```json
{
  "slide": 1,
  "visual_plate": "images/plates/slide-01.png",
  "text_blocks": [
    {
      "text": "快乐儿童节",
      "x": 0.5,
      "y": 0.22,
      "w": 0.55,
      "h": 0.12,
      "role": "title",
      "align": "center"
    }
  ]
}
```

Coordinates are normalized 0-1 relative to the slide.

## Text Layer Rules

- Use Chinese-capable local fonts.
- Prefer 1 title and 1-4 short blocks per slide.
- Keep text inside blank zones already reserved in the Roil plate.
- Use soft labels, paper strips, or translucent cards only if needed for readability.
- Do not cover faces, important illustrations, or visual focal points.
- Default output should use editable native PPT text boxes.
- Preserve original image assets in the final PPTX; do not silently recompress, re-encode, or downsample evidence images during packaging.
- Use `overlay_text_safe.py` only for non-editable preview images, visual proofs, or locked-image exports.

## Retouch Rules

- If the illustration feels wrong, regenerate the Roil plate.
- If text has typo, poor position, or low contrast, adjust the native PPT text box by default.
- If text zones are not usable, regenerate the Roil plate with clearer blank zones.
