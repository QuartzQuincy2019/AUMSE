/* =====================================================================
   render_mermaid.js —— 把 tools/_m10_diagram.mmd 离线渲染成两套静态 SVG
   ---------------------------------------------------------------------
   为什么要这么做
       M10 的继承树用 mermaid 画。但本站是纯静态、可离线打开的页面，
       不适合在运行时加载 3.4 MB 的 mermaid.min.js、也不希望「没 JS 就没图」。
       所以**只在写文档时**用 mermaid 渲染一次，把结果存成 SVG，
       页面里用 <img> 引用 —— 运行时零依赖。

   产物
       SharingGroup/tutorials/assets/img/m10-class-light.svg   （mermaid default 主题）
       SharingGroup/tutorials/assets/img/m10-class-dark.svg    （mermaid dark 主题）

   用法（需要本机装了 mermaid 与 Edge）
       node tools/render_mermaid.js [调试端口]
       默认端口 9790；会自己拉起 headless Edge，渲染完自动关掉。

   依赖
       mermaid：tools/vendor/mermaid/（11.17.2，随项目携带，含 LICENSE）
                **写文档时**的依赖，不是页面的依赖
       Edge   ：C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe

   注意
       mermaid 的 classDiagram 标签走 <foreignObject>，所以 SVG 不能被
       XML 之外的方式加工，也**不能**当 <img> 之外的用途随意内联 ——
       实测当 <img> 引用在 Chromium 里能正常渲染。
   ===================================================================== */
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = 'E:/QKMansion/CSX10/w/UME';
const MMD = path.join(ROOT, 'tools/_m10_diagram.mmd');
const OUT = path.join(ROOT, 'SharingGroup/tutorials/assets');
/* mermaid 随项目携带，见 tools/vendor/mermaid/（含 LICENSE 与版本说明）。
   以前这里指向本机全局安装的路径，换台机器就跑不了。 */
const MERMAID = path.join(ROOT, 'tools/vendor/mermaid/mermaid.min.js');
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = Number(process.argv[2] || 9790);

/* mermaid 源文本里 %% 是注释，去掉后直接塞进 <pre class="mermaid"> */
function readSource() {
  const raw = fs.readFileSync(MMD, 'utf8');
  return raw.split('\n').filter(l => !/^\s*%%/.test(l)).join('\n').trim();
}

function buildPage(src) {
  const esc = src.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{margin:0;padding:20px;background:#fff}.mermaid{text-align:center}</style>
</head><body><pre class="mermaid">${esc}</pre>
<script src="file:///${MERMAID}"></script>
<script>
  var dark = location.search.indexOf('dark') >= 0;
  mermaid.initialize({
    startOnLoad: false,
    theme: dark ? 'dark' : 'default',
    themeVariables: { fontFamily: 'Segoe UI, system-ui, sans-serif', fontSize: '14px' },
    securityLevel: 'loose'
  });
  mermaid.run();
</script></body></html>`;
}

const get = (p) => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const src = readSource();
  console.log('  源文本 ' + MMD);
  console.log('  mermaid classDiagram，' + src.split('\n').length + ' 行');

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mmd-'));
  const page = path.join(tmpDir, 'render.html');
  fs.writeFileSync(page, buildPage(src), 'utf8');
  const pageUrl = 'file:///' + page.replace(/\\/g, '/');

  const profile = path.join(tmpDir, 'profile');
  const edge = spawn(EDGE, [
    '--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
    '--allow-file-access-from-files', '--user-data-dir=' + profile,
    '--remote-debugging-port=' + PORT, '--window-size=1100,900', 'about:blank'
  ], { stdio: 'ignore' });

  try {
    let list = null;
    for (let i = 0; i < 40; i++) {
      try { list = await get('/json/list'); break; } catch (e) { await new Promise(r => setTimeout(r, 400)); }
    }
    if (!list) throw new Error('Edge 没起来（端口 ' + PORT + '）');

    const target = list.filter(x => x.type === 'page')[0];
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    let id = 0; const pend = new Map(); let onLoad = null;
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.method === 'Page.loadEventFired' && onLoad) { const f = onLoad; onLoad = null; f(); }
      if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    };
    const send = (me, p = {}) => new Promise(r => {
      const i = ++id; pend.set(i, r);
      ws.send(JSON.stringify({ id: i, method: me, params: p }));
    });
    await new Promise(r => ws.onopen = r);
    await send('Page.enable');
    await send('Runtime.enable');

    const ev = async expr => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
      if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 200));
      return r.result.result.value;
    };

    for (const [theme, name] of [['light', 'm10-class-light.svg'], ['dark', 'm10-class-dark.svg']]) {
      const loaded = new Promise(r => { onLoad = r; setTimeout(() => { if (onLoad) onLoad = null; }, 15000); });
      await send('Page.navigate', { url: 'about:blank' });
      await new Promise(r => setTimeout(r, 60));
      await send('Page.navigate', { url: pageUrl + '?theme=' + theme });
      await loaded;
      await new Promise(r => setTimeout(r, 2000));

      const info = JSON.parse(await ev(`(function(){
        var s = document.querySelector('.mermaid svg');
        if (!s) return JSON.stringify({ok:false});
        var r = s.getBoundingClientRect();
        return JSON.stringify({ok:true, w:Math.round(r.width), h:Math.round(r.height),
          nodes:s.querySelectorAll('g.node').length});
      })()`));
      if (!info.ok) throw new Error(theme + ' 没渲染出 SVG');

      let svg = await ev("document.querySelector('.mermaid svg').outerHTML");
      if (svg.indexOf('xmlns=') < 0) svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');

      /* 把 width="100%" 换成真实宽度：否则 <img> 的 naturalWidth 会按
         300x150 推算，尺寸信息不真（画面比例仍对）。 */
      const vb = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
      if (vb) svg = svg.replace(/(<svg[^>]*?)\swidth="100%"/, `$1 width="${vb[1]}" height="${vb[2]}"`);

      const dst = path.join(OUT, name);
      fs.writeFileSync(dst, '<?xml version="1.0" encoding="UTF-8"?>\n' + svg + '\n', 'utf8');
      console.log('  ✓ ' + name.padEnd(22) + ' ' + Math.round(info.w) + 'x'
        + Math.round(info.h) + '  节点 ' + info.nodes
        + '  ' + Math.round(fs.statSync(dst).size / 1024) + ' KB');
    }
    ws.close();
  } finally {
    edge.kill();
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch (e) {}
  }
  console.log('  完成。页面用 <img> 引用这两个文件即可。');
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
