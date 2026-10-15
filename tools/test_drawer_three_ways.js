/* 抽屉里点目录项：分三种方式，定位「点了不跳」到底出在哪一环
     A. JS 直接 .click()            —— 只验证锚点本身管不管用
     B. dispatchEvent 造一个点击     —— 验证事件冒泡里有没有被拦
     C. 真实鼠标事件（CDP Input）    —— 验证命中测试这一层 */
const http = require('http');
const PORT = process.argv[2];
const URL_ = process.argv[3];
const W = Number(process.argv[4] || 375);
const H = Number(process.argv[5] || 667);

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
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: W, height: H, deviceScaleFactor: 2, mobile: true });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 200);
    return r.result.result.value;
  };
  const reload = async () => {
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 250));
    await send('Page.navigate', { url: URL_ });
    await new Promise(r => setTimeout(r, 2000));
  };
  const openDrawer = async () => {
    await ev(`document.getElementById('tocToggle').click()`);
    await new Promise(r => setTimeout(r, 400));
  };

  // ---------- A. JS .click() ----------
  await reload(); await openDrawer();
  console.log('--- A. JS 直接 .click() ---');
  console.log('  抽屉开着: ' + await ev(`document.getElementById('toc').classList.contains('open')`));
  console.log('  hash 前: ' + await ev('location.hash || "(空)"'));
  await ev(`document.querySelectorAll('#toc a')[4].click()`);
  await new Promise(r => setTimeout(r, 600));
  console.log('  hash 后: ' + await ev('location.hash || "(空)"'));
  console.log('  → ' + ((await ev('location.hash')) ? '✅ 锚点本身没问题' : '❌ 锚点自身就有问题'));

  // ---------- B. dispatchEvent ----------
  await reload(); await openDrawer();
  console.log('');
  console.log('--- B. dispatchEvent 造点击 ---');
  console.log('  hash 前: ' + await ev('location.hash || "(空)"'));
  await ev(`(()=>{const a=document.querySelectorAll('#toc a')[4];
     a.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));})()`);
  await new Promise(r => setTimeout(r, 600));
  console.log('  hash 后: ' + await ev('location.hash || "(空)"'));
  console.log('  抽屉还开: ' + await ev(`document.getElementById('toc').classList.contains('open')`));
  console.log('  → ' + ((await ev('location.hash')) ? '✅ 冒泡链没被拦' : '❌ 冒泡链上有东西拦了'));

  // ---------- C. 真实鼠标 ----------
  await reload(); await openDrawer();
  console.log('');
  console.log('--- C. 真实鼠标事件 ---');
  const p = JSON.parse(await ev(`(()=>{const a=document.querySelectorAll('#toc a')[4];
     const r=a.getBoundingClientRect();
     return JSON.stringify({x:Math.round(r.left+30),y:Math.round(r.top+r.height/2)});})()`) || 'null');
  console.log('  目标点: ' + JSON.stringify(p));
  console.log('  该点 elementFromPoint: ' + await ev(
    `(()=>{const e=document.elementFromPoint(${p.x},${p.y});
       return e?e.tagName.toLowerCase()+(e.className?'.'+String(e.className).split(' ')[0]:''):'null';})()`));
  console.log('  hash 前: ' + await ev('location.hash || "(空)"'));
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent',
      { type, x: p.x, y: p.y, button: 'left', clickCount: 1, pointerType: 'mouse' });
  }
  await new Promise(r => setTimeout(r, 700));
  console.log('  hash 后: ' + await ev('location.hash || "(空)"'));
  console.log('  抽屉还开: ' + await ev(`document.getElementById('toc').classList.contains('open')`));
  console.log('  → ' + ((await ev('location.hash')) ? '✅ 真实点击能跳' : '❌ 真实点击不跳'));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
