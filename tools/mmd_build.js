// 构建期把 mermaid 渲成 SVG（双主题），供静态页面用 <picture> 切换。
//
// 为什么这么做：教程站是纯静态的，不想为了几张图引入 3.5 MB 的运行时；
// 渲染一次存成 SVG，页面只加载几十 KB 的矢量图，缩放也不糊。
//
// 用法：node tools/mmd_build.js <port> tools/mmd/a01.json
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.argv[2] || '9658', 10);
const SPEC = process.argv[3];
// 输出文件前缀，默认 a01；A02 用 a02。
const PREFIX = process.argv[4] || 'a01';
const ROOT = 'E:/QKMansion/CSX10/w/UME';
const OUT = path.join(ROOT, 'SharingGroup/tutorials/assets/img');
const MERMAID = 'file:///C:/Users/lenovo/.dsh/profiles/desktop/node_modules/mermaid/dist/mermaid.min.js';

const spec = JSON.parse(fs.readFileSync(SPEC, 'utf8'));

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

const THEMES = {
  light: {
    startOnLoad: false, securityLevel: 'loose',
    theme: 'base',
    themeVariables: {
      fontFamily: '"华文中宋","STZhongsong",'+
        '"Microsoft YaHei","PingFang SC",sans-serif',
      fontSize: '15px',
      background: '#ffffff',
      primaryColor: '#fffdf6', primaryTextColor: '#1a1509',
      primaryBorderColor: '#c8a03a',
      secondaryColor: '#f7efd8', tertiaryColor: '#f3efe3',
      lineColor: '#8a6410',
      noteBkgColor: '#fdf4e3', noteTextColor: '#5f450a', noteBorderColor: '#c8a03a'
    }
  },
  dark: {
    startOnLoad: false, securityLevel: 'loose',
    theme: 'base',
    themeVariables: {
      fontFamily: '"华文中宋","STZhongsong",'+
        '"Microsoft YaHei","PingFang SC",sans-serif',
      fontSize: '15px',
      background: '#0b0906',
      primaryColor: '#171106', primaryTextColor: '#f0e4c6',
      primaryBorderColor: '#c8a03a',
      secondaryColor: '#1f1708', tertiaryColor: '#231b0c',
      lineColor: '#c8a03a',
      noteBkgColor: '#1f1708', noteTextColor: '#e8c877', noteBorderColor: '#6b5320'
    }
  }
};

(async () => {
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0;
  const pend = new Map();
  let cb = null;
  const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      errs.push(((d.exception && d.exception.description) || d.text || '').slice(0, 200));
    }
    if (m.method === 'Page.loadEventFired' && cb) { const f = cb; cb = null; f(); }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => {
    const i = ++id; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: me, params: p }));
  });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  const ev = async (expr, awaitP = false) => {
    const r = await send('Runtime.evaluate',
      { expression: expr, returnByValue: true, awaitPromise: awaitP });
    if (r.result.exceptionDetails) {
      const d = r.result.exceptionDetails;
      return 'EXC ' + ((d.exception && d.exception.description) || '').slice(0, 300);
    }
    return r.result.result.value;
  };

  // 造一个临时页面：只加载 mermaid，逐个渲染
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff;font-family:"Microsoft YaHei",sans-serif}</style></head>
<body><div id="host"></div>
<script src="${MERMAID}"></script>
<script>
window.__GO__ = async function (themes, items) {
  if (typeof mermaid === "undefined") return { error: "mermaid 没加载" };
  const out = {};
  for (const themeName of Object.keys(themes)) {
    mermaid.initialize(themes[themeName]);
    for (const it of items) {
      const key = it.key + "|" + themeName;
      try {
        const r = await mermaid.render("mmd-" + it.key + "-" + themeName, it.code);
        out[key] = r.svg;
      } catch (e) {
        out[key] = "ERR: " + (e && e.message ? e.message : String(e));
      }
    }
  }
  return out;
};
</script></body></html>`;
  const tmp = path.join(ROOT, 'web/_mmd.html');
  fs.writeFileSync(tmp, html, 'utf8');

  const p = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 20000); });
  await send('Page.navigate', { url: 'file:///E:/QKMansion/CSX10/w/UME/web/_mmd.html' });
  await p;
  await new Promise(r => setTimeout(r, 1500));

  const items = Object.keys(spec).map(k => ({ key: k, code: spec[k].code }));
  const res = await ev('window.__GO__(' + JSON.stringify(THEMES) + ','
    + JSON.stringify(items) + ')', true);

  if (typeof res !== 'object') {
    console.log('  渲染调用失败：' + res);
    ws.close();
    process.exit(1);
  }

  let nOk = 0, nErr = 0;
  for (const key of Object.keys(spec)) {
    for (const themeName of Object.keys(THEMES)) {
      const svg = res[key + '|' + themeName];
      const file = path.join(OUT, PREFIX + '-' + key + '-' + themeName + '.svg');
      if (!svg || svg.startsWith('ERR:') || svg.startsWith('EXC')) {
        console.log('  !! ' + key + ' / ' + themeName + ' → '
          + String(svg).slice(0, 120));
        nErr++;
        continue;
      }
      // mermaid 吐出的是 width="100%" + style="max-width:Wpx"，`<img>` 拿它当
      // 无固有尺寸的图，会缩成看不见的一点点。把 viewBox 的宽高写进 width/height，
      // 图片才有固有尺寸；页面里再用 CSS 的 max-width:100% 控制不要超出正文。
      let out = svg;
      const vb = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
      if (vb) {
        const w = Math.ceil(parseFloat(vb[1]));
        const h = Math.ceil(parseFloat(vb[2]));
        out = svg.replace(/<svg([^>]*?)width="100%"/, '<svg$1width="' + w + '"')
                 .replace(/(<svg[^>]*?)style="max-width:[^"]*"/, '$1')
                 .replace(/<svg([^>]*?)>/, '<svg$1 height="' + h + '">');
      }
      fs.writeFileSync(file, out, 'utf8');
      nOk++;
    }
  }
  console.log('  写出 ' + nOk + ' 个 SVG，失败 ' + nErr + ' 个');
  if (errs.length) console.log('  页面异常：' + errs.slice(0, 2).join(' | '));

  fs.unlinkSync(tmp);
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
