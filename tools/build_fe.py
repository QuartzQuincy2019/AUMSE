# -*- coding: utf-8 -*-
"""前端教程系列（_fe）—— 生成器。

约定
    fe-NN.html          正文
    fe-NN-FMM.html      F = File / Fundamental（与 08-F01 同一含义）
    带 * 的篇目 = 重要内容，导航页与文内都会标出
    <!--FE-TOC-->       占位符，构建时替换为前端系列导航条
    每篇写完把 <style> 抽成 assets/fe-NN.css，与现有教程一致
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
ASSETS = os.path.join(TUT, "assets")

# (文件名, 编号, 标题, 一句话说明, 是否重要)
# 「重要」= 只标该篇里真正的重点条目，不再整篇泛标
FE = [
    ("fe-01.html",     "FE-01",     "HTML 入门与标签语法",           "所写即所得、注释、空格无效性",              False),
    ("fe-02.html",     "FE-02",     "HTML 常用标签",                "p / i / strong / span / ul / div / form / table / a / title", False),
    ("fe-03-F01.html", "FE-03-F01", "十六进制颜色模型、HSV 与 Alpha", "十六进制颜色模型、Alpha 通道",              True),
    ("fe-03.html",     "FE-03",     "CSS 入门",                     "字体、背景色、字体色、装饰、阴影、cursor",   False),
    ("fe-04.html",     "FE-04",     "CSS 选择器语法",                "标签/类/id、后代、属性限定、伪类",          False),
    ("fe-05.html",     "FE-05",     "Display 与盒模型尺寸",          "block / inline-block / inline、边框、阴影、宽高", False),
    ("fe-06.html",     "FE-06",     "Writing Mode 与溢出滚动",       "writing-mode 与 word-break",                True),
    ("fe-07.html",     "FE-07",     "鼠标悬停与 transition",         "hover、过渡、缓动、常用动效",               False),
]

# 前端专属主题（暖色渐变 + 玻璃拟态），单独放一个文件方便调
_THEME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fe_theme.css")
BASE_CSS = io.open(_THEME_PATH, encoding="utf-8").read()

SCRIPT = """(function(){
  var toc = document.getElementById('toc');
  var btn = document.getElementById('tocToggle');
  if (btn && toc) {
    btn.addEventListener('click', function(){ toc.classList.toggle('open'); });
  }
  var links = [].slice.call(document.querySelectorAll('#toc a[href^="#"]'));
  var targets = links.map(function(a){ return document.querySelector(a.getAttribute('href')); })
                     .filter(Boolean);
  if (!targets.length) return;
  var io = new IntersectionObserver(function(es){
    var vis = es.filter(function(e){ return e.isIntersecting; })
                .sort(function(a,b){ return a.boundingClientRect.top - b.boundingClientRect.top; });
    if (vis[0]) {
      var id = vis[0].target.id;
      links.forEach(function(a){ a.classList.toggle('on', a.getAttribute('href') === '#' + id); });
    }
  }, { rootMargin: '-10% 0px -70% 0px' });
  targets.forEach(function(t){ io.observe(t); });

  document.querySelectorAll('.cp').forEach(function(b){
    b.addEventListener('click', function(){
      var pre = b.closest('.code-wrap').querySelector('pre');
      navigator.clipboard.writeText(pre.innerText).then(function(){
        var old = b.textContent; b.textContent = '已复制';
        setTimeout(function(){ b.textContent = old; }, 1200);
      });
    });
  });
})();"""


def page_nav(current):
    out = ['<div class="page-nav"><b>前端系列</b>　']
    for fn, num, title, desc, star in FE:
        s = ' <span style="color:#c8901a">*</span>' if star else ''
        cls = ' class="cur"' if fn == current else ''
        out.append('<a href="%s"%s>%s %s%s</a>' % (fn, cls, num, title, s))
    out.append('</div>')
    return "".join(out)


# ---------------------------------------------------------------------
# 示例展示 + 颜色拾取器（全系列共用）
# ---------------------------------------------------------------------
PREVIEW_CSS = r"""
/* ================= 示例展示：把示例真的渲染出来 ================= */
.pv-wrap{margin:18px 0}
.pv-wrap .code-wrap{margin:0;border-radius:12px 12px 0 0;border-bottom:none}
.pv-frame{border:1px solid var(--line-2);border-top:none;
  border-radius:0 0 12px 12px;background:var(--surface-solid);
  overflow:hidden;transition:box-shadow .18s}
