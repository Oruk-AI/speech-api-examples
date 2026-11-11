#!/usr/bin/env python3
"""Send one English recording to Oruk Resonance 1 and print its actual JSON.

Python 3.10+. Install the current SDK from https://oruk.ai/docs/sdks.
Set ORUK_API_KEY, then run: python emotion-api.py recording.wav
No automatic retry is made. Keep the printed request ID after a transport error.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import uuid

import httpx
from oruk import Oruk, OrukAPIError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--request-id", default=None, help="Optional trace ID for investigation; not an idempotency guarantee")
    args = parser.parse_args()
    key = os.environ.get("ORUK_API_KEY")
    if not key:
        parser.error("Set ORUK_API_KEY in the environment; do not put it in source.")
    if not args.file.is_file() or not 0 < args.file.stat().st_size <= 30_000_000:
        parser.error("Provide a nonempty supported English audio file no larger than 30 MB.")
    request_id = args.request_id or str(uuid.uuid4())
    print(f"Request ID: {request_id}", file=sys.stderr)
    try:
        with Oruk(api_key=key, max_retries=0, timeout=120) as client:
            result = client.emotions(
                args.file, model="oruk-resonance", request_id=request_id,
            )
    except OrukAPIError as error:
        print(json.dumps({"status": error.status, "code": error.code,
                          "request_id": error.request_id or request_id}), file=sys.stderr)
        print("Check your key, active trial or plan, and allowance. For 429/5xx, follow the production retry guide; this script did not retry.", file=sys.stderr)
        return 1
    except httpx.RequestError:
        print("Transport failed; completion is uncertain. Keep the request ID and check Usage before deciding whether to resend. A trace ID is not an idempotency guarantee.", file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print("Could not read the recording or parse a valid response; no credentials are printed.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
