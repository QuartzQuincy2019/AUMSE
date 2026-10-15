/* 找出最宽的 .hl-c 元素及其所在代码块 */
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
  await send('Emulation.setDeviceMetricsOverride', { width: 375, height: 667, deviceScaleFactor: 2, mobile: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 1800));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  const out = await ev(`(()=>{
    const vw = document.documentElement.clientWidth;
    const rows = [];
    document.querySelectorAll('.hl-c').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width > vw - 20) {
        // 找它所在的 pre 和 .name
        const pre = e.closest('pre');
        const wrap = e.closest('.code-wrap');
        const nm = wrap ? wrap.querySelector('.name') : null;
        rows.push({
          w: Math.round(r.width),
          right: Math.round(r.right),
          text: (e.textContent || '').trim().slice(0, 110),
          preW: pre ? Math.round(pre.getBoundingClientRect().width) : -1,
          preScrollW: pre ? pre.scrollWidth : -1,
          block: nm ? nm.textContent : '(无)',
          preWhiteSpace: pre ? getComputedStyle(pre).whiteSpace : '?'
        });
      }
    });
    return JSON.stringify({ vw, rows: rows.slice(0, 12) }, null, 1);
  })()`);
  console.log(out);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
