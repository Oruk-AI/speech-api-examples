# Speech emotion recognition

Canonical guide: [Speech emotion recognition API](https://oruk.ai/speech-emotion-recognition-api#integrate).

Complete the root [installation and sample check](../README.md#install-and-get-the-sample), then set `ORUK_API_KEY` in your environment. From the repository root:

```sh
python examples/emotion-api.py samples/grocery.wav > results/emotions.json
```

This sends one `POST /v1/audio/emotions` with `model=oruk-resonance` (Resonance 1). Use supported English WAV, FLAC, MP3, M4A, OGG or WebM, at most 30 MB and 60 minutes. It uses the separate speech-understanding allowance. Resonance 2 is a different preview contract and requires approval for new organizations; this script does not request it.

[Actual saved output](../examples/acquisition/resonance-emotions.json) · [Provenance](../examples/acquisition/resonance-emotions-provenance.json). Captured November 11, 2026 by a direct Node HTTP request with the same model/task/sample. The response task is `emotion` (singular), duration `14.45`, and `text` is `null`. Selected emotion labels are `frustrated`, `angry` and `disappointed`; the saved `frustrated` score is `0.9845753908157349`. Speaker and transcript fields are null for this emotion-only request.

These are model annotations, not ground truth or proof of private feelings. A missing label has not been selected; its score is not known to be zero. Future calls may differ. Preserve raw JSON and do not use the legacy saved cost fields as subscription invoice totals.

The script prints a trace ID and handles API/transport/file/response errors. An optional `--request-id` is for tracing, not a promise of idempotency. It does not retry automatically. See [error handling](../README.md#errors-and-production-integration).
