/* Verify web/ttf-basics.html renders: data loaded, all sections populated, no exceptions. */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9555);
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
  await send('Emulation.setDeviceMetricsOverride', { width: 1300, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/ttf-basics.html' });
  await new Promise(r => setTimeout(r, 3500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC';
    return r.result.result.value;
  };

  const checks = [
    ['data loaded',      `!!(window.UME_TTF_BASICS && window.UME_TTF_BASICS.tables)`],
    ['#tables rows',     `document.querySelectorAll('#tables tbody tr').length`],
    ['#posTable rows',   `document.querySelectorAll('#posTable tbody tr').length`],
    ['#lookupTypes rows',`document.querySelectorAll('#lookupTypes tbody tr').length`],
    ['#lookupDist bars', `document.querySelectorAll('#lookupDist div[style*=flex]').length`],
    ['#featureTable rows',`document.querySelectorAll('#featureTable tbody tr').length`],
    ['#rcltStat cards',  `document.querySelectorAll('#rcltStat .card').length`],
    ['#rcltRules blocks',`document.querySelectorAll('#rcltRules .spec').length`],
    ['#rcltWalk chain',  `document.querySelectorAll('#rcltWalk .node').length`],
    ['#lbDist rows',     `document.querySelectorAll('#lbDist tbody tr').length`],
    ['#lbMongPunct rows',`document.querySelectorAll('#lbMongPunct tbody tr').length`],
    ['#lbContrast rows', `document.querySelectorAll('#lbContrast tbody tr').length`],
    ['font loaded',      `document.fonts.check('40px "UME Mongolian"')`],
    ['doc height',       `document.documentElement.scrollHeight`],
  ];
  for (const [label, expr] of checks) console.log('  ' + label.padEnd(22), await ev(expr));
  console.log('  exceptions'.padEnd(24), errs.length ? errs.join(' | ') : 'none');

  /* capture a few sections */
  const H = await ev('document.documentElement.scrollHeight');
  const n = Math.min(12, Math.ceil(H / 1000));
  for (let i = 0; i < n; i++) {
    await ev(`window.scrollTo(0, ${i * 1000}); 1`);
    await new Promise(r => setTimeout(r, 300));
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${OUTDIR}\\_basics${String(i).padStart(2, '0')}.png`, Buffer.from(r.result.data, 'base64'));
  }
  console.log('  captured', n, 'sections of', H, 'px');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
