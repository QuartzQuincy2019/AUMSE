# -*- coding: utf-8 -*-
"""生成 kbdglyf.html —— 键位 · 字形 · 鲍培转写图。

数据取自两张扫描表：
    元音字母表.jpg   （7 个元音）
    辅音字母表.jpg   （26 个辅音，分上下两段）

两表的表头都有三行，别混：
    第 1 行  鲍培转写      （页边注「鲍培=」）
    第 2 行  书面语读音·拉丁转写  （旋转 90° 写的那行，kh / sh / ch 在这里）
    第 3 行  KBD 键位      （页边注「KBD=」）

本页只用第 1 行和第 3 行；第 2 行不列（参见 T01 §4）。

鲍培的 q/k、γ/g 在原表里没标出来（原表只写了 q、γ），本页把它们叠在一起显示 ——
同一个字母，后接阳性元音读前者，后接阴性元音读后者。
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = r"E:\QKMansion\CSX10\w\UME\kbdglyf.html"

ZWJ = "\u200d"

# (码位, 键位, 鲍培, 鲍培第二值 or None)
#
# 键位以**本机输入法**为准（F0B20850 = Microsoft 传统蒙古语(标准) TMS），
# 与教材 KBD 行有六处不同：o=Q、č=C、w=W、c=⇧C、ch=⇧Q。
# 换机器若键位不同，改这张表即可。
#
# 原表把 ᠡ 那一格的键位写成「e,E」，容易误读成「两个键打同一个字母」。
# 实际上 Shift+E 打的是另一个元音 ᠧ（U+1827，长音 ē），本页把它单独列一行。
# 位置与原表一致：排在 7 个基本元音之后，因为它只用于借词。
VOWELS = [
    (0x1820, ["a"],         "a", None),
    (0x1821, ["e"],         "e", None),
    (0x1822, ["i"],         "i", None),
    (0x1823, ["q"],         "o", None),
    (0x1824, ["v"],         "u", None),
    (0x1825, ["o"],         "ö", None),
    (0x1826, ["u"],         "ü", None),
    (0x1827, ["E"],         "ē", None),
]

CONS1 = [
    (0x1828, ["n"], "n", None),
    (0x182A, ["b"], "b", None),
    (0x182B, ["p"], "p", None),
    (0x182C, ["h"], "q", "k"),
    (0x182D, ["g"], "γ", "g"),
    (0x182E, ["m"], "m", None),
    (0x182F, ["l"], "l", None),
    (0x1830, ["s"], "s", None),
    (0x1831, ["x"], "š", None),
    (0x1832, ["t"], "t", None),
    (0x1833, ["d"], "d", None),
    (0x1834, ["c"], "č", None),
    (0x1835, ["j"], "ǰ", None),
]

CONS2 = [
    (0x1836, ["y"], "y", None),
    (0x1837, ["r"], "r", None),
    (0x1838, ["w"], "w", None),
    (0x1829, ["N"], "ng", None),
    (0x1839, ["f"], "f", None),
    (0x183A, ["k"], "k", None),
    (0x183C, ["C"], "c", None),
    (0x183D, ["z"], "z", None),
    (0x183E, ["H"], "h", None),
    (0x183F, ["R"], "ž", None),
    (0x1840, ["L"], "lh", None),
    (0x1841, ["Z"], "zh", None),
    (0x1842, ["Q"], "ch", None),
]


def forms(cp):
    """四种位置形。ZWJ 在 HarfBuzz / DirectWrite 里都是零宽，能强制位置形。"""
    c = chr(cp)
    return {
        "init": c + ZWJ,
        "medi": ZWJ + c + ZWJ,
        "fina": ZWJ + c,
        "isol": c,
    }


def kbd_html(keys):
    return "".join('<span class="k">%s</span>' % k for k in keys)


def poppe_html(p1, p2):
    if p2:
        return ('<span class="pv" title="后接阳性元音读 %s，阴性元音读 %s">'
                '<b>%s</b><i>%s</i></span>' % (p1, p2, p1, p2))
    return "<b>%s</b>" % p1


def glyph(cp, which):
    return '<div class="gl"><span>%s</span></div>' % forms(cp)[which]


def rows(data, with_isol):
    out = []
    for cp, keys, p1, p2 in data:
        cells = ['<td class="kc">%s<span class="cp">U+%04X</span></td>'
                 % (kbd_html(keys), cp)]
        for which in ("init", "medi", "fina"):
            cells.append("<td class='glyphcell'>%s</td>" % glyph(cp, which))
        if with_isol:
            cells.append("<td class='glyphcell'>%s</td>" % glyph(cp, "isol"))
        cells.append('<td class="poppe">%s</td>' % poppe_html(p1, p2))
        out.append("        <tr>%s</tr>" % "".join(cells))
    return "\n".join(out)


def head(with_isol):
    # table-layout:fixed 直接吃第一行的宽度，所以宽窄只在这里定
    ths = ['<th style="width:66px">键位</th>',
           '<th>词首<code>init</code></th>',
           '<th>词中<code>medi</code></th>',
           '<th>词末<code>fina</code></th>']
    if with_isol:
        ths.append('<th>单独<code>isol</code></th>')
    ths.append('<th class="poppe" style="width:50px">鲍培</th>')
    return "        <tr>%s</tr>" % "".join(ths)


HTML = """<!DOCTYPE html>
<html lang="zh-CN" data-font="baiti" data-dir="v" data-poppe="off">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>键位 · 字形 · 鲍培转写</title>
<script>
/* 主题：自动跟随系统，也可手动钉成浅色 / 深色。
   脚本放在 <head> 里同步执行，避免先闪一下浅色再变深。 */
