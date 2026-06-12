# Checkpoints

PPT Studio defaults to staged confirmation, not one-shot production. The user should be able to correct direction before the whole deck is generated.

## Checkpoint Sequence

Use these checkpoints unless the user explicitly requests a rough one-pass draft:

| checkpoint | when | show the user | allowed rollback |
|---|---|---|---|
| `需求确认` | after intake | goal, audience, page count, sources, assumptions | intake |
| `资料/调研确认` | after content basis | key claims, source boundaries, content focus | content branch |
| `结构确认` | after outline, page logic, and deck strategy | slide sequence, single-slide main lines, template family, layout map, image/text roles | outline, page logic, or deck strategy |
| `模板候选确认` | after concrete template matching | 2-4 candidate templates, fit reasons, reusable frameworks, risks | template candidates or deck strategy |
| `模板保真确认` | after confirmed template lock | real template preview/adapted sample, preserved slots, replaced content, fidelity risks | template fidelity or template candidates |
| `风格确认` | after style previews | 2-3 directions with cover/agenda/body previews | style preview or strategy |
| `生成前确认` | after design spec and blueprint | final blueprint, sample batch plan, export lane | planning lock |
| `样张确认` | after representative sample slides | 2-4 sample pages before full generation | style, blueprint, or page generation |
| `章节确认` | during long decks | one section or 4-6 slides at a time | affected section only |
| `成片审核通过` | before final export | review page/sheet and known issues | affected slides or export |

## Sample Batch Rule

Before generating the full deck, create a representative sample batch:

- small decks under 6 slides: cover + one body page;
- normal decks: cover + agenda + one body page;
- academic/report decks: cover + structure page + one evidence-heavy body page;
- pitch/product decks: cover + problem/solution page + KPI/product page;
- teaching/campus decks: cover + agenda/activity page + one instructional/body page;
- visual-story decks: cover + one scene page + one text-safe body page.
- When the deck has structural or explanatory pages, at least one sample should be a `core-information-figure` page rather than only a decorative cover.

Ask for `样张确认` before generating the rest. If the sample is rejected because of content or logic, return to `outline`, `page-logic`, or `deck_strategy`. If the sample is rejected because of look and feel, return to `style-preview`. If only one slide is wrong, return that slide to `page-generation`.

## Batch Generation Rule

For decks over 10 slides or high-stakes decks, generate in batches:

- one chapter at a time when the deck has clear chapters;
- otherwise 4-6 slides per batch;
- after each batch, show a review sheet and ask whether to continue, retouch, or roll back.

Do not ask the user to inspect raw internal artifacts unless useful. Show concise decisions, candidate template cards, rendered previews, and specific questions.

## Compression Rule

The user may ask for speed. In that case:

- `fast` mode may combine `资料/调研确认` and `结构确认`;
- `draft` review may skip `章节确认`;
- never skip `风格确认` for visual decks;
- never skip final review before non-draft export.
