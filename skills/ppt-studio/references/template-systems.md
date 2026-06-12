# Template Systems

Use this reference when a deck needs a stronger template system than generic cards. These systems are adapted from the Guizang PPT skill and should be translated into the current output lane.

## Template Lanes

`editable-pptx`

- Default PPT Studio lane.
- Use PowerPoint-native text, shapes, lines, diagrams, and image panels.
- Borrow Guizang layout logic, but do not force every slide into a full-slide image.
- Best for reports, applications, teaching, business decks, and any deck that must remain editable.

`html-guizang`

- Use only when the user asks for a single-file HTML/web PPT, horizontal swipe deck, magazine deck, or strict Swiss web deck.
- Start from `assets/guizang/template-magazine.html` or `assets/guizang/template-swiss.html`.
- Keep `assets/guizang/NOTICE.md` and `assets/guizang/LICENSE` with any copied template package.

## Style Families From Guizang

`magazine-eink`

- Visual thesis: editorial magazine plus e-ink atmosphere.
- Use for: humanistic talks, industry observation, narrative keynote, culture/design topics, less formal personal presentations.
- PPTX translation: serif-like display titles where available, warm paper backgrounds, asymmetric image/text spreads, large quotes, chapter dividers, calm screenshot mats.
- Avoid: too many small cards, SaaS gradients, tech neon, dashboard density.
- Suggested palettes:
  - ink classic: `#0a0a0b`, paper `#f1efea`;
  - indigo porcelain: `#0a1f3d`, paper `#f1f3f5`;
  - forest ink: `#1a2e1f`, paper `#f5f1e8`;
  - kraft paper: `#2a1e13`, paper `#eedfc7`;
  - dune: `#1f1a14`, paper `#f0e6d2`.

`swiss-grid`

- Visual thesis: Swiss International Style, strict grid, high contrast, single accent color.
- Use for: AI/product/engineering decks, case applications, evidence-heavy reports, data summaries, launch/demo-day decks.
- PPTX translation: 12/16-column grid, left-top titles, very large thin numbers, straight hairlines, rectangular image evidence blocks, one accent color only.
- Avoid: gradients, shadows, rounded cards, centered body titles, mixed accent colors, decorative screenshots.
- Suggested palettes:
  - IKB: accent `#002FA7`, paper `#fafaf8`, ink `#0a0a0a`;
  - lemon: accent `#FFD500`, paper `#fafaf8`, ink `#0a0a0a`;
  - lemon green: accent `#C5E803`, paper `#fafaf8`, ink `#0a0a0a`;
  - safety orange: accent `#FF6B35`, paper `#fafaf8`, ink `#0a0a0a`.

`academic-report`

- Visual thesis: formal research report with a restrained journal/conference tone.
- Use for: academic reports, thesis/defense decks, teaching-research cases, policy-grounded education reports, and application reports that need rigor.
- PPTX translation: numbered sections, research-question page, literature/policy grounding page, method/design framework, evidence tables, cautious findings, limitations, and future work.
- Avoid: product-launch hero language, exaggerated value claims, large decorative typography, promotional slogans, unsupported causal claims.
- Suggested palettes:
  - journal blue: paper `#F8FAFC`, ink `#102033`, accent `#1F4E79`;
  - slate academic: paper `#F6F4EF`, ink `#1D2430`, accent `#5A6B7A`;
  - education green: paper `#F7FAF5`, ink `#1E2A22`, accent `#2E6F58`.

## PPTX Layout Translation Rules

Before generating a structured PPTX, write a short layout map:

```text
slide -> template family -> layout job -> image slot -> editable text blocks
```

Use at least five distinct layout jobs in decks over eight slides:

- `cover-statement`: oversized title, compact metadata, one strong visual or empty stage.
- `chapter-divider`: large section label plus one-line shift.
- `claim-evidence`: one dominant claim with one large screenshot/diagram.
- `image-hero`: top or side hero image, 2-3 editable evidence captions.
- `duo-compare`: two columns with a hard dividing rule.
- `kpi-ledger`: large numbers with short labels.
- `process-strip`: 4-6 steps on a strict axis.
- `matrix-grid`: 2x3 or 3x2 evidence grid with uniform image slots.
- `closing-takeaway`: one final sentence plus 3 actions or conclusions.
- `research-question`: one central question plus 2-3 subquestions.
- `literature-policy`: citations/policy anchors mapped to the deck's design response.
- `method-evidence`: implementation path plus evidence boundaries.
- `limitations-future`: cautious limitations and next research/improvement directions.

For report/case decks, prefer `claim-evidence`, `image-hero`, `process-strip`, and `kpi-ledger` over dense card grids.

For academic reports, prefer `research-question`, `literature-policy`, `method-evidence`, `claim-evidence`, and `limitations-future`. Keep claims conservative and label stage evidence clearly.

## Academic Report Rules For Editable PPTX

- Begin with a research/application framing, not a product slogan.
- Make the deck's logic explicit: problem -> literature/policy basis -> design goal -> system design -> implementation -> evidence -> limitations.
- Include source/citation numbers when the source material contains references. Do not invent new citations.
- Findings must be cautious when evidence is limited. Prefer “阶段性证据表明” over “显著提升”.
- Use tables and comparison matrices when they clarify evidence boundaries.
- Keep visual style restrained: light background, dark ink, one muted academic accent, thin rules, readable captions.
- Put long literature detail in notes or compact citation boxes, not in dense body paragraphs.

## Swiss Rules For Editable PPTX

- Body titles default to the top-left content axis; do not center them except on covers, dividers, and closing statement pages.
- Use one accent color per deck. If a second color is needed, use neutral gray, not another saturated accent.
- Keep images rectangular. Use no shadow and no rounded corners unless the source deck already requires them.
- White screenshots or diagrams should sit on paper/white, not inside gray cards.
- Large typography should be visually light; small labels should be heavier enough to read.
- Do not fill every page. Swiss rhythm needs white space and strong alignment.
- For single large screenshots, use a `21:9`, `16:10`, or `16:9` evidence slot and make it large enough to read.

## Magazine Rules For Editable PPTX

- Use one strong image or quote per page; avoid dashboard density.
- Alternate quiet paper pages with dark/ink chapter pages.
- Let title blocks breathe. Do not pack title, subtitle, bullets, and image all into the same corner.
- Use captions as editorial notes, not redundant descriptions.
- Use paper texture or screenshot mats only as support; do not let background effects compete with content.

## Screenshot Framing

Use `scripts/frame_screenshot.py` when a user screenshot or product image needs a clean template-compatible stage before insertion into PPTX.

Default mapping:

- `swiss-grid`: square corners, no shadow, plain/grid background, one accent.
- `magazine-eink`: subtle corners, editorial shadow, paper or low-contrast background.

Bundled background assets live under `assets/guizang/screenshot-backgrounds/`.

## HTML Guizang Lane

If the user explicitly asks for HTML/web PPT:

1. Copy one template into the run directory:
   - magazine: `assets/guizang/template-magazine.html`
   - Swiss: `assets/guizang/template-swiss.html`
2. Put images under `images/` next to `index.html`.
3. Replace template title placeholders.
4. For Swiss pages, every slide must declare a registered `data-layout`.
5. Validate Swiss HTML with:

```bash
node /Users/apple/.codex/skills/ppt-studio/assets/guizang/scripts/validate-swiss-deck.mjs index.html
```

Do not expose Guizang provenance inside generated slide content. Keep source notices in project files only.
