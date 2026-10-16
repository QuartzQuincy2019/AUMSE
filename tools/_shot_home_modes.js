const http = require('http'), fs = require('fs');
const PORT = 9873;
const OUT = 'E:/QKMansion/CSX10/w/UME/.shots/';
const get = p => new Promise((res, rej) => {
  http.get({host: '127.0.0.1', port: PORT, path: p}, r => {
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
    const i = ++id; pend.set(i, r); ws.send(JSON.stringify({id: i, method: me, params: p}));
  });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', {cacheDisabled: true});
  await send('Emulation.setDeviceMetricsOverride',
             {width: 1280, height: 900, deviceScaleFactor: 2, mobile: false});
  const ev = async e => {
    const r = await send('Runtime.evaluate', {expression: e, returnByValue: true});
    return r.result.exceptionDetails ? 'EXC' : r.result.result.value;
  };
  const jobs = [];

  for (const mode of ['light', 'dark']) {
    await send('Emulation.setEmulatedMedia',
               {features: [{name: 'prefers-color-scheme', value: mode}]});
    const w = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 8000); });
    await send('Page.navigate', {url: 'about:blank'});
    await new Promise(r => setTimeout(r, 60));
    await send('Page.navigate',
      {url: 'file:///E:/QKMansion/CSX10/w/UME/index.html'});
    await w;
    await new Promise(r => setTimeout(r, 1500));

    console.log('  === ' + mode + ' ===');
    console.log('   ' + await ev(`(function(){
      var as=[].slice.call(document.querySelectorAll('a.card'));
      var a=as.filter(function(x){return /q07/.test(x.getAttribute('href'))})[0];
      var cs=getComputedStyle(a);
      var m=cs.backgroundImage.match(/linear-gradient\\([^)]*\\)[^,]*/);
      return 'background-size=' + cs.backgroundSize
        + '\\n        遮罩渐变=' + (m ? m[0].slice(0,120) : '?');
    })()`));

    for (const hover of [false, true]) {
      await ev(`(function(){
        var as=[].slice.call(document.querySelectorAll('a.card'));
        var a=as.filter(function(x){return /q07/.test(x.getAttribute('href'))})[0];
        a.scrollIntoView({block:'center'});})()`);
      await new Promise(r => setTimeout(r, 500));
      const b = JSON.parse(await ev(`(function(){
        var as=[].slice.call(document.querySelectorAll('a.card'));
        var a=as.filter(function(x){return /q07/.test(x.getAttribute('href'))})[0];
        var r=a.getBoundingClientRect();
        return JSON.stringify({x:Math.round(r.left),y:Math.round(r.top),
                               w:Math.round(r.width),h:Math.round(r.height),
                               mx:Math.round(r.left+r.width/2),
                               my:Math.round(r.top+r.height/2)});})()`));
      // 真实鼠标移动 —— :hover 只能这样触发
      await send('Input.dispatchMouseEvent',
                 {type: 'mouseMoved', x: hover ? b.mx : 4, y: hover ? b.my : 4});
      await new Promise(r => setTimeout(r, 800));
      const r2 = await send('Page.captureScreenshot', {format: 'png'});
      const tag = mode + (hover ? '-hover' : '');
      fs.writeFileSync(OUT + 'raw-' + tag + '.png',
                       Buffer.from(r2.result.data, 'base64'));
      jobs.push({tag: tag, box: b});
      console.log('   已截 ' + tag);
    }
  }
  fs.writeFileSync(OUT + 'jobs.json', JSON.stringify(jobs));
  console.log('  JS 异常: ' + (errs.length ? '有' : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
