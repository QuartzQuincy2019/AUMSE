/* 调试 pv 作用域注入 */
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
  await send('Log.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2200));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const out = [];
    const w = document.querySelector('.pv-wrap[data-pv="1"]');
    out.push('找到 pv1: ' + !!w);
    out.push('dataset.pv = ' + (w ? w.dataset.pv : '-'));
    out.push('dataset.pvKind = ' + (w ? w.dataset.pvKind : '-'));
    const pre = w ? w.querySelector('pre') : null;
    out.push('pre 存在: ' + !!pre);
    if (pre) {
      const txt = pre.textContent;
      out.push('pre.textContent 长度 = ' + txt.length);
      out.push('前 160 字符: ' + JSON.stringify(txt.slice(0,160)));
      out.push('含 { : ' + txt.includes('{') + '   含 } : ' + txt.includes('}'));
    }
    const body = w ? w.querySelector('.pv-body') : null;
    out.push('.pv-body 存在: ' + !!body + '  子元素 ' + (body?body.children.length:'-'));
    const st = w ? w.querySelector('style') : null;
    out.push('注入的 <style> 存在: ' + !!st + '  长度 ' + (st?st.textContent.length:'-'));
    if (st) out.push('style 内容: ' + JSON.stringify(st.textContent.slice(0,300)));
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
