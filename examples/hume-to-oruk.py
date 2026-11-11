"""Replace an English Hume file-analysis step with native Oruk analysis.

Python 3.10+. Install the pinned SDK in the accompanying guide for live mode.
Code: MIT. Sample audio and saved output retain their separate CC BY attribution.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def excerpt(result: dict) -> dict:
    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object")
    if result.get("model") != "oruk-resonance" or result.get("task") != "analysis":
        raise ValueError("Expected a Resonance 1 analysis response")
    if not isinstance(result.get("segments"), list):
        raise ValueError("Response is missing its segments array")
    return {key: result[key] for key in ("model", "duration", "text")} | {
        "segments": result["segments"][:1]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio", type=Path, help="Submit one English recording")
    source.add_argument("--saved-response", type=Path, help="Inspect saved JSON, without a key or network")
    parser.add_argument("--output", type=Path, help="Save the full successful live response to a new file")
    args = parser.parse_args()
    try:
        if args.saved_response:
            if args.output:
                raise ValueError("--output is for live mode; keep the original saved response")
            if args.saved_response.stat().st_size > 16 * 1024 * 1024:
                raise ValueError("Saved response exceeds this example's 16 MiB limit")
            result = json.loads(args.saved_response.read_text(encoding="utf-8"))
        else:
            if not args.output or args.output.exists():
                raise ValueError("Live mode requires --output pointing to a new file")
            if not args.audio.is_file() or not 0 < args.audio.stat().st_size <= 30_000_000:
                raise ValueError("Use a nonempty local audio file no larger than 30 MB")
            key = os.environ.get("ORUK_API_KEY")
            if not key:
                raise ValueError("Set ORUK_API_KEY in your shell; never put it in this file")
            import httpx
            from oruk import Oruk, OrukAPIError
            try:
                with Oruk(api_key=key, max_retries=0, timeout=120) as client:
                    result = client.analyze(args.audio, model="oruk-resonance", diarize=True)
            except OrukAPIError as error:
                print(f"API request failed: HTTP {error.status}; code={error.code}; request_id={error.request_id}", file=sys.stderr)
                print("Check key/access, plan usage or input format. No automatic retry was made.", file=sys.stderr)
                return 1
            except httpx.RequestError:
                print("Transport failed; the server may have processed the request. Check usage before retrying.", file=sys.stderr)
                return 1
            # Preserve the entire response, including usage, before interpreting it.
            with args.output.open("x", encoding="utf-8") as output:
                json.dump(result, output, ensure_ascii=False, indent=2)
                output.write("\n")
        print(json.dumps(excerpt(result), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"Cannot complete this example: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
