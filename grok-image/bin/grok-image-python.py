#!/usr/bin/env python3
"""Fallback Grok Imagine image generator for OpenAI-compatible gateways."""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "grok-imagine-image-quality"
DEFAULT_API_URL = "https://api.x.ai"
SIZES = ("1024x1024", "1536x1024", "1024x1536")
QUALITIES = ("low", "medium", "high", "auto")


def endpoint(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    return f"{base_url}/images/generations" if base_url.endswith("/v1") else f"{base_url}/v1/images/generations"


def output_paths(out: str, n: int) -> list[Path]:
    path = Path(out)
    if n == 1:
        return [path]
    suffix = path.suffix or ".png"
    stem = path.with_suffix("") if path.suffix else path
    return [Path(f"{stem}-{index}{suffix}") for index in range(1, n + 1)]


def decode_image(item: dict, timeout: float) -> bytes:
    if item.get("b64_json"):
        try:
            return base64.b64decode(item["b64_json"])
        except Exception as exc:  # pragma: no cover - defensive API error path
            raise RuntimeError("API returned invalid base64 image data") from exc
    if item.get("url"):
        try:
            with urlopen(item["url"], timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError("could not download image URL") from exc
    raise RuntimeError("API image entry contains neither b64_json nor url")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--size", choices=SIZES, default="1024x1024")
    parser.add_argument("--quality", choices=QUALITIES, default="low")
    parser.add_argument("--n", type=int, choices=range(1, 11), default=1)
    parser.add_argument("--model", default=os.getenv("GROK_IMAGE_MODEL", MODEL))
    parser.add_argument("--timeout", type=float, default=150)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base_url = os.getenv("GROK_API_URL", DEFAULT_API_URL)
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "n": args.n,
        "response_format": "b64_json",
    }
    paths = output_paths(args.out, args.n)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "endpoint": endpoint(base_url), "payload": payload, "outputs": [str(p) for p in paths]}, ensure_ascii=False, indent=2))
        return 0

    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        print("ERROR: GROK_API_KEY is not set.", file=sys.stderr)
        return 2

    request = Request(
        endpoint(base_url),
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "grok-image-python-fallback/1.0",
        },
    )

    try:
        with urlopen(request, timeout=args.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"NETWORK ERROR: {exc}", file=sys.stderr)
        return 1

    data = result.get("data") or []
    if not data:
        print("ERROR: API did not return data:", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, indent=2)[:4000], file=sys.stderr)
        return 1

    if len(data) != len(paths):
        print(f"ERROR: API returned {len(data)} image(s), expected {len(paths)}", file=sys.stderr)
        return 1

    try:
        images = [decode_image(item, args.timeout) for item in data]
        for path, image in zip(paths, images):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(image)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for path in paths:
        print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
