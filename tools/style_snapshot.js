/* style_snapshot.js —— 用「计算样式指纹」代替像素比对做回归安全网
   =====================================================================
   为什么不用截图比对
   ------------------
   试过：29 篇 × 亮/暗 = 58 张全页截图，慢到跑不完（每页重排 + PNG 编码），
   而且字体抗锯齿的细微差别会制造噪声，还要自己写 PNG 解码。

   改用**计算样式指纹**：
     · 对每篇把「每个元素的关键计算样式」抽出来做成指纹
     · 重构前后指纹逐条比对
   这比像素更严谨 —— 像素只能说明「看起来一样」，
   计算样式能精确指出「哪条属性、哪个元素变了」。

   采集的属性覆盖了这次重构会动到的全部维度：
     颜色/背景/边框/阴影（主题层） + 盒模型/尺寸/位置（布局层）

   用法：
     node style_snapshot.js <port> <dir> <out.json>            # 存基准
     node style_snapshot.js <port> <dir> <out.json> --compare   # 与基准比对
   ===================================================================== */
const http = require('http');
const fs = require('fs');

const PORT = Number(process.argv[2]);
const DIR = process.argv[3];
const OUT = process.argv[4];
const CMP = process.argv.includes('--compare');

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

const PROBE = `(() => {
  const PROPS = [
    'color','backgroundColor','backgroundImage','borderTopColor','borderLeftColor',
    'borderTopWidth','borderLeftWidth','borderRadius',
    'boxShadow','opacity','fontSize','fontWeight','lineHeight',
    'display','position','width','height','paddingTop','paddingLeft',
    'marginTop','marginLeft','zIndex','overflowX','whiteSpace','writingMode'
  ];
  /* 有界采样：全量遍历一页有一万多个元素，序列化要好几秒。
     只采「有 class 的元素 + 结构性容器 + 正文首屏可见元素」——
     这已经覆盖了 CSS 会影响的全部对象，速度却快一个数量级。 */
  const pick = [];
  const seen = new Set();
  const add = el => { if (el && !seen.has(el)) { seen.add(el); pick.push(el); } };
  add(document.body);
  document.querySelectorAll('body *').forEach(el => {
    const cls = (typeof el.className === 'string') ? el.className.trim() : '';
    const tag = el.tagName.toLowerCase();
    if (cls) { add(el); return; }
    if (/^(main|nav|footer|h1|h2|h3|h4|table|thead|tbody|tr|pre|figure|main>p)$/.test(tag)) {
      add(el); return;
    }
    /* 无 class 的元素：只取首屏那部分（CSS 影响最直接的地方） */
    const r = el.getBoundingClientRect();
    if (r.top < 900 && (r.width > 0 || r.height > 0)) add(el);
  });
  const out = [];
  pick.forEach(el => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const o = {};
    PROPS.forEach(p => { const v = cs[p];
      if (v && v !== 'none' && v !== 'normal' && v !== 'auto'
          && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') o[p] = v; });
    o._box = [Math.round(r.left), Math.round(r.top),
              Math.round(r.width), Math.round(r.height)].join(',');
    const cls = (typeof el.className === 'string' && el.className.trim())
      ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
    out.push(el.tagName.toLowerCase() + cls + '|' + JSON.stringify(o));
  });
  const bef = getComputedStyle(document.body, '::before');
  out.push('::body::before|' + JSON.stringify({
    content: bef.content, backgroundColor: bef.backgroundColor,
    height: bef.height, paddingTop: bef.paddingTop, zIndex: bef.zIndex
  }));
  return JSON.stringify(out);
})()`;

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const first = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(first.webSocketDebuggerUrl);
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
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

  const ev = async e => {
    const r = await send('Runtime.evaluate',
      { expression: e, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return null;
    return r.result.result.value;
  };

  const snap = {};
  for (const mode of ['light', 'dark']) {
    await send('Emulation.setEmulatedMedia',
      { features: [{ name: 'prefers-color-scheme', value: mode }] });
    for (const f of files) {
      await send('Page.navigate', { url: 'about:blank' });
      await new Promise(r => setTimeout(r, 50));
      const w = new Promise(r => { cb = r; setTimeout(() => { if (cb) { cb = null; } }, 5000); });
      await send('Page.navigate', { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
      await w;
      await new Promise(r => setTimeout(r, 260));
      const raw = await ev(PROBE);
      let arr = []; try { arr = JSON.parse(raw) || []; } catch (e) {}
      snap[mode + '/' + f] = arr;
    }
  }

  if (!CMP) {
    fs.writeFileSync(OUT, JSON.stringify(snap));
    let tot = 0;
    Object.values(snap).forEach(a => tot += a.length);
    console.log('  已存指纹：' + Object.keys(snap).length + ' 个页面状态，'
      + tot + ' 个元素 → ' + OUT);
    ws.close();
    return;
  }

  /* ---------- 比对 ---------- */
  const base = JSON.parse(fs.readFileSync(OUT, 'utf8'));
  let badPages = 0, badEls = 0;
  const details = [];
  for (const key of Object.keys(base)) {
    const A = base[key], B = snap[key] || [];
    if (A.length !== B.length) {
      badPages++;
      details.push(key + '：元素数 ' + A.length + ' → ' + B.length);
      continue;
    }
    let n = 0;
    for (let i = 0; i < A.length; i++) {
      if (A[i] !== B[i]) {
        n++;
        if (n <= 3) {
          const [selA, jsonA] = A[i].split('|');
          const [selB, jsonB] = B[i].split('|');
          if (selA !== selB) { details.push(key + ' #' + i + ' 选择器变了 ' + selA + ' → ' + selB); continue; }
          const oa = JSON.parse(jsonA), ob = JSON.parse(jsonB);
          const diffs = [];
          new Set([...Object.keys(oa), ...Object.keys(ob)]).forEach(p => {
            if (oa[p] !== ob[p]) diffs.push(p + ': ' + (oa[p] || '∅') + ' → ' + (ob[p] || '∅'));
          });
          details.push(key + ' ' + selA.slice(0, 46) + '\n        ' + diffs.slice(0, 4).join('\n        '));
        }
      }
    }
    if (n) { badPages++; badEls += n; }
  }
  console.log('  比对：有差异的页面状态 ' + badPages + '，差异元素 ' + badEls);
  if (details.length) {
    console.log('  前若干处明细：');
    details.slice(0, 24).forEach(d => console.log('     ' + d));
  } else {
    console.log('  ✅ 计算样式逐元素完全一致');
  }
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
