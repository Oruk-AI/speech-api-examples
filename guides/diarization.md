# Transcription with diarization

Canonical guide: [Orukeet transcription with diarization](https://oruk.ai/guides/orukeet-transcription-diarization).

Complete the root [installation and sample check](../README.md#install-and-get-the-sample), then set `ORUK_API_KEY` in your environment. From the repository root:

```sh
python examples/orukeet-api.py samples/grocery.wav --diarize > results/diarization.json
```

This sends one `POST /v1/audio/transcriptions` with `model=oruk-orukeet` and diarization enabled. Diarization adds $0.004 per audio minute to base transcription and uses the same Orukeet allowance. Limits remain 60 seconds and 4 MiB for the whole multipart request. Check [current subscription terms](https://oruk.ai/pricing).

[Actual saved output](../examples/acquisition/orukeet-diarization.json) · [Provenance](../examples/acquisition/orukeet-diarization-provenance.json). Captured November 11, 2026 by a direct Node HTTP request with the same model/options/sample. The first returned turn spans `0.185`–`4.305` seconds with `speaker: "speaker_0"`. Speaker labels identify clusters within the recording, not real-world identities. Turn boundaries are not word timestamps or an accuracy guarantee.

Keep full JSON; inspect `diarized`, `speakers` and `segments` rather than assuming every recording contains multiple speakers. Future output can differ. Legacy recorded `usage` fields are not subscription invoice totals. Errors and uncertain transport outcomes are handled without automatic retries; see [error handling](../README.md#errors-and-production-integration).
