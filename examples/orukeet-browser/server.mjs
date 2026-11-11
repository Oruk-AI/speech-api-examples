// Node.js 22+. Local demo only; do not expose this key-backed server publicly.
// Canonical guide: https://oruk.ai/guides/orukeet-browser-dictation
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';

const host = '127.0.0.1:8787';
const origin = 'http://' + host;
const maximum = 3 * 1024 * 1024; // Leaves space under the API's 4 MiB multipart limit.
const sampleUrl = 'https://oruk.ai/samples/conversations/02-grocery-prices.wav';
const send = (res, status, value) => {
  if (res.destroyed || res.writableEnded) return;
  res.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff', 'Connection': 'close' });
  res.end(JSON.stringify(value));
};

// A slow or oversized upload must release the single request slot without
// forwarding a partial recording. The response closes the rejected connection.
function readAudio(req, timeoutMs) {
  return new Promise((resolve, reject) => {
    const chunks = []; let length = 0; let settled = false;
    const finish = (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      req.off('data', onData); req.off('end', onEnd);
      // Retain the error listener until this request is collected: an aborted
      // socket can emit error after aborted, including after we sent rejection.
      req.off('aborted', onAbort);
      if (error) { req.pause(); reject(error); } else resolve(chunks);
    };
    const failure = (status, message) => Object.assign(new Error(message), { status });
    const onData = chunk => {
      length += chunk.length;
      if (length > maximum) return finish(failure(413, 'Recording exceeds the demo 3 MiB limit.'));
      chunks.push(chunk);
    };
    const onEnd = () => finish(length ? null : failure(400, 'Recording is empty.'));
    const onError = () => finish(failure(400, 'Upload failed before inference.'));
    const onAbort = () => finish(failure(400, 'Upload ended before the recording was complete.'));
    const timer = setTimeout(() => finish(failure(408, 'Upload timed out before inference.')), timeoutMs);
    req.on('data', onData); req.on('end', onEnd);
    req.on('error', onError); req.on('aborted', onAbort);
  });
}

// Exported for offline tests. The command below binds only the loopback address.
export function createDemoServer({ key, audio, html, fetcher = fetch, uploadTimeoutMs = 30000 }) {
  if (!key) throw new Error('Set ORUK_API_KEY in your environment.');
  let active = false;
  return createServer(async (req, res) => {
    // Exact Host and Origin checks prevent a foreign site from spending this demo key.
    if (req.headers.host !== host) return send(res, 403, { error: 'Unexpected host.' });
    if (req.method === 'GET' && req.url === '/') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
        'Content-Security-Policy': "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'" });
      return res.end(html);
    }
    if (req.method === 'GET' && req.url === '/sample.wav') {
      res.writeHead(200, { 'Content-Type': 'audio/wav', 'Content-Length': audio.length,
        'X-Content-Type-Options': 'nosniff' });
      return res.end(audio);
    }
    if (req.method !== 'POST' || req.url !== '/transcribe') return send(res, 404, { error: 'Not found.' });
    if (req.headers.origin !== origin || req.headers['x-oruk-demo'] !== '1') return send(res, 403, { error: 'Same-origin demo requests only.' });
    if (active) return send(res, 429, { error: 'Wait for the current request.' });
    const mime = req.headers['content-type']?.split(';')[0];
    if (!['audio/wav', 'audio/webm', 'audio/ogg', 'audio/mp4'].includes(mime)) return send(res, 415, { error: 'Unsupported recorder format.' });
    if (Number(req.headers['content-length']) > maximum) return send(res, 413, { error: 'Recording exceeds the demo 3 MiB limit.' });
    active = true;
    const requestId = randomUUID();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 120000);
    let issued = false;
    try {
      const chunks = await readAudio(req, uploadTimeoutMs);
      const form = new FormData();
      form.set('model', 'oruk-orukeet');
      form.set('file', new Blob(chunks, { type: mime }), 'recording.' + ({'audio/wav':'wav','audio/webm':'webm','audio/ogg':'ogg','audio/mp4':'m4a'}[mime]));
      issued = true;
      const upstream = await fetcher('https://speech-api.oruk.ai/v1/audio/transcriptions', {
        method: 'POST', headers: { Authorization: 'Bearer ' + key, 'X-Request-ID': requestId },
        body: form, signal: controller.signal, redirect: 'error',
      });
      const body = await upstream.json();
      if (!upstream.ok) {
        const code = body.error?.code || body.code;
        return send(res, upstream.status, { error: typeof code === 'string' && /^[a-z0-9_]{1,80}$/.test(code) ? code : 'API request failed', request_id: requestId });
      }
      return send(res, 200, body);
    } catch (error) {
      if (!issued && error.status) return send(res, error.status, { error: error.message });
      return send(res, 502, { error: issued ? 'Request outcome unknown. No automatic retry was made.' : 'Upload failed before inference.', request_id: requestId });
    } finally { clearTimeout(timer); active = false; }
  });
}

async function main() {
  const key = process.env.ORUK_API_KEY;
  if (!key) throw new Error('Set ORUK_API_KEY in your environment.');
  const sample = await fetch(sampleUrl, { signal: AbortSignal.timeout(15000), redirect: 'error' });
  if (!sample.ok) throw new Error('Sample download failed.');
  const audio = Buffer.from(await sample.arrayBuffer());
  if (audio.length !== 1387244 || createHash('sha256').update(audio).digest('hex') !== '72b99dab1f5670436f542ec41269d9e41a6bd5367b74a6d36427ca846a421a99') throw new Error('Sample checksum mismatch.');
  const html = await readFile(new URL('./index.html', import.meta.url));
  createDemoServer({ key, audio, html }).listen(8787, '127.0.0.1', () => console.log('Open ' + origin + '. Local demo only; Ctrl-C to stop.'));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(() => { console.error('Could not start the local demo. Check ORUK_API_KEY, sample connectivity and port 8787. No credentials are printed.'); process.exitCode = 1; });
}
