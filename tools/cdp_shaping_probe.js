/* Measure whether UME.html's feature toggle changes Mongolian shaping, over CDP.
 *
 * Canvas is NOT usable: Chromium never implemented ctx.fontFeatureSettings.
 * So we drive the real DOM/CSS path, force the state explicitly (rather than
 * relying on class toggling), and crop to the text column before comparing.

 * Requires msedge/chrome listening on --remote-debugging-port.
 *
 * argv: <port> <file-url> <outdir>
 */
const fs = require('fs');
const http = require('http');

const PORT = Number(process.argv[2] || 9222);
const FILE_URL = process.argv[3];
const OUTDIR = process.argv[4];
const VIEW_W = 1500, VIEW_H = 950;

const get = (path) => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const targets = await get('/json/list');
  const page = targets.find(t => t.type === 'page');
  if (!page) throw new Error('no page target');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const pending = new Map();
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  const send = (method, params = {}) => new Promise(res => {
    const i = ++id; pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  await new Promise(r => ws.onopen = r);

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: VIEW_W, height: VIEW_H, deviceScaleFactor: 2, mobile: false
  });
  await send('Page.navigate', { url: FILE_URL });
  await new Promise(r => setTimeout(r, 4000));

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result && r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
    return r.result.result.value;
  };

  const fontOk = await ev(`document.fonts.check('40px "UME Mongolian"')`);
  const vw = await ev(`(()=>{const r=document.getElementById('vtext').getBoundingClientRect();
      return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)});})()`);
  console.log('font loaded :', fontOk);
  console.log('vtext rect  :', vw);

  const box = JSON.parse(vw);

  /* Force the two states explicitly and read back what the browser resolved. */
  const setFeat = async (on) => {
    await ev(`(()=>{const t=document.getElementById('vtext');
        t.classList.toggle('no-feat', ${on ? 'false' : 'true'});
        return 'ok';})()`);
    await new Promise(r => setTimeout(r, 500));
    return ev(`(()=>{const t=document.getElementById('vtext');
        const cs=getComputedStyle(t);
        return JSON.stringify({cls:t.className, ffs:cs.fontFeatureSettings,
          wm:cs.writingMode, fam:cs.fontFamily});})()`);
  };

  const infoOn = JSON.parse(await setFeat(true));
  const shotOn = await send('Page.captureScreenshot', { format: 'png' });
  if (!shotOn.result || !shotOn.result.data) throw new Error('screenshot failed: ' + JSON.stringify(shotOn).slice(0, 300));
  fs.writeFileSync(OUTDIR + '\\_feat_on.png', Buffer.from(shotOn.result.data, 'base64'));

  const infoOff = JSON.parse(await setFeat(false));
  const shotOff = await send('Page.captureScreenshot', { format: 'png' });
  if (!shotOff.result || !shotOff.result.data) throw new Error('screenshot failed: ' + JSON.stringify(shotOff).slice(0, 300));
  fs.writeFileSync(OUTDIR + '\\_feat_off.png', Buffer.from(shotOff.result.data, 'base64'));

  await setFeat(true);

  console.log('ON  resolved:', JSON.stringify(infoOn));
  console.log('OFF resolved:', JSON.stringify(infoOff));
  console.log('crop box    :', JSON.stringify(box));
  ws.close();
})().catch(e => { console.error('ERROR: ' + e.message); process.exit(1); });
