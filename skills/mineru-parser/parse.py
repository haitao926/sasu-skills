#!/usr/bin/env python3
"""
MinerU Cloud API Document Parser
Parse documents using MinerU Cloud API with OCR support.
"""

import os
import sys
import json
import time
import argparse
import requests
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# Skill directory
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config.json"
REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 30
POLL_INTERVAL_SECONDS = 3

DEFAULT_CONFIG = {
    "api_token": "",
    "api_base_url": "https://mineru.net/api/v4",
    "default_model": "vlm",
    "default_language": "ch",
    "enable_ocr": False,
    "enable_formula": True,
    "enable_table": True,
    "extra_formats": [],
    "output_dir": str(Path.home() / "Downloads" / "mineru_output")
}

TOKEN_ENV_KEYS = ("MINERU_TOKEN", "MINERU_API_TOKEN", "MINERU_API_KEY")

def load_config():
    """Load configuration from config.json or create default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return {**DEFAULT_CONFIG, **config}
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def resolve_api_token(config):
    """Prefer env token, then fall back to config.json."""
    for key in TOKEN_ENV_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return str(config.get("api_token", "")).strip()


def mask_secret(value):
    """Mask secrets for display."""
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def api_headers(api_token):
    """Build standard API headers."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }


def parse_api_json(response):
    """Validate and decode a MinerU API response."""
    try:
        result = response.json()
    except ValueError as exc:
        raise Exception(
            f"API returned invalid JSON: {response.text[:200]}"
        ) from exc

    if result.get("code") != 0:
        raise Exception(f"API error: {result.get('msg', 'Unknown error')}")

    if "data" not in result:
        raise Exception("API response missing 'data' field")

    return result["data"]


def api_request_json(method, url, headers, payload=None):
    """Send a JSON request to MinerU and return the parsed data field."""
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise Exception(f"Network error while calling {url}: {exc}") from exc

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    return parse_api_json(response)


