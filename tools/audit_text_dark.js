/* audit_text_dark.js —— 暗色模式「文字可读性」审计（判据正确的版本）
   =====================================================================
   为什么重写：check_contrast.js 在用**元素自身背景**上有个错 ——
   当元素自己带不透明背景时，它仍然从 body 重新合成，
   于是「浅底深字」的正常元素被算成「深底深字」，误报一堆。

   真实例子（fe-04 示例区）：
       p  color=rgb(26,31,40)  bg=rgb(255,233,168)   ← 深字浅底，对比度 14:1，
                                                        完全正常
       check_contrast 却报 1.01（它拿 body 的深色当成了背景）

   本脚本的算法：
     1. 算元素的实际背景：从元素自身开始往上取第一层**不透明**背景；
        沿途的半透明层按 alpha 依次合成。
     2. 前景若半透明，也与该背景合成。
     3. 比 WCAG 对比度，< 4.5 才报。
     4. 只查**有文字**的叶子元素，避免拿容器重复报。
     5. 跳过代码块/输出块（它们有自己的语法配色，且是深底亮字的设计）。
   ===================================================================== */
const http = require('http');
const fs = require('fs');

const PORT = Number(process.argv[2]);
const DIR = process.argv[3];
const MODE = process.argv[4] || 'dark';

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
    { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setEmulatedMedia',
    { features: [{ name: 'prefers-color-scheme', value: MODE }] });

  const PROBE = `(() => {
    const SKIP = '.code-wrap,.out-wrap,.term,.plain-pre';
    function parse(c){
      const m = String(c).match(/[\\d.]+/g);
      if (!m) return null;
      return { r:+m[0], g:+m[1], b:+m[2], a: m.length > 3 ? +m[3] : 1 };
    }
    function over(f, b){
      const a = f.a;
      return { r:f.r*a + b.r*(1-a), g:f.g*a + b.g*(1-a),
               b:f.b*a + b.b*(1-a), a:1 };
    }
    function lum(c){
      const f = v => { v = v/255;
        return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
      return 0.2126*f(c.r) + 0.7152*f(c.g) + 0.0722*f(c.b);
    }

    /* 元素的实际背景：自身 → 上溯，第一层不透明就停；半透明层逐层合成 */
    function bgOf(el){
      const layers = [];
      let n = el;
      while (n && n !== document.documentElement){
        const c = parse(getComputedStyle(n).backgroundColor);
        if (c && c.a > 0) layers.push(c);
        if (c && c.a >= 1) break;          /* 已不透明，不必再往上 */
        n = n.parentElement;
      }
      let bg = { r:255, g:255, b:255, a:1 };
      layers.reverse().forEach(L => { bg = L.a >= 1 ? L : over(L, bg); });
      return bg;
    }

    const bad = [], seen = new Set();
    document.querySelectorAll('main *').forEach(el => {
      if (el.closest(SKIP)) return;
      /* 只查直接含文字的叶子，避免父子重复报 */
      let hasText = false;
      el.childNodes.forEach(n => {
        if (n.nodeType === 3 && n.textContent.trim()) hasText = true;
      });
      if (!hasText) return;
      const r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 6) return;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (parseFloat(cs.opacity) < 0.35) return;

      const bg = bgOf(el);
      let fg = parse(cs.color);
      if (!fg) return;
      if (fg.a < 1) fg = over(fg, bg);
      const hi = Math.max(lum(fg), lum(bg)), lo = Math.min(lum(fg), lum(bg));
      const ratio = (hi + 0.05) / (lo + 0.05);
      if (ratio >= 4.5) return;

      const cls = (typeof el.className === 'string' && el.className.trim())
        ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
      const key = el.tagName.toLowerCase() + cls + '|' + cs.color;
      if (seen.has(key)) return;
      seen.add(key);
      bad.push({ sel: el.tagName.toLowerCase() + cls,
        ratio: +ratio.toFixed(2), fg: cs.color,
        bg: 'rgb(' + [bg.r,bg.g,bg.b].map(Math.round).join(',') + ')',
        txt: (el.textContent || '').trim().slice(0, 22) });
    });
    return JSON.stringify(bad);
  })()`;

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  console.log('模式: ' + MODE + '　判据: WCAG 对比度 < 4.5（按元素实际背景算）');
  console.log('文件'.padEnd(34) + '数  最低对比度与示例');
  console.log('-'.repeat(108));
  let total = 0, pagesBad = 0;
  for (const f of files) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 70));
    const w = new Promise(r => {
      cb = r; setTimeout(() => { if (cb) { cb(); cb = null; } }, 5000);
    });
    await send('Page.navigate',
      { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await w;
    await new Promise(r => setTimeout(r, 300));
    const raw = await ev(PROBE);
    let arr = [];
    try { arr = JSON.parse(raw) || []; } catch (e) {}
    total += arr.length;
    if (arr.length) pagesBad++;
    console.log(('  ' + (arr.length ? '!!' : 'OK') + ' ' + f).padEnd(34)
      + String(arr.length).padStart(3) + '  '
      + arr.slice(0, 3).map(x => x.sel + ' ' + x.ratio + ' "' + x.txt + '"').join('  |  '));
  }
  console.log('');
  console.log('  对比度不足的文字: ' + total + '　有问题的页面 ' + pagesBad + ' / ' + files.length);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
