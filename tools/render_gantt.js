/* =====================================================================
   render_gantt.js —— 把 tools/_gantt/*.mmd 离线渲染成两套静态 SVG
   ---------------------------------------------------------------------
   为什么预渲染
       本站是纯静态、可离线打开的页面。之前 M10 的类图已经定过规矩：
       **写文档时**用 mermaid 渲染一次，存成 SVG，页面只 <img> 引用 ——
       运行时不加载 3.4 MB 的 mermaid，也不要求浏览器开 JS。

   产物
       SharingGroup/tutorials/assets/q11-<名字>-light.svg
       SharingGroup/tutorials/assets/q11-<名字>-dark.svg

   用法（需要本机 mermaid 与 Edge）
       node tools/render_gantt.js [调试端口]
       默认 9789；会自己拉起 headless Edge，渲染完自动关掉。

   依赖
       mermaid 11.17.2（写文档时的依赖，不是页面的依赖）
       Edge（headless）
   ===================================================================== */
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = 'E:/QKMansion/CSX10/w/UME';
const SRC = path.join(ROOT, 'tools/_gantt');
const OUT = path.join(ROOT, 'SharingGroup/tutorials/assets');
/* mermaid 随项目携带，见 tools/vendor/mermaid/（含 LICENSE 与版本说明）。
   以前这里指向本机全局安装的路径，换台机器就跑不了。 */
const MERMAID = path.join(ROOT, 'tools/vendor/mermaid/mermaid.min.js');
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = Number(process.argv[2] || 9789);

function readSource(file) {
  return fs.readFileSync(path.join(SRC, file), 'utf8')
    .split('\n').filter(l => !/^\s*%%/.test(l)).join('\n').trim();
}

function buildPage(src, dark) {
  const esc = src.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{margin:0;padding:18px;background:${dark ? '#15171c' : '#ffffff'}}</style>
</head><body><pre class="mermaid">${esc}</pre>
<script src="file:///${MERMAID}"></script>
<script>
  mermaid.initialize({
    startOnLoad: false,
    theme: ${dark ? "'dark'" : "'default'"},
    securityLevel: 'loose',
    themeVariables: ${dark ? `{
      fontFamily: 'Segoe UI, system-ui, sans-serif',
      fontSize: '12px',
      background: '#15171c',
      primaryColor: '#2e8f72',
      primaryTextColor: '#ffffff',
      primaryBorderColor: '#3aa887',
      secondaryColor: '#2a2f38',
      tertiaryColor: '#1b1f26',
      gridColor: '#3a4150',
      taskBkgColor: '#2e8f72',
      taskBorderColor: '#3aa887',
      taskTextColor: '#ffffff',
      taskTextDarkColor: '#ffffff',
      taskTextOutsideColor: '#e6ecf4',
      activeTaskBkgColor: '#3aa887',
      activeTaskBorderColor: '#4fc098',
      doneTaskBkgColor: '#2a2f38',
      doneTaskBorderColor: '#3a4150',
      critBkgColor: '#c2603f',
      critBorderColor: '#d97a58',
      sectionBkgColor: '#1b1f26',
      altSectionBkgColor: '#20242c',
      sectionBkgColor2: '#1b1f26'
    }` : `{
      fontFamily: 'Segoe UI, system-ui, sans-serif',
      fontSize: '12px',
      background: '#ffffff',
      primaryColor: '#0c8261',
      primaryTextColor: '#ffffff',
      primaryBorderColor: '#0a6b50',
      gridColor: '#e2e8f0',
      taskBkgColor: '#0c8261',
      taskBorderColor: '#0a6b50',
      taskTextColor: '#ffffff',
      taskTextDarkColor: '#ffffff',
      taskTextOutsideColor: '#33404f',
      activeTaskBkgColor: '#0c8261',
      activeTaskBorderColor: '#0a6b50',
      doneTaskBkgColor: '#eef2f7',
      doneTaskBorderColor: '#d6dee8',
      critBkgColor: '#c2603f',
      critBorderColor: '#a94f31',
      sectionBkgColor: '#f1f5f9',
      altSectionBkgColor: '#f7fafc',
      sectionBkgColor2: '#f1f5f9'
    }`}
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
  const files = fs.readdirSync(SRC).filter(f => f.endsWith('.mmd')).sort();
  if (!files.length) throw new Error('tools/_gantt 里没有 .mmd');
  console.log('  待渲染 %d 张：%s', files.length, files.join(', '));

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gantt-'));
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
    if (!list) throw new Error('Edge 没起来');

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
      if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 220));
      return r.result.result.value;
    };

    for (const f of files) {
      const base = 'q11-' + f.replace(/\.mmd$/, '');
      const src = readSource(f);
      for (const dark of [false, true]) {
        const page = path.join(tmpDir, base + (dark ? '-d' : '-l') + '.html');
        fs.writeFileSync(page, buildPage(src, dark), 'utf8');
        const loaded = new Promise(r => { onLoad = r; setTimeout(() => { if (onLoad) onLoad = null; }, 15000); });
        await send('Page.navigate', { url: 'about:blank' });
        await new Promise(r => setTimeout(r, 60));
        await send('Page.navigate', { url: 'file:///' + page.replace(/\\/g, '/') });
        await loaded;
        await new Promise(r => setTimeout(r, 1600));

        const info = JSON.parse(await ev(`(function(){
          var s = document.querySelector('.mermaid svg');
          if (!s) return JSON.stringify({ok:false, txt: document.querySelector('.mermaid').textContent.slice(0,120)});
          var r = s.getBoundingClientRect();
          return JSON.stringify({ok:true, w:Math.round(r.width), h:Math.round(r.height)});
        })()`));
        if (!info.ok) {
          console.log('  !! %s %s 没渲染出来：%s', base, dark ? 'dark' : 'light', info.txt);
          continue;
        }

        let svg = await ev("document.querySelector('.mermaid svg').outerHTML");

        /* mermaid 的甘特图会给 active 任务加上
           .activeTextN{fill:#ffffff!important} —— 当标签放不进条里、被挪到
           条外时，那行白字就落在浅色卡片上，等于隐形（实测就这样）。
           这里补一条优先级更高的规则，把「条外文字」单独定成深色。
           条内文字仍是白色（压在深色条上，对比度够）。 */
        const outsideColor = dark ? '#cbd5e1' : '#33404f';
        const fixCss = '<style>.taskTextOutsideLeft,.taskTextOutsideRight{fill:'
          + outsideColor + '!important}</style>';
        /* 用函数式替换：替换串里不出现 $，免得被外层脚本（PowerShell）先吃掉；
           并且一定要把命中的开标签原样拼回去，否则 <svg> 会整段丢失、SVG 变成废文件。 */
        svg = svg.replace(/<svg\b[^>]*>/, function (m) { return m + fixCss; });
        if (svg.indexOf('xmlns=') < 0) svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
        const vb = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
        if (vb) svg = svg.replace(/(<svg[^>]*?)\swidth="100%"/, `$1 width="${vb[1]}" height="${vb[2]}"`);
        const dst = path.join(OUT, base + (dark ? '-dark' : '-light') + '.svg');
        fs.writeFileSync(dst, '<?xml version="1.0" encoding="UTF-8"?>\n' + svg + '\n', 'utf8');
        console.log('  ✓ %s  %dx%d  %d KB',
          path.basename(dst), info.w, info.h, Math.round(fs.statSync(dst).size / 1024));
      }
    }
    ws.close();
  } finally {
    edge.kill();
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch (e) {}
  }
  console.log('  完成。');
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
