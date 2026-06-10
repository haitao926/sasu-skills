---
name: mineru-parser
description: Parse PDF and other documents using MinerU Cloud API with OCR support.
homepage: https://mineru.net
metadata: {"openclaw":{"emoji":"📄","requires":{"bins":["python3"]}}}
---

# MinerU Cloud API Document Parser

Parse PDF and other documents using MinerU Cloud API with OCR support.

## Description

This skill provides a wrapper around MinerU Cloud API for parsing documents. It supports PDF, DOC, DOCX, PPT, PPTX, PNG, JPG, JPEG, and HTML files with OCR and layout analysis capabilities.

## When to Use

Use this skill when you need to:
- Extract text from scanned PDF documents
- Parse complex document layouts with tables, formulas, and images
- Convert documents to markdown, JSON, DOCX, HTML, or LaTeX format
- Handle multi-page documents with OCR
- Extract structured content from academic papers, reports, or textbooks
- Batch process multiple documents

## Features

- **Cloud-based**: No local model download required
- **Fast processing**: Powered by MinerU's cloud infrastructure
- **Multiple formats**: Supports PDF, DOC, DOCX, PPT, PPTX, images, and HTML
- **OCR support**: High-quality OCR for scanned documents
- **Formula recognition**: Extract mathematical formulas
- **Table recognition**: Preserve table structures
- **Multiple output formats**: Markdown, JSON, DOCX, HTML, LaTeX
- **Resume support**: Re-check upload and task status after interruptions
- **Progress tracking**: Monitor parsing progress in real time

## Configuration

This wrapper supports either:

- `{baseDir}/config.json`
- environment variables: `MINERU_TOKEN`, `MINERU_API_TOKEN`, or `MINERU_API_KEY`

If both exist, the environment variable wins.

Config file example:

```json
{
  "api_token": "your_api_token_here",
  "api_base_url": "https://mineru.net/api/v4",
  "default_model": "vlm",
  "default_language": "ch",
  "enable_ocr": false,
  "enable_formula": true,
  "enable_table": true,
  "extra_formats": [],
  "output_dir": "~/Downloads/mineru_output"
}
```

### Configuration Options

- `api_token`: Your MinerU API token (required) - Get it from https://mineru.net
- `api_base_url`: API base URL (default: https://mineru.net/api/v4)
- `default_model`: Model version - `pipeline`, `vlm`, or `MinerU-HTML` (default: vlm)
- `default_language`: OCR language - `ch` (Chinese), `en` (English), etc. (default: ch)
- `enable_ocr`: Enable OCR for scanned documents (default: false)
- `enable_formula`: Enable formula recognition (default: true)
- `enable_table`: Enable table recognition (default: true)
- `extra_formats`: Additional output formats - `["docx", "html", "latex"]` (default: [])
- `output_dir`: Fallback directory for URL tasks or explicit `--output` runs (default: ~/Downloads/mineru_output)

## Usage

### From Command Line

```bash
# Parse a single PDF file (URL mode)
{baseDir}/parse.py https://example.com/document.pdf

# Parse a local file (upload mode)
{baseDir}/parse.py /path/to/document.pdf

# Specify output formats
{baseDir}/parse.py document.pdf --formats docx html

# Enable OCR for scanned documents
{baseDir}/parse.py document.pdf --ocr

# Parse specific page ranges
{baseDir}/parse.py document.pdf --pages "1-10,15,20-25"

# Wait for completion and download results
{baseDir}/parse.py document.pdf --wait

# Check an existing task later
{baseDir}/parse.py --check-task <task_id>

# Check an existing batch later
{baseDir}/parse.py --check-batch <batch_id>
```

For local files, parsed results now default to a dedicated sibling folder beside the source document:

```text
/path/to/document.pdf
-> /path/to/document_mineru_output/
```

Use `--output /custom/path` to override that behavior.

Prefer executing `parse.py` directly instead of wrapping it with `python3`.
The script already has a shebang, and direct execution keeps the gateway exec allowlist narrow to this specific skill.

### From OpenClaw

When you need to parse a document, invoke this skill:

```
Please use the mineru-parser skill to extract text from this PDF: /path/to/document.pdf
```

The assistant will:
1. Load the skill and configuration
2. Upload the file or submit the URL
3. Create a parsing task
4. Monitor the progress
5. Download and extract the results
6. Return the parsed content

Current wrapper scope:

- One file or one URL per run
- Task status lookup via `--check-task` / `--check-batch`
- If you need true multi-file batch processing, loop over files or extend `parse.py`

## API Limits

- Single file size: Max 200MB
- File pages: Max 600 pages
- Daily quota: 2000 pages at highest priority (additional pages at lower priority)
- Upload batches accepted by the API: Max 200 files per batch
- Upload link validity: 24 hours

## Output

The parser generates a ZIP file containing:
- **{filename}.md**: Main content in markdown format
- **{filename}_model.json**: Structured data with layout information
- **images/**: Extracted images from the document
- **{filename}.docx**: Word document (if requested)
- **{filename}.html**: HTML version (if requested)
- **{filename}.tex**: LaTeX source (if requested)

## Examples

### Example 1: Parse a Chinese textbook (scanned PDF)

```bash
~/.openclaw/skills/mineru-parser/parse.py 教材.pdf --ocr --language ch --wait
```

### Example 2: Parse an English academic paper with formulas

```bash
~/.openclaw/skills/mineru-parser/parse.py paper.pdf --language en --formats latex --wait
```

### Example 3: Parse from URL

```bash
{baseDir}/parse.py https://example.com/document.pdf --wait
```

### Example 4: Parse specific pages only

```bash
{baseDir}/parse.py document.pdf --pages "1-5,10,15-20" --wait
```

### Example 5: Check a task after interruption

```bash
{baseDir}/parse.py --check-task task_xxx
```

## Task States

- `pending`: Task is queued
- `running`: Document is being parsed
- `converting`: Converting to additional formats
- `done`: Parsing completed successfully
- `failed`: Parsing failed (check error message)
- `waiting-file`: Waiting for file upload (batch mode)

## Troubleshooting

### Token errors (A0202, A0211)

Check your API token in `{baseDir}/config.json`, or export `MINERU_TOKEN`. Get a new token from https://mineru.net if expired.

Use `--show-config` to confirm which token source is active. The CLI masks the token and reports whether it came from the environment or config file.

### File size/page limit errors (-60005, -60006)

- Split large files into smaller parts
- Use page_ranges to parse specific pages only

### File format errors (-60002)

Ensure the file has the correct extension and is one of the supported formats.

### Network timeout (-60008)

- Check if the URL is accessible
- For foreign URLs (GitHub, AWS), consider downloading and uploading instead

### Parsing failed (-60010)

- Try a different model version (pipeline vs vlm)
- Check if the file is corrupted
- Retry after a few minutes

## Model Versions

- **pipeline**: Traditional pipeline model, good for standard documents
- **vlm**: Vision-Language Model, better for complex layouts and scanned documents
- **MinerU-HTML**: Specialized for HTML files

## Notes

- First-time users get 2000 pages of high-priority parsing quota daily
- Results are cached for 15 minutes by default (configurable)
- Callback URLs can be configured for automatic result notification
- All API requests require Bearer token authentication

## Version

- Skill version: 2.0.0 (Cloud API)
- MinerU API version: v4
- Last updated: 2026-03-05
