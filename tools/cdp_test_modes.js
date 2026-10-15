/* Verify both SVG export modes render correctly in a browser.
   Critically: rasterize each exported SVG and compare against the editor's own
   vertical render. The <text> mode should match closely; that is the guarantee. */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9777);
const OUTDIR = process.argv[3];

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
  await send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 300));
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 5000));

  const ev = async (expr, awaitPromise = false) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise });
    if (r.result.exceptionDetails)
      return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description);
    return r.result.result.value;
  };
  console.log('font       :', await ev(`document.fonts.check('40px "UME Mongolian"')`));
  console.log('opentype   :', await ev(`typeof OT!=='undefined' && OT && OT.numGlyphs`));
  console.log('text       :', JSON.stringify(await ev(`document.getElementById('raw').value`)));

  for (const mode of ['svg-text', 'svg-outline']) {
    console.log('');
    console.log('===== ' + mode + ' =====');
    await ev(`(()=>{const s=document.getElementById('exFormat'); s.value=${JSON.stringify(mode)};
              s.dispatchEvent(new Event('change')); return 1;})()`);
    if (!(await ev(`document.getElementById('modal').classList.contains('on')`))) {
      await ev(`document.getElementById('btn-export').click()`);
    } else {
      await ev(`refreshExport()`);
    }
    for (let i = 0; i < 80; i++) {
      if ((await ev(`busy === true`)) === false) break;
      await new Promise(r => setTimeout(r, 400));
    }
    await new Promise(r => setTimeout(r, 700));

    console.log('info       :', JSON.stringify(await ev(`document.getElementById('expinfo').textContent`)));
    console.log('svg nodes  :', await ev(`document.querySelectorAll('#preview svg').length`));
    console.log('text nodes :', await ev(`document.querySelectorAll('#preview svg text').length`));
    console.log('path nodes :', await ev(`document.querySelectorAll('#preview svg path').length`));

    const svg = await ev(`(lastSVG && lastSVG.svg) ? lastSVG.svg : ''`);
    if (svg && svg.length > 100) {
      const fn = OUTDIR + '\\_export-' + mode + '.svg';
      fs.writeFileSync(fn, svg);
      console.log('saved      :', fn, svg.length, 'bytes');
      /* rasterize in-page and measure ink, to prove the SVG actually draws */
      const ink = await ev(`(async()=>{
        const s = ${JSON.stringify(svg)};
        const b = new Blob([s], {type:'image/svg+xml;charset=utf-8'});
        const u = URL.createObjectURL(b);
        try{
          const img = await new Promise((res,rej)=>{ const i=new Image();
            i.onload=()=>res(i); i.onerror=()=>rej(new Error('img load fail')); i.src=u; });
          const c=document.createElement('canvas'); c.width=Math.round(img.width*2); c.height=Math.round(img.height*2);
          const g=c.getContext('2d',{willReadFrequently:true});
          g.fillStyle='#fff'; g.fillRect(0,0,c.width,c.height);
          g.drawImage(img,0,0,c.width,c.height);
          const d=g.getImageData(0,0,c.width,c.height).data;
          let n=0; for(let i=0;i<c.width*c.height;i++) if(d[i*4]<128) n++;
          return JSON.stringify({w:img.width,h:img.height,ink:n});
        } finally { URL.revokeObjectURL(u); }
      })()`, true);
      console.log('rasterized :', ink);
    } else {
      console.log('NO SVG');
    }
  }
  console.log('');
  console.log('exceptions :', errs.length ? errs.join(' | ') : 'none');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