(function(){
  try{
    var t = localStorage.getItem('kbdglyf.theme') || 'auto';
    if (t === 'dark' || (t === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches))
      document.documentElement.classList.add('dark');
  }catch(e){}
})();
</script>
<style>
@font-face{
  font-family:"UME Noto";
  src:url("font/NotoSansMongolian-Regular.ttf") format("truetype");
  font-display:swap;
}
:root{
  color-scheme:light;
  --bg:#fbf9f4;--fg:#241f18;--dim:#6b6459;--line:#e3dccd;--card:#fff;
  --head:#f6f1e6;--accent:#9a6b0a;--accent2:#c8a24a;--soft:#fdf7e8;
  /* 键位胶囊：原来 accent 压 soft，对比只有 4.5:1，字又小；这里单独给一组高对比色 */
  --kfg:#3d2b00;--kbg:#ffe9b8;--kbd:#cf9f3e;
}
html.dark{
  color-scheme:dark;
  /* 与 mmkb/mmkb.html 共用同一套暗色值，两页并排看底色一致 */
  --bg:#12151a;--fg:#e8ecf3;--dim:#a6b0bf;--line:#2d333c;--card:#1a1e24;
  --head:#20242b;--accent:#e0b45e;--accent2:#8a6f33;--soft:#242932;
  --kfg:#ffe6a6;--kbg:#33290f;--kbd:#8a6a26;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);
  font:15px/1.7 "Microsoft YaHei","PingFang SC",sans-serif;
  -webkit-font-smoothing:antialiased}
main{max-width:1480px;margin:0 auto;padding:30px 22px 80px}

h1{font-size:25px;margin:0 0 6px;letter-spacing:.5px}
.sub{color:var(--dim);font-size:14px;margin:0 0 22px}
.sub b{color:var(--fg);font-weight:600}

.bar{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;
  background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:12px 16px;margin-bottom:26px}
.grp{display:flex;align-items:center;gap:8px;font-size:13.5px}
.grp>span:first-child{color:var(--dim)}
select,button{font:inherit;font-size:13.5px;color:var(--fg);background:var(--soft);
  border:1px solid var(--line);border-radius:8px;padding:5px 9px;cursor:pointer}