def print_content_preview(md_file):
    """Print a short preview of the generated markdown output."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\n{'='*60}")
    print("CONTENT PREVIEW (first 1000 chars):")
    print(f"{'='*60}")
    print(content[:1000])
    if len(content) > 1000:
        print(f"\n... ({len(content) - 1000} more characters)")
    print(f"{'='*60}")


def print_follow_up_command(identifier_flag, identifier_value):
    """Show how to resume a task later."""
    print("\nCheck status with:")
    print(f"  {sys.argv[0]} {identifier_flag} {identifier_value}")

def is_url(path):
    """Check if path is a URL."""
    try:
        result = urlparse(path)
        return result.scheme in ['http', 'https']
    except:
        return False

def create_task_from_url(config, file_url, **kwargs):
    """Create parsing task from URL."""
    url = f"{config['api_base_url']}/extract/task"
    headers = api_headers(config['api_token'])
    
    data = {
        "url": file_url,
        "model_version": kwargs.get('model', config['default_model']),
        "language": kwargs.get('language', config['default_language']),
        "is_ocr": kwargs.get('ocr', config['enable_ocr']),
        "enable_formula": kwargs.get('formula', config['enable_formula']),
        "enable_table": kwargs.get('table', config['enable_table'])
    }
    
    if kwargs.get('page_ranges'):
        data['page_ranges'] = kwargs['page_ranges']
    
    if kwargs.get('extra_formats') or config['extra_formats']:
        data['extra_formats'] = kwargs.get('extra_formats', config['extra_formats'])
    
    print(f"Creating task for URL: {file_url}")
    result = api_request_json("POST", url, headers, payload=data)
    return result['task_id']

def upload_and_create_task(config, file_path, **kwargs):
    """Upload file and create parsing task."""
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Step 1: Request upload URL
    url = f"{config['api_base_url']}/file-urls/batch"
    headers = api_headers(config['api_token'])
    
    data = {
        "files": [{"name": file_path.name}],
        "model_version": kwargs.get('model', config['default_model']),
        "language": kwargs.get('language', config['default_language']),
        "enable_formula": kwargs.get('formula', config['enable_formula']),
        "enable_table": kwargs.get('table', config['enable_table'])
    }
    
    if kwargs.get('page_ranges'):
        data['files'][0]['page_ranges'] = kwargs['page_ranges']
    
    if kwargs.get('ocr', config['enable_ocr']):
        data['files'][0]['is_ocr'] = True
    
    if kwargs.get('extra_formats') or config['extra_formats']:
        data['extra_formats'] = kwargs.get('extra_formats', config['extra_formats'])
    
    print(f"Requesting upload URL for: {file_path.name}")
    result = api_request_json("POST", url, headers, payload=data)
    
    batch_id = result['batch_id']
    upload_url = result['file_urls'][0]
    
    # Step 2: Upload file
    print(f"Uploading file... (size: {file_path.stat().st_size / 1024 / 1024:.2f} MB)")
    try:
        with open(file_path, 'rb') as f:
            upload_response = requests.put(upload_url, data=f, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise Exception(f"File upload failed: {exc}") from exc
    
    if upload_response.status_code != 200:
        raise Exception(f"File upload failed: {upload_response.status_code}")
    
    print(f"✓ File uploaded successfully")
    print(f"Batch ID: {batch_id}")
    
    return batch_id

def get_task_status(config, task_id):
    """Get task status by task_id."""
    url = f"{config['api_base_url']}/extract/task/{task_id}"
    headers = api_headers(config['api_token'])
    return api_request_json("GET", url, headers)

def get_batch_status(config, batch_id):
    """Get batch status by batch_id."""
    url = f"{config['api_base_url']}/extract-results/batch/{batch_id}"
    headers = api_headers(config['api_token'])
    return api_request_json("GET", url, headers)

def wait_for_completion(config, task_id=None, batch_id=None, timeout=600):
    """Wait for task completion with progress display."""
    start_time = time.time()
    last_progress = None
    
    while time.time() - start_time < timeout:
        try:
            if task_id:
                status = get_task_status(config, task_id)
                state = status['state']
                
                if state == 'done':
                    return status
                elif state == 'failed':
                    raise Exception(f"Parsing failed: {status.get('err_msg', 'Unknown error')}")
                elif state == 'running':
                    progress = status.get('extract_progress', {})
                    if progress != last_progress:
                        extracted = progress.get('extracted_pages', 0)
                        total = progress.get('total_pages', 0)
                        print(f"Progress: {extracted}/{total} pages")
                        last_progress = progress
                elif state in ['pending', 'converting']:
                    print(f"Status: {state}")
            
            elif batch_id:
                batch_status = get_batch_status(config, batch_id)
                results = batch_status.get('extract_result', [])
                
                if not results:
                    print("Waiting for task to start...")
                else:
                    result = results[0]
                    state = result['state']
                    
                    if state == 'done':
                        return result
                    elif state == 'failed':
                        raise Exception(f"Parsing failed: {result.get('err_msg', 'Unknown error')}")
                    elif state == 'running':
                        progress = result.get('extract_progress', {})
                        if progress != last_progress:
                            extracted = progress.get('extracted_pages', 0)
                            total = progress.get('total_pages', 0)
                            print(f"Progress: {extracted}/{total} pages")
                            last_progress = progress
                    elif state in ['pending', 'waiting-file', 'converting']:
                        print(f"Status: {state}")
            
            time.sleep(POLL_INTERVAL_SECONDS)
        
        except KeyboardInterrupt:
            print("\n\nTask interrupted. You can check status later with:")
            if task_id:
                print(f"  Task ID: {task_id}")
            if batch_id:
                print(f"  Batch ID: {batch_id}")
            sys.exit(1)
    
    raise TimeoutError(f"Task timeout after {timeout} seconds")

def download_and_extract(zip_url, output_dir):
    """Download and extract result ZIP file."""
    output_dir = Path(output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nDownloading results...")
    # Retry with different SSL settings
    response = None
    for attempt in range(3):
        try:
            response = requests.get(
                zip_url,
                stream=True,
                verify=True,
                timeout=DOWNLOAD_TIMEOUT,
            )
            break
        except requests.exceptions.SSLError:
            if attempt < 2:
                print(f"SSL error, retrying... (attempt {attempt + 2}/3)")
                time.sleep(2)
            else:
                # Try without SSL verification as last resort
                print("Trying without SSL verification...")
                response = requests.get(
                    zip_url,
                    stream=True,
                    verify=False,
                    timeout=DOWNLOAD_TIMEOUT,
                )
                break
        except requests.RequestException as exc:
            raise Exception(f"Download failed: {exc}") from exc

    if response is None:
        raise Exception("Download failed before receiving a response")
    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}")
    
    zip_path = output_dir / "result.zip"
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Extracting to: {output_dir}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    zip_path.unlink()
    
    # Find markdown file
    md_files = list(output_dir.rglob("*.md"))
    if md_files:
        return md_files[0]
    return None

def resolve_output_dir(file_arg, explicit_output, config_output_dir):
    """Resolve where parsed results should be extracted."""
    if explicit_output:
        return Path(explicit_output).expanduser()

    if file_arg and not is_url(file_arg):
        source_path = Path(file_arg).expanduser().resolve()
        # Keep outputs beside the source document, but isolate them in a
        # dedicated folder because MinerU extracts generic names like full.md.
        return source_path.parent / f"{source_path.stem}_mineru_output"

    return Path(config_output_dir).expanduser()

def main():
    parser = argparse.ArgumentParser(
        description="Parse documents using MinerU Cloud API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf --wait
  %(prog)s https://example.com/doc.pdf --wait
  %(prog)s document.pdf --ocr --language en --wait
  %(prog)s document.pdf --pages "1-10" --formats docx html --wait
  %(prog)s --set-token YOUR_TOKEN
        """
    )
    
    parser.add_argument("file", nargs='?', help="File path or URL to parse")
    parser.add_argument("-o", "--output",
                       help="Output directory (defaults to a sibling folder beside local files)")
    parser.add_argument("-m", "--model", choices=["pipeline", "vlm", "MinerU-HTML"],
                       help="Model version")
    parser.add_argument("-l", "--language", help="Language code (ch, en, etc.)")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR")
    parser.add_argument("--no-formula", action="store_true", help="Disable formula recognition")
    parser.add_argument("--no-table", action="store_true", help="Disable table recognition")
    parser.add_argument("--pages", help="Page ranges (e.g., '1-10,15,20-25')")
    parser.add_argument("--formats", nargs='+', choices=["docx", "html", "latex"],
                       help="Additional output formats")
    parser.add_argument("--wait", action="store_true", help="Wait for completion and download results")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")
    parser.add_argument("--set-token", help="Set API token in config")
    parser.add_argument("--show-config", action="store_true", help="Show current configuration")
    parser.add_argument("--check-task", help="Check task status by task ID")
    parser.add_argument("--check-batch", help="Check batch status by batch ID")
    
    args = parser.parse_args()
    
    try:
        config = load_config()
        
        # Handle --set-token
        if args.set_token:
            config['api_token'] = args.set_token
            save_config(config)
            print(f"✓ API token saved to: {CONFIG_FILE}")
            return 0
        
        # Handle --show-config
        if args.show_config:
            safe_config = dict(config)
            safe_config["api_token"] = mask_secret(resolve_api_token(config))
            safe_config["api_token_source"] = (
                "environment"
                if any(os.environ.get(key, "").strip() for key in TOKEN_ENV_KEYS)
                else "config"
            )
            print(json.dumps(safe_config, indent=2))
            return 0

        # Check existing task or batch status without creating a new one.
        if args.check_task:
            config["api_token"] = resolve_api_token(config)
            if not config["api_token"]:
                print("Error: API token not configured", file=sys.stderr)
                print(f"Set token with: {sys.argv[0]} --set-token YOUR_TOKEN", file=sys.stderr)
                print("Or export one of: MINERU_TOKEN / MINERU_API_TOKEN / MINERU_API_KEY", file=sys.stderr)
                return 1
            print(json.dumps(get_task_status(config, args.check_task), indent=2, ensure_ascii=False))
            return 0

        if args.check_batch:
            config["api_token"] = resolve_api_token(config)
            if not config["api_token"]:
                print("Error: API token not configured", file=sys.stderr)
                print(f"Set token with: {sys.argv[0]} --set-token YOUR_TOKEN", file=sys.stderr)
                print("Or export one of: MINERU_TOKEN / MINERU_API_TOKEN / MINERU_API_KEY", file=sys.stderr)
                return 1
            print(json.dumps(get_batch_status(config, args.check_batch), indent=2, ensure_ascii=False))
            return 0

        # Validate token
        config['api_token'] = resolve_api_token(config)
        if not config['api_token']:
            print("Error: API token not configured", file=sys.stderr)
            print(f"Set token with: {sys.argv[0]} --set-token YOUR_TOKEN", file=sys.stderr)
            print("Or export one of: MINERU_TOKEN / MINERU_API_TOKEN / MINERU_API_KEY", file=sys.stderr)
            return 1
        
        # Validate file argument
        if not args.file:
            parser.print_help()
            return 1
        
        # Prepare kwargs
        kwargs = {
            'model': args.model,
            'language': args.language,
            'ocr': args.ocr,
            'formula': not args.no_formula,
            'table': not args.no_table,
            'page_ranges': args.pages,
            'extra_formats': args.formats
        }
        
        # Create task
        if is_url(args.file):
            task_id = create_task_from_url(config, args.file, **kwargs)
            print(f"✓ Task created: {task_id}")
            
            if args.wait:
                print("\nWaiting for completion...")
                result = wait_for_completion(config, task_id=task_id, timeout=args.timeout)
                
                output_dir = resolve_output_dir(args.file, args.output, config['output_dir'])
                md_file = download_and_extract(result['full_zip_url'], output_dir)
                
                print(f"\n✓ Parsing completed!")
                print(f"Output directory: {output_dir}")
                if md_file:
                    print(f"Markdown file: {md_file}")
                    print_content_preview(md_file)
            else:
                print_follow_up_command("--check-task", task_id)
        
        else:
            batch_id = upload_and_create_task(config, args.file, **kwargs)
            
            if args.wait:
                print("\nWaiting for completion...")
                result = wait_for_completion(config, batch_id=batch_id, timeout=args.timeout)
                
                output_dir = resolve_output_dir(args.file, args.output, config['output_dir'])
                md_file = download_and_extract(result['full_zip_url'], output_dir)
                
                print(f"\n✓ Parsing completed!")
                print(f"Output directory: {output_dir}")
                if md_file:
                    print(f"Markdown file: {md_file}")
                    print_content_preview(md_file)
            else:
                print_follow_up_command("--check-batch", batch_id)
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
