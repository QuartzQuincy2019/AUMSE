/* Objective check: does the DEFAULT (no explicit font-feature-settings) render
   produce joined Mongolian, matching HarfBuzz ground truth?

   HarfBuzz (script=mong, default features) for "mongol" gives:
     u182E.M.init  u1823.O.medi  u1829.AG.medi  u182D_u1823.GO.medi  u182F.L.fina
   i.e. 5 glyphs from 6 codepoints -- a LIGATURE is formed (u182D_u1823).
   The buggy explicit-feature version produced 6 isolated glyphs and no ligature.

   Measure: advance width of the whole run, and whether it differs from the
   all-isolated rendition. A ligature means the run is NARROWER. */
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
  await send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 4500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };

  console.log('resolved ffs :', await ev(
    `getComputedStyle(document.getElementById('vtext')).fontFeatureSettings`));
  console.log('font loaded  :', await ev(`document.fonts.check('40px "UME Mongolian"')`));

  /* 用 Range 量出「整词」的排版长度：连字成立则比逐字母相加更短 */
  const measure = async (label, text) => {
    const w = await ev(`(()=>{
      const d=document.createElement('div');
      d.style.cssText="position:absolute;left:-9999px;top:0;white-space:pre;"
        +"font-family:'UME Mongolian',serif;font-size:100px;line-height:1;"
        +"writing-mode:horizontal-tb";
      d.textContent=${JSON.stringify(text)};
      document.body.appendChild(d);
      const r=document.createRange(); r.selectNodeContents(d);
      const n=r.getBoundingClientRect().width;
      d.remove(); return n;})()`);
    console.log(label.padEnd(22), w.toFixed(2));
    return w;
  };

  const MON = '\u182E\u1823\u1829\u182D\u1823\u182F';
  console.log('');
  const joined = await measure('整词 (mongol)', MON);
  const isolated = await measure('逐字母加空格', [...MON].join(' '));

  /* HarfBuzz 预计：整词 = 492+573+614+838+383 = 2900 units /1000 em → 2.9em */
  const em = await measure('1em 基准 (单个 MA)', '\u182E');
  console.log('');
  console.log('整词宽度 / 100px字号 =', (joined / 100).toFixed(4), 'em');
  console.log('HarfBuzz 预计（带连字）= 2.9000 em');
  console.log('HarfBuzz 预计（无连字，逐形位相加）= '
    + ((492 + 573 + 614 + 838 + 383) / 1000).toFixed(4) + ' em ※见下');

  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
