/* 验证颜色拾取器：改滑块 → 四个数值联动是否正确 */
const http = require('http');
const PORT = process.argv[2];
const URL = process.argv[3];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 200));
  await send('Page.navigate', { url: URL });
  await new Promise(r => setTimeout(r, 2000));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 200);
    return r.result.result.value;
  };

  console.log(await ev(`(()=>{
    const out = [];
    const P = document.getElementById('picker');
    out.push('拾取器存在: ' + !!P);
    if (!P) return out.join('\\n');
    out.push('滑块数量: ' + P.querySelectorAll('input[type=range]').length);
    out.push('预设色块: ' + P.querySelectorAll('#pkPresets i').length);
    out.push('原生取色器: ' + P.querySelectorAll('input[type=color]').length);
    out.push('复制按钮: ' + P.querySelectorAll('.cp2').length);
    out.push('');

    function set(id, v){
      const e = document.getElementById(id);
      e.value = v; e.dispatchEvent(new Event('input', {bubbles:true}));
    }
    function snap(label){
      out.push('  ' + label.padEnd(20) +
        ' hex=' + document.getElementById('pkHex').textContent.padEnd(9) +
        ' rgb=' + document.getElementById('pkRgb').textContent.padEnd(20) +
        ' ' + document.getElementById('pkHsl').textContent);
    }
    snap('初始');
    set('pkR',255); set('pkG',0); set('pkB',0);
    snap('纯红 255,0,0');
    set('pkR',0); set('pkG',0); set('pkB',0);
    snap('纯黑 0,0,0');
    set('pkR',255); set('pkG',255); set('pkB',255);
    snap('纯白 255,255,255');
    set('pkR',128); set('pkG',128); set('pkB',128);
    snap('灰 128 三通道相同');
    set('pkR',31); set('pkG',111); set('pkB',235);
    snap('回到 1F6FEB');
    out.push('');
    // Alpha
    const A = document.getElementById('pkA');
    A.value = 50; A.dispatchEvent(new Event('input',{bubbles:true}));
    out.push('  A=50% 时 含Alpha 一栏: ' + document.getElementById('pkRgba').textContent);
    out.push('  色块 background: ' + document.getElementById('pkSwatch').style.background);
    A.value = 100; A.dispatchEvent(new Event('input',{bubbles:true}));
    out.push('  A=100% 时 含Alpha 一栏: ' + document.getElementById('pkRgba').textContent);
    out.push('');
    // 点一个预设
    const box = P.querySelectorAll('#pkPresets i');
    box[2].click();
    out.push('  点第 3 个预设(' + box[2].title + ') → hex=' +
      document.getElementById('pkHex').textContent);
    out.push('');
    // 缩放滑块轨道是否上色
    out.push('  轨道渐变色已设: ' + (document.getElementById('pkR').style.getPropertyValue('--tk') ? '是' : '否'));
    return out.join('\\n');
  })()`));

  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
