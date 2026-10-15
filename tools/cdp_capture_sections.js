/* Capture process.html section by section for review. */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9555);
const OUTDIR = process.argv[3];

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
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1300, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/process.html' });
  await new Promise(r => setTimeout(r, 3500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    return r.result.result.value;
  };
  const H = await ev('document.documentElement.scrollHeight');
  console.log('doc height =', H);

  const shots = Math.min(12, Math.ceil(H / 1000));
  for (let i = 0; i < shots; i++) {
    await ev(`window.scrollTo(0, ${i * 1000}); 1`);
    await new Promise(r => setTimeout(r, 350));
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${OUTDIR}\\_sec${String(i).padStart(2, '0')}.png`, Buffer.from(r.result.data, 'base64'));
  }
  console.log('captured', shots, 'sections');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
