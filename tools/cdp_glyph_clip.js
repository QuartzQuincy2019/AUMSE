/* Compare the rendered PIXELS of the first glyph of MA in different contexts.
   If positional features (init/medi/fina/isol) are applied, the three clips
   must differ. Canvas is useless here (no ctx.fontFeatureSettings in Chromium),
   so we screenshot the page and crop the first-character box server-side. */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9333);
const OUT = process.argv[3];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (m, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 700, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/report/_measure2.html' });
  await new Promise(r => setTimeout(r, 3000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };
  const boxes = JSON.parse(await ev('JSON.stringify(Object.assign({},window.__boxes,{size:(()=>{const e=document.querySelectorAll(".wrap")[0].getBoundingClientRect();return {x:e.left,y:e.top};})()}))'));
  console.log('layout boxes:', JSON.stringify(boxes));

  /* viewport-relative rectangles for each first-char cell */
  const rects = JSON.parse(await ev(`(()=>{
    const els=[...document.querySelectorAll('.m')];
    const out={};
    ['ctx','iso','mid'].forEach((k,i)=>{
      const el=els[i]; const r=document.createRange();
      r.setStart(el.firstChild,0); r.setEnd(el.firstChild,1);
      const b=r.getBoundingClientRect();
      out[k]=[b.left,b.top,b.width,b.height];
    });
    return JSON.stringify(out);})()`));
  console.log('viewport rects:', JSON.stringify(rects));

  const shots = {};
  for (const k of ['ctx', 'iso', 'mid']) {
    const [left, top, width, height] = rects[k];
    const r = await send('Page.captureScreenshot', {
      format: 'png',
      clip: { x: Math.max(0, left - 2), y: Math.max(0, top - 4), width: Math.min(width + 4, 900), height: Math.min(height + 10, 200), scale: 4 }
    });
    if (!r.result || !r.result.data) { console.log('clip failed for ' + k + ': ' + JSON.stringify(r).slice(0, 200)); continue; }
    const p = OUT + '\\_clip_' + k + '.png';
    fs.writeFileSync(p, Buffer.from(r.result.data, 'base64'));
    shots[k] = p;
  }
  console.log('clips: ' + JSON.stringify(shots));
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
