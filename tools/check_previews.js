/* 检查「示例展示」是否真的生效：
   1. 每个 .pv-wrap 是否有 .pv-body 内容
   2. CSS 示例的 scoped <style> 是否注入、规则数是否 > 0
   3. 被选中的元素背景色是否真的变了（对比默认） */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];

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
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2200));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 200);
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const out = [];
    const wraps = document.querySelectorAll('.pv-wrap[data-pv]');
    out.push('示例展示块数量: ' + wraps.length);
    out.push('');
    let injected = 0, empty = 0;
    wraps.forEach(w => {
      const n = w.dataset.pv, kind = w.dataset.pvKind || 'html';
      const body = w.querySelector('.pv-body');
      const st = w.querySelector('style');
      const rules = st ? (st.textContent.match(/\\{/g) || []).length : 0;
      const hasContent = body && body.children.length > 0;
      if (kind === 'css') { if (rules) injected++; else empty++; }
      else { if (hasContent) injected++; else empty++; }
      // 统计示例框里「背景色不是透明/白」的元素数，作为「选择器真的生效」的证据
      let colored = 0;
      if (body) body.querySelectorAll('*').forEach(e => {
        const bg = getComputedStyle(e).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'rgb(255, 255, 255)') colored++;
      });
      out.push('  pv' + String(n).padStart(2) + ' [' + kind + '] 规则' +
        String(rules).padStart(3) + ' 子元素' + String(body ? body.children.length : 0).padStart(3) +
        ' 有底色元素' + String(colored).padStart(3) + (kind==='css' ? '' : '') +
        ((kind==='css' && !rules) || (kind==='html' && !hasContent) ? '   ← 空!' : ''));
    });
    out.push('');
    out.push('生效 ' + injected + ' / 空 ' + empty);
    // 检查 scoped CSS 有没有泄漏到文档本身
    const h1bg = getComputedStyle(document.querySelector('h1')).backgroundColor;
    const bodyBg = getComputedStyle(document.body).backgroundColor;
    out.push('泄漏检查: body 背景=' + bodyBg + '  h1 背景=' + h1bg);
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
