# Replace a Hume file-analysis step

Canonical guide: [Hume Expression Measurement migration](https://oruk.ai/compare/hume-expression-measurement-alternative).

This example uses Oruk's native synchronous `POST /v1/audio/analysis`, with `model=oruk-resonance` and diarization. It is not a Hume SDK/base-URL swap, and it does not supply EVI/TTS, face/video, text-sentiment or Audio Decisions compatibility. Do not assume an Oruk-hosted `/compat/hume` runtime is available.

## Inspect the exact saved response

From the repository root, with Python 3.10+ (no key, SDK or network needed):

```sh
python3 examples/hume-to-oruk.py --saved-response examples/acquisition/hume-replacement.json
```

The script validates the response model/task, then prints the model, duration, transcript and first segment. It does not alter the saved file. [Full JSON](../examples/acquisition/hume-replacement.json) · [Provenance](../examples/acquisition/hume-replacement-provenance.json).

This exact script ran once on November 11, 2026, **20:21:45.546–20:21:55.629 UTC**, using Python 3.12.13 and SDK 0.2.15, with exit 0 and no retry. The saved response has duration `14.45`; its first segment spans `0.185`–`4.325` seconds, selected emotion `disappointed` (`0.8679338097572327`) and style `casual` (`0.8688268065452576`). These are model annotations, not ground truth. No immutable model revision is exposed, and future responses may differ. Raw legacy-account `usage` fields are preserved; they are not a subscription invoice.

## Make one live request

Complete the root [installation and sample check](../README.md#install-and-get-the-sample), then set `ORUK_API_KEY` in your environment:

```sh
python examples/hume-to-oruk.py --audio samples/grocery.wav --output results/analysis.json
```

The output path must not exist. The script saves the complete response before printing an excerpt. Live mode needs eligible API access and speech-understanding allowance or existing credits. Supported English audio is limited to 30 MB and 60 minutes. It never retries automatically. API status/code/request ID are reported where available; transport failures may leave a processed request, so check Usage before resending. Keep sensitive recordings and results access-controlled.

## Adapt the parser deliberately

| Existing integration | Change for this example |
| --- | --- |
| Legacy Hume batch jobs and nested prosody/grouped predictions | Replace polling with one synchronous Oruk request and parse the native JSON object's `segments` |
| Current Hume Expression Measurement v1 audio upload | Replace `https://api.cloud.hume.ai/v1/expression/audio/file` with Oruk's native analysis endpoint and change request/output parsers |
| Current Hume `utterances`/`measurements`, millisecond spans | Parse Oruk second-based `segments`; divide source milliseconds by 1,000 only for timeline alignment |
| Hume expression/voice-attribute taxonomies | Evaluate Oruk's selected emotion/style labels; there is no validated label/score/threshold mapping |

A missing Oruk label is not a zero score. Resonance 1 emotion can use a highest-score fallback; styles may be empty. Evaluate thresholds on representative permitted recordings instead of carrying Hume thresholds across.

Official sources reviewed November 11, 2026: [Hume overview](https://dev.hume.ai/expression-measurement/docs/overview), [audio upload](https://dev.hume.ai/expression-measurement/docs/audio/upload), [billing](https://dev.hume.ai/expression-measurement/docs/billing). Hume's current billing documentation describes a 10-second minimum per billable run; no numeric current tariff was verified, so this example makes no savings claim. [Oruk prices and allowances](https://oruk.ai/pricing).
