# Fourier 2B English transcription (`oruk-fourier-2b`)

Canonical docs: [Oruk models](https://oruk.ai/models#model-comparison) · [Benchmarks](https://oruk.ai/benchmarks) · [Pricing](https://oruk.ai/pricing) · [Hugging Face model card](https://huggingface.co/oruk/oruk-fourier-2b).

`oruk-fourier-2b` serves the exact released [`oruk/oruk-fourier-2b`](https://huggingface.co/oruk/oruk-fourier-2b) BF16 checkpoint (revision `8c2a8871f1304aa2f634da4fb95e24438c4945b9`) behind Oruk's OpenAI-compatible `POST /v1/audio/transcriptions` endpoint.

- **Rate:** **$0.0080 / audio minute** (`$0.48/hr`, billed per audio second, 1 s minimum, from the shared speech-understanding allowance).
- **Input limits:** English audio (`en`, `en-US`, `en-GB`; WAV, FLAC, MP3, M4A, OGG, WebM), up to **30 MiB** and **60 minutes (3,600 s)** per request via server-side chunking.
- **Verified English accuracy:** Live on the Hugging Face Open ASR Leaderboard (`v1.16.3`, [`open_asr_leaderboard#298`](https://github.com/huggingface/open_asr_leaderboard/pull/298)) at **#7 / 68 overall** and **#1 single-model open-weights** (**5.52%** 9-dataset avg WER / **4.95%** 7-split public English mean vs. **5.75%** base `Qwen/Qwen3-ASR-1.7B-hf`; default 3-beam vs. greedy base), plus **10.92%** Open ASR English Long-Form avg WER, **#1/16** on SpeechColab GigaSpeechBench English Accents (`12.73%`) and Vertical-Domain (`6.09%`), **6.33% (#2/35)** on MERaLiON AudioBench `ASR-English`, and **8.57% WER (#4/43)** / **3.02% Canonical M-WER (#8/43)** on Omi Health PriMock57.

## cURL

Set `ORUK_API_KEY` in your environment ([sign up](https://oruk.ai/auth/signup) · [API keys](https://oruk.ai/account/api-keys)), then run:

```sh
curl --fail-with-body --connect-timeout 10 --max-time 120 \
  https://speech-api.oruk.ai/v1/audio/transcriptions \
  -H "Authorization: Bearer $ORUK_API_KEY" \
  -H "X-Request-ID: $(uuidgen)" \
  -F model=oruk-fourier-2b \
  -F language=en \
  -F response_format=json \
  -F file=@samples/grocery.wav
```

## Python (standard library only)

Complete the sample download from the [root README](../README.md#install-and-get-the-sample) (no extra pip packages are required for this script), set `ORUK_API_KEY`, and run from the repository root:

```sh
python3 examples/fourier-2b-api.py samples/grocery.wav > results/fourier-2b.json
```

Pass `--response-format text` for plain text or `--response-format verbose_json` for full response metadata (`model_revision`, `duration`, `usage`). Missing keys/files and files exceeding 30 MiB (minus 64 KiB multipart overhead) are rejected locally. API errors print status, code, and request ID to stderr; transport failures do not retry automatically. See [error handling](../README.md#errors-and-production-integration).