.pv-wrap:hover .pv-frame{box-shadow:0 8px 22px rgba(76,29,149,.13)}
.pv-cap{padding:6px 14px;background:linear-gradient(90deg,
  rgba(124,58,237,.10),rgba(219,39,119,.07));
  border-bottom:1px solid var(--line);font:600 11.5px/1.6 var(--sans);
  color:#6d28d9;letter-spacing:.04em}
.pv-cap::before{content:"示例展示 · ";opacity:.7}
.pv-body{padding:18px 16px;overflow:auto;font:16px/1.8 var(--sans);color:var(--fg)}
.pv-body>*:first-child{margin-top:0}
.pv-body>*:last-child{margin-bottom:0}
.pv-body table{margin:0}
.pv-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}

/* 示例框里 .box / .nl / .zt … 的基础样式 —— 放在这里，
   示例代码就只留要讲的那条规则 */
.pv-body .box{border:1px dashed var(--line-2);border-radius:10px;padding:10px 14px;
  background:rgba(255,255,255,.66)}
.pv-body .box p{margin:4px 0;padding:3px 8px;border-radius:6px}
.pv-body .box a{display:inline-block;margin:3px 0;padding:2px 9px;border-radius:6px;
  text-decoration:none;color:var(--fg);background:rgba(124,58,237,.07);
  border:1px solid transparent}
.pv-body .nl{margin:0;padding-left:22px}
.pv-body .nl li{padding:3px 8px;border-radius:6px}
.pv-body .zt{border-collapse:collapse;width:100%;font-size:14px;background:none;
  box-shadow:none;border-radius:0}
.pv-body .zt th,.pv-body .zt td{border:1px solid var(--line-2);padding:6px 12px;
  background:none}
.pv-body .zt th{background:rgba(124,58,237,.09)}
.pv-body .s8 p{margin:3px 0;padding:3px 8px;border-radius:6px;font-size:15px}
.pv-body .fx{margin:0;padding:12px 14px;background:rgba(255,255,255,.66);
  border-left:4px solid var(--blue);border-radius:0 10px 10px 0}
