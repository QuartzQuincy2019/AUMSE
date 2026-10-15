/* 找出移动端导致横向溢出的元素 */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];

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
  await send('Emulation.setDeviceMetricsOverride', { width: 375, height: 667, deviceScaleFactor: 1, mobile: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 1800));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description || '');
    return r.result.result.value;
  };

  const out = await ev(`(()=>{
    const vw = document.documentElement.clientWidth;
    const bad = [];
    document.querySelectorAll('body *').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.right > vw + 1 || r.width > vw + 1) {
        // 只报「自己宽」而不是「被父级带着宽」的
        const p = e.parentElement;
        const pr = p ? p.getBoundingClientRect() : null;
        const selfWide = !pr || r.width > pr.width + 1;
        if (selfWide) {
          bad.push({
            tag: e.tagName.toLowerCase(),
            cls: (e.className || '').toString().slice(0, 44),
            w: Math.round(r.width),
            right: Math.round(r.right),
            txt: (e.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 56)
          });
        }
      }
    });
    return JSON.stringify({ vw, bad: bad.slice(0, 16) }, null, 1);
  })()`);
  console.log(out);

  // 具体看 thead 所在的 table
  const tbl = await ev(`(()=>{
    const res = [];
    document.querySelectorAll('table').forEach((tb, i) => {
      const r = tb.getBoundingClientRect();
      if (r.width > document.documentElement.clientWidth + 1) {
        res.push({
          idx: i,
          w: Math.round(r.width),
          parent: tb.parentElement.tagName.toLowerCase() + '.' + (tb.parentElement.className||''),
          parentOverflowX: getComputedStyle(tb.parentElement).overflowX,
          cols: tb.querySelectorAll('thead th').length,
          headers: [...tb.querySelectorAll('thead th')].map(h=>h.textContent.trim().slice(0,20)).join(' | '),
          style: tb.getAttribute('style') || '(none)'
        });
      }
    });
    return JSON.stringify(res, null, 1);
  })()`);
  console.log('--- 超宽表格 ---');
  console.log(tbl);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
