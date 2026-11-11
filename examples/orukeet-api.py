"""Transcribe short English audio with the Orukeet hosted preview.

Python 3.10+. Install the versioned SDK documented in the canonical guide:
https://oruk.ai/guides/orukeet-python-transcription
Set ORUK_API_KEY, then run: python orukeet-api.py sample.wav [--diarize]
Prints complete JSON to stdout. No automatic retry after an uncertain request.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import uuid

from oruk import Oruk, OrukAPIError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--diarize", action="store_true")
    args = parser.parse_args()
    key = os.environ.get("ORUK_API_KEY")
    if not key:
        parser.error("Set ORUK_API_KEY in your environment; never put it in source.")
    if not args.audio.is_file():
        parser.error("Audio file does not exist.")
    # Reserve 64 KiB for multipart fields and headers below the API 4 MiB cap.
    if not 0 < args.audio.stat().st_size <= 4 * 1024 * 1024 - 64 * 1024:
        parser.error("Use a nonempty file at most 4 MiB minus 64 KiB; the whole multipart request must fit 4 MiB.")
    request_id = str(uuid.uuid4())
    print(f"Request ID: {request_id}", file=sys.stderr)
    try:
        with Oruk(api_key=key, max_retries=0, timeout=120) as client:
            result = client.transcribe(
                args.audio, model="oruk-orukeet", diarize=args.diarize,
                request_id=request_id,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except OrukAPIError as error:
        print(json.dumps({"status": error.status, "code": error.code,
                          "request_id": error.request_id or request_id}), file=sys.stderr)
        print("Check the guide's error table before trying again. No retry was made.", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"{type(error).__name__}; request {request_id}. Outcome may be unknown; no retry was made.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
