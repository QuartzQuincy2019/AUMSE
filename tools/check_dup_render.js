/* 检查页面上是否出现了重复的一级标题 / 系列导航条 */
const http = require('http');
const DIR = process.argv[2];
const PORT = process.argv[3];
const fs = require('fs');

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
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  console.log('文件'.padEnd(36) + 'h1  .sub-title  series-nav  page-nav  main数  h1文字');
  console.log('-'.repeat(118));

  let bad = 0;
  for (const f of files) {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 180));
    await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await new Promise(r => setTimeout(r, 1700));

    const r = await ev(`(()=>{
      const q = s => document.querySelectorAll(s).length;
      const h1s = [...document.querySelectorAll('h1')].map(e => e.textContent.trim().slice(0,28));
      return JSON.stringify({
        h1: q('h1'), sub: q('.sub-title'), sn: q('.series-nav'),
        pn: q('.page-nav'), main: q('main'), fab: q('.home-fab'),
        txt: h1s.join(' / ')
      });
    })()`);
    let o; try { o = JSON.parse(r); } catch (e) { console.log('  ?? ' + f + ' ' + r); continue; }
    const dup = (o.h1 > 1 || o.sub > 1 || o.sn > 1 || o.pn > 1 || o.main > 1 || o.fab > 1);
    if (dup) bad++;
    console.log(('  ' + (dup ? '!!' : 'OK') + ' ' + f).padEnd(36)
      + String(o.h1).padStart(3)
      + String(o.sub).padStart(11)
      + String(o.sn).padStart(12)
      + String(o.pn).padStart(10)
      + String(o.main).padStart(7)
      + '   ' + o.txt
      + (dup ? '   ← 重复!' : ''));
  }
  console.log('');
  console.log('  有重复的页面: ' + bad + ' / ' + files.length);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
