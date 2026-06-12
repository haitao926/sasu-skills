# Defaults

This file records the canonical PPT Studio v1 production defaults.

## Default Output

Default output is:

```text
Roil-drawn visual assets + editable native PowerPoint text boxes
```

Do not burn Chinese text into final slide images unless the user explicitly asks for a locked-image export.
If a slide only looks good when its text is rasterized, treat that as a design failure for the editable lane and redesign the text layer.
Do not compress, transcode, or downsample source images for delivery; preserve the original image bytes in the final PPTX and use layout scaling only.
For Chinese PPTX, make fonts WPS-safe: set East Asian font declarations (`a:ea`) and complex-script declarations (`a:cs`) in addition to Latin fonts. Do not rely on `font.name` alone.

## Default Confirmation Mode

Default confirmation mode is `staged`.

- show requirements before locking the brief;
- show content basis before final outline;
- show structure and style previews before blueprint lock;
- show representative sample slides before full generation;
- show section batches on long or high-stakes decks;
- do not skip final review before export.

## Default Tooling

- Generate visual plates with `roil-drawing`.
- Use `references/template-systems.md` when the deck needs a strong structural template language, especially report/case/product decks.
- Use `scripts/frame_screenshot.py` to stage screenshots or evidence images on Guizang-inspired backgrounds before placing them into PPTX.
- Package final PPTX with `scripts/package_editable_text_pptx.py`.
- Patch editable Chinese PPTX fonts with `scripts/patch_pptx_fonts.py` or equivalent OOXML handling before delivery.
- Use `scripts/overlay_text_safe.py` only for preview sheets, visual proofs, or locked-image exports.
- Use `scripts/package_image_pptx.py` only when exporting non-editable full-slide images.
- Keep preview/raster helper outputs separate from delivery assets so evidence images stay untouched in the final deck.

## Default Structure Policy

For reports, case applications, product explanations, teaching materials, and evidence-heavy decks:

- Start from a slide structure map before generating visuals.
- Write `page_logic.md` or a `page_logic` section in `slide_blueprint.md` before template matching. The logic must choose the slide claim, audience takeaway, main line, content job, evidence need, visual carrier, and editable text policy.
- Write `deck_strategy.md` before `style_options.md`. The strategy must choose deck type, background system, template family, layout vocabulary, image roles, text roles, figure-text contract, and export lane.
- Keep titles, claims, captions, diagrams, and body text editable.
- Use Roil for scenes, atmosphere, reference redraws, hero visuals, or complete core information figures.
- Use PPT-native shapes for hierarchy, evidence panels, process strips, comparison layouts, and KPI pages.
- Use a `complete Roil information figure + editable page context` contract when the main explanation belongs inside the image.
- Use a `visual layer + editable PPT labels` contract when the image is only supporting the text.
- Prefer Guizang-inspired `swiss-grid` for AI/product/engineering decks and `magazine-eink` for narrative/editorial decks.

## Default Figure-Text Policy

- Images should usually be evidence, diagrams, screenshots, atmosphere, or reference redraws. Do not insert a picture just because a slide feels empty.
- Text should usually be claims, interpretation, captions, labels, citations, or speaker notes. Do not repeat exactly what the image already says.
- If the user asks for a richer Roil figure or says the picture itself should contain more information, use a core-information-figure contract and keep PPT text outside the image.
- For academic/report decks, use “claim + evidence + boundary” as the default composition.
- For teaching decks, use “instruction + example + practice cue” as the default composition.
- For story/campus/festival decks, use “Roil scene + short editable title + activity cue” as the default composition.
- For product/technical decks, use “architecture/process/screenshot + concise labels + implication” as the default composition.

## Default Children/Campus/Festival Style

For children, campus, festival, classroom, and activity decks:

- Roil must generate the main visual atmosphere.
- Code must not draw the main illustration.
- Ask Roil for blank text zones.
- Put Chinese text in native PPT text boxes.
- Keep text short and editable.
- Read `references/teaching-courseware.md`; generated images support classroom atmosphere/material context, while exact concepts and labels should remain editable unless a reviewed core-information figure is explicitly chosen.
