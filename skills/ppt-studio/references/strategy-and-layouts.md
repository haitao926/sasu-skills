# Strategy And Layouts

Use this reference before style previews and page generation. It adapts the template-first discipline from `html-ppt-skill`: choose a theme/background, choose a template family, choose page layouts, then create visuals.

## Strategy Gate

Write `deck_strategy.md` after `outline.md` and before `style_options.md`.

Minimum sections:

```markdown
# Deck Strategy

## Diagnosis
- scenario:
- audience:
- stakes:
- primary job: argument | evidence | teaching | story | sales | demo | mixed
- density:

## Page Logic
| slide | slide claim | audience takeaway | main line | content job |

## Background And Template
- selected background system:
- selected template family:
- selected template_id:
- selected template_profile_path:
- rejected alternatives:

## Layout Vocabulary
| slide | layout job | template framework_id | primary carrier | why |

## Image Plan
| slide | image role | source/generation | why needed | complete figure? |

## Text Plan
| slide | text role | max density |

## Figure-Text Contract
- default composition:
- rules for evidence slides:
- rules for visual/story slides:

## Export Lane
- lane:
- reason:
```

## Template Matching Contract

For template-backed PPTX work, the template is not just a skin. It is a reusable framework source.

Use this order:

1. Match the task scenario and stakes against `assets/template-library/template-library-tag-index.json`.
2. Inspect `assets/template-library/template-library-frame-index.json` to find templates with the needed `layout_job` mix.
3. Open the selected per-template profile at `assets/template-library/profiles/<template_id>.json`.
4. For each planned slide, choose a reusable `framework_id` whose `layout_job`, `primary_carrier`, density, and slots match the slide's content job.
5. Write the mapping into the run's `slide_framework.json` and mirror the same IDs in `slide_blueprint.md`, `editable_text_spec.json`, `review_manifest.json`, and `delivery_manifest.json` when those files exist.

Minimal `slide_framework.json` shape:

```json
{
  "template_id": "011-联合基金亚热带岩性森林蓝色-xxxxxxxx",
  "template_profile_path": "assets/template-library/profiles/011-联合基金亚热带岩性森林蓝色-xxxxxxxx.json",
  "slides": [
    {
      "number": 1,
      "title": "以评价牵引的课堂数据平台",
      "content_job": "解释平台定位和技术框架",
      "framework_id": "011-联合基金亚热带岩性森林蓝色-xxxxxxxx-s05",
      "layout_job": "architecture-diagram",
      "primary_carrier": "diagram-shapes",
      "image_roles": ["screenshot", "diagram"],
      "text_roles": ["claim", "label", "caption"],
      "slot_mapping": [
        {"slot": "title", "role": "claim", "editable": true},
        {"slot": "main_visual", "role": "diagram", "editable": true},
        {"slot": "evidence_1", "role": "screenshot", "editable": false}
      ]
    }
  ]
}
```

Reject a candidate framework if:

- the slide's main content job does not match the framework's `layout_job`;
- the selected framework has a different `primary_carrier` than the slide needs;
- the template density is too high or too low for the page content;
- the evidence image would be too small to read after placement;
- the framework forces important Chinese text into a non-editable image.

## Scenario To Template

`academic report / defense / teaching-research case`

- Background: paper, light grid, restrained dark cover, citation-safe evidence boards.
- Template family: academic-paper, editorial-serif, Swiss grid, engineering whiteprint.
- Layouts: cover, toc, research-question, literature-policy, method-evidence, table, matrix-grid, limitations-future.
- Composition: claim + evidence + boundary.
- Avoid: product slogans, oversized decorative images, unsupported causal claims.

`business report / internal review`

- Background: corporate clean white, light gray panels, restrained navy/green accent.
- Template family: corporate-clean, Swiss grid, data-room.
- Layouts: executive-summary, KPI grid, table, comparison, roadmap, claim-evidence.
- Composition: decision + evidence + implication.

`product pitch / roadshow`

- Background: clean stage, strong hero, product screenshot mats.
- Template family: pitch-deck-vc, product narrative, Swiss grid.
- Layouts: cover, problem-solution, market map, product demo, KPI grid, roadmap, CTA.
- Composition: claim + proof + next action.

`technical sharing / architecture`

- Background: engineering whiteprint, blueprint, dark code stage, grid.
- Template family: engineering-whiteprint, blueprint, terminal, Swiss grid.
- Layouts: architecture diagram, flow diagram, code, terminal, comparison, process-steps.
- Composition: system diagram + labels + design implication.

`training / courseware`

- Background: calm classroom, course module, high readability.
- Template family: course-module, academic-paper, soft learning.
- Layouts: learning-goal, concept-example, process-steps, checklist, practice, recap.
- Composition: instruction + example + practice cue.

`festival / campus / children`

- Background: Roil-generated scene or illustrated atmosphere with blank text zones.
- Template family: visual-story, campus activity, editorial soft.
- Layouts: cover, agenda, activity card, process-steps, image-hero, closing.
- Composition: Roil scene + short editable title + activity cue.

## Background Systems

Choose one primary background system per deck:

- `plain-paper`: off-white or white, best for academic/report decks.
- `light-grid`: subtle grid, best for systems, technology, evidence, and architecture.
- `dark-stage`: dark cover/chapter pages, best for serious academic/technical openings.
- `editorial-paper`: warm paper, best for narrative reports and long-form talks.
- `evidence-board`: neutral page with strong image/table containers, best for source-heavy decks.
- `full-bleed-visual`: Roil image as atmosphere, best for visual-story, festival, and campus decks.
- `hybrid`: dark cover + light body, or Roil dividers + structured body.

