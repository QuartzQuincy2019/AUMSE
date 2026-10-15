/* 用真实坐标点击逐个验证「目录」抽屉：开 / 关 / 遮罩关闭 */
const http = require('http');
const fs = require('fs');
const PORT = process.argv[2];
const LISTFILE = process.argv[3];
let URLS = [];
try {
  URLS = JSON.parse(fs.readFileSync(LISTFILE, 'utf8'));
} catch (e) {
  console.error('读取 URL 列表失败 (' + LISTFILE + '): ' + e.message);
  process.exit(1);
}
if (!URLS.length) { console.error('URL 列表为空'); process.exit(1); }

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
  const tap = async (x, y) => {
    for (const type of ['mousePressed', 'mouseReleased'])
      await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1, pointerType: 'touch' });
  };
  const centerOf = async sel => JSON.parse(await ev(`(()=>{const b=document.querySelector(${JSON.stringify(sel)});
      if(!b) return 'null'; const r=b.getBoundingClientRect();
      return JSON.stringify({x:r.left+r.width/2,y:r.top+r.height/2,w:Math.round(r.width),h:Math.round(r.height)});})()`));

  const VIEWPORTS = [
    { n: 'iPhone SE 375', w: 375, h: 667, dpr: 2 },
    { n: 'Pixel 412', w: 412, h: 915, dpr: 2.6 },
    { n: 'iPad 744', w: 744, h: 1133, dpr: 2 },
  ];

  for (const u of URLS) {
    console.log('===== ' + u.tag + ' =====');
    for (const vp of VIEWPORTS) {
      await send('Emulation.setDeviceMetricsOverride',
        { width: vp.w, height: vp.h, deviceScaleFactor: vp.dpr, mobile: true });
      await send('Page.navigate', { url: 'about:blank' });
      await new Promise(r => setTimeout(r, 200));
      await send('Page.navigate', { url: u.url });
      await new Promise(r => setTimeout(r, 1900));

      const init = await ev(`(()=>{const r=document.getElementById('toc').getBoundingClientRect();
        return JSON.stringify({x:Math.round(r.left),w:Math.round(r.width),h:Math.round(r.height),
          disp:getComputedStyle(document.getElementById('toc')).display});})()`);
      const b = await centerOf('#tocToggle');
      if (!b) { console.log('  ' + vp.n + ' 按钮缺失'); continue; }

      /* 点开 */
      await tap(b.x, b.y);
      await new Promise(r => setTimeout(r, 520));
      const opened = await ev(`(()=>{const r=document.getElementById('toc').getBoundingClientRect();
        return JSON.stringify({open:document.getElementById('toc').classList.contains('open'),
          x:Math.round(r.left), w:Math.round(r.width)});})()`);

      /* 点目录里的一个链接，应自动收起 */
      const link = await centerOf('#toc a[href="#s5"]') || await centerOf('#toc a');
      let afterLink = 'n/a';
      if (link && JSON.parse(opened).x === 0) {
        await tap(link.x, link.y);
        await new Promise(r => setTimeout(r, 520));
        afterLink = await ev(`document.getElementById('toc').classList.contains('open') ? '仍展开' : '已收起'`);
      }

      /* 再点按钮开、然后点右侧空白（遮罩）关 */
      await tap(b.x, b.y);
      await new Promise(r => setTimeout(r, 500));
      const reopened = await ev(`document.getElementById('toc').classList.contains('open')`);
      await tap(vp.w - 22, vp.h / 2);
      await new Promise(r => setTimeout(r, 520));
      const closedByBackdrop = await ev(`document.getElementById('toc').classList.contains('open') ? '否' : '是'`);

      const o = JSON.parse(opened);
      console.log('  ' + vp.n.padEnd(14) +
        '初始[' + JSON.parse(init).disp + ' ' + JSON.parse(init).x + 'px]  ' +
        '点开 ' + (o.open && o.x === 0 ? 'OK' : 'FAIL') + ' (w=' + o.w + ')  ' +
        '点链接 ' + afterLink + '  ' +
        '再点开 ' + (reopened ? 'OK' : 'FAIL') + '  ' +
        '点遮罩关 ' + closedByBackdrop);
    }
    console.log('');
  }
  console.log('JS 异常 : ' + (errs.length ? errs.join(' | ') : 'none'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
