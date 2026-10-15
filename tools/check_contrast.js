/* 对比度检查：把每个可见元素的文字色与其**实际合成后的**背景比一遍。
   要点（踩过的坑）：
     · 必须做 alpha 合成 —— 只看 backgroundColor 会把半透明底当成透明，
       误报一堆「深字压深底」。
     · 渐变不会出现在 backgroundColor 里，遇到带背景图的元素要标注出来，
       这类结果要人工看一眼再决定是不是真问题。 */
const http = require('http');
const PORT = process.argv[2];
const PAGE = process.argv[3];
const MODE = process.argv[4] || 'light';

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

function parse(c) {
  const m = String(c).match(/[\d.]+/g);
  if (!m) return null;
  return { r: +m[0], g: +m[1], b: +m[2], a: m.length > 3 ? +m[3] : 1 };
}
function over(fg, bg) {
  const a = fg.a;
  return { r: fg.r * a + bg.r * (1 - a), g: fg.g * a + bg.g * (1 - a),
           b: fg.b * a + bg.b * (1 - a), a: 1 };
}
function lum(c) {
  const f = v => { v = v / 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
}
function ratio(a, b) {
  const l1 = lum(a), l2 = lum(b);
  const hi = Math.max(l1, l2), lo = Math.min(l1, l2);
  return (hi + 0.05) / (lo + 0.05);
}

(async () => {
  await new Promise(res => {
    http.get({ host: '127.0.0.1', port: Number(PORT), path: '/json/new?about:blank' },
      r => { r.on('data', () => {}); r.on('end', res); }).on('error', res);
  });
  await new Promise(r => setTimeout(r, 400));
  const t = (await get('/json/list')).filter(x => x.type === 'page').pop();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: MODE }] });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: PAGE });
  await new Promise(r => setTimeout(r, 2600));

  const ev = async e => {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 250);
    return r.result.result.value;
  };

  const raw = await ev(`(()=>{
    function bgLayers(el){
      const out=[]; let n=el;
      while(n && n!==document.documentElement){
        const cs=getComputedStyle(n);
        const c=cs.backgroundColor;
        if(c && !/rgba\\(0, 0, 0, 0\\)/.test(c)) out.push(c);
        if(cs.backgroundImage && cs.backgroundImage!=='none') out.push('__IMG__');
        n=n.parentElement;
      }
      out.push(getComputedStyle(document.body).backgroundColor);
      return out.reverse();
    }
    const sels=['.card-t','.sub-title','h1','h2','h2 .n','h3','h4','a','p','li','td','th',
      '.tag','code','.home-fab','.s-nav-h','.s-nav-grid a','.s-nav-toc a','.key-mark',
      '.fig figcaption','.series-nav b','.series-nav a','.card.note p','.card.key p',
      '.tag b','.out-wrap pre','.code-wrap pre','.card-t','.cap'];
    const seen=new Set(), out=[];
    sels.forEach(s=>{
      document.querySelectorAll(s).forEach(el=>{
        const r=el.getBoundingClientRect();
        if(r.width<2||r.height<2) return;
        const cs=getComputedStyle(el);
        const layers=bgLayers(el);
        const key=s+'|'+cs.color+'|'+layers.join(',');
        if(seen.has(key)) return; seen.add(key);
        out.push({sel:s, fg:cs.color, layers:layers,
          txt:(el.textContent||'').trim().slice(0,18)});
      });
    });
    return JSON.stringify(out);
  })()`);

  let arr;
  try { arr = JSON.parse(raw); } catch (e) { console.log('parse fail ' + raw); process.exit(1); }
  const base = { r: 255, g: 255, b: 255, a: 1 };
  const bad = [];
  arr.forEach(o => {
    const fg = parse(o.fg); if (!fg) return;
    let bg = { ...base }, img = false;
    o.layers.forEach(L => {
      if (L === '__IMG__') { img = true; return; }
      const c = parse(L); if (!c) return;
      bg = c.a >= 1 ? c : over(c, bg);
    });
    const fgEff = fg.a >= 1 ? fg : over(fg, bg);
    const r = ratio(fgEff, bg);
    if (r < 4.5) bad.push({ sel: o.sel, r: +r.toFixed(2), fg: o.fg,
      bg: 'rgb(' + [bg.r, bg.g, bg.b].map(Math.round) + ')', img, txt: o.txt });
  });
  bad.sort((a, b) => a.r - b.r);
  console.log('模式: ' + MODE + '   组合数: ' + arr.length + '   对比度<4.5: ' + bad.length);
  bad.forEach(o => console.log('  ' + String(o.r).padStart(5) + '  ' + o.sel.padEnd(18)
    + ' fg=' + o.fg.padEnd(22) + ' bg(合成)=' + o.bg.padEnd(20)
    + (o.img ? ' [含渐变] ' : ' ') + '"' + o.txt + '"'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
