/* 检查关键元素的计算样式：代码区配色对比 + .term 字体 */
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
  const m = rgb.match(/\d+/g);
  if (!m) return null;
  const [r, g, b] = m.slice(0, 3).map(Number).map(v => {
    v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a, b) {
  const la = lum(a), lb = lum(b);
  if (la == null || lb == null) return null;
  const hi = Math.max(la, lb), lo = Math.min(la, lb);
  return ((hi + 0.05) / (lo + 0.05)).toFixed(2);
}

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
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description);
    return r.result.result.value;
  };

  for (const u of URLS) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 180));
    await send('Page.navigate', { url: u.url });
    await new Promise(r => setTimeout(r, 1700));
    console.log('===== ' + u.tag + ' =====');

    const info = JSON.parse(await ev(`(()=>{
      const g = (sel, prop) => { const e = document.querySelector(sel);
        return e ? getComputedStyle(e)[prop] : null; };
      const pick = (sel) => { const e = document.querySelector(sel);
        if (!e) return null;
        const s = getComputedStyle(e);
        return { font: s.fontFamily, size: s.fontSize, color: s.color, bg: s.backgroundColor }; };
      return JSON.stringify({
        isF: document.body.classList.contains('fseries'),
        bodyBg: getComputedStyle(document.body).backgroundColor,
        code: pick('.code-wrap pre'),
        out: pick('.out-wrap pre'),
        term: pick('.term pre'),
        termBar: pick('.term .tbar'),
        inlinePre: pick('.card pre') || pick('p pre') || pick('.mnemonic pre'),
      });
    })()`));

    console.log('  F 系列主题 : ' + (info.isF ? '是' : '否'));
    console.log('  页面底色   : ' + info.bodyBg);
    for (const [k, label] of [['code','代码块'],['out','运行结果'],['term','终端窗口'],['inlinePre','内嵌代码片']]) {
      const v = info[k];
      if (!v) { console.log('  ' + label.padEnd(11) + ': 无'); continue; }
      const c = contrast(v.bg, v.color);
      console.log('  ' + label.padEnd(11) + ': 底=' + String(v.bg).padEnd(22)
        + ' 字=' + String(v.color).padEnd(22)
        + ' 对比=' + String(c).padEnd(7) + ' 字号=' + v.size);
      console.log('  ' + ' '.repeat(11) + ' 字体=' + v.font);
    }
  }
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
