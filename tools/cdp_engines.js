/* Screenshot UME.html in each vertical engine so the two can be compared,
   and report which engine is active plus whether the font loaded. */
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

  /* collect any uncaught exception thrown while the page boots */
  const errors = [];
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      errors.push((d.exception && d.exception.description) || d.text);
    }
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
      errors.push('console.error: ' + m.params.args.map(a => a.value).join(' '));
    }
  });

  await send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 4000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };
  console.log('font loaded :', await ev(`document.fonts.check('40px "UME Mongolian"')`));
  console.log('raw value   :', JSON.stringify(await ev(`document.getElementById('raw').value`)));
  console.log('palette keys:', await ev(`document.querySelectorAll('#palbody .key').length`));
  console.log('EXCEPTIONS  :', errors.length ? errors.join(' | ') : 'none');

  const shot = async (name) => {
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(OUT + '\\' + name, Buffer.from(r.result.data, 'base64'));
  };

  /* engine A */
  await ev(`(()=>{const s=document.getElementById('engine'); s.value='wm'; s.dispatchEvent(new Event('change')); return 1;})()`);
  await new Promise(r => setTimeout(r, 900));
  console.log('A visible   :', await ev(`document.getElementById('vwrap').style.display !== 'none'`));
  await shot('_engine_a.png');

  /* engine B */
  await ev(`(()=>{const s=document.getElementById('engine'); s.value='rot'; s.dispatchEvent(new Event('change')); return 1;})()`);
  await new Promise(r => setTimeout(r, 900));
  console.log('B visible   :', await ev(`document.getElementById('vrot-wrap').style.display !== 'none'`));
  console.log('B transform :', await ev(`getComputedStyle(document.getElementById('vrot')).transform`));
  console.log('B diag      :', await ev(`(()=>{
    const t=document.getElementById('vrot'), w=document.getElementById('vrot-wrap');
    const rotor=document.getElementById('vrot-rotor');
    const tr=rotor.getBoundingClientRect(), w2=w.getBoundingClientRect();
    return JSON.stringify({
      rotorLayoutBox: [Math.round(tr.x), Math.round(tr.y), Math.round(tr.width), Math.round(tr.height)],
      wrapBox: [Math.round(w2.x), Math.round(w2.y), Math.round(w2.width), Math.round(w2.height)],
      wrapScroll: [w.scrollWidth, w.scrollHeight, w.clientWidth, w.clientHeight],
      wrapScrollPos: [w.scrollLeft, w.scrollTop],
      textClientBox: [t.clientWidth, t.clientHeight],
      textStyleTransform: t.style.transform || '(none)',
      textInlineW: t.style.width
    });})()`));
  await shot('_engine_b.png');

  /* split */
  await ev(`document.getElementById('btn-split').click()`);
  await new Promise(r => setTimeout(r, 900));
  console.log('split shown :', await ev(`document.getElementById('vsplit').style.display`));
  await shot('_engine_split.png');

  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
