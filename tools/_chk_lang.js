const http = require('http'), fs = require('fs');
const PORT = 9863;
const OUT = 'E:/QKMansion/CSX10/w/UME/.shots/lang-';
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
             { width: 1280, height: 1000, deviceScaleFactor: 2, mobile: false });
  const ev = async e => {
    const r = await send('Runtime.evaluate', { expression: e, returnByValue: true });
    return r.result.exceptionDetails ? 'EXC' : r.result.result.value;
  };

  for (const mode of ['light', 'dark']) {
    await send('Emulation.setEmulatedMedia',
               { features: [{ name: 'prefers-color-scheme', value: mode }] });
    const w2 = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 8000); });
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 60));
    await send('Page.navigate',
               { url: 'file:///E:/QKMansion/CSX10/w/UME/index.html' });
    await w2;
    await new Promise(r => setTimeout(r, 1500));

    console.log('  === ' + mode + ' ===');
    console.log('  语言种类: ' + await ev(
      "Object.keys((function(){var s={};document.querySelectorAll" +
      "('a.card .lang').forEach(function(e){s[e.textContent]=1});return s})())" +
      ".sort().join(' ')"));
    console.log('  Qt 徽章: ' + await ev(
      "(function(){var e=null;document.querySelectorAll('a.card .lang')" +
      ".forEach(function(x){if(x.textContent==='Qt')e=x});" +
      "if(!e)return '** 仍然没有 **';var cs=getComputedStyle(e);" +
      "return 'class='+e.className+'  bg-image='+(cs.backgroundImage||'none')" +
      ".slice(0,80)+'  color='+cs.color})()"));
    console.log('  Shell 徽章: ' + await ev(
      "(function(){var e=null;document.querySelectorAll('a.card .lang')" +
      ".forEach(function(x){if(x.textContent==='Shell')e=x});" +
      "if(!e)return '无';var cs=getComputedStyle(e);" +
      "return '背景='+cs.backgroundColor+' 字='+cs.color+" +
      "' 边框='+cs.borderTopColor})()"));

    await ev("(function(){var a=null;document.querySelectorAll('a.card')" +
             ".forEach(function(x){if(/r03/.test(x.getAttribute('href')))a=x});" +
             "if(a)a.scrollIntoView({block:'center'})})()");
    await new Promise(r => setTimeout(r, 700));
    const r2 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(OUT + mode + '.png', Buffer.from(r2.result.data, 'base64'));
  }
  console.log('  JS 异常: ' + (errs.length ? '有' : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
