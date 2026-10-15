# -*- coding: utf-8 -*-
"""FE-03《CSS 入门》—— 重建，给视觉类知识点配「示例展示」。

做法：把原来那些「只有代码」的块换成 pv()（代码 + 真实渲染）。
非视觉的（语法、选择器优先级表）保持原样，不硬凑示例。
"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build
from fe_kit import pv, code

TOC = """  <a href="#s1">1 · CSS 是什么</a>
  <a href="#s2">2 · 三种写 CSS 的位置</a>
  <a href="#s3">3 · 语法：选择器 + 声明块</a>
  <a href="#s4">4 · 常用选择器</a>
  <a href="#s5">5 · 字体相关</a>
  <a href="#s6">6 · 背景与文字颜色</a>
  <a href="#s7">7 · 文字装饰：text-decoration / text-shadow</a>
  <a href="#s8">8 · 鼠标光标：cursor</a>
  <a href="#s9">9 · 优先级与继承</a>
  <a href="#s10">10 · 一页速查</a>"""

P = {}

# ---------- 5 字体 ----------
P["f1"] = pv(1, "font-family 字体回退链",
             """/* 浏览器的查找顺序：有 Consolas 用它，没有就试下一个 */
.mono { font-family: "Consolas", "Cascadia Mono", monospace; }
.sans { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }
.serif{ font-family: Georgia, "Times New Roman", serif; }""",
             demo=('<p class="mono">Consolas 等宽：0123456789 abcXYZ</p>'
                   '<p class="sans">Microsoft YaHei 无衬线：中文与 English 混排</p>'
                   '<p class="serif">Georgia 衬线：The quick brown fox</p>'))

P["f2"] = pv(2, "字号与粗细",
             """.s1{font-size:13px}
.s2{font-size:16px}
.s3{font-size:22px}
.w3{font-weight:300}
.w7{font-weight:700}
.w9{font-weight:900}""",
             demo=('<p class="s1">13px 小字</p>'
                   '<p class="s2">16px 正文（默认）</p>'
                   '<p class="s3">22px 大字</p>'
                   '<p class="w3">font-weight: 300 细</p>'
                   '<p class="w7">font-weight: 700 粗</p>'
                   '<p class="w9">font-weight: 900 更粗</p>'))

P["f3"] = pv(3, "行高 line-height —— 同一个字号，不同行高",
             """/* 无单位 = 字号的倍数，推荐写法 */
