#!/usr/bin/env python3
import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG_PATH = SKILL_ROOT / "config.local.json"
DEFAULT_BASE_URL = "http://10.15.46.72:8010/v1"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_OUTPUT = "outputs/imagegen/sasu-image2.png"
ALLOWED_SIZES = {
    "1024x1024",
    "1024x1536",
    "1536x1024",
    "2048x1152",
    "2048x2048",
}


def ensure_openai():
    try:
        from openai import OpenAI  # noqa: F401
        return
    except ImportError:
        pass

    deps = SKILL_ROOT / ".python-deps"
    deps.mkdir(parents=True, exist_ok=True)
    if str(deps) not in sys.path:
        sys.path.insert(0, str(deps))

    try:
        from openai import OpenAI  # noqa: F401
        return
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--target", str(deps), "openai"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        sys.path.insert(0, str(deps))


def extract_b64(response):
    data = getattr(response, "data", None)
    if not data:
        raise RuntimeError("Image API returned no image data")
    first = data[0]
    b64 = getattr(first, "b64_json", None)
    if b64:
        return b64
    url = getattr(first, "url", None)
    if url:
        raise RuntimeError(f"Image API returned a URL instead of base64 output: {url}")
    raise RuntimeError("Image API response did not include b64_json or url")


def load_local_config():
    if not LOCAL_CONFIG_PATH.exists():
        return {}

    try:
        return json.loads(LOCAL_CONFIG_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {LOCAL_CONFIG_PATH}: {exc}") from exc


def load_runtime_defaults():
    local_config = load_local_config()
    model = os.getenv("SASU_IMAGE2_MODEL") or local_config.get("model") or DEFAULT_MODEL
    api_key = os.getenv("SASU_IMAGE2_API_KEY") or local_config.get("api_key")
    base_url = os.getenv("SASU_IMAGE2_BASE_URL") or local_config.get("base_url") or DEFAULT_BASE_URL
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def require_api_key(runtime_config):
    if runtime_config.get("api_key"):
        return runtime_config
    raise SystemExit(
        "Missing SASU image2 API key. Set SASU_IMAGE2_API_KEY or create "
        f"{LOCAL_CONFIG_PATH}."
    )


def resolve_output_path(output_arg):
    out = Path(output_arg)
    if out.is_dir():
        raise SystemExit(f"Output path points to a directory, not a file: {out}")
    return out


def validate_size(size):
    if size not in ALLOWED_SIZES:
        allowed = ", ".join(sorted(ALLOWED_SIZES))
        raise SystemExit(f"Unsupported size '{size}'. Supported sizes: {allowed}")


def write_image_bytes(out_path, image_b64):
    out_path.write_bytes(base64.b64decode(image_b64))


def main():
    parser = argparse.ArgumentParser(description="Generate an image via SASU image2.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", default=DEFAULT_OUTPUT)
    parser.add_argument("--size", default="1024x1536")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true", help="Validate config and arguments without calling the API")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    validate_size(args.size)
    out = resolve_output_path(args.out)
    if out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {out}. Pass --force to replace it.")
    out.parent.mkdir(parents=True, exist_ok=True)

    runtime_config = load_runtime_defaults()
    model = args.model or runtime_config["model"]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "out": str(out),
                    "size": args.size,
                    "quality": args.quality,
                    "model": model,
                    "base_url": runtime_config["base_url"],
                },
                indent=2,
            )
        )
        return

    runtime_config = require_api_key(runtime_config)
    ensure_openai()
    from openai import OpenAI

    client = OpenAI(api_key=runtime_config["api_key"], base_url=runtime_config["base_url"])
    print(f"Calling SASU image2 API with model={model}, size={args.size}, quality={args.quality}", file=sys.stderr)
    try:
        response = client.images.generate(
            model=model,
            prompt=args.prompt,
            size=args.size,
            quality=args.quality,
            n=1,
            output_format="png",
        )
    except Exception as exc:
        raise SystemExit(f"SASU image2 API request failed: {exc}") from exc

    image_b64 = extract_b64(response)
    write_image_bytes(out, image_b64)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
