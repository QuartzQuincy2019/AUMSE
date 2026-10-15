/* 用真实坐标点击来测「目录」按钮（而不是 DOM .click()），
   这样能查出「被别的元素挡住」这类问题。 */
const http = require('http');
const [PORT, URL_] = process.argv.slice(2);

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
    if (m.method === 'Runtime.consoleAPICalled')
      errs.push('console.' + m.params.type + ': ' + m.params.args.map(a => a.value ?? a.description).join(' '));
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Log.enable').catch(() => {});
  await send('Emulation.setDeviceMetricsOverride', { width: 393, height: 852, deviceScaleFactor: 2, mobile: true });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: URL_ });
  await new Promise(r => setTimeout(r, 2500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description);
    return r.result.result.value;
  };

  console.log('按钮是否存在 :', await ev(`!!document.getElementById('tocToggle')`));
  console.log('按钮可见     :', await ev(`(()=>{const b=document.getElementById('tocToggle');
      if(!b) return 'n/a'; const s=getComputedStyle(b); const r=b.getBoundingClientRect();
      return JSON.stringify({display:s.display,visibility:s.visibility,opacity:s.opacity,
        zIndex:s.zIndex,pos:s.position,rect:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]});})()`));
  console.log('按钮中心命中的元素 :', await ev(`(()=>{const b=document.getElementById('tocToggle');
      if(!b) return 'n/a'; const r=b.getBoundingClientRect();
      const el=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2);
      return el ? (el.tagName + (el.id?'#'+el.id:'') + (el.className?'.'+String(el.className).split(' ')[0]:'')) : 'null';})()`));
  console.log('#toc 初始 transform :', await ev(`getComputedStyle(document.getElementById('toc')).transform`));
  console.log('#toc 初始 rect      :', await ev(`(()=>{const r=document.getElementById('toc').getBoundingClientRect();
      return JSON.stringify([Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]);})()`));

  /* --- 真实坐标点击 --- */
  const box = JSON.parse(await ev(`(()=>{const b=document.getElementById('tocToggle');
      const r=b.getBoundingClientRect(); return JSON.stringify({x:r.left+r.width/2,y:r.top+r.height/2});})()`));
  console.log('');
  console.log('真实点击坐标 :', JSON.stringify(box));

  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {
      type, x: box.x, y: box.y, button: 'left', clickCount: 1, pointerType: 'touch',
    });
  }
  await new Promise(r => setTimeout(r, 600));

  console.log('点击后 open  :', await ev(`document.getElementById('toc').classList.contains('open')`));
  console.log('点击后 body  :', await ev(`document.body.className`));
  console.log('点击后按钮文字:', await ev(`document.getElementById('tocToggle').textContent`));
  console.log('点击后 transform:', await ev(`getComputedStyle(document.getElementById('toc')).transform`));
  console.log('点击后 rect  :', await ev(`(()=>{const r=document.getElementById('toc').getBoundingClientRect();
      return JSON.stringify([Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]);})()`));

  console.log('');
  console.log('异常/日志 :', errs.length ? errs.join(' | ') : 'none');
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