.lh1{line-height:1.1;background:#f2f6fb}
.lh2{line-height:1.8;background:#e7f6ee}
.lh3{line-height:2.6;background:#fdf4e3}""",
             demo=('<p class="lh1">行高 1.1：这几行会挤在一起，读起来很累。'
                   '行高太小是排版里最常见的毛病之一。</p>'
                   '<p class="lh2">行高 1.8：正文最舒服的区间，'
                   '本系列文档正文用的就是这个值。</p>'
                   '<p class="lh3">行高 2.6：太松了，行与行的关系变弱，'
                   '适合诗句或需要留白的场合。</p>'))

P["f4"] = pv(4, "字间距 letter-spacing",
             """.ls1{letter-spacing:0}
.ls2{letter-spacing:.08em}
.ls3{letter-spacing:.28em;text-transform:uppercase;font-size:13px;font-weight:700}""",
             demo=('<p class="ls1">正常字间距 ABCDEFG</p>'
                   '<p class="ls2">加宽一点 ABCDEFG</p>'
                   '<p class="ls3">很宽 ABCDEFG</p>'))

# ---------- 6 颜色与背景 ----------
P["c1"] = pv(5, "文字颜色 color",
             """/* 注意：文字颜色就叫 color，不是 font-color */
.c1{color:#1a1f28}
.c2{color:#1f6feb}
.c3{color:#c0392b}
.c4{color:#17864a}
.c5{color:#8b95a5}""",
             demo=('<p class="c1">#1a1f28 近黑 —— 正文就该用这个</p>'
                   '<p class="c2">#1f6feb 蓝 —— 链接、强调</p>'
                   '<p class="c3">#c0392b 红 —— 错误、危险</p>'
                   '<p class="c4">#17864a 绿 —— 成功</p>'
                   '<p class="c5">#8b95a5 灰 —— 辅助说明</p>'))

P["c2"] = pv(6, "背景色 background-color",
             """.b1{background:#f7f9fc;padding:8px 12px;border-radius:6px}
.b2{background:#e8f1fe;padding:8px 12px;border-radius:6px}
.b3{background:#1a1f28;color:#fff;padding:8px 12px;border-radius:6px}
.b4{background:rgba(31,111,235,.08);padding:8px 12px;border-radius:6px}""",
             demo=('<p class="b1">#f7f9fc 浅灰底</p>'
                   '<p class="b2">#e8f1fe 浅蓝底</p>'
                   '<p class="b3">深底浅字</p>'
                   '<p class="b4">rgba 半透明底（叠在什么背景上都自然）</p>'))

P["c3"] = pv(7, "渐变背景 linear-gradient",
             """/* 135deg = 从左上到右下 */
.g1{background:linear-gradient(135deg,#fffdf5,#fdf3dc)}
.g2{background:linear-gradient(135deg,#1f6feb,#6b46c1);color:#fff}
.g3{background:linear-gradient(90deg,#c9f0d8,#e8f1fe,#ffd9d4)}
.g1,.g2,.g3{padding:14px 16px;border-radius:8px;margin:6px 0}""",
             demo=('<div class="g1">暖色渐变（导航页的星标卡片用的就是这个）</div>'
                   '<div class="g2">蓝紫渐变 + 白字</div>'
                   '<div class="g3">横向三色渐变</div>'))

# ---------- 7 文字装饰 ----------
P["d1"] = pv(8, "text-decoration 五种值",
             """.d1{text-decoration:underline}
.d2{text-decoration:line-through}
.d3{text-decoration:overline}
.d4{text-decoration:underline dotted #c0392b}
.d5{text-decoration:underline wavy #1f6feb}""",
             demo=('<p class="d1">underline 下划线</p>'
                   '<p class="d2">line-through 删除线</p>'
                   '<p class="d3">overline 上划线</p>'
                   '<p class="d4">虚线下划线 + 指定颜色</p>'
                   '<p class="d5">波浪线 wavy</p>'))

P["d2"] = pv(9, "去掉链接下划线（导航菜单起手式）",
             """a.nav-link{
  display:inline-block;margin:4px 8px 4px 0;padding:4px 12px;
  border-radius:6px;text-decoration:none;color:#4b5563;
  transition:background .15s,color .15s;
}
a.nav-link:hover{background:#e8f1fe;color:#1f6feb}""",
             demo=('<a class="nav-link" href="#">首页</a>'
                   '<a class="nav-link" href="#">教程</a>'
                   '<a class="nav-link" href="#">关于</a>'
                   '<p style="font-size:13px;color:#8b95a5;margin-top:6px">'
                   '鼠标移上去试试：没有下划线，靠底色变化表示悬停。</p>'))

P["d3"] = pv(10, "text-shadow 文字阴影（四段式）",
             """/* 水平偏移  垂直偏移  模糊  颜色 */
.ts1{text-shadow:0 1px 2px rgba(0,0,0,.35)}
.ts2{text-shadow:0 0 10px #1f6feb;font-weight:700;color:#1f6feb}
.ts3{text-shadow:2px 2px 0 #c0392b;font-weight:700}
.ts4{text-shadow:-1px -1px 0 #fff,1px 1px 0 #fff;font-weight:700;color:#1f6feb}
.ts5{text-shadow:0 2px 6px rgba(0,0,0,.6)}
.ts5,.ts1,.ts2,.ts3,.ts4{font-size:19px;margin:12px 0}
.dark{background:#1a1f28;padding:14px 16px;border-radius:8px}
.dark p{color:#fff;margin:8px 0}""",
             demo=('<p class="ts1">轻微浮起（最实用）</p>'
                   '<p class="ts2">发光（偏移 0，只有模糊）</p>'
                   '<p class="ts3">硬阴影（复古感）</p>'
                   '<p class="ts4">白描边（偏移不模糊）</p>'
                   '<div class="dark">'
                   '<p class="ts5">深色底上的文字加阴影，读起来更清楚</p>'
                   '</div>'))

# ---------- 8 cursor ----------
P["cu1"] = pv(11, "cursor 常用值 —— 把鼠标移到每一行上",
             """.cu{display:inline-block;min-width:150px;margin:3px 8px 3px 0;
  padding:6px 12px;background:#f2f6fb;border:1px solid #ccd5e3;border-radius:6px;
  font-family:Consolas,monospace;font-size:13px}
.cu1{cursor:pointer}
.cu2{cursor:default}
.cu3{cursor:text}
.cu4{cursor:move}
.cu5{cursor:not-allowed}
.cu6{cursor:grab}
.cu7{cursor:help}
.cu8{cursor:wait}
.cu9{cursor:crosshair}""",
             demo=('<span class="cu cu1">pointer 手形</span>'
                   '<span class="cu cu2">default 箭头</span>'
                   '<span class="cu cu3">text 文本竖线</span>'
                   '<span class="cu cu4">move 移动</span>'
                   '<span class="cu cu5">not-allowed 禁止</span>'
                   '<span class="cu cu6">grab 可抓取</span>'
                   '<span class="cu cu7">help 帮助</span>'
                   '<span class="cu cu8">wait 忙</span>'
                   '<span class="cu cu9">crosshair 十字</span>'))

P["cu2"] = pv(12, "把 div 做成可点击的样子（四件套）",
             """/* 浏览器只给 <a> 和 <button> 自动加手形，
   自己做的「假按钮」要手动补齐这四件事 */
.my-btn{
  cursor:pointer;                    /* ① 手形 */
  background:#1f6feb;color:#fff;     /* ② 看起来是个按钮 */
  padding:9px 20px;border-radius:8px;/* ③ 圆角 */
  transition:background .15s;        /* ④ 悬停有反馈 */
  display:inline-block;
}
.my-btn:hover{background:#1558b8}""",
             demo=('<span class="my-btn">假按钮（其实是 span）</span>'
                   '<p style="font-size:13px;color:#8b95a5;margin-top:8px">'
                   '它没有 href，但因为补了 cursor:pointer，'
                   '鼠标移上去仍然是手形 —— 用户才知道这里能点。</p>'))

BODY = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>HTML 决定「<b>有什么</b>」，CSS 决定「<b>长什么样</b>」。</p>
  <p>这一篇讲 CSS 的<b>语法</b>和一批<b>最常用的属性</b>：
  字体、颜色、文字装饰、阴影、光标。</p>
  <p>凡是有视觉效果的知识点，下面都配了<b>「示例展示」</b> ——
  代码块下面的框里就是真实渲染出来的样子。</p>
  <p><b>选择器的详细语法另有一篇</b>：FE-04《CSS 选择器语法》。</p>
</div>

<h2 id="s1"><span class="n">1</span>CSS 是什么</h2>

<p><b>CSS = Cascading Style Sheets（层叠样式表）</b>。</p>

<table>
<thead><tr><th style="width:24%">词</th><th>含义</th></tr></thead>
<tbody>
<tr><td><b>Style</b></td><td>样式 —— 它只管外观，不管内容</td></tr>
<tr><td><b>Sheet</b></td><td>一张表 —— 一堆样式规则写在一起</td></tr>
<tr><td><b>Cascading</b></td><td><b>层叠</b> —— 多条规则可以同时作用于一个元素，
  按优先级决定谁赢（第 9 节讲）</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">核心思路：选中 + 描述</div>
  <p>CSS 的每一条规则都在回答两个问题：</p>
  <ol>
    <li><b>选中谁？</b>（选择器）</li>
    <li><b>把它怎么样？</b>（属性: 值）</li>
  </ol>
  <p>就这么简单。<b>难的不是语法，是「怎么组合出想要的效果」。</b></p>
</div>

<h2 id="s2"><span class="n">2</span>三种写 CSS 的位置</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">① 行内样式：直接写在标签上</span><span class="cp">复制</span></div><pre>&lt;p style="color: red; font-size: 20px;"&gt;红字&lt;/p&gt;</pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">② 内部样式表：写在 head 里的 style 标签</span><span class="cp">复制</span></div><pre>&lt;head&gt;
  &lt;style&gt;
    p { color: red; }
  &lt;/style&gt;
&lt;/head&gt;</pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">③ 外部样式表：单独一个 .css 文件（推荐）</span><span class="cp">复制</span></div><pre>&lt;!-- HTML 里只写一行链接 --&gt;
&lt;link rel="stylesheet" href="assets/style.css"&gt;

/* style.css 里写规则 */
p { color: red; }</pre></div>

<table>
<thead><tr><th style="width:20%"></th><th style="width:26%">优点</th><th>缺点</th></tr></thead>
<tbody>
<tr><td><b>行内</b></td><td>立刻生效，好调试</td>
    <td><b>优先级最高、难覆盖</b>；改一处要翻 HTML；不能复用</td></tr>
<tr><td><b>内部</b></td><td>一个文件搞定，适合单页小 demo</td>
    <td>多个页面要各写一遍</td></tr>
<tr><td><b>外部</b></td><td><span class="tag g">推荐</span>
      <b>多个页面共用一份</b>，浏览器还会缓存</td>
    <td>多一个文件要管</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">本系列文档用的是哪一种</div>
  <p>一开始是<b>内部样式表</b>，后来改成了<b>外部样式表</b> ——
  每篇一个 <code>assets/fe-0N.css</code>。</p>
  <p>原因很实际：15 篇教程原本各自内嵌一份几乎相同的 CSS，
  总共 28 万字符；抽出来之后只剩 8 万。<b>这就是外部样式表的价值。</b></p>
</div>

<h2 id="s3"><span class="n">3</span>语法：选择器 + 声明块</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">一条规则的解剖</span><span class="cp">复制</span></div><pre><span class="hl-f">.card</span> <span class="arw">{</span>
    <span class="hl-k">color</span>: <span class="hl-n">red</span>;
    <span class="hl-k">font-size</span>: <span class="hl-n">16px</span>;
<span class="arw">}</span>
<span class="arw">└─┬─┘ │  └──┬──┘ └─┬┘ │</span>
<span class="arw">  │   │     │      │  └─ 分号结尾（最后一条可省，但建议都写）</span>
<span class="arw">  │   │     │      └─ 值</span>
<span class="arw">  │   │     └─ 冒号</span>
<span class="arw">  │   └─ 属性名</span>
<span class="arw">  └─ 选择器：选中谁</span></pre></div>

<div class="card warn">
  <div class="card-t">三个最容易写错的地方</div>
  <ol>
    <li><b>用冒号不是等号</b>：<code>color: red</code>，
      不是 <code>color = red</code></li>
    <li><b>用花括号不是圆括号</b>：<code>{ }</code></li>
    <li><b>每条声明末尾要有分号</b>（漏了会让下一条也失效）</li>
  </ol>
  <p><b>好消息</b>：CSS 出错不报错，只是那条不生效 ——
  靠 F12 的 Styles 面板能看到哪条被划掉了。</p>
</div>

<h4>注释</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">CSS 只有一种注释</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 这是 CSS 注释，可以跨行 */</span>
<span class="hl-k">color</span>: red;  <span class="hl-c">/* 也可以写在行尾 */</span>

<span class="hl-c">/* 注意：CSS 里不能用 // ，那是 JS 和 C 的 */</span></pre></div>

<h2 id="s4"><span class="n">4</span>常用选择器</h2>

<table>
<thead><tr><th style="width:24%">写法</th><th style="width:26%">选中什么</th><th>例子</th></tr></thead>
<tbody>
<tr><td class="c">p</td><td>所有 <code>&lt;p&gt;</code> 标签</td>
    <td class="c">p { }</td></tr>
<tr><td class="c">.card</td><td><b>class 含 card 的所有元素</b></td>
    <td class="c">.card { }&nbsp;&nbsp;← 最常用</td></tr>
<tr><td class="c">#header</td><td>id 是 header 的那<b>一个</b></td>
    <td class="c">#header { }</td></tr>
<tr><td class="c">*</td><td>所有元素</td><td class="c">* { }</td></tr>
<tr><td class="c">div p</td><td>div <b>里面</b>的所有 p（后代）</td>
    <td class="c">.card p { }</td></tr>
<tr><td class="c">div &gt; p</td><td>div 的<b>直接子元素</b>里的 p</td>
    <td class="c">.card &gt; p { }</td></tr>
<tr><td class="c">.a, .b</td><td>a <b>或</b> b（并列）</td>
    <td class="c">h1, h2 { }</td></tr>
<tr><td class="c">a:hover</td><td>鼠标<b>悬停</b>时的 a</td>
    <td class="c">.btn:hover { }&nbsp;&nbsp;← FE-07</td></tr>
<tr><td class="c">[href=""]</td><td>属性等于某值的元素</td>
    <td class="c">a[href^="https"] { }</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">选择器另有一篇专讲</div>
  <p>上面这张表够日常用。但属性限定、伪类、伪元素、优先级这些
  <b>值得单独一篇</b> —— 见 <b>FE-04《CSS 选择器语法》</b>，
  那一篇每个知识点都配了示例展示。</p>
</div>

<h2 id="s5"><span class="n">5</span>字体相关</h2>

<h4>font-family 字体回退链</h4>
%(f1)s
<p>写法是<b>一串候选，逗号隔开</b>，浏览器从左往右找第一个有的。
<b>最后一定写一个通用族</b>（<code>sans-serif</code> / <code>monospace</code>），
保证一定落到某个字体。字体名<b>有空格要加引号</b>。</p>

<h4>字号与粗细</h4>
%(f2)s
<table>
<thead><tr><th style="width:22%">属性</th><th>常用值</th></tr></thead>
<tbody>
<tr><td class="c">font-size</td><td class="c">16px　1.2rem　120%</td></tr>
<tr><td class="c">font-weight</td><td class="c">400 正常　700 粗　100~900</td></tr>
<tr><td class="c">font-style</td><td class="c">normal　italic</td></tr>
</tbody>
</table>

<h4>行高 line-height —— 比字号更影响可读性</h4>
%(f3)s
<div class="card key">
  <div class="card-t">为什么不写单位</div>
  <p><code>line-height: 1.8</code> 表示「行高 = 当前字号的 1.8 倍」。</p>
  <p>写成 <code>28.8px</code> 的话，字号一变行高就不匹配了。
  写成倍数，<b>字号怎么变行高都跟着变</b>。</p>
  <p>正文 <b>1.6~1.8</b> 最舒服；标题 1.3 左右。</p>
</div>

<h4>字间距 letter-spacing</h4>
%(f4)s
<table>
<thead><tr><th style="width:26%">字号单位</th><th>相对谁</th></tr></thead>
<tbody>
<tr><td class="c">px</td><td>绝对，最好理解</td></tr>
<tr><td class="c">em</td><td><b>父元素</b>字号，会层层累积</td></tr>
<tr><td class="c">rem</td><td><span class="tag g">推荐</span>
    <b>根元素</b>字号，改一处全站缩放</td></tr>
</tbody>
</table>

<h2 id="s6"><span class="n">6</span>背景与文字颜色</h2>

<h4>文字颜色 <code>color</code></h4>
%(c1)s
<div class="card warn">
  <div class="card-t">新手最常写错的属性名</div>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">font-color: red;        ❌ 没有这个属性
text-color: red;        ❌ 没有这个属性
color: red;             ✅ 文字颜色就是 color
                        （从「墨水的颜色」这个角度命名的）</pre>
</div>

<h4>背景色 background-color</h4>
%(c2)s

<h4>渐变背景 linear-gradient</h4>
%(c3)s

<h2 id="s7"><span class="n">7</span>文字装饰：text-decoration / text-shadow</h2>

<h4>text-decoration 五种值</h4>
%(d1)s

<h4>最常用的其实是 <code>none</code> —— 去掉链接下划线</h4>
%(d2)s

<h4>text-shadow 文字阴影</h4>
%(d3)s
<div class="card key">
  <div class="card-t">四个参数怎么读</div>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">text-shadow: 2px 2px 4px rgba(0,0,0,.4);
             └┬┘ └┬┘ └┬┘ └──────┬──────┘
              │   │   │         └─ 颜色（含透明度）
              │   │   └─ 模糊半径，越大越糊
              │   └─ 垂直偏移（正数往下）
              └─ 水平偏移（正数往右）</pre>
  <p style="margin-top:10px"><b>偏移小、模糊大</b> = 柔和（推荐）；
  <b>偏移大、模糊 0</b> = 生硬。</p>
</div>

<h2 id="s8"><span class="n">8</span>鼠标光标：cursor</h2>

%(cu1)s

<div class="card key">
  <div class="card-t"><code>pointer</code> 这个名字的坑</div>
  <p>它<b>不是</b>「指针箭头」的意思 ——
  它指的是「<b>手形</b>」（像指着东西的手指）。</p>
  <p>想要普通箭头是 <code>default</code>。
  <b>很多人第一次都写反了。</b></p>
</div>

%(cu2)s

<h2 id="s9"><span class="n">9</span>优先级与继承</h2>

<h4>多条规则冲突时谁赢</h4>
<table>
<thead><tr><th style="width:34%">来源</th><th style="width:16%">权重</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">行内 style="..."</td><td>最高</td><td>直接写在标签上，几乎总能赢</td></tr>
<tr><td class="c">#id</td><td>高</td><td>100</td></tr>
<tr><td class="c">.class / :hover / [attr]</td><td>中</td><td>10</td></tr>
<tr><td class="c">标签名 p / div</td><td>低</td><td>1</td></tr>
<tr><td class="c">*</td><td>最低</td><td>0</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">三句话记住</div>
  <ol>
    <li><b>越具体越赢</b>：<code>#id</code> &gt; <code>.class</code> &gt; <code>标签</code></li>
    <li><b>同样具体时，后写的赢</b></li>
    <li><b>行内样式基本无敌</b> —— 所以尽量别用</li>
  </ol>
  <p><b>实用建议</b>：不要为了「赢」而堆选择器
  （<code>#a .b div p</code> 这种）—— 那是维护的噩梦。
  <b>把 class 用对，就不需要斗优先级。</b></p>
</div>

<h4>继承：有些属性会「传下去」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">继承的效果</span><span class="cp">复制</span></div><pre>body {
    <span class="hl-k">font-family</span>: <span class="hl-s">"Microsoft YaHei"</span>, sans-serif;
    <span class="hl-k">color</span>: <span class="hl-n">#1a1f28</span>;
}

