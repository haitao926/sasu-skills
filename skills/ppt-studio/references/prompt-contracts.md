# Prompt Contracts

Use these contracts before calling Roil. First declare the image role in `page_logic.md` or `slide_blueprint.md`. Prompts should be concrete enough to produce the selected visual carrier, not generic poster art.

## Global Constraints

- aspect ratio: 16:9 unless specified otherwise;
- state whether output is a complete slide preview, a `core-information-figure`, or a `visual-layer`;
- keep text short and legible;
- use topic-specific visual motifs;
- preserve brand/institution identity if provided;
- avoid watermarks, fake logos, QR codes, unreadable microtext, and random UI chrome.
- do not use a complete-slide prompt when the page only needs a figure block or visual layer.

## Role Selection

Choose one contract before prompting:

- `complete slide preview`: only for previewing deck-wide visual direction or explicitly locked-image pages.
- `core-information-figure`: for a complete mechanism, architecture, workflow, method, or value-chain figure that sits inside a structured slide.
- `visual-layer`: for atmosphere, background, icon language, or a text-safe illustrated plate; PPT-native text carries the meaning.
- `reference-redraw`: for redrawing a supplied visual reference.

## Preview Prompt Contract

Use one direction across three preview prompts: cover, agenda, body.

```text
Create a 16:9 complete presentation slide preview for a deck about: <topic>.
Audience and occasion: <audience/occasion>.
Visual direction: <direction name and thesis>.
Identity anchors: <brand/school/company/lab, if any>.
Slide type: <cover|agenda|body>.
Visible text: <short exact text>.
Content intent: <what this slide must communicate>.
Composition: <layout, hierarchy, focal area, density>.
Style constraints: <typography, color logic, motifs, do-not-use>.
The slide must look like part of a coherent deck system, not a standalone poster.
```

## Core Information Figure Prompt Contract

Use when the generated image itself must explain the main mechanism or workflow. Build the prompt from `page_logic.md`, `slide_blueprint.md`, and `spec_lock.md`.

```text
Create a presentation-ready information figure for insertion into a 16:9 slide.
What this figure explains: <one-sentence main line>.
Figure role: core-information-figure.
Fixed composition and reading order: <left-to-right / top-to-bottom / central engine with inputs and outputs>.
Required modules: <maximum 4-7 named modules>.
Exact allowed labels only: <short exact labels>.
Main visual flow: <arrows, loop, hierarchy, or causal chain>.
Result/output area: <what the viewer should see as the outcome>.
Visual system: <style lock summary>.
Do not add: extra modules, fake UI, random English, garbled text, decorative filler, watermarks, logos, QR codes, or unreadable microtext.
The main line must be understandable within 3 seconds and labels must remain readable when the figure occupies <slot size> of a projected slide.
```

## Visual Layer Prompt Contract

Use when PPT-native labels and text must remain editable.

```text
Create a presentation visual layer for insertion into a 16:9 slide.
Topic and visual intent: <topic and mood>.
Figure role: visual-layer.
Composition: <blank zones, icon language, scene, texture, non-text structure>.
Reserve clean PPT text zones: <positions and sizes>.
Do not render Chinese text, English text, random letters, UI chrome, watermarks, logos, or QR codes.
The layer must support editable PPT labels without competing with them.
```

## Locked Final Slide Prompt Contract

Use only when the user explicitly wants a non-editable complete slide image.

```text
Create a 16:9 complete presentation slide.
Deck topic: <topic>.
Slide intent: <single job of the slide>.
Visible text exactly: <short exact text>.
Composition: <layout, hierarchy, spacing, density>.
Accuracy constraints: <provided facts only>.
Do not include: watermarks, random logos, QR codes, unreadable microtext, extra claims, decorative filler.
```

## Text Budget

For core information figures:

- prefer 4-7 short labels;
- labels must be exact and spatially necessary;
- keep page title, conclusion, caption, and citation outside the image as editable PPT text;
- if labels are not readable at slide size, simplify or regenerate.

For visual layers with editable PPT text:

- cover: title, subtitle, optional date/identity;
- agenda: 3-6 section labels;
- body: title plus 2-4 short blocks, each under roughly 12 Chinese characters or 8 English words where possible;
- data slides: labels and values only; keep interpretation in the title or a single takeaway.

If the source requires long text, summarize it into slide text and preserve details in `content_report.md` or notes.

## Retouch Prompt Contract

```text
Revise the provided slide while preserving the confirmed visual system.
Keep unchanged: <elements>.
Change exactly: <text/layout/color/content corrections>.
Reason for change: <review issue>.
Do not add new claims, random icons, watermarks, or extra decorative elements.
```

If reference-image editing is unavailable, regenerate the slide from the updated final slide prompt and state that it is a full regeneration.
