/* 全站回归：窄屏抽屉里**每一个**目录项是否都能点中。
   判定标准（最严格的一条）：该链接中心点的 elementFromPoint
   必须落在链接自身或其子元素上 —— 只要被任何东西盖住就算失败。 */
const http = require('http');
const DIR = process.argv[2];
const PORT = process.argv[3];
const W = Number(process.argv[4] || 375);
const H = Number(process.argv[5] || 667);
const fs = require('fs');
const path = require('path');

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: W, height: H, deviceScaleFactor: 1, mobile: true });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  let totalLinks = 0, totalBad = 0, badPages = 0;
  console.log('文件'.padEnd(36) + '目录项   点不中   首个被挡的项');
  console.log('-'.repeat(96));

  for (const f of files) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 200));
    await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await new Promise(r => setTimeout(r, 1800));

    await ev(`(()=>{const b=document.getElementById('tocToggle'); if(b) b.click();})()`);
    await new Promise(r => setTimeout(r, 350));

    const res = await ev(`(()=>{
      const toc = document.getElementById('toc');
      if (!toc) return JSON.stringify({err:'没有目录'});
      const vh = window.innerHeight;
      let bad = 0, first = '', n = 0, offscreen = 0;
      toc.querySelectorAll('a').forEach(a => {
        const r = a.getBoundingClientRect();
        const x = Math.round(r.left + Math.min(r.width / 2, 40));
        const y = Math.round(r.top + r.height / 2);
        n++;
        if (y < 0 || y > vh) { offscreen++; return; }   /* 视口外，需要滚动，不算被挡 */
        const hit = document.elementFromPoint(x, y);
        const ok = hit === a || (hit && a.contains(hit));
        if (!ok) {
          bad++;
          if (!first) first = '「' + a.textContent.trim().slice(0,22) + '」y=' + y
            + ' 被 ' + (hit ? hit.tagName.toLowerCase()
              + (hit.id ? '#' + hit.id : '')
              + (hit.className ? '.' + String(hit.className).split(' ')[0] : '') : 'null') + ' 挡';
        }
      });
      return JSON.stringify({n:n, bad:bad, offscreen:offscreen, first:first});
    })()`);

    let o;
    try { o = JSON.parse(res); } catch (e) { console.log('  !! ' + f + '  ' + res); continue; }
    if (o.err) { console.log('  ?? ' + f.padEnd(34) + o.err); continue; }

    totalLinks += o.n;
    totalBad += o.bad;
    if (o.bad > 0) badPages++;
    const mark = o.bad === 0 ? 'OK' : '!!';
    console.log(('  ' + mark + ' ' + f).padEnd(36)
      + String(o.n).padStart(5)
      + String(o.bad).padStart(9)
      + (o.first ? '   ' + o.first : '')
      + (o.offscreen ? '   (视口外 ' + o.offscreen + ')' : ''));
  }

  console.log('');
  console.log('  合计目录项 ' + totalLinks + '，点不中 ' + totalBad
    + '，有问题的页面 ' + badPages + ' / ' + files.length
    + (totalBad === 0 ? '   ✅ 全部可点' : ''));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
