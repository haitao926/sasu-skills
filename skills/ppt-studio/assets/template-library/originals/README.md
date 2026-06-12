# Template originals not included

The local `ppt-studio` skill can use a large PowerPoint template library under this directory. The original PPTX/preview asset pack is intentionally excluded from this repository because it is approximately 1.3 GB and may carry separate licensing constraints.

Included in this repository:

- `assets/template-library/template-library-*.json` and `.md` indexes
- `assets/template-library/profiles/*.json` framework profiles
- `assets/guizang/` lightweight HTML templates and validators

If you need full template-faithful generation, install or mount the original template pack locally at the same relative path, then rebuild profiles with:

```bash
python3 scripts/build_template_profiles.py
```
