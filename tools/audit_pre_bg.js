/* 检查 F 系列里所有「代码类」元素的底色，找出还是浅色的 */
const http = require('http');
const fs = require('fs');
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
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 1800));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  // 统计所有 pre 的底色分布
  const out = await ev(`(()=>{
    const groups = {};
    document.querySelectorAll('pre').forEach(p => {
      const cs = getComputedStyle(p);
      let bg = cs.backgroundColor;
      // 透明就往父级找，找到第一个不透明的
      let el = p, guard = 0;
      while ((bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') && el && guard++ < 8) {
        el = el.parentElement;
        if (el) bg = getComputedStyle(el).backgroundColor;
      }
      const key = bg;
      if (!groups[key]) groups[key] = { n: 0, color: cs.color, size: cs.fontSize, ex: [], sel: [] };
      groups[key].n++;
      if (groups[key].ex.length < 3) {
        groups[key].ex.push((p.textContent||'').replace(/\\s+/g,' ').trim().slice(0,42));
        groups[key].sel.push((p.parentElement.className||p.parentElement.tagName).toString().slice(0,30));
      }
    });
    return JSON.stringify(groups, null, 1);
  })()`);
  console.log(out);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
