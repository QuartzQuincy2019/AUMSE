/* audit_dark.js —— 暗色模式系统性审计
   =====================================================================
   存在意义：以前我是「用户报一个、我补一个」，补不完。
   这里改成**穷举**：把每篇里所有可见元素的**实际渲染背景**取出来，
   凡是在暗色模式下仍然偏亮的，一律列出来 —— 不再靠人工枚举选择器。

   判定：背景（含 alpha 合成后的实际值）的**相对亮度 > 0.35** 即视为
        「暗色下不该出现的浅底」。这个阈值能放过浅色文字、金色左条这类
        小面积装饰（它们是 border/文字，不是背景），只抓大块浅底。

   同时报出每个元素的 选择器线索（tag + class），方便定位。
   ===================================================================== */
const http = require('http');
const fs = require('fs');

const PORT = Number(process.argv[2]);
const DIR = process.argv[3];
const MODE = process.argv[4] || 'dark';
const OUT = process.argv[5] || '';

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const first = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(first.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let cb = null; const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description
                || m.params.exceptionDetails.text);
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
    { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setEmulatedMedia',
    { features: [{ name: 'prefers-color-scheme', value: MODE }] });

  const PROBE = `(() => {
    function parse(c){const m=String(c).match(/[\\d.]+/g); if(!m) return null;
      return {r:+m[0],g:+m[1],b:+m[2],a:m.length>3?+m[3]:1};}
    function over(f,b){const a=f.a;return{r:f.r*a+b.r*(1-a),g:f.g*a+b.g*(1-a),
      b:f.b*a+b.b*(1-a),a:1};}
    function lum(c){const f=v=>{v=v/255;return v<=0.03928?v/12.92:
      Math.pow((v+0.055)/1.055,2.4);};
      return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}

    const bad = [];
    const seen = new Set();
    document.querySelectorAll('body *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 24 || r.height < 12) return;          /* 太小，只可能是装饰 */
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      /* 从元素往上合成实际背景 */
      const layers = [];
      let n = el;
      while (n && n !== document.documentElement) {
        const c = getComputedStyle(n).backgroundColor;
        if (c && !/rgba\\(0, 0, 0, 0\\)/.test(c)) layers.push(c);
        n = n.parentElement;
      }
      layers.push(getComputedStyle(document.body).backgroundColor);
      let bg = {r:255,g:255,b:255,a:1};
      layers.reverse().forEach(L => { const c = parse(L); if (!c) return;
        bg = c.a >= 1 ? c : over(c, bg); });
      const L = lum(bg);
      if (L <= 0.35) return;                              /* 够深，放行 */

      const cls = (el.className && typeof el.className === 'string')
        ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
      const key = el.tagName.toLowerCase() + cls;
      if (seen.has(key)) return;
      seen.add(key);
      bad.push({sel: key, lum: +L.toFixed(3),
        bg: 'rgb(' + [bg.r,bg.g,bg.b].map(Math.round).join(',') + ')',
        txt: (el.textContent || '').trim().slice(0, 24)});
    });
    return JSON.stringify(bad);
  })()`;

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  console.log('模式: ' + MODE + '　阈值: 背景亮度 > 0.35');
  console.log('文件'.padEnd(34) + '浅底元素数   明细');
  console.log('-'.repeat(112));
  let total = 0, pagesBad = 0;
  const all = {};
  for (const f of files) {
    errs.length = 0;
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 80));
    const w = new Promise(r => { cb = r; setTimeout(() => { if (cb) { cb(); cb = null; } }, 5000); });
    await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await w;
    await new Promise(r => setTimeout(r, 330));
    const raw = await ev(PROBE);
    let arr = [];
    try { arr = JSON.parse(raw); } catch (e) { arr = []; }
    all[f] = arr;
    total += arr.length;
    if (arr.length) pagesBad++;
    console.log(('  ' + (arr.length ? '!!' : 'OK') + ' ' + f).padEnd(34)
      + String(arr.length).padStart(6) + '     '
      + arr.slice(0, 4).map(x => x.sel + '(' + x.lum + ')').join('  '));
  }
  console.log('');
  console.log('  浅底元素合计 ' + total + '　有问题的页面 ' + pagesBad + ' / ' + files.length);
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(all, null, 1));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
