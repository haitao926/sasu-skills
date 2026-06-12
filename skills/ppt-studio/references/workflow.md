# PPT Studio Workflow

This reference defines the execution state machine for PPT Studio. Keep the front-stage conversation simple, but keep artifacts and gates strict.

## Modes

`default` is the normal mode. It runs the complete artifact chain but keeps user interaction light.

`fast` is for low-stakes decks under roughly 8 slides. It may compress content research and outline drafting, but must still create requirements, style previews, blueprint, review, and export artifacts.

`full` is for long, high-stakes, research-heavy, or audit-heavy decks. It uses the complete branch, artifact, validation, preview, review, and export sequence.

`html-backed` is an advanced lane for users who explicitly request HTML slide intermediates, stricter DOM/CSS QA, or SVG-like export. Do not choose it by default; Roil visual plates plus editable PPT text is the default product promise.

`html-guizang` is a specialized HTML-backed lane for users who explicitly request web PPT, horizontal swipe slides, magazine-style HTML decks, or strict Swiss Style HTML. Use `references/template-systems.md` and the bundled `assets/guizang/` templates.

## Confirmation Model

Default `confirmation_mode` is `staged`. PPT Studio should not silently generate the whole deck after intake. The user should see and approve the work at natural decision points:

- `需求确认`: requirements and assumptions;
- `资料/调研确认`: content basis and source boundaries;
- `结构确认`: outline, deck strategy, template family, layout map, image/text roles;
- `模板候选确认`: 2-4 concrete template candidates, fit reasons, risks, and reusable frameworks;
- `模板保真确认`: real template preview/adapted sample and what will be preserved or replaced;
- `风格确认`: real cover/agenda/body previews;
- `生成前确认`: design spec, slide blueprint, sample batch plan, export lane;
- `样张确认`: representative sample slides before full generation;
- `章节确认`: section or 4-6 slide batches for long/high-stakes decks;
- `成片审核通过`: final review before non-draft export.

Read `references/checkpoints.md` when deciding how many previews or batches to show.

## Stage Machine

1. `intake`
   Collect the minimum useful facts. Prefer concise synthesis over questionnaires.

2. `requirements-lock`
   Write `requirements.md` and ask for `需求确认`. Include assumptions, target audience, slide count, aspect ratio, branch, review strictness, confirmation mode, and planned checkpoints.

3. `branch`
   Choose one:
   - `research`: external facts, trends, market info, recent data, or public entities are needed.
   - `source`: the user supplied enough files/text to ground the deck.
   - `thin-topic`: only a topic exists and research is unavailable or not desired.

4. `content-brief`
   Write `content_report.md`. Also write `research_brief.md` for research branch or `source_brief.md` for source branch. For `thin-topic`, write `source_brief.md` with assumptions labeled. For normal/high-stakes work, show the content basis and ask for `资料/调研确认` before moving into final outline.

5. `outline`
   Write `outline.md` as a slide-by-slide narrative. It must map to target page count and include each slide's job.

6. `page-logic`
   Write `page_logic.md` or add a page-logic section to `slide_blueprint.md`. Before choosing a layout, template framework, screenshot, or generated image, declare for every slide:
   - `slide_claim`: the one statement the slide proves or explains;
   - `audience_takeaway`: what the audience should remember;
   - `main_line`: the one-sentence reading path;
   - `content_job`: claim-evidence, architecture, flow, process, comparison, image-hero, or another explicit job;
   - `evidence_needed`: real screenshots/photos/documents or none;
   - `visual_carrier`: evidence, core-information-figure, visual-layer, diagram-support, or no image;
   - `editable_text_policy`: what remains native PPT text and what may be burned into a complete figure.

   If the main line cannot be written in one sentence, split or simplify the slide. Read `page-logic-and-image-roles.md`. Do not move to template matching until this gate is complete.

7. `deck-strategy`
   Write `deck_strategy.md` before any style preview or page generation. This is the key diagnosis gate adapted from template-first HTML PPT workflows. It must decide:
   - scenario type: academic report, business report, product pitch, technical sharing, training/courseware, festival/campus, visual story, or mixed;
   - background system: plain paper, grid, dark stage, editorial paper, campus/illustrated scene, evidence board, or full-bleed visual;
   - template family: academic-paper, corporate-clean, Swiss grid, editorial/magazine, engineering whiteprint, visual-story, course-module, or custom hybrid;
   - layout vocabulary: cover, toc, section-divider, claim-evidence, two-column, three-column, image-hero, process-steps, timeline, roadmap, table, KPI grid, architecture diagram, flow diagram, comparison, quote, closing;
   - image strategy: which slides need no image, evidence images, screenshots, core information figures, visual layers, editable diagram support, Roil scenes, Roil redraws, charts, or decorative texture;
   - text strategy: which slides need claims, explanations, captions, citations, labels, notes, or speaker support;
   - export lane: editable PPTX, Roil plates + editable text, HTML-backed, html-guizang, or locked image export.

   Template family diagnosis is part of this stage, but concrete template selection has its own confirmation gate. Do not silently choose the final template here.

   Present `outline.md`, `page_logic.md`, and `deck_strategy.md` together for `结构确认`. If `deck_strategy.md` is missing, do not move to `template-candidates`.