<span class="hl-c">/* body 里所有元素都会自动用这个字体和颜色 ——
   不需要给每个 p、每个 div 各写一遍 */</span></pre></div>

<table>
<thead><tr><th style="width:44%">会继承的（文字相关）</th><th>不会继承的（盒子相关）</th></tr></thead>
<tbody>
<tr><td class="c">font-*　color　line-height</td>
    <td class="c">background　border　padding　margin　width</td></tr>
<tr><td class="c">text-align　letter-spacing</td>
    <td class="c">display　position　box-shadow</td></tr>
</tbody>
</table>

<p><b>规律</b>：<b>「文字长什么样」会继承，「盒子怎么摆」不会。</b>
这也符合直觉 —— 字体自然是全篇统一，但每个盒子各管各的边距。</p>

<h2 id="s10"><span class="n">10</span>一页速查</h2>

<table>
<thead><tr><th style="width:36%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>外部样式表</td><td class="c">&lt;link rel="stylesheet" href="x.css"&gt;</td></tr>
<tr><td>选中 class / id</td><td class="c">.card { }　#head { }</td></tr>
<tr><td>选中后代 / 同时选多个</td><td class="c">.card p { }　h1, h2 { }</td></tr>
<tr><td>悬停状态</td><td class="c">.btn:hover { }</td></tr>
<tr><td>注释</td><td class="c">/* 注释 */</td></tr>
<tr><td>字体</td><td class="c">font-family: "Consolas", monospace;</td></tr>
<tr><td>字号 / 粗细</td><td class="c">font-size: 16px;　font-weight: 700;</td></tr>
<tr><td>行高（倍数）</td><td class="c">line-height: 1.8;</td></tr>
<tr><td>字间距</td><td class="c">letter-spacing: 0.02em;</td></tr>
<tr><td>文字色</td><td class="c">color: #1a1f28;</td></tr>
<tr><td>背景色 / 渐变</td>
    <td class="c">background-color: #f7f9fc;　background: linear-gradient(…);</td></tr>
