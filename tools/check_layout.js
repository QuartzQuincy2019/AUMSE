/* check_layout.js —— 响应式布局断言（常驻回归工具）
   =====================================================================
   为什么需要它
   -----------
   CSS 分层重构期间，这一条断言抓出过两个真实缺陷：
     · f03 的 `#toc{position:sticky…}` 与窄屏 `#toc{display:block…}`
       被区间删除法留下的碎片吞掉，窄屏目录退化成 sticky（本该是抽屉）
     · 8 篇 FE 未挂公共层，窄屏 shell 仍是 flex
   只靠「结构检查 + 溢出检查」看不出这类问题 —— 它们不改锚点、也不溢出。

   断言内容（每页 × 亮暗 × 宽窄，每页只加载一次）
     宽屏(1280)  正文页 shell=flex        toc=sticky
     窄屏(375)   正文页 shell=block       toc≠sticky（必须是抽屉）
     FE           shell 恒为 flex（设计如此），但窄屏 toc 同样必须≠sticky
     两种宽度   都不得有横向溢出

   用法： node check_layout.js <port> <tutorialsDir>
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

const READ = `(() => {
  const g = (s, p) => { const e = document.querySelector(s);
    return e ? getComputedStyle(e)[p] : '-'; };
  return JSON.stringify({
    shell: g('#shell', 'display'),
    toc:   g('#toc', 'position'),
    tocW:  g('#toc', 'width'),
    over:  document.documentElement.scrollWidth - innerWidth
  });
})()`;

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
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

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    return r.result.exceptionDetails ? null : r.result.result.value;
  };

  let bad = 0;
  for (const mode of ['light', 'dark']) {
    await send('Emulation.setEmulatedMedia',
      { features: [{ name: 'prefers-color-scheme', value: mode }] });
    for (const f of files) {
      const isFE = f.startsWith('fe-');
      await send('Emulation.setDeviceMetricsOverride',
        { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
      await send('Page.navigate', { url: 'about:blank' });
      await new Promise(r => setTimeout(r, 50));
      const w = new Promise(r => { cb = r; setTimeout(() => { if (cb) { cb = null; } }, 5000); });
      await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
      await w;
      await new Promise(r => setTimeout(r, 240));
      const wide = JSON.parse(await ev(READ) || '{}');

      await send('Emulation.setDeviceMetricsOverride',
        { width: 375, height: 900, deviceScaleFactor: 1, mobile: true });
      await new Promise(r => setTimeout(r, 280));
      const narrow = JSON.parse(await ev(READ) || '{}');

      const p = [];
      if (wide.over > 3) p.push('宽屏溢出 ' + wide.over);
      if (narrow.over > 3) p.push('窄屏溢出 ' + narrow.over);
      if (!isFE && wide.shell !== 'flex') p.push('宽屏 shell=' + wide.shell);
      if (!isFE && narrow.shell !== 'block') p.push('窄屏 shell=' + narrow.shell);
      if (isFE && wide.shell !== 'flex') p.push('FE 宽屏 shell=' + wide.shell);
      if (narrow.toc === 'sticky') p.push('窄屏 toc 仍 sticky');
      if (wide.toc !== 'sticky') p.push('宽屏 toc=' + wide.toc);
      if (p.length) { bad++; console.log('   !! ' + mode + ' ' + f + '  ' + p.join(' / ')); }
    }
  }
  console.log('  布局断言失败 ' + bad + ' 处 '
    + (bad === 0 ? '✅ ' + files.length + ' 篇全部符合预期' : '❌'));
  console.log('  JS 异常: '
    + (errs.length ? errs.slice(0, 3).join('|').slice(0, 180) : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
