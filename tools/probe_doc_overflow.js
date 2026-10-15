/* 检查文档级横向溢出，并找出把 scrollWidth 撑大的元素 */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];
const W = Number(process.argv[4] || 375);

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
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: 667, deviceScaleFactor: 2, mobile: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 1800));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const de = document.documentElement;
    const out = [];
    out.push('视口宽 clientWidth = ' + de.clientWidth);
    out.push('文档 scrollWidth   = ' + de.scrollWidth);
    out.push('横向溢出           = ' + (de.scrollWidth - de.clientWidth));
    out.push('');
    // 逐个检查可能撑宽文档的容器
    const probes = ['#shell','main','#toc','.code-wrap','.out-wrap','table','.page-nav','pre'];
    out.push('各容器的 scrollWidth/clientWidth:');
    for (const sel of probes) {
      const e = document.querySelector(sel);
      if (!e) { out.push('  ' + sel.padEnd(12) + ' (无)'); continue; }
      const sw = e.scrollWidth, cw = e.clientWidth;
      const flag = sw > cw + 1 ? '  ← 溢出 ' + (sw - cw) : '';
      out.push('  ' + sel.padEnd(12) + ' sw=' + String(sw).padStart(5) + ' cw=' + String(cw).padStart(5) + flag);
    }
    out.push('');
    // 找出 scrollWidth 超过自身 clientWidth 且「没有被 overflow 收住」的元素
    out.push('溢出且未被子元素滚动条收住的元素:');
    let cnt = 0;
    document.querySelectorAll('body *').forEach(el => {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const contained = cs.overflowX === 'auto' || cs.overflowX === 'scroll' || cs.overflowX === 'hidden';
      if (r.right > de.clientWidth + 1 && !contained) {
        if (cnt < 10) out.push('  ' + el.tagName.toLowerCase() +
          (el.className ? '.' + String(el.className).split(' ')[0] : '') +
          '  right=' + Math.round(r.right) + '  overflowX=' + cs.overflowX +
          '  ws=' + cs.whiteSpace);
        cnt++;
      }
    });
    if (!cnt) out.push('  （无）');
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
