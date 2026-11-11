# Oruk speech API examples

Small, runnable integrations for Oruk's hosted speech API. Python 3.10+ for file examples; Node.js 22+ for the browser demo. [API documentation](https://oruk.ai/docs) · [Current plans and allowances](https://oruk.ai/pricing).

| Integration | Run instructions | Canonical guide |
| --- | --- | --- |
| Python transcription | [Python recipe](guides/transcription.md) | [Orukeet Python transcription](https://oruk.ai/guides/orukeet-python-transcription) |
| Transcription with diarization | [Speaker recipe](guides/diarization.md) | [Orukeet speaker diarization](https://oruk.ai/guides/orukeet-transcription-diarization) |
| Browser dictation | [Browser recipe](guides/browser-dictation.md) | [Orukeet browser dictation](https://oruk.ai/guides/orukeet-browser-dictation) |
| Speech emotion recognition | [Emotion recipe](guides/emotion-recognition.md) | [Speech emotion recognition API](https://oruk.ai/speech-emotion-recognition-api#integrate) |
| Hume file-analysis migration | [Migration recipe](guides/hume-migration.md) | [Hume migration guide](https://oruk.ai/compare/hume-expression-measurement-alternative) |

## Install and get the sample

Run commands from this repository's root:

```sh
git clone https://github.com/Oruk-AI/speech-api-examples.git
cd speech-api-examples
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://oruk.ai/sdk/oruk-0.2.15-py3-none-any.whl
mkdir -p samples results
curl --fail --location -o samples/grocery.wav https://oruk.ai/samples/conversations/02-grocery-prices.wav
python -c "import hashlib,pathlib; p=pathlib.Path('samples/grocery.wav'); assert p.stat().st_size == 1387244; assert hashlib.sha256(p.read_bytes()).hexdigest() == '72b99dab1f5670436f542ec41269d9e41a6bd5367b74a6d36427ca846a421a99'; print('Sample verified')"
```

On Windows activate `.venv\Scripts\activate`. The versioned wheel installs the hosted client `oruk==0.2.15`; it is separate from the downloadable Orukeet model/runtime. The browser demo needs no npm packages and downloads and verifies this same sample itself.

The 14.45-second recording is from **Open Yap 1K, The Agentic Data Company (2026)**, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), excerpted and downmixed by Oruk. [Original dataset](https://huggingface.co/datasets/TheAgenticDataCompany/open-yap-1k) · [Full attribution](examples/call-review-attribution.txt). Preserve that notice with redistributed audio and transcript-derived results. The creators do not endorse Oruk or these outputs. Audio is downloaded rather than bundled here.

## Authentication and cost

Set `ORUK_API_KEY` in your environment using your normal secret-management method. Keep the key on your local machine or backend, never in a browser script, committed file, command-line argument or shared output. This package reads the environment directly; it does not load `.env` files. Create a key at [API keys](https://oruk.ai/account/api-keys).

Live calls require eligible API access and an active trial, subscription allowance or existing credit entitlement. A subscription is required for new ongoing API usage. Orukeet base transcription is $0.027 per audio hour, with its own subscription allowance; diarization adds $0.004 per minute from that allowance. Resonance 1 uses the separate speech-understanding allowance. Check [current prices, caps and trial terms](https://oruk.ai/pricing) before submitting audio. These are metered requests, including sample submissions.

You can inspect the Hume migration response without an API key, SDK install or network request:

```sh
python3 examples/hume-to-oruk.py --saved-response examples/acquisition/hume-replacement.json
```

## Actual saved outputs

All four JSON files in [`examples/acquisition`](examples/acquisition/) preserve actual responses captured on **November 11, 2026 (UTC)**. Their adjacent provenance records contain endpoint, request options, timestamps and sample/response SHA-256 values. The transcription, diarization and emotion captures were direct multipart **Node.js HTTP requests**, not Python captures. The Hume replacement capture came from the exact included Python script using Python 3.12.13 and SDK 0.2.15. Do not describe these as a browser microphone validation or a comparative quality benchmark.

The captures used an existing legacy prepaid demonstration account. Returned `usage`, reference rates and estimated costs remain unchanged; they are **not subscription invoice totals**. New requests can return different IDs, timings, transcripts and scores. A response does not expose an immutable model revision. Scores are acoustic model annotations, not facts about a speaker's private feelings; validate on your own representative data.

## Errors and production integration

All examples disable automatic inference retries. File recipes reject missing/oversized inputs. Orukeet requires short English audio: at most 60 seconds and 4 MiB for the whole multipart request; the Python example reserves 64 KiB of that limit for request overhead. Resonance 1 accepts supported English recordings up to 30 MB and 60 minutes. The browser demo caps recordings at 55 seconds and 3 MiB.

For 401/403, fix authentication or access; for usage/budget failures, check your account; for 413/415, correct the input. On 429/5xx, follow the [production retry guide](https://oruk.ai/docs/production). After a timeout or disconnect, the server may have processed the request: preserve the request ID where present and check Usage before deciding whether to send again. Trace IDs are not a general idempotency guarantee.

The browser server binds only `127.0.0.1:8787`, verifies Host/Origin, permits one request at a time, and keeps the API key server-side. It is a local demo. Before any public deployment, add your own authenticated users, quotas, storage controls and abuse protection.

## Licensing

Example code and authored guides are [MIT licensed](LICENSE). The recording and source-derived transcript material retain their separate CC BY 4.0 attribution; the MIT license does not replace it. SDK dependencies retain their own licenses. No model weights are included.
