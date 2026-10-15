/* 定位某个元素并截图：node find_shot.js <port> <url> <selector> <out.png> */
const fs = require('fs');
const http = require('http');
const [PORT, URL_, SEL, OUT] = process.argv.slice(2);

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
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
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 300));
  await send('Page.navigate', { url: URL_ });
  await new Promise(r => setTimeout(r, 2500));

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception||{}).description);
    return r.result.result.value;
  };

  const top = await ev(`(()=>{const e=document.querySelector(${JSON.stringify(SEL)});
      if(!e) return -1; const y = e.getBoundingClientRect().top + window.scrollY - 24; window.scrollTo(0, y); return Math.round(y);})()`);
  if (top === -1) { console.error('selector not found: ' + SEL); process.exit(1); }
  console.log('scrolled to y=' + top);
  await new Promise(r => setTimeout(r, 1200));
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(OUT, Buffer.from(r.result.data, 'base64'));
  console.log('saved ' + OUT);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