select:hover,button:hover{border-color:var(--accent2)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg button{border:0;border-radius:0;background:transparent;padding:6px 13px}
.seg button+button{border-left:1px solid var(--line)}
.seg button[aria-pressed="true"]{background:var(--accent);color:#fff;font-weight:600}

h2{font-size:16px;margin:0 0 9px;padding-left:10px;border-left:4px solid var(--accent)}
h2 code{font-size:12px;color:var(--dim);font-weight:400}
.hint{color:var(--dim);font-size:12.5px;margin:9px 2px 0;line-height:1.6}
.hint code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:12px}
/* 正文里夹的单字蒙文：13.5px 的正文里它会小得看不清，单独放大并换字体 */
.mn{font-family:"Mongolian Baiti","UME Noto",serif;font-size:1.45em;line-height:1;
  vertical-align:-3px;padding:0 1px}

/* ---- 三张表并排（表很长，竖着堆会拖出一屏多） ---- */
.tables{display:grid;grid-template-columns:repeat(auto-fit,minmax(318px,1fr));
  gap:18px;align-items:start}
.sec{min-width:0}
.wrap{background:var(--card);border:1px solid var(--line);border-radius:12px;
  overflow-x:auto;padding:2px;width:100%}
table{border-collapse:collapse;width:100%;table-layout:fixed}
th,td{border-bottom:1px solid var(--line);padding:5px 4px;text-align:center;vertical-align:middle}
thead th{background:var(--head);font-size:12.5px;font-weight:600;color:var(--dim)}
thead th code{font-size:10.5px;opacity:.75;display:block;line-height:1.3}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--soft)}

td.kc{width:92px;white-space:nowrap}
td.poppe{width:56px}
.cp{display:block;font:11px/1.35 Consolas,monospace;color:var(--dim);opacity:.7}
/* 键位胶囊：字号再放大一档（17 → 22 → 28px），配色单独给（见 :root 的 --kfg/--kbg/--kbd）
   —— 原来用 accent 压 soft，浅色下 4.5:1、深色下更糊 */
.k{display:inline-block;min-width:36px;padding:1px 9px;margin:1px 0;
  font:700 28px/1.2 Consolas,"Courier New",monospace;
  color:var(--kfg);background:var(--kbg);border:1px solid var(--kbd);border-radius:7px}

/* ---- 字形 ---- */
.glyphcell{padding:0}
.gl{height:92px;display:flex;align-items:center;justify-content:center;
  color:var(--fg);font-size:46px;line-height:1;overflow:visible}
html[data-dir="v"] .gl span{writing-mode:vertical-lr;direction:ltr}

/* ---- 字体 ---- */
/* 三支都用系统字体名引用，仓库里只放 Noto（OFL，可分发）。
   Baiti / Qimed 不能进仓库：fsType = 8，微软 / 蒙科立授权。 */
html[data-font="baiti"] .gl{font-family:"Mongolian Baiti","Menk Qimed Tig","UME Noto",serif}
html[data-font="qimed"] .gl{font-family:"Menk Qimed Tig","Mongolian Baiti","UME Noto",serif}
html[data-font="noto"]  .gl{font-family:"UME Noto","Mongolian Baiti",serif}

/* ---- 鲍培列 ---- */
html[data-poppe="off"] .poppe{display:none}
/* 鲍培转写用等宽字体：γ / š / č / ǰ / ö / ü 在比例字体里宽度不一，
   一列排下来对不齐，也容易和正文混淆 */
td.poppe{white-space:nowrap;font-family:Consolas,"Cascadia Mono","Courier New",monospace;
  font-size:22px;font-weight:700;color:var(--fg)}
.pv{display:inline-flex;flex-direction:column;line-height:1.05;vertical-align:middle}
.pv b{font-weight:600}
.pv i{font-style:normal;font-size:15px;font-weight:700;color:var(--dim)}

.note{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent2);
  border-radius:10px;padding:13px 17px;margin:26px 0;font-size:14px;color:var(--dim)}
