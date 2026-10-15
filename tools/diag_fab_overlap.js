/* 诊断：窄屏下「返回 home」悬浮按钮是否盖住了目录项，导致点不中。
   做法：
     1. 列出目录里每个链接的位置
     2. 列出 home 按钮的位置
     3. 逐个做「命中测试」—— 用 elementFromPoint 看这个坐标上真正拿到事件的是谁
     4. 再模拟一次真实点击，看抽屉会不会关、跳转会不会发生 */
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
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: URL_ });
  await new Promise(r => setTimeout(r, 2200));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
    return r.result.result.value;
  };

  // 1) 打开抽屉
  console.log(await ev(`(()=>{
    const btn = document.getElementById('tocToggle');
    if (!btn) return '没有 #tocToggle 按钮（宽屏？）';
    btn.click();
    return '已点开抽屉按钮；toc.open = ' + document.getElementById('toc').classList.contains('open');
  })()`));
  await new Promise(r => setTimeout(r, 500));

  console.log(await ev(`(()=>{
    const out = [];
    const vw = window.innerWidth, vh = window.innerHeight;
    out.push('视口 ' + vw + 'x' + vh);

    const fab = document.querySelector('.home-fab');
    const toc = document.getElementById('toc');
    if (!toc) return '没有 #toc';

    const fr = fab ? fab.getBoundingClientRect() : null;
    const tr = toc.getBoundingClientRect();
    out.push('');
    out.push('目录面板: left=' + Math.round(tr.left) + ' right=' + Math.round(tr.right)
      + ' top=' + Math.round(tr.top) + ' bottom=' + Math.round(tr.bottom));
    out.push('  计算样式 z-index=' + getComputedStyle(toc).zIndex
      + '  position=' + getComputedStyle(toc).position);
    if (fr) {
      out.push('home 按钮: left=' + Math.round(fr.left) + ' right=' + Math.round(fr.right)
        + ' top=' + Math.round(fr.top) + ' bottom=' + Math.round(fr.bottom));
      out.push('  计算样式 z-index=' + getComputedStyle(fab).zIndex
        + '  pointer-events=' + getComputedStyle(fab).pointerEvents);
    } else {
      out.push('home 按钮: 不存在');
    }

    // 2) 逐个目录项做命中测试（取该项水平居中、垂直居中的点）
    out.push('');
    out.push('目录项命中测试（middle 点上真正拿到事件的元素）:');
    const links = [...toc.querySelectorAll('a')];
    let blocked = 0;
    links.forEach((a, i) => {
      const r = a.getBoundingClientRect();
      const x = Math.round(r.left + Math.min(r.width / 2, 40));
      const y = Math.round(r.top + r.height / 2);
      let hit = null, desc = '(视口外)';
      if (y >= 0 && y <= vh) {
        hit = document.elementFromPoint(x, y);
        desc = hit ? (hit.tagName.toLowerCase()
          + (hit.className ? '.' + String(hit.className).split(' ')[0] : '')) : 'null';
      }
      const selfHit = hit === a || (hit && a.contains(hit));
      if (!selfHit && y >= 0 && y <= vh) blocked++;
      out.push('  ' + String(i + 1).padStart(2) + ' y=' + String(y).padStart(4)
        + '  ' + (selfHit ? 'OK  ' : '挡住!') + ' 命中=' + desc
        + '  「' + a.textContent.trim().slice(0, 20) + '」');
    });
    out.push('');
    out.push('被挡住的目录项: ' + blocked + ' / ' + links.length);
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
