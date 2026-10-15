/* 检查桌面端布局是否被移动端补丁影响：
   #toc 是否仍是侧栏、正文起始位置是否正常、有无横向溢出 */
const http = require('http');
const fs = require('fs');
const PORT = process.argv[2];
const LISTFILE = process.argv[3];
const URLS = JSON.parse(fs.readFileSync(LISTFILE, 'utf8'));

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text);
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description);
    return r.result.result.value;
  };

  const SIZES = [
    { n: '1920 (FHD)  ', w: 1920, h: 1080 },
    { n: '1440 (MBP)   ', w: 1440, h: 900 },
    { n: '1280 (常用)  ', w: 1280, h: 800 },
    { n: '1024 (小屏)  ', w: 1024, h: 768 },
  ];

  console.log('尺寸            横向溢出  #toc显示  #toc宽  正文左边距  按钮可见  正文高');
  console.log('-'.repeat(80));

  for (const u of URLS) {
    console.log('--- ' + u.tag + ' ---');
    for (const s of SIZES) {
      await send('Emulation.setDeviceMetricsOverride',
        { width: s.w, height: s.h, deviceScaleFactor: 1, mobile: false });
      await send('Page.navigate', { url: 'about:blank' });
      await new Promise(r => setTimeout(r, 180));
      await send('Page.navigate', { url: u.url });
      await new Promise(r => setTimeout(r, 1600));

      const o = JSON.parse(await ev(`(()=>{
        const de = document.documentElement;
        const toc = document.getElementById('toc');
        const tr = toc.getBoundingClientRect();
        const main = document.querySelector('main');
        const mr = main.getBoundingClientRect();
        const btn = document.getElementById('tocToggle');
        return JSON.stringify({
          over: de.scrollWidth - de.clientWidth,
          tocDisp: getComputedStyle(toc).display,
          tocW: Math.round(tr.width),
          tocLeft: Math.round(tr.left),
          mainLeft: Math.round(mr.left),
          btn: btn ? getComputedStyle(btn).display : 'absent',
          h: de.scrollHeight,
        });
      })()`));

      console.log(
        s.n +
        String(o.over === 0 ? '无' : ('有 ' + o.over)).padEnd(9) +
        o.tocDisp.padEnd(9) + String(o.tocW).padEnd(8) +
        String(o.mainLeft).padEnd(12) +
        String(o.btn).padEnd(10) + o.h
      );
    }
    console.log('');
  }
  console.log('JS 异常 : ' + (errs.length ? errs.join(' | ') : 'none'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