@media (max-width:900px){ .tables{grid-template-columns:1fr} }
.note b{color:var(--fg)}
.note code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:12.5px}
ul{margin:8px 0 0;padding-left:22px}
li{margin:4px 0}
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
  font-size:13px;color:var(--dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
footer a{color:var(--accent);text-decoration:none}
footer a:hover{text-decoration:underline}
@media (max-width:720px){
  main{padding:22px 12px 70px}
  .gl{height:86px;font-size:38px}
  h1{font-size:21px}
}
</style>
</head>
<body>
<main>

<h1>键位 · 字形 · 鲍培转写</h1>
<p class="sub">教材《蒙古文元音字母表》《蒙古文辅音字母表》的数据，做成可交互的表。
<b>键位</b>按本机输入法（Microsoft 传统蒙古语(标准) TMS）实测，<b>字形</b>按四种位置形实时排版，<b>鲍培转写</b>默认关闭。</p>

<div class="bar">
  <label class="grp"><span>字体</span>
    <select id="fontSel">
      <option value="baiti" selected>Baiti</option>
      <option value="qimed">Qimed</option>
      <option value="noto">Noto Sans Mongolian</option>
    </select>
  </label>

  <div class="grp"><span>排版</span>
    <span class="seg" id="dirSeg">
      <button data-v="v" aria-pressed="true">竖排</button>
      <button data-v="h" aria-pressed="false">横排</button>
    </span>
  </div>

  <div class="grp"><span>鲍培转写</span>
    <span class="seg" id="popSeg">
      <button data-v="off" aria-pressed="true">关</button>
      <button data-v="on" aria-pressed="false">开</button>
    </span>
  </div>

  <div class="grp"><span>主题</span>
    <span class="seg" id="themeSeg">
      <button data-v="auto" aria-pressed="true">自动</button>
      <button data-v="light" aria-pressed="false">浅色</button>
      <button data-v="dark" aria-pressed="false">深色</button>
    </span>
  </div>
</div>

<div class="tables">

<section class="sec">
<h2>一、元音 <code>7 + 1 个</code></h2>
<div class="wrap">
  <table>
    <thead>
{{HEADV}}
    </thead>
    <tbody>
{{ROWSV}}
    </tbody>
  </table>
</div>
<p class="hint">前 7 个是基本元音。最后一行 <span class="mn">ᠧ</span> 是长音 <code>ē</code>，
只用于借词 —— 原表把它并在 <code>e</code> 那一格里（写作 <code>e,E</code>），本页拆开单列。</p>
</section>

<section class="sec">
<h2>二、辅音 · 上段 <code>13 个</code></h2>
<div class="wrap">
  <table>
    <thead>
{{HEADC1}}
    </thead>
    <tbody>
{{ROWSC1}}
    </tbody>
  </table>
</div>
</section>

<section class="sec">
<h2>三、辅音 · 下段 <code>13 个</code></h2>
<div class="wrap">
  <table>
    <thead>
{{HEADC2}}
    </thead>
    <tbody>
{{ROWSC2}}
    </tbody>
  </table>
</div>
</section>

</div>

<div class="note">
  <p><b>怎么读这张表</b></p>
  <ul>
    <li><b>键位</b>是微软蒙文输入法的按键。<b>大写 = 加 <code>Shift</code></b>，
        打出来的往往是<b>另一个</b>字母 —— 例如 <code>e</code> 打 <span class="mn">ᠡ</span>（U+1821），
        <code>Shift+E</code> 打的却是 <span class="mn">ᠧ</span>（U+1827），两者不是同一个码位。</li>
    <li><b>四种字形</b>是同一个码位在词首 / 词中 / 词末 / 单独时的样子 ——
        <b>不是四个码位</b>，只是字体按上下文换形状。表里用零宽连接符
        <code>U+200D</code> 强制出各个位置形。</li>
    <li><b>鲍培的 <code>q/k</code>、<code>γ/g</code> 各是一个字母的两个读音</b>：
        后接阳性元音读上面那个（<code>q</code>、<code>γ</code>），阴性元音读下面那个
        （<code>k</code>、<code>g</code>）。原表只写了 <code>q</code>、<code>γ</code>，
        这层区分没标出来。</li>
    <li>原表<b>没有</b> <span class="mn">ᠻ</span>（U+183B，<code>kh</code>）—— 它只出现在借词里，这张表没列。</li>
    <li><b>字体</b>默认 Mongolian Baiti。它是 Windows 自带的系统字体，
        <b>不随本仓库分发</b>（微软授权，fsType = 8）。换到没装它的机器上会自动
        落到 Qimed 或仓库里的 Noto Sans Mongolian。</li>
  </ul>
</div>

<footer>
  <span>数据来源：SharingGroup/tutorials/assets/ref/ 下的两张扫描表</span>
  <a href="index.html">← 返回教程首页</a>
</footer>

</main>

<script>
(function(){
  var root = document.documentElement;

  function seg(id, attr, onPick){
    var box = document.getElementById(id);
    box.addEventListener('click', function(e){
      var b = e.target.closest('button');
      if(!b) return;
      Array.prototype.forEach.call(box.querySelectorAll('button'), function(x){
        x.setAttribute('aria-pressed', String(x === b));
      });
      onPick(b.dataset.v);
    });
  }

  function set(attr, v){
    if(!v) return;
    root.setAttribute(attr, v);
    try{ localStorage.setItem('kbdglyf.' + attr, v); }catch(e){}
  }

  seg('dirSeg', 'data-dir', function(v){ set('data-dir', v); });
  seg('popSeg', 'data-poppe', function(v){ set('data-poppe', v); });

  /* 主题：auto 跟系统，light / dark 钉死。
     深色是靠 <html class="dark"> 切换的，head 里那段已经先把类打上了，
     这里只负责用户点击后的切换与持久化。 */
  var mq = matchMedia('(prefers-color-scheme: dark)');
  function applyTheme(t){
    var dark = (t === 'dark') || (t === 'auto' && mq.matches);
    root.classList.toggle('dark', dark);
    try{ localStorage.setItem('kbdglyf.theme', t); }catch(e){}
    Array.prototype.forEach.call(
      document.querySelectorAll('#themeSeg button'),
      function(x){ x.setAttribute('aria-pressed', String(x.dataset.v === t)); });
  }
  seg('themeSeg', 'theme', applyTheme);
  mq.addEventListener('change', function(){
    var t = 'auto';
    try{ t = localStorage.getItem('kbdglyf.theme') || 'auto'; }catch(e){}
    if(t === 'auto') applyTheme('auto');
  });

  var sel = document.getElementById('fontSel');
  sel.addEventListener('change', function(){ set('data-font', sel.value); });

  // 恢复上次的选择（字体默认仍然是 Baiti，这里只恢复用户改过的）
  try{
    var savedTheme = localStorage.getItem('kbdglyf.theme');
    if(savedTheme) applyTheme(savedTheme);
    ['data-font','data-dir','data-poppe'].forEach(function(a){
      var v = localStorage.getItem('kbdglyf.' + a);
      if(!v) return;
      root.setAttribute(a, v);
      if(a === 'data-font'){ sel.value = v; }
      else{
        var box = document.getElementById(a === 'data-dir' ? 'dirSeg' : 'popSeg');
        Array.prototype.forEach.call(box.querySelectorAll('button'), function(x){
          x.setAttribute('aria-pressed', String(x.dataset.v === v));
        });
      }
    });
  }catch(e){}
})();
</script>
</body>
</html>
"""

# 模板里有大量 CSS 的 %（width:100% 之类），不能用 % 格式化，改用占位符替换
page = HTML
for token, value in (
    ("{{HEADV}}", head(True)),
    ("{{ROWSV}}", rows(VOWELS, True)),
    ("{{HEADC1}}", head(False)),
    ("{{ROWSC1}}", rows(CONS1, False)),
    ("{{HEADC2}}", head(False)),
    ("{{ROWSC2}}", rows(CONS2, False)),
):
    page = page.replace(token, value)

io.open(OUT, "w", encoding="utf-8", newline="").write(page)
print("   已写 %s  (%d 字符)" % (OUT, len(page)))
print("   元音 %d 行 · 辅音上段 %d 行 · 辅音下段 %d 行"
      % (len(VOWELS), len(CONS1), len(CONS2)))
