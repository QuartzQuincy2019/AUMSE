/* Test PNG export: click 保存文件 with png selected and verify a PNG is produced. */
const http = require('http');
const PORT = Number(process.argv[2] || 9400);
const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
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
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 300));
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 5000));
  const ev = async (expr, awaitPromise = false) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception||{}).description);
    return r.result.result.value;
  };

  console.log('UI check:');
  console.log('  format options :', await ev(`[...document.querySelectorAll('#exFormat option')].map(o=>o.value).join(' | ')`));
  console.log('  has outline opt:', await ev(`!!document.querySelector('#exFormat option[value="svg-outline"]')`));

  /* 切到 PNG，测栅格化 */
  console.log('');
  console.log('PNG rasterization:');
  console.log(await ev(`(async()=>{
    const out = [];
    document.getElementById('exFormat').value = 'png';
    document.getElementById('exPx').value = '3';
    document.getElementById('btn-export').click();
    for (let i=0;i<60 && busy; i++) await new Promise(r=>setTimeout(r,200));
    await new Promise(r=>setTimeout(r,600));
    out.push('  expinfo = ' + document.getElementById('expinfo').textContent.replace(/\\n/g,' | '));
    out.push('  exSize  = ' + document.getElementById('exSize').textContent);
    // 直接跑栅格化路径，检查产出的 PNG 尺寸
    const svg = lastSVG.svg;
    const blob = new Blob([svg], {type:'image/svg+xml;charset=utf-8'});
    const u = URL.createObjectURL(blob);
    try{
      const img = await new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>rej(new Error('load fail'));i.src=u;});
      const px = 3;
      const c = document.createElement('canvas');
      c.width = Math.round(lastSVG.W*px); c.height = Math.round(lastSVG.H*px);
      const g = c.getContext('2d',{willReadFrequently:true});
      g.drawImage(img,0,0,c.width,c.height);
      const d = g.getImageData(0,0,c.width,c.height).data;
      let ink=0; for(let i=0;i<c.width*c.height;i++) if(d[i*4]<128) ink++;
      out.push('  PNG canvas = ' + c.width + 'x' + c.height + '  ink=' + ink);
      const b64 = c.toDataURL('image/png');
      out.push('  PNG bytes  = ' + Math.round(b64.length*3/4));
    } finally { URL.revokeObjectURL(u); }
    return out.join('\\n');
  })()`, true));
  console.log('');
  console.log('exceptions :', errs.length ? errs.join(' | ') : 'none');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
