# Teaching Courseware

Use this reference for classroom decks, especially primary/secondary school lessons and training decks where the audience must look, judge, discuss, or do something.

## Core Contract

A courseware slide is not a document page. Visible text and images must support a classroom action.

For every slide, declare:

```yaml
slide:
lesson_job: concept | observe | compare | predict | hands-on | misconception-check | practice | recap
student_action: look | say | judge | discuss | build | test | summarize
visible_text:
  title_role: conclusion | task | question
  body_role: instruction | label | contrast-keyword | safety-boundary
image_role: material-scene | evidence-photo | core-information-figure | editable-diagram | visual-layer | none
teacher_notes_role:
```

If `student_action` cannot be named, the slide is probably just narration. Redesign it.

## Visible Text Rules

Use visible PPT text only for:

- the slide's main conclusion or task;
- an observation / judgment instruction;
- short diagram labels;
- comparison keywords;
- safety or operating boundaries.

Move teacher talk, long explanation, and background detail to notes or source artifacts.

For primary school science:

- title: 26-36 pt, conclusion or task sentence;
- body/instruction: 20-26 pt;
- diagram labels: 14-18 pt;
- each body block: roughly 18-24 Chinese characters max;
- one slide: 1 main title, 1 core visual, 1-3 short text blocks.

Prefer:

```text
串联：一个接一个，只有一条路
```

over:

```text
什么是串联电路
```

## Image Role Rules

Generated images are useful, but they must not replace accurate teaching structure.

Use generated images for:

- cover atmosphere;
- classroom/material scene;
- evidence/photo-like craft or experiment context;
- practice backgrounds where the exact answer is carried by editable labels or teacher discussion.

Use PPT-native editable diagrams for:

- exact current paths;
- circuit branching;
- open/closed states;
- labels that must be accurate in Chinese;
- step-by-step judgment logic.

Do not let generated images alone explain circuit topology, math procedure, safety-critical steps, or any concept where small visual errors change the meaning.

For generated visual plates:

- ask for blank zones for PPT-native text;
- forbid rendered Chinese/English text, watermarks, logos, and random letters;
- after generation, classify the image as `material-scene`, `visual-layer`, or `core-information-figure`;
- if the image contains scientific inaccuracies, keep it as atmosphere/material context only and add editable diagrams for the accurate logic.

## Layout Rhythm

For decks over 8 slides:

- include at least one observe/predict/practice slide;
- avoid three consecutive slides with the same text position and visual structure;
- use comparison layouts for contrast, not two paragraphs;
- use process/path layouts for mechanisms, not bullet lists;
- make the core visual large enough to read from the back of a classroom.

## Courseware QA

Before delivery, check:

- Can a student tell what to do on the slide within 3 seconds?
- Is the main concept carried by an accurate editable diagram or a reviewed core figure?
- Are generated images supporting the lesson rather than decorating empty space?
- Are Chinese labels editable and WPS-safe?
- Are safety reminders visible where students may handle materials?
