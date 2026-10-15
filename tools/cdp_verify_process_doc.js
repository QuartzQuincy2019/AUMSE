/* Verify process.html loads and renders correctly over file:// (and reports errors). */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9555);

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

  for (const url of ['file:///E:/QKMansion/CSX10/w/UME/web/process.html',
                     'http://127.0.0.1:8899/web/process.html']) {
    errs.length = 0;
    await send('Page.navigate', { url });
    await new Promise(r => setTimeout(r, 3500));
    const ev = async expr => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
      if (r.result.exceptionDetails) return 'EXC';
      return r.result.result.value;
    };
    console.log('--- ' + url);
    console.log('  data loaded   :', await ev(`!!(window.UME_PROCESS_DATA && window.UME_PROCESS_DATA.words)`));
    console.log('  glyph chips   :', await ev(`document.querySelectorAll('#shape-demo .gl').length`));
    console.log('  liga badges   :', await ev(`document.querySelectorAll('#shape-demo .gl.lig').length`));
    console.log('  position rows :', await ev(`document.querySelectorAll('#shape-demo tbody tr').length`));
    console.log('  warn card     :', await ev(`document.querySelectorAll('#shape-demo .card.warn').length`));
    console.log('  font loaded   :', await ev(`document.fonts.check('40px "UME Mongolian"')`));
    console.log('  toc links     :', await ev(`document.querySelectorAll('#toc a').length`));
    console.log('  svg diagrams  :', await ev(`document.querySelectorAll('.geo svg').length`));
    console.log('  exceptions    :', errs.length ? errs.join(' | ') : 'none');
  }
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
