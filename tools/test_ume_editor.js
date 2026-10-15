/* web/UME.html 编辑器回归测试
   重构「竖排内核」前后都要跑，用来证明编辑器行为没有变化。
   检查点：
     1. 页面加载、字体可用、无 JS 异常
     2. 竖排容器真的竖排（writing-mode / direction / text-orientation）
     3. 输入蒙文后：字素簇 span 数、统计栏文字
     4. 测量值（用编辑器内部函数量同一串）—— 与重构前对比
     5. 导出弹窗能打开、能生成 SVG、SVG 合法 */
const http = require('http');
const PORT = process.argv[2];
const PAGE = process.argv[3];

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
  let id = 0; const pend = new Map(); const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 950, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: PAGE });
  await new Promise(r => setTimeout(r, 3000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 250);
    return r.result.result.value;
  };

  console.log('--- 1. 加载 ---');
  console.log('  标题: ' + await ev('document.title'));
  console.log('  UMCompos 可用: ' + await ev('!!window.UMCompos'));
  console.log('  字体可用: ' + await ev('document.fonts.check(\'100px "UME Mongolian"\')'));

  console.log('--- 2. 竖排容器 ---');
  console.log(await ev(`(()=>{
    const v = document.getElementById('vtext');
    if (!v) return '  找不到 #vtext';
    const cs = getComputedStyle(v);
    return '  writing-mode=' + cs.writingMode + '  direction=' + cs.direction
      + '  text-orientation=' + cs.textOrientation
      + '  font-family=' + cs.fontFamily.slice(0,42);
  })()`));

  console.log('--- 3. 输入蒙文后的渲染与统计 ---');
  const TEXT = '\\u182E\\u1823\\u1829\\u182D\\u1823\\u182F \\u182A\\u1822\\u1834\\u1822\\u182D';
  console.log(await ev(`(()=>{
    const raw = document.getElementById('raw');
    raw.value = '${TEXT}';
    raw.dispatchEvent(new Event('input', { bubbles: true }));
    return '  已输入 ' + [...raw.value].length + ' 个码位';
  })()`));
  await new Promise(r => setTimeout(r, 900));
  console.log(await ev(`(()=>{
    const v = document.getElementById('vtext');
    const spans = v.querySelectorAll('span');
    const out = [];
    out.push('  渲染出的 span 数: ' + spans.length);
    out.push('  统计栏: ' + (document.getElementById('rawstat')||{}).textContent);
    out.push('  右侧标签: ' + (document.getElementById('rtag')||{}).textContent);
    out.push('  右侧统计: ' + (document.getElementById('rtstat')||{}).textContent);
    return out.join('\\n');
  })()`));

  console.log('--- 4. 测量值（与重构前对比）---');
  console.log(await ev(`(()=>{
    const U = window.UMCompos;
    const T = '${TEXT}';
    const out = [];
    if (U) {
      const plan = U.layout(T);
      const sum = plan[0].items.reduce((a,b)=>a+b.adv,0);
      out.push('  UMCompos 行长: ' + plan[0].length.toFixed(1)
        + '   簇数: ' + plan[0].items.length
        + '   advance 和: ' + sum.toFixed(1));
    }
    return out.join('\\n') || '  （无）';
  })()`));

  console.log('--- 5. 导出 SVG ---');
  console.log(await ev(`(async ()=>{
    const out = [];
    const btn = document.getElementById('btn-export');
    if (!btn) return '  找不到导出按钮';
    btn.click();
    await new Promise(r=>setTimeout(r,1500));
    const modal = document.getElementById('modal');
    out.push('  弹窗打开: ' + modal.classList.contains('on'));
    const prev = modal.querySelector('iframe, img, svg, .preview, #exPreview');
    out.push('  预览元素: ' + (prev ? prev.tagName.toLowerCase() : '（未找到）'));
    // 直接调内部导出函数更可靠
    if (typeof buildSVGText === 'function') {
      const r = buildSVGText();
      if (r && r.svg) {
        out.push('  buildSVGText 成功: ' + Math.round(r.W) + 'x' + Math.round(r.H)
          + '  <text> ' + (r.svg.match(/<text/g)||[]).length + ' 个');
        const d = new DOMParser().parseFromString(r.svg, 'image/svg+xml');
        out.push('  SVG 合法: ' + (!d.querySelector('parsererror')));
      } else out.push('  buildSVGText 返回: ' + JSON.stringify(r).slice(0,120));
    } else out.push('  buildSVGText 不在全局作用域（正常，它是模块内函数）');
    return out.join('\\n');
  })()`));

  console.log('');
  console.log('JS 异常: ' + (errs.length ? errs.join(' | ').slice(0, 400) : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
