# Python transcription

Canonical guide: [Orukeet Python transcription](https://oruk.ai/guides/orukeet-python-transcription).

Complete the root [installation and sample check](../README.md#install-and-get-the-sample), then set `ORUK_API_KEY` in your environment. From the repository root:

```sh
python examples/orukeet-api.py samples/grocery.wav > results/transcription.json
```

This sends one `POST /v1/audio/transcriptions` with `model=oruk-orukeet`. It prints the full JSON to stdout and a request ID to stderr. Exit 0 means a parsed successful response; on failure the output file may be empty. Base transcription uses the Orukeet allowance. Supported inputs are short English recordings up to 60 seconds and 4 MiB total multipart; the client reserves 64 KiB for overhead.

[Actual saved output](../examples/acquisition/orukeet-transcription.json) · [Provenance](../examples/acquisition/orukeet-transcription-provenance.json). Captured November 11, 2026 by a direct Node HTTP request with the same model/task/sample. Its duration is `14.45`, task is `transcription`, and text begins “I'm sorry. The price of food has gone up so much.” Its plain-transcription `segments` array is empty; do not invent word timestamps from it. Future requests may differ.

The saved account's legacy `usage` cost fields are not subscription invoice totals. Missing keys/files and excessive file size are rejected locally. API errors print status/code/request ID; transport failures can have uncertain outcomes. No automatic retry occurs. See [error handling](../README.md#errors-and-production-integration).
