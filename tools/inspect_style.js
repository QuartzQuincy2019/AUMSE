/* 检查某个元素的实际生效样式与匹配到的规则 */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];
const SEL = process.argv[4];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

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
  await send('Page.enable'); await send('Runtime.enable'); await send('DOM.enable'); await send('CSS.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 200);
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const e = document.querySelector(${JSON.stringify(SEL)});
    if (!e) return '找不到元素';
    const cs = getComputedStyle(e);
    const out = [];
    out.push('元素: ' + e.tagName + '  class="' + e.className + '"');
    out.push('background-image : ' + cs.backgroundImage);
    out.push('background-color : ' + cs.backgroundColor);
    out.push('border-left      : ' + cs.borderLeft);
    out.push('padding          : ' + cs.padding);
    out.push('box-shadow       : ' + cs.boxShadow);
    out.push('');
    out.push('样式表数量: ' + document.styleSheets.length);
    let n = 0, matched = [];
    for (const ss of document.styleSheets) {
      let rules;
      // 注意：这里必须用 try 包住「只读取 cssRules 这一句」。
      // 早期版本把外层循环也写在 try 里，一旦某个表读不到就 continue 到外层，
      // 结果「规则总数」永远是 0，看起来像样式表全坏了 —— 其实是检查器自己的锅。
      try { rules = ss.cssRules; } catch (err) {
        out.push('  (读不到: ' + (ss.href ? ss.href.split('/').pop() : 'inline') + ')');
        continue;
      }
      for (const r of rules) {
        n++;
        if (r.selectorText && /key-h|key-mark/.test(r.selectorText)) {
          matched.push('  ' + (ss.href ? ss.href.split('/').pop() : 'inline') + ' → ' + r.selectorText);
        }
      }
    }
    out.push('规则总数: ' + n);
    out.push('匹配 key-h / key-mark 的规则:');
    out.push(matched.length ? matched.join('\\n') : '  （一条都没有！）');
    out.push('');
    out.push('该元素匹配到的全部规则:');
    const list = [];
    for (const ss of document.styleSheets) {
      let rules; try { rules = ss.cssRules; } catch (err) { continue; }
      for (const r of rules) {
        if (!r.selectorText) continue;
        for (const sel of r.selectorText.split(',')) {
          try { if (e.matches(sel.trim())) list.push('  ' + sel.trim() + '  ← ' + (ss.href?ss.href.split('/').pop():'inline')); } catch (err) {}
        }
      }
    }
    out.push(list.join('\\n'));
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
