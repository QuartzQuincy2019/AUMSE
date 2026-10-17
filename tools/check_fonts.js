/* 把「浏览器实际用了哪个字体」的探针固化成常规检查。

为什么需要
    上一轮 R04 换字体时，「看起来成功了」其实完全没生效：
      · getComputedStyle().fontFamily 回显的是**声明值**，不是真正用的字体
      · document.fonts.check() 也返回 true
    真正的证据只有 CDP 的 CSS.getPlatformFontsForNode —— 它报告的是
    排版引擎实际取用的平台字体。

用法
    node check_fonts.js <端口> <页面 URL> <选择器列表，逗号分隔>
例
    node check_fonts.js 9740 file:///.../r04.html "code .ipa,td.c .ipa"
*/
const http = require('http');

const PORT = parseInt(process.argv[2] || '9222', 10);
const URL = process.argv[3];
const SELS = (process.argv[4] || 'code .ipa').split(',').map(s => s.trim()).filter(Boolean);
const WANT = (process.argv[5] || '').trim();   // 期望的字体名（可选）

if (!URL) {
  console.error('用法：node check_fonts.js <端口> <URL> <选择器，逗号分隔> [期望字体]');
  process.exit(2);
}

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let cb = null;
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Page.loadEventFired' && cb) { const f = cb; cb = null; f(); }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => {
    const i = ++id; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: me, params: p }));
  });

  await new Promise(r => ws.onopen = r);
  await send('Page.enable');
  await send('DOM.enable');
  await send('CSS.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });

  const p = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 12000); });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 60));
  await send('Page.navigate', { url: URL });
  await p;
  await new Promise(r => setTimeout(r, 1500));

  const { result: doc } = await send('DOM.getDocument', { depth: -1 });
  const root = doc.root.nodeId;

  let bad = 0;
  for (const sel of SELS) {
    const q = await send('DOM.querySelector', { nodeId: root, selector: sel });
    if (!q.result || !q.result.nodeId) {
      console.log('  ? ' + sel.padEnd(26) + ' 找不到元素');
      continue;
    }
    const f = await send('CSS.getPlatformFontsForNode', { nodeId: q.result.nodeId });
    const fonts = (f.result && f.result.fonts) || [];
    const list = fonts.map(x => x.familyName + '(' + x.glyphCount + ')').join(', ') || '无';
    const ok = !WANT || fonts.some(x => x.familyName.includes(WANT));
    if (!ok) bad++;
    console.log('  ' + (ok ? 'OK ' : '✗  ') + sel.padEnd(26) + ' → ' + list);
  }

  console.log('');
  if (bad) {
    console.log('  有 ' + bad + ' 个选择器没有用到 ' + WANT + ' ✗');
    process.exit(1);
  }
  console.log('  实际渲染字体检查通过' + (WANT ? '（期望含 ' + WANT + '）' : '') + ' OK');
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
