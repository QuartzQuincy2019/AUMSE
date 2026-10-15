/* 检查教程页所有站内锚点是否都能解析 */
const fs = require('fs');
const http = require('http');
const [PORT, URL_] = process.argv.slice(2);

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
  await send('Page.navigate', { url: URL_ });
  await new Promise(r => setTimeout(r, 2200));

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception||{}).description);
    return r.result.result.value;
  };

  console.log('断链（href 指向不存在的 id）:');
  console.log(await ev(`(()=>{
    const bad = [];
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      const id = a.getAttribute('href').slice(1);
      if (id && !document.getElementById(id)) bad.push(a.getAttribute('href') + '  «' + a.textContent.trim() + '»');
    });
    return bad.length ? bad.join('\\n  ') : '  无';
  })()`));

  console.log('');
  console.log('孤立的 id（有 id 但目录里没链接）:');
  console.log(await ev(`(()=>{
    const linked = new Set([...document.querySelectorAll('a[href^="#"]')]
      .map(a => a.getAttribute('href').slice(1)));
    const orphan = [];
    document.querySelectorAll('h2[id],h3[id]').forEach(h => {
      if (!linked.has(h.id)) orphan.push(h.id + '  «' + h.textContent.trim().slice(0,40) + '»');
    });
    return orphan.length ? orphan.join('\\n  ') : '  无';
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
