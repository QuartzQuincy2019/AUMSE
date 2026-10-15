/* End-to-end test of UME.html's SVG export:
   open the editor, trigger export, read back the generated SVG and the
   per-glyph identity/confidence, then verify against known ground truth. */
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
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
      errs.push('console.error: ' + m.params.args.map(a => a.value ?? a.description).join(' '));
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1500, height: 950, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 400));
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/UME.html' });
  await new Promise(r => setTimeout(r, 5000));

  const ev = async (expr, awaitPromise = false) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise });
    if (r.result.exceptionDetails)
      return 'EXC ' + JSON.stringify(r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description);
    return r.result.result.value;
  };

  console.log('font loaded   :', await ev(`document.fonts.check('40px "UME Mongolian"')`));
  console.log('opentype ready:', await ev(`typeof OT !== 'undefined' && !!OT && OT.numGlyphs`));
  console.log('raw value     :', JSON.stringify(await ev(`document.getElementById('raw').value`)));
  console.log('mstat         :', await ev(`document.getElementById('mstat').textContent`));

  /* 打开导出并等待生成完成 */
  await ev(`document.getElementById('btn-export').click()`);
  await new Promise(r => setTimeout(r, 600));
  for (let i = 0; i < 60; i++) {
    const busy = await ev(`busy === true`);
    if (busy === false) break;
    await new Promise(r => setTimeout(r, 500));
  }
  await new Promise(r => setTimeout(r, 600));

  console.log('');
  console.log('export info   :', JSON.stringify(await ev(`document.getElementById('expinfo').textContent`)));
  console.log('export size   :', await ev(`document.getElementById('exSize').textContent`));
  console.log('warn visible  :', await ev(`document.getElementById('exWarn').style.display !== 'none'`));
  console.log('svg in preview:', await ev(`!!document.querySelector('#preview svg')`));
  console.log('path count    :', await ev(`document.querySelectorAll('#preview svg path').length`));

  /* 逐簇的字形身份与置信度（先用 outline 模式，确保 GLYPH_INDEX 已建好） */
  await ev(`(()=>{const s=document.getElementById('exFormat'); s.value='svg-outline';
            s.dispatchEvent(new Event('change')); return 1;})()`);
  await ev(`refreshExport()`);
  for (let i = 0; i < 80; i++) {
    if ((await ev(`busy === true`)) === false) break;
    await new Promise(r => setTimeout(r, 400));
  }
  await new Promise(r => setTimeout(r, 500));

  console.log('');
  console.log('outline info  :', JSON.stringify(await ev(`document.getElementById('expinfo').textContent`)));
  console.log('glyph recovery:');
  console.log(await ev(`(()=>{
    const plan = layoutDoc(document.getElementById('raw').value);
    const out = [];
    for (const ln of plan){
      out.push('  line len = ' + Math.round(ln.length) + '  (clusters ' + ln.items.length + ')');
      const gs = matchLine(ln.items);
      for (const g of gs){
        const it = ln.items[g.cluster];
        const cpH = it ? it.cps.map(c=>'U+'+c.toString(16).toUpperCase().padStart(4,'0')).join('+') : '?';
        let name = '(blank)';
        if (g.gid != null){ try { name = OT.glyphs.get(g.gid).name; } catch(e){ name='gid '+g.gid; } }
        out.push('    ' + cpH.padEnd(14) + ' adv=' + String(Math.round(it?it.adv:0)).padStart(5)
          + ' span=' + (g.span||1)
          + '  -> ' + (g.gid==null?'-':'gid '+g.gid).padEnd(10)
          + name.padEnd(24) + ' IoU ' + (g.score||0).toFixed(3));
      }
    }
    return out.join('\\n');
  })()`));

  /* 取回 SVG 存盘（outline 模式） */
  const svg = await ev(`(typeof lastSVG !== 'undefined' && lastSVG && lastSVG.svg) ? lastSVG.svg : ''`);
  if (svg && svg.length > 100) {
    fs.writeFileSync(OUTDIR + '\\_export-outline.svg', svg);
    console.log('');
    console.log('outline svg   :', svg.length, 'bytes saved');
  } else {
    console.log('NO OUTLINE SVG');
  }

  console.log('exceptions    :', errs.length ? errs.join(' | ') : 'none');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
