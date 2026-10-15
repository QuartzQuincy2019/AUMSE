/* check_home.js —— 一次加载查完首页：分组顺序、留言、配色、响应式、截图 */
const http = require('http');
const fs = require('fs');

const PORT = Number(process.argv[2]);
const FILE = process.argv[3];
const SHOT = process.argv[4] || '';
const MODE = process.argv[5] || 'light';

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  await new Promise(res => {
    http.get({ host: '127.0.0.1', port: PORT, path: '/json/new?about:blank' },
      r => { r.on('data', () => {}); r.on('end', res); }).on('error', res);
  });
  await new Promise(r => setTimeout(r, 350));
  const t = (await get('/json/list')).filter(x => x.type === 'page').pop();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let loaded = null; const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description
                || m.params.exceptionDetails.text);
    if (m.method === 'Page.loadEventFired' && loaded) { loaded(); loaded = null; }
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
  await send('Emulation.setEmulatedMedia',
    { features: [{ name: 'prefers-color-scheme', value: MODE }] });

  const ev = async expr => {
    const r = await send('Runtime.evaluate',
      { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 200);
    return r.result.result.value;
  };

  console.log('===== 桌面 1400 宽 · ' + MODE + ' =====');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1400, height: 1400, deviceScaleFactor: 1, mobile: false });
  let wait = new Promise(r => { loaded = r; setTimeout(r, 4000); });
  await send('Page.navigate', { url: FILE });
  await wait;
  await new Promise(r => setTimeout(r, 400));

  console.log(await ev(`(() => {
    const out = [];
    out.push('分组顺序: ' + [...document.querySelectorAll('h2')]
      .map(h => h.textContent.replace(/共 \\d+ 篇|暂空/, '').trim()).join(' → '));
    out.push('卡片 ' + document.querySelectorAll('a.card').length
      + ' / 星标 ' + document.querySelectorAll('a.card.star').length
      + ' / 空槽 ' + document.querySelectorAll('.empty-slot').length);
    const m = document.querySelector('.lead-msg');
    out.push('留言块: ' + (m ? '有' : '❌ 无'));
    if (m) {
      const b = m.querySelector('.lead-msg-b'), d = m.querySelector('.lead-msg-d');
      out.push('  正文 ' + b.textContent.length + ' 字: ' + b.textContent.slice(0, 26) + '…');
      out.push('  日期: ' + d.textContent + '   text-align=' + getComputedStyle(d).textAlign);
      out.push('  正文字体: ' + getComputedStyle(b).fontFamily.slice(0, 30)
        + '  weight=' + getComputedStyle(b).fontWeight);
    }
    out.push('未替换占位符: ' + ((document.body.innerHTML.match(/@@[A-Z_]+@@/g) || []).join(',') || '无'));
    return out.join('\\n');
  })()`));

  if (SHOT) {
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(SHOT, Buffer.from(r.result.data, 'base64'));
    console.log('截图: ' + SHOT);
  }

  console.log('');
  console.log('===== 响应式 =====');
  console.log('设备'.padEnd(20) + '视口    横向溢出  卡片  分组');
  for (const [n, w, h] of [['iPhone SE', 375, 667], ['Galaxy S20 Ultra', 360, 800],
                           ['iPad mini', 744, 1133], ['桌面', 1400, 1000]]) {
    await send('Emulation.setDeviceMetricsOverride',
      { width: w, height: h, deviceScaleFactor: 1, mobile: w < 800 });
    wait = new Promise(r => { loaded = r; setTimeout(r, 4000); });
    await send('Page.navigate', { url: FILE });
    await wait;
    await new Promise(r => setTimeout(r, 300));
    const raw = await ev(`(() => {
      const de = document.documentElement;
      const over = [];
      document.querySelectorAll('.wrap *').forEach(e => {
        const b = e.getBoundingClientRect(), p = e.parentElement;
        if (!p || b.width < 2) return;
        if (b.right > p.getBoundingClientRect().right + 4 && over.length < 2)
          over.push(e.tagName.toLowerCase()
            + (e.className ? '.' + String(e.className).split(' ')[0] : ''));
      });
      return JSON.stringify({ sw: de.scrollWidth, vw: innerWidth,
        cards: document.querySelectorAll('a.card').length,
        groups: document.querySelectorAll('.grid').length, over: over });
    })()`);
    const o = JSON.parse(raw);
    console.log(('  ' + n).padEnd(20) + String(o.vw).padEnd(8)
      + (o.sw > o.vw + 2 ? ('有 ' + (o.sw - o.vw) + 'px ' + o.over.join(',')) : '无').padEnd(10)
      + String(o.cards).padStart(5) + String(o.groups).padStart(6));
  }
  console.log('');
  console.log('JS 异常: ' + (errs.length ? errs.join(' | ').slice(0, 200) : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
