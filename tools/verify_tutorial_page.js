/* 验证教程页：结构完整性 + 无 JS 报错 + 截图 */
const fs = require('fs');
const http = require('http');
const PORT = Number(process.argv[2] || 9600);
const FILE = process.argv[3];
const OUTDIR = process.argv[4];
const TAG = process.argv[5] || 'doc';

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
      errs.push('console: ' + m.params.args.map(a => a.value).join(' '));
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 300));
  await send('Page.navigate', { url: FILE });
  await new Promise(r => setTimeout(r, 2500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception||{}).description);
    return r.result.result.value;
  };

  const checks = [
    ['标题',        `document.title`],
    ['h2 小节数',   `document.querySelectorAll('h2').length`],
    ['代码块数',    `document.querySelectorAll('.code-wrap').length`],
    ['输出块数',    `document.querySelectorAll('.out-wrap').length`],
    ['复制按钮数',  `document.querySelectorAll('.cp').length`],
    ['表格数',      `document.querySelectorAll('table').length`],
    ['卡片数',      `document.querySelectorAll('.card').length`],
    ['目录链接数',  `document.querySelectorAll('#toc a').length`],
    ['悬停元素数',  `document.querySelectorAll('.cell,.flow .s,.card,.code-wrap,.out-wrap,.k').length`],
    ['正文高度',    `document.documentElement.scrollHeight`],
    ['代码字体',    `getComputedStyle(document.querySelector('.code-wrap pre')).fontFamily`],
    ['输出字体',    `getComputedStyle(document.querySelector('.out-wrap pre')).fontFamily`],
  ];
  for (const [label, expr] of checks) console.log('  ' + label.padEnd(12), await ev(expr));
  console.log('  ' + 'JS 异常'.padEnd(12), errs.length ? errs.join(' | ') : 'none');

  const H = await ev('document.documentElement.scrollHeight');
  const n = Math.min(14, Math.ceil(H / 1000));
  for (let i = 0; i < n; i++) {
    await ev(`window.scrollTo(0, ${i * 1000}); 1`);
    await new Promise(r => setTimeout(r, 220));
    const r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${OUTDIR}\\_${TAG}_${String(i).padStart(2,'0')}.png`, Buffer.from(r.result.data, 'base64'));
  }
  console.log('  截图', n, '张，文档高', H, 'px');
  ws.close();
})().catch(e => { console.error('ERROR ' + e.message); process.exit(1); });
