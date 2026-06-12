---
name: sasu-image2
description: Generate images using the user's SASU API key with gpt-image-2. Use when the user asks to draw, generate an image, create artwork, or explicitly says to use SASU image2.
---

# SASU Image2

Use this skill when the user wants image generation through the saved SASU image2 configuration.

## Workflow

1. Preferred path: use the bundled wrapper script when Python is available.

   ```bash
   python skills/sasu-image2/scripts/draw.py \
     --prompt "<image description>" \
     --out outputs/imagegen/result.png
   ```

   Windows PowerShell:

   ```powershell
   py .\skills\sasu-image2\scripts\draw.py `
     --prompt "<image description>" `
     --out outputs\imagegen\result.png
   ```

2. If the other machine cannot run Python, call the image endpoint directly with `curl` or PowerShell. The skill does not require the Python wrapper to use the API.

   `curl` example:

   ```bash
   curl http://10.15.46.72:8010/v1/images/generations \
     -H "Authorization: Bearer $SASU_IMAGE2_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-image-2",
       "prompt": "A refined poster of orbital geometry on warm paper",
       "size": "1024x1536",
       "quality": "high",
       "n": 1,
       "output_format": "png"
     }'
   ```

   The direct API response contains base64 image data in `data[0].b64_json`. If the machine is on Windows, prefer the PowerShell example below because it both requests the image and writes the PNG file.

   Windows PowerShell example:

   ```powershell
   $headers = @{
     Authorization = "Bearer $env:SASU_IMAGE2_API_KEY"
     "Content-Type" = "application/json"
   }
   $body = @{
     model = "gpt-image-2"
     prompt = "A refined poster of orbital geometry on warm paper"
     size = "1024x1536"
     quality = "high"
     n = 1
     output_format = "png"
   } | ConvertTo-Json

   $response = Invoke-RestMethod `
     -Uri "http://10.15.46.72:8010/v1/images/generations" `
     -Method Post `
     -Headers $headers `
     -Body $body

   $bytes = [Convert]::FromBase64String($response.data[0].b64_json)
   [IO.File]::WriteAllBytes(".\\outputs\\imagegen\\result.png", $bytes)
   ```

2. Defaults:
   - Model: `gpt-image-2`
   - Base URL: `http://10.15.46.72:8010/v1`
   - API key: loaded from `config.local.json` or `SASU_IMAGE2_API_KEY`
   - Size: `1024x1536`
   - Quality: `high`
   - Output format: PNG
   - `base_url` can be overridden by `SASU_IMAGE2_BASE_URL` or `config.local.json`

3. Save final images under the current workspace's `outputs/imagegen/` unless the user requests another workspace-local output path.

4. Do not print, commit, or reveal the saved API key in chat or command output.

5. Minimal local setup:

   ```json
   {
     "api_key": "your-sasu-key",
     "base_url": "http://10.15.46.72:8010/v1",
     "model": "gpt-image-2"
   }
   ```

6. Validation and failure handling:
   - Use `--dry-run` first when you need to confirm config, model, output path, or size without making a paid API call.
   - The wrapper refuses to overwrite an existing file unless `--force` is passed.
   - If the API key is missing or invalid, stop and fix config instead of retrying blind.
   - If the upstream API returns a URL instead of base64 image bytes, treat it as an unsupported response and report that explicitly.

## Options

```bash
python skills/sasu-image2/scripts/draw.py \
  --prompt "A refined poster of orbital geometry on warm paper" \
  --size 1024x1536 \
  --quality high \
  --out outputs/imagegen/sasu-image2-orbit.png \
  --force
```

Supported sizes are whatever the upstream `gpt-image-2` endpoint accepts, commonly `1024x1024`, `1024x1536`, `1536x1024`, `2048x1152`, and `2048x2048`.