8. `template-candidates`
   Use `assets/template-library/template-library-tag-index.json` to shortlist templates by scenario/family, then inspect `assets/template-library/template-library-frame-index.json` and candidate `assets/template-library/profiles/<template_id>.json` files to identify reusable page frameworks.

   Write `template_candidates.md` before choosing a template. Include 2-4 candidates. For each candidate, show:
   - `template_id` and profile path;
   - why it fits the deck scenario, audience, and density;
   - reusable framework examples for cover, structure page, body/evidence page, process/comparison page;
   - risks and what it would make worse;
   - what kind of Roil visual integration it supports.

   Ask for `模板候选确认`. Do not move to `style-preview`, `planning-lock`, or `page-generation` until the user confirms a candidate or explicitly asks the agent to choose.

9. `template-lock`
   After confirmation, write `template_selection.json` and record the selected `template_id`, `template_profile_path`, rejected alternatives, and selected per-slide framework approach. The detailed per-slide mapping can be finalized in `planning-lock`, but the selected template must be locked first.

10. `template-fidelity`
   Read `references/template-fidelity.md`. Write `template_fidelity.md` and show a real template preview, real PPTX-derived thumbnail, or a real template-adapted sample. The artifact must state what source slide/framework structure is preserved and what content is replaced.

   If only a hand-drawn PNG/HTML/PIL/SVG mockup is available, label it as a non-template style sketch and do not present it as a confirmed template preview.

11. `style-preview`
   Generate 2-3 visual directions. Each direction should include three preview images: cover, agenda, body. For template-backed decks, previews should be rendered from real template framework choices, not invented cards. Use Roil according to `roil-integration.md` when the direction depends on generated visuals. Use `template-systems.md` when the direction depends on Guizang magazine/Swiss structure. Ask for `风格确认`.

12. `planning-lock`
   Write in this order:
   - `design_spec.md`
   - `slide_blueprint.md`
   - `slide_framework.json` when the deck reuses a template profile
   - `spec_lock.md`
   Include the sample batch plan. Each slide plan should map content to a template `framework_id`, declare the page logic, `layout_job`, `primary_carrier`, image roles, text roles, figure-text contract, and which slots are editable. Ask for `生成前确认`.

13. `page-generation`
   Build slide structure first. For template-backed decks, copy the selected page framework logic from the template profile JSON: margins, slot hierarchy, evidence placement, title zones, and dominant carrier. Then execute the declared figure-text contract:
   - `complete Roil information figure + editable page context`: call Roil directly for the complete mechanism/workflow figure. Keep the page title, conclusion, caption, and citation as native PPT text. Do not replace the figure with SVG/HTML/PIL/PPT drawings unless recording an explicit deterministic fallback.
   - `visual layer + editable PPT labels`: call Roil only for atmosphere, icon language, or non-text visuals. Use native PPT text/shapes for exact labels and structure.
   - `evidence + editable caption`: preserve the original screenshot/photo/document bytes and place them without compression. Use PPT-native captions and boundaries.

   For HTML Guizang decks, start from the relevant bundled template and validate Swiss HTML when used. Offer multiple visual candidates per slide for high-stakes work.

   Before generating the whole deck, generate a representative sample batch and ask for `样张确认`. Use cover + agenda + body by default; for academic/report decks include one evidence-heavy page. After sample approval, generate remaining pages in batches. For decks over 10 slides or high-stakes decks, ask for `章节确认` after each section or 4-6 slide batch unless the user explicitly requested a faster draft.

14. `review-retouch`
   Run `render_review_page.py` for locked-image previews or create a preview sheet for editable exports. Collect user feedback. Visual issues return to Roil; wording and placement issues update the editable text spec.

15. `export`
   Run `package_editable_text_pptx.py` by default. Use `package_image_pptx.py` only for locked visual exports. Write `delivery_manifest.json`. Ask for or record `成片审核通过`.

## Rollback Rules

- Failed Roil generation: retry the current image with a clearer prompt; if login is required, stop with the Roil login handoff.
- Failed validation: repair the current artifact; do not advance.
- Missing or unclear page logic: return to `page-logic`; do not compensate by adding decoration.
- Template candidate rejection: return to `template-candidates`, not `style-preview`.
- Missing template confirmation: stop at `template-candidates`; do not make a silent final template choice.
- Template fidelity failure: return to `template-fidelity`; do not compensate with a new hand-drawn style.
- Style rejection: return to `style-preview`, not `planning-lock`.
- Blueprint rejection: return to `outline` or `planning-lock` depending on whether the narrative changed.
- Sample rejection: return to `style-preview`, `planning-lock`, or the affected slide depending on whether the issue is visual system, structure, or local execution.
- Slide review rejection: return only the affected slide(s) to `page-generation`.

## Research Rules

Use web browsing for recent, factual, market, legal, financial, medical, product, or public-entity claims. Store sources or source summaries in `research_brief.md`. If facts are inferred, mark them as inferred.

## Review Strictness

`draft`: one pass review; export may be marked draft.

`normal`: review every slide image once, fix obvious text/layout/content errors.

`high-stakes`: require source checking for claims, style consistency check, text legibility check, and one user approval pass before export.

## HTML-Backed Lane

Use only when explicitly requested. The implementation should follow the same front-stage gates, then produce HTML slide pages and screenshots before PPTX packaging. This lane may adapt ppt-agent-style planning and validation, but should not expose subagent internals unless needed for debugging.

For Guizang-style HTML decks, copy from `assets/guizang/template-magazine.html` or `assets/guizang/template-swiss.html`. Keep `assets/guizang/NOTICE.md` and `LICENSE` when distributing the template package. Swiss HTML must pass `assets/guizang/scripts/validate-swiss-deck.mjs`.
