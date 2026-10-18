/* 生成一张「字体自检图」：把页面里的 MN_FONTS 逐支直接渲染出来，
   旁边标族名与实测缩放，用来肉眼+像素确认每支字体真的接管了排版。

   做法：拷一份 globpreview.html 到 refs/，在 </body> 前注入一段脚本，
   由脚本用页面自己的 MN_FONTS 造一个自检面板（第 0 屏）。
   然后用 Edge headless 的 --screenshot 出图（--dump-dom 在 Windows 上
   走不通：msedge.exe 是 GUI 子系统程序，stdout 接不上控制台）。 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const SRC = path.join(ROOT, 'web', 'globpreview.html');
const TMP = path.join(ROOT, 'refs', 'gp_selftest.html');
const PNG = path.join(ROOT, 'refs', 'globpreview-fonts.png');
const EDGE = [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
].find(p => fs.existsSync(p));

const PANEL = `
<script>
/* ===== 自检面板（只出现在这份副本里，不进仓库页面） ===== */
(async function(){
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 100; i++){            /* 等 boot 把选项填出来 */
    await sleep(80);
    if (document.querySelectorAll('#fontsel option').length > 2) break;
  }
  const sel = document.getElementById('fontsel');
  const WORD = '\\u182E\\u1823\\u1829\\u182D\\u1823\\u182F';  /* ᠮᠣᠩᠭᠣᠯ */
  const notInstalled = Array.from(sel.options)
    .filter(o => o.textContent.includes('未安装')).map(o => o.value);

  /* 逐支直接点名渲染：这一栏不走 applyFont，只证明「字体本机能排」 */
  const cells = MN_FONTS.map(f =>
    '<span style="display:inline-block;width:82px;text-align:center;vertical-align:top">'
    + '<span style="font-family:\\'' + f.f + '\\',serif;font-size:26px;line-height:1.1;'
    + 'writing-mode:vertical-lr;text-orientation:mixed;height:52px">' + WORD + '</span>'
    + '<i style="display:block;font:8px/1.1 monospace;color:#555;'
    + 'overflow:hidden;white-space:nowrap">' + f.f.replace('Menk ', '') + '</i>'
    + '<b style="display:block;font:8px/1.1 monospace;color:#b06">' + f.s.toFixed(2) + '</b>'
    + '</span>').join('');

  /* 再走一遍页面的真实机制：applyFont → --mn-font / --mn-scale */
  sel.value = 'Menk Qagan Tig';
  sel.dispatchEvent(new Event('change'));
  const rootStyle = document.documentElement.style;
  const realW = advance(WORD).toFixed(2);
  sel.value = 'UME Mongolian';
  sel.dispatchEvent(new Event('change'));
  const notoW = advance(WORD).toFixed(2);

  const box = document.createElement('div');
  box.style.cssText = 'background:#fffbee;border-bottom:2px solid #c90;'
    + 'padding:6px 10px;font:11px/1.5 monospace;color:#333';
  box.innerHTML =
      '<b style="font-size:13px">SELFTEST</b>  '
    + '选项总数=<b>' + sel.options.length + '</b>  '
    + '分组=' + Array.from(sel.querySelectorAll('optgroup'))
        .map(g => g.label + ':' + g.querySelectorAll('option').length).join(' | ') + '  '
    + '<br>未安装=' + (notInstalled.length ? notInstalled.join(',') : '无')
    + '　内置@font-face=' + document.fonts.check('40px "UME Mongolian"')
    + '<br>applyFont 生效：--mn-font=' + rootStyle.getPropertyValue('--mn-font')
    + '　--mn-scale=' + rootStyle.getPropertyValue('--mn-scale')
    + '　推进量 Noto ' + notoW + ' vs MenkQagan ' + realW
    + '<div style="margin-top:5px">' + cells + '</div>';
  document.body.insertBefore(box, document.body.firstChild);
})();
</script>
`;

if (!EDGE) { console.error('找不到 msedge.exe'); process.exit(1); }

let html = fs.readFileSync(SRC, 'utf8');
html = html.replace(/<\/body>/i, PANEL + '\n</body>');
fs.writeFileSync(TMP, html, 'utf8');

const prof = path.join(os.tmpdir(), 'ume-gp-shot-' + Date.now());
const uri = 'file:///' + TMP.replace(/\\/g, '/');
const r = spawnSync(EDGE, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--user-data-dir=' + prof,
  '--virtual-time-budget=12000',
  '--window-size=1480,760',
  '--force-device-scale-factor=2',
  '--screenshot=' + PNG,
  uri,
], { stdio: 'inherit', timeout: 90000 });

console.log('edge exit =', r.status);
console.log('png =', fs.existsSync(PNG) ? fs.statSync(PNG).size + ' bytes' : 'MISSING');
try { fs.rmSync(prof, { recursive: true, force: true }); } catch (e) {}
