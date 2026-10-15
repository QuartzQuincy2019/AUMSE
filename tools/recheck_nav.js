/* recheck_nav.js —— 26 篇页尾导航样式的完整普查
   =====================================================================
   上一轮这个普查卡住了（>10 分钟），原因是没有给导航兜底超时：
   某个页面若 loadEventFired 一直不来，脚本就永久挂住。
   这里每一页都设**硬超时**（3.5s），到点就继续，绝不空等。

   同时把判据写清楚 —— 「有样式」= 边框/圆角/内边距三者都不为 0，
   并且当前篇那一项拿到了视觉标记（底色或渐变）。
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

  /* 每页硬超时，绝不空等 */
  const nav = (url) => new Promise(resolve => {
    let done = false;
    const fin = () => { if (done) return; done = true; cb = null; resolve(); };
    cb = fin;
    setTimeout(fin, 3500);
    send('Page.navigate', { url }).catch(fin);
  });

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  const PROBE = `(() => {
    const e = document.querySelector('.s-nav,.series-nav');
    if (!e) return JSON.stringify({ none: true });
    const cs = getComputedStyle(e);
    const r  = e.getBoundingClientRect();
    // 当前篇那一项：.cur（FE 用 a.cur）或 .ss-cur
    const cur = e.querySelector('a.cur,.ss-cur');
    let marked = false, mark = '-';
    if (cur) {
      const c = getComputedStyle(cur);
      const solid = c.backgroundColor !== 'rgba(0, 0, 0, 0)';
      const grad  = c.backgroundImage !== 'none';
      marked = solid || grad;
      mark = grad ? 'gradient' : (solid ? c.backgroundColor : 'none');
    }
    return JSON.stringify({
      cls: e.className,
      bd: cs.borderTopWidth, rd: cs.borderRadius, pad: cs.paddingTop,
      bg: cs.backgroundColor, h: Math.round(r.height), mark: mark,
      links: e.querySelectorAll('a').length, marked: marked
    });
  })()`;

  console.log('文件'.padEnd(34) + '类            边框   圆角   内边距  高    链接  当前项标记');
  console.log('-'.repeat(112));
  let bad = 0, js = 0;
  for (const f of files) {
    errs.length = 0;
    await nav('about:blank');
    await nav('file:///' + DIR.replace(/\\/g, '/') + '/' + f);
    await new Promise(r => setTimeout(r, 260));
    const raw = await ev(PROBE);
    let o; try { o = JSON.parse(raw); } catch (e) { o = null; }
    if (!o || o.none) { console.log(('  !! ' + f).padEnd(34) + '（无页尾导航）'); bad++; continue; }
    const styled = o.bd !== '0px' && o.rd !== '0px' && o.pad !== '0px';
    const ok = styled && o.marked && o.links >= 3;
    if (!ok) bad++;
    if (errs.length) js++;
    console.log(('  ' + (ok ? 'OK' : '!!') + ' ' + f).padEnd(34)
      + String(o.cls).padEnd(14) + o.bd.padEnd(7) + o.rd.padEnd(7)
      + o.pad.padEnd(8) + String(o.h).padEnd(6) + String(o.links).padEnd(6) + o.mark.slice(0, 26));
  }
  console.log('');
  console.log('  导航样式不合格: ' + bad + ' / ' + files.length);
  console.log('  有 JS 异常的页面: ' + js + ' / ' + files.length);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