Do not choose a decorative background before knowing the deck's scenario and density.

## Layout Vocabulary

Use these layout jobs when writing `slide_blueprint.md`:

- `cover`: title, metadata, one hero image or empty stage.
- `toc`: section map or agenda.
- `section-divider`: chapter transition.
- `research-question`: one central question plus subquestions.
- `literature-policy`: sources/citations mapped to design implications.
- `claim-evidence`: one claim plus one evidence image/table/diagram.
- `two-column`: concept and example, before and after, text and image.
- `three-column`: three principles, three findings, three options.
- `image-hero`: one dominant image plus 1-2 interpretation blocks.
- `process-steps`: 4-6 steps in sequence.
- `timeline`: chronological development or research process.
- `roadmap`: now/next/later/future.
- `table`: dense evidence, source mapping, comparison, limitations.
- `kpi-grid`: 3-5 metrics with short labels.
- `architecture-diagram`: system layers and interfaces.
- `flow-diagram`: pipeline, learning path, workflow.
- `comparison`: before/after, current/proposed, option A/B.
- `quote`: strong statement or policy excerpt.
- `limitations-future`: validity boundaries and next steps.
- `closing`: final conclusion and action.

## Image Roles

Every image must declare one role:

- `hero-atmosphere`: sets mood; needs text-safe blank zones.
- `evidence`: proves or illustrates a claim; needs caption and boundary.
- `core-information-figure`: carries the mechanism, architecture, workflow, or method explanation as a complete visual block; use Roil when the user asks for a richer generated figure.
- `diagram`: explains structure or flow; text should help read it.
- `screenshot`: demonstrates product/system state; frame cleanly.
- `data-chart`: carries quantitative evidence; text interprets, not repeats.
- `reference-redraw`: Roil redraw from source/reference.
- `visual-layer`: Roil or image layer that provides atmosphere/icons/texture while PPT-native text carries the meaning.
- `diagram-support`: deterministic editable shapes, arrows, and simple icons.
- `decorative-texture`: subtle support only; never competes with text.

If the role is unclear, remove the image or redesign the slide.

Decision rules:

- Use real screenshots/photos/documents as `evidence`; preserve original quality and add editable captions.
- Use `core-information-figure` when the image itself must explain the platform mechanism, research method, architecture, workflow, or classroom loop.
- Use native PPT/SVG/HTML only for simple deterministic diagrams or editable `diagram-support`.
- Use Roil for complete core figures when the user asks for "Roil 画", "核心展示图", or "图片本身信息更充实".
- Do not use evidence images to explain abstract logic; pair them with a separate core figure or editable structure.

## Text Roles

Every visible text block must declare one role:

- `claim`: the main point of the slide.
- `explanation`: compact reasoning or context.
- `caption`: tells the audience how to read an image.
- `label`: identifies parts of a diagram.
- `citation`: source or reference note.
- `boundary`: what the evidence does not prove.
- `instruction`: what the audience/student should do.
- `speaker-support`: belongs in notes, not on the visible slide.

## Figure-Text Contracts

`claim + evidence + boundary`

- Use for academic reports, case applications, research summaries.
- Text makes the claim and boundary. Image provides evidence.
- The caption must explain what the image proves.

`diagram + labels + implication`

- Use for systems, architecture, workflows.
- Diagram shows structure. Labels orient the viewer. Text states the design implication.

`complete Roil information figure + editable page context`

- Use when a page section should be a complete visual explanation, not just a background.
- Roil figure carries the main mechanism/workflow with limited accurate labels.
- PPT-native text still carries page title, conclusion sentence, caption, source note, and surrounding context.
- Reject the figure if it is only decorative, has low information density, has unreadable labels, or needs dense PPT labels overlaid to make sense.

`visual layer + editable PPT labels`

- Use when editability and exact Chinese wording matter more than integrated illustration.
- Roil creates atmosphere, icon language, or non-text visual structure.
- PPT shapes/text carry exact labels, bullets, and captions.
- Do not choose this contract when the user explicitly asks for a complete Roil information figure.

`scene + title + cue`

- Use for campus, festival, children, activity decks.
- Roil scene creates atmosphere. Title and cue remain editable.

`instruction + example + practice`

- Use for courseware.
- Text instructs, image/example demonstrates, practice cue drives action.

`decision + data + action`

- Use for business and product reports.
- Text states the decision, chart/table provides data, final line states action.

## Rejection Rules

Reject a strategy if:

- the template family does not match audience and stakes;
- body slides would rely on decorative backgrounds rather than structure;
- images and text repeat the same information;
- images have no evidence/story/teaching role;
- evidence screenshots/photos are used as the only explanation for abstract system logic;
- a requested Roil core figure is replaced by SVG/HTML/PPT drawing without declaring fallback;
- a core generated figure is merely a decorative background with PPT labels overlaid when the selected contract was complete figure;
- a diagram's information density hides the main line or cannot be read within 3 seconds;
- generated labels are blurry, inaccurate, overlapped, or too small at slide size;
- text exceeds the selected layout density;
- the deck lacks enough layout variety for its length;
- academic/report decks hide evidence boundaries;
- editable text is sacrificed without user request.