<tr><td>去链接下划线</td><td class="c">text-decoration: none;</td></tr>
<tr><td>删除线 / 波浪线</td>
    <td class="c">line-through　underline wavy #1f6feb</td></tr>
<tr><td>文字阴影</td><td class="c">text-shadow: 0 1px 2px rgba(0,0,0,.3);</td></tr>
<tr><td>手形光标</td><td class="c">cursor: pointer;</td></tr>
<tr><td>禁止光标</td><td class="c">cursor: not-allowed;</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的五句话</div>
  <ol>
    <li><b>CSS = 选中谁 + 把它怎么样</b>：
      <code>选择器 { 属性: 值; }</code>，冒号不是等号，末尾要分号。</li>
    <li><b>九成时间用 <code>.class</code> 选</b>；
      行内样式优先级最高但最难维护，别用。</li>
    <li><b><code>font-family</code> 写一串候选</b>，最后兜一个
      <code>sans-serif</code> / <code>monospace</code>；
      <b><code>line-height</code> 不写单位</b>（写倍数）。</li>
    <li><b>文字色是 <code>color</code></b>（不是 <code>font-color</code>）；
      <code>cursor: pointer</code> 是<b>手形</b>，不是箭头。</li>
    <li><b>文字属性会继承、盒子属性不会</b>；
      同样具体时<b>后写的赢</b>。</li>
  </ol>
</div>"""

if __name__ == "__main__":
    body = BODY
    for k, v in P.items():
        body = body.replace("%(" + k + ")s", v)
    left = [ln.strip()[:60] for ln in body.split("\n") if "%(" in ln]
    if left:
        print("!! 未替换:"); [print("   " + x) for x in left[:6]]; raise SystemExit(1)
    print(build("fe-03.html", "FE-03", "CSS 入门", body, TOC))
