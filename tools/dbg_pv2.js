/* 诊断：pv-wrap 在 HTML 里有 N 个，为什么 DOM 里少了 */
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
  const jsErrors = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      jsErrors.push((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 250);
    return r.result.result.value;
  };

  console.log('JS 异常: ' + (jsErrors.length ? jsErrors.join(' | ').slice(0, 300) : '无'));
  console.log(await ev(`(()=>{
    const out = [];
    out.push('DOM 里 .pv-wrap: ' + document.querySelectorAll('.pv-wrap').length);
    out.push('DOM 里 [data-pv]  : ' + document.querySelectorAll('[data-pv]').length);
    out.push('');
    // 列出 main 的直接子元素序列，看看结构是否被破坏
    const main = document.querySelector('main');
    out.push('main 子元素 ' + main.children.length + ' 个:');
    let n = 0;
    for (const c of main.children) {
      const cls = (c.className || '').toString().split(' ')[0];
      out.push('  ' + String(++n).padStart(3) + ' ' + c.tagName.toLowerCase() +
        (cls ? '.' + cls : '') + '  h=' + Math.round(c.getBoundingClientRect().height));
      if (n > 60) { out.push('  …'); break; }
    }
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
