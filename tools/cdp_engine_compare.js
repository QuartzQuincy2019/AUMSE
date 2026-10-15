/* Definitive engine comparison.
   Switch engines in place and screenshot the SAME fixed viewport rectangle, then
   crop both to their ink bounding box. If the two engines render the same glyphs,
   the ink crops will be identical (up to their start offset). */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9333);
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
  const send = (m, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 4000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };

  /* widest fixed window inside the right pane, avoiding the palette/status bars */
  const BOX = { x: 400, y: 110, width: 700, height: 560 };
  const grab = async (name) => {
    const r = await send('Page.captureScreenshot', { format: 'png', clip: Object.assign({ scale: 2 }, BOX) });
    fs.writeFileSync(OUT + '\\' + name, Buffer.from(r.result.data, 'base64'));
  };

  await ev(`(()=>{const s=document.getElementById('engine'); s.value='wm'; s.dispatchEvent(new Event('change')); return 1;})()`);
  await new Promise(r => setTimeout(r, 900));
  await grab('_cmp_a.png');

  await ev(`(()=>{const s=document.getElementById('engine'); s.value='rot'; s.dispatchEvent(new Event('change')); return 1;})()`);
  await new Promise(r => setTimeout(r, 900));
  await grab('_cmp_b.png');

  console.log('captured both engines into viewport box ' + JSON.stringify(BOX));
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
