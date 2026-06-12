# sasu-skills

Curated skill pack for Codex / Claude Code / `cc-switch`, organized in the repository layout that `cc-switch` expects:

```text
https://github.com/{owner}/{name}/tree/{branch}/{subdirectory}
```

This repository uses:

- `owner`: `haitao926`
- `name`: `sasu-skills`
- `branch`: `main`
- `subdirectory`: `skills`

So the canonical GitHub-style path is:

```text
https://github.com/haitao926/sasu-skills/tree/main/skills
```

## Included skills

### Document Processing

- `mineru-parser` - Parse PDFs and other documents through MinerU Cloud API with OCR and structured output support.

### Image Generation

- `sasu-image2` - Generate images through a saved SASU `gpt-image-2` endpoint with dry-run validation and safe output handling.
  - Default base URL: `http://10.15.46.72:8010/v1`
  - Supports direct API calls when Python is unavailable on the target machine.

### Presentation Production

- `ppt-studio` - Structure-first PowerPoint production workflow for editable Chinese PPTX decks, template-guided layouts, Roil-generated visuals, review gates, and WPS-safe font patching.
  - Keeps Chinese text editable by default.
  - Includes lightweight template indexes/profiles and Guizang HTML templates.
  - Excludes the large original PPTX template asset pack; see `skills/ppt-studio/assets/template-library/originals/README.md`.

## Repository layout

```text
skills/
  mineru-parser/
    SKILL.md
    parse.py
    config.example.json
    tests/
  sasu-image2/
    SKILL.md
    config.example.json
    scripts/
    tests/
  ppt-studio/
    SKILL.md
    references/
    scripts/
    assets/
docs/
  cc-switch-gitea.md
```

## Installing with cc-switch

Use the repository fields in the `cc-switch` skill repo form:

- Owner: `haitao926`
- Name: `sasu-skills`
- Branch: `main`
- Subdirectory: `skills`

If `cc-switch` accepts a GitHub repository entry, it should discover each folder under `skills/` as an installable skill.

## Gitea note

`cc-switch` appears to model remote skill repositories as `owner + name + branch` plus a GitHub-style subdirectory path. See [docs/cc-switch-gitea.md](docs/cc-switch-gitea.md) for the current compatibility conclusion and workarounds.

## Local validation

The included skills keep their own lightweight tests:

```bash
python3 -m unittest discover -s skills/mineru-parser/tests
python3 -m unittest discover -s skills/sasu-image2/tests
python3 -m py_compile skills/ppt-studio/scripts/*.py
python3 skills/ppt-studio/scripts/patch_pptx_fonts.py --help
```

## Publishing strategy

Recommended setup:

1. Keep `Gitea` as your primary editable remote.
2. Keep `GitHub` as the compatibility mirror for `cc-switch`.
3. Push the same repository structure to both remotes.

That gives you self-hosted ownership without losing `cc-switch` installability.