.pv-body .btn{display:inline-block;margin:4px 6px 4px 0;padding:8px 18px;
  border-radius:10px;color:#fff;cursor:pointer;
  background:linear-gradient(135deg,#7c3aed,#db2777);
  box-shadow:0 3px 12px rgba(124,58,237,.3);
  transition:filter .15s,transform .15s}
.pv-body .inp{margin-top:8px;padding:8px 12px;border:1px solid var(--line-2);
  border-radius:10px;outline:none;transition:box-shadow .15s;font:inherit;
  width:min(100%,260px);background:rgba(255,255,255,.9)}
.pv-body .tagp{display:inline-block;padding:4px 10px;border-radius:999px;
  background:var(--blue-soft);color:var(--blue);font-size:13px}
.pv-body .li2{margin:6px 0}

/* ================= 插图 ================= */
.fig{margin:20px 0;padding:0}
.fig img{display:block;width:100%;height:auto;max-width:620px;margin:0 auto;
  border:1px solid var(--line-2);border-radius:16px;background:#fff;padding:7px;
  box-shadow:0 4px 18px rgba(76,29,149,.10);
  transition:box-shadow .2s,transform .2s}
.fig:hover img{box-shadow:0 16px 40px rgba(76,29,149,.20);transform:translateY(-3px)}
.fig figcaption{margin:12px auto 0;max-width:620px;font-size:12.5px;
  color:var(--fg-3);line-height:1.75;text-align:center}
.fig figcaption b{color:var(--fg-2)}

/* ================= 颜色拾取器 ================= */
.picker{border:1px solid var(--line-2);border-radius:16px;overflow:hidden;
  background:var(--surface);margin:18px 0;
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
  box-shadow:0 4px 20px rgba(76,29,149,.10)}
.picker .pk-top{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.picker .pk-swatch{flex:1 1 200px;min-height:156px;display:flex;align-items:flex-end;
  padding:14px 16px;background:#7c3aed;transition:background .12s}
.picker .pk-swatch span{font:700 15px/1.4 var(--mono);color:#fff;
  text-shadow:0 1px 4px rgba(0,0,0,.55)}
.picker .pk-out{flex:1 1 320px;padding:14px 16px;display:grid;gap:9px;
  align-content:center;background:rgba(255,255,255,.5)}
.picker .pk-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.picker .pk-row b{min-width:78px;color:var(--fg-3);font-weight:600;
  font-family:var(--mono);font-size:12px}
.picker .pk-row code{font-size:12.5px;background:rgba(255,255,255,.85)}
/* 十六进制那一行：放大强调 —— 它是最常被抄走的值 */
.picker .pk-row.pk-hex{align-items:baseline}
.picker .pk-row.pk-hex code{font-size:27px;font-weight:700;letter-spacing:.02em;
  padding:4px 12px;border-radius:10px;line-height:1.25;color:#4c1d95;
  background:linear-gradient(135deg,#ede9fe,#fce7f3);
  border:1px solid rgba(124,58,237,.35);
  text-shadow:0 1px 0 rgba(255,255,255,.7)}
.picker .pk-row .cp2{margin-left:auto;font-size:11.5px;color:var(--blue);cursor:pointer;
  border:1px solid rgba(124,58,237,.32);border-radius:7px;padding:1px 9px;
  background:rgba(255,255,255,.8)}
.picker .pk-row .cp2:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
.picker .pk-ctl{padding:14px 16px;display:grid;gap:12px}
.picker .pk-sl{display:grid;grid-template-columns:104px 1fr 70px;align-items:center;gap:12px;
  font-size:13px}
.picker .pk-sl label{font-family:var(--mono);font-size:12.5px;color:var(--fg-2)}
.picker .pk-sl input[type=range]{width:100%;height:22px;cursor:pointer;
  -webkit-appearance:none;appearance:none;background:transparent}
.picker .pk-sl input[type=range]::-webkit-slider-runnable-track{height:11px;
  border-radius:6px;border:1px solid var(--line-2);background:var(--tk,#e3e8f0)}
.picker .pk-sl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;
  width:19px;height:19px;margin-top:-5px;border-radius:50%;background:#fff;
  border:2px solid #7c3aed;box-shadow:0 1px 4px rgba(76,29,149,.4)}
.picker .pk-sl .val{font-family:var(--mono);font-size:12.5px;color:var(--fg-2);
  text-align:right}
.picker .pk-sw{display:flex;flex-wrap:wrap;gap:7px;padding:0 16px 14px}
.picker .pk-sw i{width:30px;height:30px;border-radius:9px;cursor:pointer;
  border:1px solid rgba(0,0,0,.14);transition:transform .12s}
.picker .pk-sw i:hover{transform:scale(1.16)}
.picker .pk-native{margin:0 16px 12px}
.picker .pk-note{padding:0 16px 15px;font-size:12px;color:var(--fg-3);line-height:1.7}
@media (max-width:560px){
  .picker .pk-row.pk-hex code{font-size:21px}
  .picker .pk-sl{grid-template-columns:78px 1fr 58px;gap:8px}
  .pv-body{padding:14px 12px;font-size:15px}
}
"""

PICKER_HTML = r"""<div class="picker" id="picker">
  <div class="pk-top">
    <div class="pk-swatch" id="pkSwatch"><span id="pkSample">示例文字 Sample</span></div>
    <div class="pk-out">
      <div class="pk-row pk-hex"><b>十六进制</b><code id="pkHex">#1F6FEB</code>
        <span class="cp2" data-cp="pkHex">复制</span></div>
      <div class="pk-row"><b>十进制 RGB</b><code id="pkRgb">rgb(31, 111, 235)</code>
        <span class="cp2" data-cp="pkRgb">复制</span></div>
      <div class="pk-row"><b>HSL / HSV</b><code id="pkHsl">hsl(217, 83%, 52%)</code>
        <span class="cp2" data-cp="pkHsl">复制</span></div>
      <div class="pk-row"><b>含 Alpha</b><code id="pkRgba">#1f6febff</code>
        <span class="cp2" data-cp="pkRgba">复制</span></div>
    </div>
  </div>
  <div class="pk-ctl">
    <div class="pk-sl"><label>红 R</label>
      <input type="range" id="pkR" min="0" max="255" value="31"><span class="val" id="pkRv">31</span></div>
    <div class="pk-sl"><label>绿 G</label>
      <input type="range" id="pkG" min="0" max="255" value="111"><span class="val" id="pkGv">111</span></div>
    <div class="pk-sl"><label>蓝 B</label>
      <input type="range" id="pkB" min="0" max="255" value="235"><span class="val" id="pkBv">235</span></div>
    <div class="pk-sl"><label>透明度 A</label>
      <input type="range" id="pkA" min="0" max="100" value="100"><span class="val" id="pkAv">100%</span></div>
  </div>
  <div class="pk-sw" id="pkPresets"></div>
  <div class="pk-note">拖动滑块，看四个数值怎么联动。
    <b>Alpha 写成两位十六进制时 <code>80</code> ≈ 50%</b>，不是 80%。</div>
</div>"""

PICKER_JS = r"""
/* ================= 颜色拾取器 ================= */
(function(){
  var el = document.getElementById('picker');
  if (!el) return;
  var R=document.getElementById('pkR'), G=document.getElementById('pkG'),
      B=document.getElementById('pkB'), A=document.getElementById('pkA');
  var sw=document.getElementById('pkSwatch');
  var hx=document.getElementById('pkHex'), rg=document.getElementById('pkRgb'),
      hs=document.getElementById('pkHsl'), ra=document.getElementById('pkRgba');

  function h2(n){ n=Math.round(n); return (n<16?'0':'')+n.toString(16).toUpperCase(); }
  function hue(r,g,b,mx,mn,d){
    if (!d) return 0;
    var h;
    if (mx===r) h=((g-b)/d)%6;
    else if (mx===g) h=(b-r)/d+2;
    else h=(r-g)/d+4;
    h*=60; return h<0?h+360:h;
  }
  function sync(){
    var r=+R.value, g=+G.value, b=+B.value, a=+A.value;
    document.getElementById('pkRv').textContent=r;
    document.getElementById('pkGv').textContent=g;
    document.getElementById('pkBv').textContent=b;
    document.getElementById('pkAv').textContent=a+'%';

    var hexv='#'+h2(r)+h2(g)+h2(b);
    sw.style.background = a>=100 ? hexv : 'rgba('+r+','+g+','+b+','+(a/100)+')';

    var mx=Math.max(r,g,b)/255, mn=Math.min(r,g,b)/255, d=mx-mn;
    var h=Math.round(hue(r/255,g/255,b/255,mx,mn,d));
    var sv = mx ? Math.round(d/mx*100) : 0;
    var v  = Math.round(mx*100);
    var l  = Math.round((mx+mn)/2*100);
    var sl = (mx+mn)===0||(mx+mn)===2 ? 0
             : Math.round(d/(1-Math.abs(mx+mn-1))*100);

    hx.textContent = hexv;
    rg.textContent = 'rgb('+r+', '+g+', '+b+')';
    hs.textContent = 'hsl('+h+', '+sl+'%, '+l+'%)  /  hsv('+h+', '+sv+'%, '+v+'%)';
    ra.textContent = (hexv+h2(a*255/100)).toLowerCase()
                   + '  rgba('+r+', '+g+', '+b+', '+(a/100).toFixed(2)+')';

    /* 滑块轨道跟着变色，好看清各通道的作用 */
    R.style.setProperty('--tk',
      'linear-gradient(90deg, rgb(0,'+g+','+b+'), rgb(255,'+g+','+b+'))');
    G.style.setProperty('--tk',
      'linear-gradient(90deg, rgb('+r+',0,'+b+'), rgb('+r+',255,'+b+'))');
    B.style.setProperty('--tk',
      'linear-gradient(90deg, rgb('+r+','+g+',0), rgb('+r+','+g+',255))');
    A.style.setProperty('--tk',
      'linear-gradient(90deg, rgba('+r+','+g+','+b+',0), rgb('+r+','+g+','+b+'))');
  }
  [R,G,B,A].forEach(function(s){ s.addEventListener('input', sync); });

  var presets = ['#1F6FEB','#17864A','#C0392B','#A4690D','#6B46C1','#0D7D7D',
                 '#1a1f28','#4b5563','#8b95a5','#ccd5e3','#e3e8f0','#f7f9fc',
                 '#ffffff','#000000','#ff0000','#ff6f00','#ffd400'];
  var box = document.getElementById('pkPresets');
  presets.forEach(function(c){
    var i = document.createElement('i');
    i.style.background = c; i.title = c;
    i.addEventListener('click', function(){
      R.value = parseInt(c.slice(1,3),16);
      G.value = parseInt(c.slice(3,5),16);
      B.value = parseInt(c.slice(5,7),16);
      A.value = 100;
      sync();
    });
    box.appendChild(i);
  });

  el.querySelectorAll('.cp2').forEach(function(b){
    b.addEventListener('click', function(){
      var full = document.getElementById(b.dataset.cp).textContent;
      var txt = full.split('  ')[0].trim();
      navigator.clipboard.writeText(txt).then(function(){
        var o=b.textContent; b.textContent='已复制';
        setTimeout(function(){ b.textContent=o; }, 1100);
      });
    });
  });

  var inp = document.createElement('input');
  inp.type = 'color'; inp.value = '#1f6feb';
  inp.style.cssText = 'width:34px;height:30px;padding:0;border:1px solid #ccd5e3;'
    + 'border-radius:7px;cursor:pointer;background:#fff';
  inp.addEventListener('input', function(){
    R.value = parseInt(inp.value.slice(1,3),16);
    G.value = parseInt(inp.value.slice(3,5),16);
    B.value = parseInt(inp.value.slice(5,7),16);
    sync();
  });
  el.querySelector('.pk-sw').parentNode.insertBefore(inp, el.querySelector('.pk-sw'));
  sync();
})();

/* ================= 示例展示 =================
   把代码块里的内容真的渲染出来。
   关键：CSS 示例里的 .card / div 之类选择器不能作用到文档本身，
   所以给每条规则的选择器加上 [data-pv="N"] 前缀，只在那个示例框内生效。
   前缀不改变任何偏移量，示例内部的优先级关系与真实页面一致。

   注意：必须**数花括号配平**，不能找第一个 '}' ——
   示例 CSS 已经排成三行式，而且可能有 @media 这类嵌套块。
   字符串里的花括号也要跳过，避免误判。 */
(function(){
  function scoped(css, scope){
    var out = '', i = 0, n = css.length;
    while (i < n) {
      if (css.substr(i, 2) === '/*') {            /* 跳过注释 */
        var ce = css.indexOf('*/', i + 2);
        i = ce < 0 ? n : ce + 2;
        continue;
      }
      var b = css.indexOf('{', i);
      if (b < 0) break;
      var sel = css.slice(i, b).replace(/\/\*[\s\S]*?\*\//g, '').trim();
      var depth = 1, k = b + 1, q = null;         /* 数配平，跳过字符串 */
      while (k < n && depth > 0) {
        var ch = css[k];
        if (q) { if (ch === q && css.charAt(k - 1) !== '\\') q = null; }
        else if (ch === '"' || ch === "'") q = ch;
        else if (ch === '{') depth++;
        else if (ch === '}') depth--;
        k++;
      }
      var body = css.slice(b + 1, k - 1);
      if (sel && sel.charAt(0) !== '@') {
        sel = sel.split(',').map(function(x){
          x = x.trim();
          return x ? scope + ' ' + x : x;
        }).join(', ');
      }
      out += sel + '{' + body + '}';
      i = k;
    }
    return out;
  }

  document.querySelectorAll('.pv-wrap[data-pv]').forEach(function(w){
    var scope = '[data-pv="' + w.dataset.pv + '"]';
    var body  = w.querySelector('.pv-body');
    var code  = w.querySelector('pre');
    if (!body || !code) return;
    var text = code.textContent;
    var kind = w.dataset.pvKind || 'html';

    if (kind === 'css') {
      var st = document.createElement('style');
      st.textContent = scoped(text, scope);
      w.appendChild(st);
    } else {
      body.innerHTML = text;
    }
  });
})();
"""


TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
@@STYLE@@
</head>
<body>
<button id="tocToggle">目录</button>
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
@@TOC@@
</nav>

<main id="top">
<h1>@@HTITLE@@@@STAR@@</h1>
<p class="sub-title">UME 项目组内部教程 · 前端系列（FE）· @@NUM@@</p>
@@BODY@@
@@NAV@@
<footer>
UME 项目组内部教程 · 前端系列 @@NUM@@《@@TITLE@@》<br>
示例均以 <b>Consolas</b> 等宽字体呈现；标着「示例展示」的代码块会把效果真的渲染出来。
</footer>
</main>
</div>
@@SCRIPT@@
</body>
</html>
"""


def build(fn, num, title, body, toc, css_extra="", with_picker=False):
    """注意：绝不可以用 % 格式化或 str.format ——
       CSS/JS 里有 width:100%、margin-top:-5px 这类内容，会被当成格式符，
       轻则内容被悄悄吃掉，重则直接抛异常。一律用 replace。"""
    meta = next(m for m in FE if m[0] == fn)
    star = meta[4]
    star_mark = (' <span class="star" style="color:#c8901a;cursor:help"'
                 ' title="重要内容">*</span>') if star else ''
    if with_picker:
        body = body + "\n\n" + PICKER_HTML

    style = '<style>%s%s%s</style>' % (BASE_CSS, PREVIEW_CSS, css_extra)
    script = "<script>%s\n%s</script>" % (SCRIPT, PICKER_JS)

    reps = [
        ("@@TITLE@@", title),
        ("@@HTITLE@@", title),
        ("@@STAR@@", star_mark),
        ("@@NUM@@", num),
        ("@@STYLE@@", style),
        ("@@TOC@@", toc),
        ("@@BODY@@", body),
        ("@@NAV@@", page_nav(fn)),
        ("@@SCRIPT@@", script),
    ]
    html = TPL
    for k, v in reps:
        html = html.replace(k, v)

    left = [k for k, _ in reps if k in html]
    if left:
        raise RuntimeError("build(%s): 占位符未替换 %s" % (fn, left))

    io.open(os.path.join(TUT, fn), "w", encoding="utf-8", newline="").write(html)
    return len(html)


def extract_css(doc_names):
    """把每篇的 <style> 抽成 assets/<stem>.css（与现有教程同一套做法）。"""
    for fn in doc_names:
        p = os.path.join(TUT, fn)
        t = io.open(p, encoding="utf-8").read()
        m = re.search(r'(?s)<style>(.*?)</style>', t)
        if not m:
            continue
        stem = re.sub(r'[^A-Za-z0-9]+', '_', os.path.splitext(fn)[0]).strip('_')
        target = stem + ".css"
        io.open(os.path.join(ASSETS, target), "w",
                encoding="utf-8", newline="\n").write(m.group(1).strip() + "\n")
        t = t.replace(m.group(0),
                      '<link rel="stylesheet" href="assets/%s">' % target, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(t)


if __name__ == "__main__":
    pass