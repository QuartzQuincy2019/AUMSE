/* 诊断：手机端文档开头为什么有大片空白 */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];
const W = Number(process.argv[4] || 375);
const H = Number(process.argv[5] || 667);

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
  await send('Emulation.setDeviceMetricsOverride',
    { width: W, height: H, deviceScaleFactor: 2, mobile: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 1800));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description || '');
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const vh = window.innerHeight;
    const out = [];
    const push = (label, sel) => {
      const e = document.querySelector(sel);
      if (!e) { out.push(label + ': (无此元素)'); return; }
      const cs = getComputedStyle(e);
      const r = e.getBoundingClientRect();
      out.push(label + ':');
      out.push('    position=' + cs.position + '  top=' + cs.top + '  height=' + cs.height
        + '  display=' + cs.display);
      out.push('    marginTop=' + cs.marginTop + '  paddingTop=' + cs.paddingTop);
      out.push('    rect.top=' + Math.round(r.top) + '  rect.height=' + Math.round(r.height));
    };
    out.push('视口高度 vh = ' + vh + 'px');
    out.push('');
    push('#toc        ', '#toc');
    push('#shell      ', '#shell');
    push('main        ', 'main');
    push('h1          ', 'h1');
    out.push('');
    // 关键：h1 距页面顶部到底多远
    const h1 = document.querySelector('h1');
    if (h1) out.push('h1 距文档顶部 = ' + Math.round(h1.getBoundingClientRect().top + window.scrollY) + 'px');
    // body 第一个可见内容的偏移
    const main = document.querySelector('main');
    if (main) {
      const r = main.getBoundingClientRect();
      out.push('main.rect.top = ' + Math.round(r.top) + 'px');
      out.push('main 的 paddingTop = ' + getComputedStyle(main).paddingTop);
    }
    // shell 是否 flex
    const sh = document.querySelector('#shell');
    if (sh) out.push('#shell display = ' + getComputedStyle(sh).display);
    out.push('');
    out.push('body.scrollHeight = ' + document.body.scrollHeight);
    out.push('滚到 0 时，视口最上方元素: ');
    window.scrollTo(0,0);
    return out.join('\\n');
  })()`));

  console.log('\n--- 视口顶部 300px 内命中的元素 ---');
  console.log(await ev(`(()=>{
    const vh = window.innerHeight;
    const hits = [];
    document.querySelectorAll('body *').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.height > 0 && r.top < 300 && r.bottom > 0) {
        const cs = getComputedStyle(e);
        hits.push({
          tag: e.tagName.toLowerCase(),
          cls: (e.className||'').toString().slice(0,30),
          top: Math.round(r.top), bottom: Math.round(r.bottom), h: Math.round(r.height),
          pos: cs.position
        });
      }
    });
    return JSON.stringify(hits.slice(0, 14), null, 1);
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
