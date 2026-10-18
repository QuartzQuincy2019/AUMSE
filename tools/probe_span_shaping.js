const http = require('http'), fs = require('fs');
const PORT = parseInt(process.argv[2] || '9642', 10);
const URL = 'file:///E:/QKMansion/CSX10/w/UME/web/span-probe.html';
const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});
(async () => {
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let cb = null;
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Page.loadEventFired' && cb) { const f = cb; cb = null; f(); }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => {
    const i = ++id; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: me, params: p }));
  });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  const ev = async e => {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) {
      const d = r.result.exceptionDetails;
      return 'EXC ' + ((d.exception && d.exception.description) || '').slice(0, 200);
    }
    return r.result.result.value;
  };
  await send('Emulation.setDeviceMetricsOverride',
    { width: 900, height: 1100, deviceScaleFactor: 2, mobile: false });
  const p = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 15000); });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 60));
  await send('Page.navigate', { url: URL });
  await p;
  await new Promise(r => setTimeout(r, 1800));

  const m = await ev('window.__measure__()');
  console.log('  UA: ' + String(m.ua).replace(/^.*(Edg\/[\d.]+).*$/, '$1'));
  const names = { a: 'A 纯文本', b: 'B span 改字号', c: 'C span 改颜色',
                  d: 'D span 加背景', e: 'E 硬切 inline-block', f: 'F 单字',
                  g: 'G span 合成粗体', h: 'H span 换字体族', i: 'I span opacity' };
  for (const k of ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']) {
    console.log('   ' + names[k].padEnd(20) + ' 宽 ' + m[k].width + ' px');
  }
  console.log('   A 的逐码位前缀宽度: ' + JSON.stringify(m.perUnit));

  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  fs.writeFileSync('E:/QKMansion/CSX10/w/UME/.shots/span-probe.png',
    Buffer.from(r.result.data, 'base64'));
  console.log('   已截 span-probe');
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
