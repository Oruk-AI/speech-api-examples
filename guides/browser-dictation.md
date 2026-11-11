# Browser dictation with a backend key

Canonical guide: [Orukeet browser dictation](https://oruk.ai/guides/orukeet-browser-dictation).

Install Node.js 22+, set `ORUK_API_KEY` in your server environment, then run from the repository root:

```sh
node examples/orukeet-browser/server.mjs
```

To download just the browser example instead of cloning this repository:

```sh
mkdir orukeet-browser && cd orukeet-browser
curl --fail --location -O https://oruk.ai/examples/orukeet-browser/server.mjs
curl --fail --location -o index.html https://oruk.ai/examples/orukeet-browser/index.html.txt
node server.mjs
```

The HTML source is served as a text download and saved locally as `index.html`.

Open **http://127.0.0.1:8787** exactly. No npm install is required. The server downloads the licensed grocery sample and verifies its size/SHA-256 before listening. See [sample attribution](../examples/call-review-attribution.txt). The key stays on the server; the browser posts audio only to the local backend.

Choose **Transcribe sample**, or allow microphone access, record English speech and choose **Stop and transcribe**. The recorder stops at 55 seconds and rejects recordings over 3 MiB. This is a record-then-upload transcription demo, not incremental streaming. Supported recorder formats depend on the browser; use the sample button if recording is unavailable.

The page displays the full actual response of your request. [Saved transcription JSON](../examples/acquisition/orukeet-transcription.json) shows the same endpoint/model on this sample, captured November 11, 2026 with a direct Node HTTP request. It is not evidence that a browser microphone session was run. The saved transcript begins “I'm sorry. The price of food has gone up so much.” Request IDs, timings and transcript wording can vary. Preserve the [provenance](../examples/acquisition/orukeet-transcription-provenance.json); legacy saved cost fields are not subscription invoice totals.

The local server checks exact Host and Origin, allows one active transcription, rejects unsupported/oversized/empty uploads, bounds upload and API waits, and disables automatic inference retries. HTTP errors appear in the UI. If a request times out after submission, check Usage before resending. Use Ctrl-C to stop the server. Do not expose this demo publicly; a production backend needs authentication, quotas and abuse controls.
