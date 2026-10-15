/* 真实点击测试：抽屉打开后，目录项到底能不能点、点了会不会跳转 */
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
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: W, height: H, deviceScaleFactor: 2, mobile: true });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };
  const tap = async (x, y) => {
    for (const type of ['mousePressed', 'mouseReleased']) {
      await send('Input.dispatchMouseEvent',
        { type, x, y, button: 'left', clickCount: 1, pointerType: 'mouse' });
    }
  };
  const pos = async sel => ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});
    if(!e) return null; const r=e.getBoundingClientRect();
    return JSON.stringify({x:Math.round(r.left+Math.min(r.width/2,40)),
      y:Math.round(r.top+r.height/2)});})()`);

  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: URL_ });
  await new Promise(r => setTimeout(r, 2200));

  // --- A. 用真实鼠标事件点第 5 个目录项 ---
  console.log('--- A. 点目录项（真实鼠标事件）---');
  await ev(`document.getElementById('tocToggle').click()`);
  await new Promise(r => setTimeout(r, 500));
  let p = JSON.parse(await pos('#toc a:nth-of-type(5)') || 'null');
  console.log('  目标点: ' + JSON.stringify(p));
  console.log('  点击前 hash: ' + await ev('location.hash || "(空)"'));
  console.log('  点击前该点命中: ' + await ev(
    `(()=>{const e=document.elementFromPoint(${p.x},${p.y});
      return e?e.tagName.toLowerCase()+(e.className?'.'+String(e.className).split(' ')[0]:''):'null';})()`));
  await tap(p.x, p.y);
  await new Promise(r => setTimeout(r, 700));
  console.log('  点击后 hash: ' + await ev('location.hash || "(空)"'));
  console.log('  抽屉还开着吗: ' + await ev(
    `document.getElementById('toc').classList.contains('open')`));
  console.log('  → ' + (await ev('location.hash') ? '跳转成功' : '❌ 没有跳转'));

  // --- B. home 按钮遮挡了抽屉底部多少 ---
  console.log('');
  console.log('--- B. home 按钮 vs 抽屉 ---');
  await ev(`document.getElementById('tocToggle').click()`);
  await new Promise(r => setTimeout(r, 400));
  console.log(await ev(`(()=>{
    const out=[];
    const fab=document.querySelector('.home-fab');
    const toc=document.getElementById('toc');
    const fr=fab.getBoundingClientRect(), tr=toc.getBoundingClientRect();
    out.push('  抽屉占 ' + Math.round(tr.width) + 'x' + Math.round(tr.height)
      + '，按钮占 ' + Math.round(fr.width) + 'x' + Math.round(fr.height));
    out.push('  水平重叠: ' + Math.max(0, Math.min(fr.right,tr.right)-Math.max(fr.left,tr.left)) + 'px');
    out.push('  垂直重叠: ' + Math.max(0, Math.min(fr.bottom,tr.bottom)-Math.max(fr.top,tr.top)) + 'px');
    // 抽屉里所有可点元素，看谁被按钮压住
    const hit=[];
    toc.querySelectorAll('a').forEach(a=>{
      const r=a.getBoundingClientRect();
      const x=Math.round(r.left+Math.min(r.width/2,40)), y=Math.round(r.top+r.height/2);
      const e=document.elementFromPoint(x,y);
      if (e && fab.contains(e)) hit.push(a.textContent.trim().slice(0,24)+'  y='+y);
    });
    out.push('  被按钮压住、点不到的条目: ' + (hit.length?('\\n     '+hit.join('\\n     ')):'无'));
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
