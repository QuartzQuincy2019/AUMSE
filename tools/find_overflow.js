/* find_overflow.js —— 找出「真正超出视口」的元素，并区分它是否被可滚动容器包住
   =====================================================================
   为什么之前的判据不可靠：
     verify_mobile.js 逐个元素比较 `e.right > parent.right`，
     而「放在 overflow:auto 容器里的宽表格/长代码行」**本来就会**超过父级，
     那是块内滚动，不是页面级溢出。于是它一直报警，却指不出真问题。

   本脚本的判据：
     1. 页面级：documentElement.scrollWidth > innerWidth  → 真正的横向滚动
     2. 元素级：算元素相对**视口**的右边界；
        若它超出视口，再看它是否被某个 overflow-x:auto/scroll 的祖先包着。
          · 被包住 → 属于「块内滚动」，列出但不计入错误
          · 没被包住 → 真正的溢出，必须修
   ===================================================================== */
const http = require('http');
const fs = require('fs');

const PORT = Number(process.argv[2]);
const DIR = process.argv[3];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const first = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(first.webSocketDebuggerUrl);
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
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 360, height: 800, deviceScaleFactor: 1, mobile: true });

  const PROBE = `(() => {
    const vw = innerWidth;
    const page = document.documentElement.scrollWidth - vw;
    function scroller(el){
      let n = el.parentElement;
      while (n && n !== document.documentElement){
        const ox = getComputedStyle(n).overflowX;
        if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') return n;
        n = n.parentElement;
      }
      return null;
    }
    const free = [], held = [];
    document.querySelectorAll('main *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 4) return;
      const over = Math.round(r.right - vw);
      if (over <= 3) return;
      const cls = (typeof el.className === 'string' && el.className.trim())
        ? '.' + el.className.trim().split(/\\s+/)[0] : '';
      const tag = el.tagName.toLowerCase() + cls;
      const s = scroller(el);
      const rec = tag + ' 超 ' + over + 'px'
        + (s ? '  ← ' + s.tagName.toLowerCase()
               + (typeof s.className === 'string' && s.className.trim()
                  ? '.' + s.className.trim().split(/\\s+/)[0] : '')
               + ' 包住' : '');
      if (s) { if (held.length < 4) held.push(rec); }
      else   { if (free.length < 6) free.push(rec); }
    });
    return JSON.stringify({ page: page, free: free, held: held });
  })()`;

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  console.log('视口 360×800');
  console.log('文件'.padEnd(34) + '页面滚动   未被包住的溢出元素');
  console.log('-'.repeat(110));
  let bad = 0;
  for (const f of files) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 70));
    const w = new Promise(r => { cb = r; setTimeout(() => { if (cb) { cb(); cb = null; } }, 5000); });
    await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await w;
    await new Promise(r => setTimeout(r, 330));
    const raw = await ev(PROBE);
    let o; try { o = JSON.parse(raw); } catch (e) { continue; }
    const isBad = o.page > 3 || o.free.length > 0;
    if (isBad) bad++;
    console.log(('  ' + (isBad ? '!!' : 'OK') + ' ' + f).padEnd(34)
      + (o.page > 3 ? ('有 ' + o.page + 'px') : '无').padEnd(11)
      + (o.free.length ? o.free.join('  |  ') : '（无）'));
  }
  console.log('');
  console.log('  有真问题的页面: ' + bad + ' / ' + files.length);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
