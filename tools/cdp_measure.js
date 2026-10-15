/* Objective shaping check via CDP:
   1. Does the browser CHANGE the glyph when MA is word-initial vs isolated?
      (if init/medi/fina work, the advance width and rendered pixels differ)
   2. Does vertical-lr keep Latin upright, and does rotate(90deg) flip it?

   Uses Range.getClientRects() so we measure what the engine actually laid out.
   Canvas cannot be used: Chromium never implemented ctx.fontFeatureSettings. */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9222);
const OUT = process.argv[3];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/report/_measure2.html' });
  await new Promise(r => setTimeout(r, 3500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };
  console.log(await ev('window.__report'));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(OUT + '\\_measure2.png', Buffer.from(shot.result.data, 'base64'));
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
