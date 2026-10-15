/* 干净的桌面截图：先重置设备指标，再截指定元素附近 */
const http = require('http');
const fs = require('fs');
const PORT = process.argv[2];
const URL = process.argv[3];
const SEL = process.argv[4];
const OUT = process.argv[5];
const W = Number(process.argv[6] || 1400);
const H = Number(process.argv[7] || 1000);

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  // 可能开了多个标签页 —— 必须新建一个，否则会截到别的页
  await new Promise((res, rej) => {
    http.get({ host: '127.0.0.1', port: Number(PORT), path: '/json/new?about:blank' },
      r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res(d)); }).on('error', rej);
  });
  await new Promise(r => setTimeout(r, 400));
  const list = await get('/json/list');
  const t = list.filter(x => x.type === 'page').pop();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });

  // 关键：先清掉移动端模拟，再设桌面尺寸
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: W, height: H, deviceScaleFactor: 1, mobile: false });

  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2200));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  const y = await ev(`(()=>{
    const e = document.querySelector(${JSON.stringify(SEL)});
    if (!e) return null;
    const r = e.getBoundingClientRect();
    window.scrollTo(0, Math.max(0, r.top + window.scrollY - 24));
    return Math.round(window.scrollY);
  })()`);
  console.log('视口 ' + W + 'x' + H + '  滚动到 y=' + y);
  await new Promise(r => setTimeout(r, 400));

  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(OUT, Buffer.from(shot.result.data, 'base64'));
  console.log('saved ' + OUT);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
