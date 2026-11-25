#!/usr/bin/env python3
"""Transcribe English audio with Oruk Fourier 2B on the hosted Speech API.

Python 3.10+ (standard library only; no extra packages required).
Set ORUK_API_KEY in your environment, then run:
  python3 examples/fourier-2b-api.py samples/grocery.wav

Prints the complete JSON (or plain text with --response-format text) to stdout
and the request ID to stderr. No automatic retry is made after an uncertain
request. Keep the printed request ID if a transport error occurs.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import uuid

DEFAULT_BASE_URL = "https://speech-api.oruk.ai"
MODEL_ID = "oruk-fourier-2b"
MAX_REQUEST_BYTES = 30 * 1024 * 1024
MULTIPART_OVERHEAD_BYTES = 64 * 1024
ALLOWED_LANGUAGES = ("en", "en-US", "en-GB")
ALLOWED_FORMATS = ("json", "verbose_json", "text")


def encode_multipart(
    fields: list[tuple[str, str]],
    file_field: str,
    file_path: Path,
) -> tuple[bytes, str]:
    """Encode multipart/form-data using the Python standard library."""
    boundary = f"oruk-{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    safe_name = file_path.name.replace("\\", "_").replace('"', "_")

    parts: list[bytes] = []
    for name, value in fields:
        parts.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n"
            ).encode("utf-8")
        )
    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{file_field}"; filename="{safe_name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    parts.append(file_path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, help="Path to an English audio file (<= 30 MiB, <= 60 min)")
    parser.add_argument(
        "--language",
        default="en",
        choices=ALLOWED_LANGUAGES,
        help="English locale hint sent to the API (default: en)",
    )
    parser.add_argument(
        "--response-format",
        default="json",
        choices=ALLOWED_FORMATS,
        help="Response format: json, verbose_json, or text (default: json)",
    )
    parser.add_argument(
        "--request-id",
        default=None,
        help="Optional trace ID for investigation; not an idempotency guarantee",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ORUK_BASE_URL", DEFAULT_BASE_URL),
        help=f"Oruk Speech API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds (default: 120)",
    )
    args = parser.parse_args(argv)

    key = os.environ.get("ORUK_API_KEY")
    if not key:
        parser.error("Set ORUK_API_KEY in your environment; never put it in source.")
    if not args.audio.is_file():
        parser.error("Audio file does not exist.")
    file_size = args.audio.stat().st_size
    if not 0 < file_size <= MAX_REQUEST_BYTES - MULTIPART_OVERHEAD_BYTES:
        parser.error(
            "Use a nonempty audio file at most 30 MiB minus 64 KiB; the whole multipart request must fit 30 MiB."
        )

    request_id = args.request_id or str(uuid.uuid4())
    print(f"Request ID: {request_id}", file=sys.stderr)

    fields = [
        ("model", MODEL_ID),
        ("language", args.language),
        ("response_format", args.response_format),
    ]
    try:
        body, content_type = encode_multipart(fields, "file", args.audio)
    except OSError:
        print("Could not read the audio file; no request was sent.", file=sys.stderr)
        return 1

    url = f"{args.base_url.rstrip('/')}/v1/audio/transcriptions"
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": content_type,
            "X-Request-ID": request_id,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        err_body = err.read().decode("utf-8", errors="replace")
        err_code = None
        err_req_id = err.headers.get("X-Request-ID") or request_id
        try:
            parsed = json.loads(err_body)
            if isinstance(parsed, dict):
                err_obj = parsed.get("error") if isinstance(parsed.get("error"), dict) else parsed
                err_code = err_obj.get("code") or err_obj.get("type")
                err_req_id = parsed.get("request_id") or err_obj.get("request_id") or err_req_id
        except ValueError:
            pass
        print(
            json.dumps({"status": err.code, "code": err_code, "request_id": err_req_id}),
            file=sys.stderr,
        )
        print(
            "Check your key, active trial/plan allowance, and input limits. No retry was made.",
            file=sys.stderr,
        )
        return 1
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(
            f"{type(exc).__name__}; request {request_id}. Outcome may be unknown; check Usage before retrying. No retry was made.",
            file=sys.stderr,
        )
        return 1

    if args.response_format == "text":
        print(raw.rstrip("\n"))
        return 0

    try:
        parsed_ok = json.loads(raw)
    except ValueError:
        print(
            f"Invalid JSON response for request {request_id}; no credentials are printed.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(parsed_ok, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
