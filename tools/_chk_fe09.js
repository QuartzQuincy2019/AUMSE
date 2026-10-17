const http = require('http'), fs = require('fs');
const PORT = 9855;
const OUT = 'E:/QKMansion/CSX10/w/UME/.shots/';
const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});
(async () => {
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let cb = null; const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown') errs.push('EXC');
    if (m.method === 'Page.loadEventFired' && cb) { const f = cb; cb = null; f(); }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => {
    const i = ++id; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: me, params: p }));
  });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride',
             { width: 1280, height: 900, deviceScaleFactor: 2, mobile: false });
  const ev = async e => {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true });
    return r.result.exceptionDetails ? 'EXC' : r.result.result.value;
  };

  for (const mode of ['light', 'dark']) {
    await send('Emulation.setEmulatedMedia',
               { features: [{ name: 'prefers-color-scheme', value: mode }] });

    // ① FE-09 教程页
    let w = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 8000); });
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 60));
    await send('Page.navigate',
               { url: 'file:///E:/QKMansion/CSX10/w/UME/SharingGroup/tutorials/fe-09.html' });
    await w;
    await new Promise(r => setTimeout(r, 1200));
    console.log('  === ' + mode + ' · FE-09 ===');
    console.log('  徽章: ' + await ev(
      "(function(){var a=[];document.querySelectorAll('.lang').forEach(function(e){" +
      "a.push(e.textContent+'('+e.className.replace('lang ','')+')')});return a.join('  ')})()"));
    await ev("window.scrollTo(0,0)");
    await new Promise(r => setTimeout(r, 500));
    let r2 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(OUT + 'fe09-badges-' + mode + '.png',
                     Buffer.from(r2.result.data, 'base64'));

    // ② 首页卡片
    w = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 8000); });
    await send('Page.navigate',
               { url: 'file:///E:/QKMansion/CSX10/w/UME/index.html' });
    await w;
    await new Promise(r => setTimeout(r, 1500));
    console.log('  ' + mode + ' 首页 FE-09 卡片徽章: ' + await ev(
      "(function(){var a=null;document.querySelectorAll('a.card').forEach(function(x){" +
      "if(/fe-09/.test(x.getAttribute('href')))a=x});if(!a)return '找不到卡片';" +
      "var s=[];a.querySelectorAll('.lang').forEach(function(e){" +
      "s.push(e.textContent+'('+e.className+')')});return s.join('  ')})()"));
    await ev("(function(){var a=null;document.querySelectorAll('a.card').forEach(function(x){" +
             "if(/fe-09/.test(x.getAttribute('href')))a=x});" +
             "if(a)a.scrollIntoView({block:'center'})})()");
    await new Promise(r => setTimeout(r, 700));
    r2 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(OUT + 'fe09-card-' + mode + '.png',
                     Buffer.from(r2.result.data, 'base64'));
  }
  console.log('  JS 异常: ' + (errs.length ? '有' : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
