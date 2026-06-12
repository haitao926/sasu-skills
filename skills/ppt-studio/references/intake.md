# Intake

PPT Studio should feel like a focused design intake, not a long form.

## Minimal Intake

Ask only for missing high-impact information:

```text
我先按 PPT Studio 流程推进。为了少返工，我需要确认 6 个点：
1. 这份 PPT 的使用场景和听众是谁？
2. 目标页数或汇报时长是多少？
3. 是否有现成资料？如果没有，是否允许联网调研？
4. 有没有必须体现的学校/公司/品牌/课程/活动身份？
5. 风格上有什么必须要或必须不要的方向？
6. 你希望是分段确认还是尽量快出稿？默认是分段确认。
```

If the user already answered most of these, do not ask again. Summarize assumptions and ask for `需求确认`.

## Requirements Synthesis

Show a concise synthesis before writing or locking artifacts:

```text
需求判断：
- 目标：...
- 听众：...
- 内容来源：research/source/thin-topic
- 页数：...
- 风格边界：...
- 风险：...

我会先生成内容基底和 2-3 套真实视觉预览。确认吗？
```

## Defaults

Use these defaults when the user does not specify:

- aspect ratio: 16:9;
- mode: default;
- review strictness: normal;
- branch: research for recent factual topics, source when files/text are provided, thin-topic only for generic or internal topics;
- confirmation mode: staged by default; use direct draft only when the user explicitly wants speed over checkpoints;
- preview directions: 3 for high-stakes, 2 for small/fast decks;
- final candidates: one per slide unless user requests multiple candidates.

## Avoid

- Do not ask the user to pick raw parameters such as color hex codes, grid systems, or model settings.
- Do not expose internal artifact names during intake unless the user asks how the process works.
- Do not proceed from a vague topic directly to full slide generation unless the user explicitly requests a rough draft.
