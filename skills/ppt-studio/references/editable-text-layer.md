# Editable Text Layer

Use this reference for the default PPT Studio export mode.

## Principle

Each final slide should be:

```text
Roil-generated visual asset where appropriate
+ editable native PowerPoint text boxes
```

This preserves Roil's visual quality while allowing teachers, presenters, and teams to edit Chinese text after delivery.

## When Required

Use editable text by default for:

- classroom and teaching PPTs;
- business reports and presentations;
- decks with Chinese text;
- slides likely to need last-minute wording changes.

Only burn text into images when the user explicitly asks for a locked visual version.
For complete core information figures, keep the page title, conclusion, and caption editable in PPT unless the user explicitly requests a fully locked visual.

## WPS-Safe Chinese Fonts

For Chinese PPTX, setting `font.name` is not enough. WPS may ignore it and fall back to 宋体 unless the OOXML run properties include East Asian font declarations.

Every editable text run should write:

```xml
<a:latin typeface="Aptos"/>
<a:ea typeface="PingFang SC"/>
<a:cs typeface="PingFang SC"/>
```

Use `PingFang SC` for macOS/WPS deliveries unless the user requests another installed font. For Windows-focused deliveries, `Microsoft YaHei` / `微软雅黑` is acceptable, but only if the target environment has it. Also patch theme major/minor fonts so fallback behavior stays consistent.

## Spec Shape

Use the same normalized coordinate fields as text-safe specs:

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

Coordinates are normalized 0-1 relative to the slide.

## Export

Use:

```bash
python3 /Users/apple/.codex/skills/ppt-studio/scripts/package_editable_text_pptx.py \
  --run-dir ppt-output/runs/<RUN_ID> \
  --spec text_layer_spec.json \
  --out exports/presentation-editable.pptx
```

## Rules

- Text boxes must not cover faces or important artwork.
- Titles should remain editable, not rasterized.
- Use local CJK-capable fonts where available, and write `a:ea` / `a:cs` declarations for WPS compatibility.
- Keep body text short; use speaker notes or source artifacts for long material.
- Preserve the original image file in the PPTX; do not recompress or resave images as part of the editable text packaging path.

If a PPTX was generated through a custom script or template-copy lane, run:

```bash
python3 /Users/apple/.codex/skills/ppt-studio/scripts/patch_pptx_fonts.py \
  exports/presentation-editable.pptx \
  --east-asia-font "PingFang SC" \
  --latin-font "Aptos"
```
