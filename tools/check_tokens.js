/* 逐个测代码块内各类 token 的颜色与对比度 */
const http = require('http');
const fs = require('fs');
const PORT = process.argv[2];
const URLS = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

function lum(rgb) {
  const m = String(rgb).match(/[\d.]+/g);
  if (!m) return null;
  const [r, g, b] = m.slice(0, 3).map(Number).map(v => {
    v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
const ratio = (a, b) => {
  const la = lum(a), lb = lum(b);
  if (la == null || lb == null) return null;
  const hi = Math.max(la, lb), lo = Math.min(la, lb);
  return ((hi + 0.05) / (lo + 0.05)).toFixed(2);
};

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  for (const u of URLS) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 200));
    await send('Page.navigate', { url: u.url });
    await new Promise(r => setTimeout(r, 1800));
    console.log('===== ' + u.tag + ' =====');

    const info = JSON.parse(await ev(`(()=>{
      const wrap = document.querySelector('.code-wrap');
      if (!wrap) return JSON.stringify({none:true});
      const bg = getComputedStyle(wrap).backgroundColor;
      const pre = wrap.querySelector('pre');
      const preCs = getComputedStyle(pre);
      const classes = ['hl-k','hl-f','hl-n','hl-s','hl-p','hl-c','hl-b','arw','arw2','hl-bad','hl-ok'];
      const tokens = {};
      for (const c of classes){
        const el = wrap.querySelector('pre .'+c);
        if (el) tokens[c] = { color: getComputedStyle(el).color,
          sample: el.textContent.trim().slice(0,16),
          weight: getComputedStyle(el).fontWeight };
      }
      const plain = wrap.querySelector('pre');
      // 取一个没有任何 span 的纯文本行：用整体色
      return JSON.stringify({ bg, preColor: preCs.color, weight: preCs.fontWeight,
        size: preCs.fontSize, tokens });
    })()`));

    if (info.none) { console.log('  无代码块'); continue; }
    console.log('  代码块底色 : ' + info.bg);
    console.log('  正文       : ' + info.preColor + '  对比=' + ratio(info.bg, info.preColor)
      + '  ' + info.size + ' w' + info.weight);
    console.log('  --- 各 token ---');
    for (const [k, v] of Object.entries(info.tokens)) {
      console.log('    ' + k.padEnd(7) + ' ' + String(v.color).padEnd(24)
        + ' 对比=' + String(ratio(info.bg, v.color)).padEnd(6) + ' w' + v.weight
        + '  «' + v.sample + '»');
    }
  }
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
