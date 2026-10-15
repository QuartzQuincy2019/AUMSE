/* audit_dark2.js —— 暗色审计 v2：排除误报，只留真正可修的
   =====================================================================
   v1 把 119 个元素都报了出来，但里面混了三类**不该管**的东西：
     1. 行内元素（span/b/i/a/li…）压在同色父级上 —— 背景是父级给的，
        不是它自己的问题（`b(0.911)` 其实是 .mnemonic 的底）。
     2. 示例展示区（.pv-wrap / .pv-body）里**故意**用浅色演示配色，
        改了就不对了。
     3. 小节序号徽标 span.n、重点小节标题 .key-h —— 金色小色块，
        是设计的一部分，暗色下本来就要醒目。

   v2 的过滤：
     · 只查**块级**元素（display 为 block/flex/grid/table-*）
     · 跳过示例区、预览区内部
     · 跳过 .key-h / span.n / .key-mark 等已知装饰
     · 报出「谁给它上的背景」——沿 DOM 往上找第一个有非透明背景的祖先，
       这样能直接指到该改的那条规则
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
    function parse(c){const m=String(c).match(/[\\d.]+/g); if(!m) return null;
      return {r:+m[0],g:+m[1],b:+m[2],a:m.length>3?+m[3]:1};}
    function over(f,b){const a=f.a;return{r:f.r*a+b.r*(1-a),g:f.g*a+b.g*(1-a),
      b:f.b*a+b.b*(1-a),a:1};}
    function lum(c){const f=v=>{v=v/255;return v<=0.03928?v/12.92:
      Math.pow((v+0.055)/1.055,2.4);};
      return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}

    const SKIP = '.pv-wrap,.pv-body,.picker,.key-h,.key-mark,.key-hint,.code-wrap,.out-wrap';
    const IGNORE = ['SPAN','B','I','EM','STRONG','A','CODE','LI','TD','TH','TR','LABEL'];
    const bad = [], seen = new Set();
    document.querySelectorAll('body *').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      /* 只查块级容器 */
      if (!/^(block|flex|grid|table|table-row-group|list-item)$/.test(cs.display))
        return;
      if (el.matches(SKIP) || el.closest(SKIP)) return;
      const r = el.getBoundingClientRect();
      if (r.width < 40 || r.height < 16) return;

      /* 沿 DOM 往上找「谁给的背景」 */
      let owner = null, n = el;
      while (n && n !== document.documentElement) {
        const c = getComputedStyle(n).backgroundColor;
        if (c && !/rgba\\(0, 0, 0, 0\\)/.test(c)) { owner = n; break; }
        n = n.parentElement;
      }
      const ownBg = getComputedStyle(el).backgroundColor;
      /* 自己没背景、且背景来自祖先 → 那是祖先的事，跳过（避免重复报） */
      if (!ownBg || /rgba\\(0, 0, 0, 0\\)/.test(ownBg)) return;

      /* 合成实际背景 */
      const layers = []; let m2 = el;
      while (m2 && m2 !== document.documentElement) {
        const c = getComputedStyle(m2).backgroundColor;
        if (c && !/rgba\\(0, 0, 0, 0\\)/.test(c)) layers.push(c);
        m2 = m2.parentElement;
      }
      layers.push(getComputedStyle(document.body).backgroundColor);
      let bg = {r:255,g:255,b:255,a:1};
      layers.reverse().forEach(L => { const c = parse(L); if (!c) return;
        bg = c.a >= 1 ? c : over(c, bg); });

      const L = lum(bg);
      if (L <= 0.35) return;

      /* 浅底本身不等于有问题 —— 关键看**里面的字读不读得出来**。
         例：.home-fab 是青绿按钮配深色字，底色亮度 0.43 但对比度 7.9:1，
         完全正常。若自身或后代文字对比度 ≥ 4.5，就放行。 */
      const fg = parse(getComputedStyle(el).color);
      if (fg) {
        const fgE = fg.a >= 1 ? fg : over(fg, bg);
        const hi = Math.max(lum(fgE), lum(bg)), lo = Math.min(lum(fgE), lum(bg));
        if ((hi + 0.05) / (lo + 0.05) >= 4.5) {
          /* 自身文字够清楚，再看有没有后代文字是深色的（深字浅底也正常） */
          let ok = true;
          el.querySelectorAll('*').forEach(c => {
            if (!(c.textContent || '').trim()) return;
            const cf = parse(getComputedStyle(c).color);
            if (!cf) return;
            const ce = cf.a >= 1 ? cf : over(cf, bg);
            const h2 = Math.max(lum(ce), lum(bg)), l2 = Math.min(lum(ce), lum(bg));
            if ((h2 + 0.05) / (l2 + 0.05) < 4.5) ok = false;
          });
          if (ok) return;
        }
      }
      const own = getComputedStyle(el).backgroundColor;
      const cls = (typeof el.className === 'string' && el.className.trim())
        ? '.' + el.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
      const key = el.tagName.toLowerCase() + cls;
      if (seen.has(key)) return;
      seen.add(key);
      bad.push({sel: key, lum: +L.toFixed(3), rule: own,
        txt: (el.textContent || '').trim().slice(0, 20)});
    });
    return JSON.stringify(bad);
  })()`;

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  console.log('模式: ' + MODE + '　（已排除示例区与行内元素误报）');
  console.log('文件'.padEnd(34) + '数  明细（选择器 + 亮度）');
  console.log('-'.repeat(112));
  let total = 0, pagesBad = 0;
  const all = {};
  for (const f of files) {
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
      + String(arr.length).padStart(3) + '  '
      + arr.slice(0, 5).map(x => x.sel + '(' + x.lum + ')').join('  '));
  }
  console.log('');
  console.log('  真正需要修的浅底元素 ' + total + '　有问题的页面 '
              + pagesBad + ' / ' + files.length);
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(all, null, 1));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
