---
name: sasu-image2
description: Generate images using the user's SASU API key with gpt-image-2. Use when the user asks to draw, generate an image, create artwork, or explicitly says to use SASU image2.
---

# SASU Image2

Use this skill when the user wants image generation through the saved SASU image2 configuration.

## Workflow

1. Use the bundled script:

   ```bash
   python3 /Users/apple/.codex/skills/sasu-image2/scripts/draw.py \
     --prompt "<image description>" \
     --out outputs/imagegen/result.png
   ```

2. Defaults:
   - Model: `gpt-image-2`
   - Base URL: fixed in the script
   - API key: loaded from `config.local.json` or `SASU_IMAGE2_API_KEY`
   - Size: `1024x1536`
   - Quality: `high`
   - Output format: PNG

3. Save final images under the current workspace's `outputs/imagegen/` unless the user requests another workspace-local output path.

4. Do not print, commit, or reveal the saved API key in chat or command output.

5. Minimal local setup:

   ```json
   {
     "api_key": "your-sasu-key"
   }
   ```

6. Validation and failure handling:
   - Use `--dry-run` first when you need to confirm config, model, output path, or size without making a paid API call.
   - The wrapper refuses to overwrite an existing file unless `--force` is passed.
   - If the API key is missing or invalid, stop and fix config instead of retrying blind.
   - If the upstream API returns a URL instead of base64 image bytes, treat it as an unsupported response and report that explicitly.

## Options

```bash
python3 /Users/apple/.codex/skills/sasu-image2/scripts/draw.py \
  --prompt "A refined poster of orbital geometry on warm paper" \
  --size 1024x1536 \
  --quality high \
  --out outputs/imagegen/sasu-image2-orbit.png \
  --force
```

Supported sizes are whatever the upstream `gpt-image-2` endpoint accepts, commonly `1024x1024`, `1024x1536`, `1536x1024`, `2048x1152`, and `2048x2048`.
