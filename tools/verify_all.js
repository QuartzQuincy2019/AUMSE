/* =====================================================================
   verify_all.js —— 一次遍历查完所有项目
   ---------------------------------------------------------------------
   为什么合并：原来每种检查各自起一遍浏览器、各自把 26 篇走一遍，
   一遍就是 26 次页面加载（每次等 1.7 秒）≈ 45 秒，跑四种检查就三分钟。
   这里把「系列属性 / 顶部条 / 文末跳转 / 目录 / 返回 home / 结构 /
   控制台异常」合并成**一次遍历**，每篇只加载一次。

   加速手段：
     · 等 Page.loadEventFired 而不是死等固定毫秒
     · 同一张标签页复用，不反复新建
     · 结果只在末尾汇总，不逐条打印
   ===================================================================== */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.argv[2]);
const DIR = process.argv[3];
const OUT_JSON = process.argv[4] || '';

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html')).sort();
  const first = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(first.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  let errs = [];
  let loaded = null;

  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description
                || m.params.exceptionDetails.text);
    if (m.method === 'Page.loadEventFired' && loaded) { loaded(); loaded = null; }
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
    { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });

  const ev = async expr => {
    const r = await send('Runtime.evaluate',
      { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails)
      return { __err: JSON.stringify(r.result.exceptionDetails).slice(0, 200) };
    return r.result.result.value;
  };

  /* 一篇里要查的全部东西，打包成一次 evaluate */
  const PROBE = `(() => {
    const b = document.body;
    const bef = getComputedStyle(b, '::before');
    const nav = document.querySelector('.s-nav');
    const fab = document.querySelector('.home-fab');
    const sw  = document.querySelector('.s-nav-switch');
    const se  = document.querySelector('.series-nav');
    const tocLinks = [...document.querySelectorAll('#toc a[href^="#"]')];
    const missAnchor = tocLinks.filter(a => !document.querySelector(a.getAttribute('href')))
                              .map(a => a.getAttribute('href'));
    const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
    const dupId = ids.filter((x, i) => ids.indexOf(x) !== i);
    // 横向溢出：逐元素找比父级宽的
    const over = [];
    document.querySelectorAll('main *').forEach(e => {
      const r = e.getBoundingClientRect(), p = e.parentElement;
      if (!p || r.width < 2) return;
      const pr = p.getBoundingClientRect();
      if (r.right > pr.right + 4 && over.length < 3)
        over.push(e.tagName.toLowerCase()
          + (e.className ? '.' + String(e.className).split(' ')[0] : '')
          + ' ' + Math.round(r.right - pr.right) + 'px');
    });
    return JSON.stringify({
      sk: b.getAttribute('data-series'),
      cls: b.className,
      banner: (bef.content || '').replace(/^"|"$/g, ''),
      bg: getComputedStyle(b).backgroundColor,
      navLinks: nav ? nav.querySelectorAll('.s-nav-grid a').length : 0,
      navToc: nav ? nav.querySelectorAll('.s-nav-toc li').length : 0,
      navCur: nav ? nav.querySelectorAll('a[aria-current]').length : 0,
      swLinks: sw ? sw.querySelectorAll('a').length : 0,
      seLinks: se ? se.querySelectorAll('a').length : 0,
      fab: fab ? getComputedStyle(fab).position + '/' + getComputedStyle(fab).borderRadius : 'none',
      h1: document.querySelectorAll('h1').length,
      sub: document.querySelectorAll('.sub-title').length,
      main: document.querySelectorAll('main').length,
      toc: tocLinks.length,
      missAnchor: missAnchor,
      dupId: [...new Set(dupId)],
      over: over,
      title: document.title,
      /* 只数**静态**内嵌样式：脚本运行时注入的会带 id（UMCompos 的
         umcompos-style、主题注入等），那是正常行为，不算「样式没分离」。 */
      /* 只数**静态内嵌样式**。以下三种都是运行时正常注入的，排除：
           · 带 id 的（UMCompos 的 umcompos-style、主题注入块）
           · 只装 @font-face 的（UMCompos.loadFont 注入的字体声明） */
      headStyle: [...document.querySelectorAll('head style')]
                   .filter(s => !s.id && !/@font-face/.test(s.textContent)).length,
      dynStyle: [...document.querySelectorAll('head style')]
                   .filter(s => s.id || /@font-face/.test(s.textContent))
                   .map(s => s.id || '@font-face'),
      bodyStyle: document.querySelectorAll('body style').length
    });
  })()`;

  const rows = [];
  const t0 = Date.now();
  for (const f of files) {
    errs = [];
    /* 顺序很要紧：先导航到 about:blank，**再**注册 load 监听。
       反过来写的话，about:blank 的 loadEventFired 会先把这个 resolved
       兑现掉，于是真正的页面还没 load 完就去探测了 ——
       e01 / m04 两篇因此被误报成「跳转缺失」（其实只是还没执行到）。
       这也是「随机两篇出问题」的原因：取决于哪一篇先撞上竞态。 */
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 90));
    const wait = new Promise(r => {
      loaded = r;
      setTimeout(() => { if (loaded) { loaded(); loaded = null; } }, 5000);
    });
    await send('Page.navigate',
      { url: 'file:///' + DIR.replace(/\\/g, '/') + '/' + f });
    await wait;
    /* 再留一点时间给 DOMContentLoaded 之后注入的跳转块 */
    await new Promise(r => setTimeout(r, 320));
    const raw = await ev(PROBE);
    if (raw && raw.__err) { rows.push({ file: f, err: raw.__err }); continue; }
    let o; try { o = JSON.parse(raw); } catch (e) { rows.push({ file: f, err: 'parse' }); continue; }
    o.file = f; o.jsErr = errs.slice(0, 1);
    rows.push(o);
  }
  const dt = ((Date.now() - t0) / 1000).toFixed(1);

  /* ---------------- 汇总 ---------------- */
  const isFE = r => /^fe-/.test(r.file);
  const problems = [];
  rows.forEach(r => {
    if (r.err) { problems.push(r.file + ': 探测失败 ' + r.err); return; }
    if (r.jsErr.length) problems.push(r.file + ': JS 异常 ' + r.jsErr[0].slice(0, 60));
    if (r.h1 > 1) problems.push(r.file + ': h1 重复 ' + r.h1);
    if (r.sub > 1) problems.push(r.file + ': 副标题重复 ' + r.sub);
    if (r.main !== 1) problems.push(r.file + ': main 数 ' + r.main);
    if (r.missAnchor.length) problems.push(r.file + ': 断链 ' + r.missAnchor.join(','));
    if (r.dupId.length) problems.push(r.file + ': 重复 id ' + r.dupId.join(','));
    if (r.over.length) problems.push(r.file + ': 横向溢出 ' + r.over.join(' / '));
    /* head 里不该有内嵌 style（样式都在 assets/ 的独立文件里）。
       body 里的 <style> 是注入块（返回 home / 遮罩规避），属正常。 */
    if (r.headStyle > 0) problems.push(r.file + ': head 内嵌 style ' + r.headStyle);
    if (isFE(r)) return;                       // FE 外观独立，不查系列主题
    if (!r.sk) problems.push(r.file + ': 缺 data-series');
    if (!r.banner) problems.push(r.file + ': 顶部条无文案');
    if (!r.navLinks) problems.push(r.file + ': 文末系列跳转缺失');
    if (r.navCur !== 1) problems.push(r.file + ': 当前篇标记 ' + r.navCur);
    if (!r.swLinks && r.sk !== 'R') problems.push(r.file + ': 其它系列跳转缺失');
    if (r.fab === 'none') problems.push(r.file + ': 返回 home 缺失');
  });

  console.log('文件'.padEnd(34) + '系列  顶部条                          跳转 小节 其它  home');
  console.log('-'.repeat(104));
  rows.forEach(r => {
    if (r.err) { console.log('  !! ' + r.file + '  ' + r.err); return; }
    console.log(('  ' + r.file).padEnd(34)
      + String(r.sk || (isFE(r) ? 'FE' : '?')).padEnd(6)
      + (r.banner || '(无)').padEnd(32)
      + String(r.navLinks).padStart(4)
      + String(r.navToc).padStart(5)
      + String(r.swLinks).padStart(5)
      + '  ' + (r.fab === 'none' ? '!!无' : '有'));
  });
  console.log('');
  console.log('  共 ' + rows.length + ' 篇，耗时 ' + dt + ' 秒（每篇一次加载）');
  if (problems.length) {
    console.log('');
    console.log('  ⚠ 问题 ' + problems.length + ' 条：');
    problems.forEach(p => console.log('     - ' + p));
  } else {
    console.log('  ✅ 全部通过（结构 / 系列主题 / 跳转 / 返回 home / 无溢出 / 无异常）');
  }
  if (OUT_JSON) fs.writeFileSync(OUT_JSON, JSON.stringify(rows, null, 1));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
