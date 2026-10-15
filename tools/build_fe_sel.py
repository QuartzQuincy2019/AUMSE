# -*- coding: utf-8 -*-
"""FE-04《CSS 选择器语法》—— 要求：杜绝啰嗦，简明扼要地给例子。

每个知识点都是「一句话 + 代码 + 示例展示」。
"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build
from fe_kit import pv, code

TOC = """  <a href="#s1">1 · 选择器是什么</a>
  <a href="#s2">2 · 基本选择器</a>
  <a href="#s3">3 · 组合：并集与后代</a>
  <a href="#s4">4 · 属性限定 [href=""]</a>
  <a href="#s5">5 · 伪类</a>
  <a href="#s6">6 · 伪元素</a>
  <a href="#s7">7 · 优先级速查</a>
  <a href="#s8">8 · 一页速查</a>"""

# 每个示例都用同一段 HTML，方便对比不同选择器的作用范围
DEMO = ("""<div class="box">
  <p>第一段</p>
  <p class="hi">第二段（class="hi"）</p>
  <p data-t="uniq">第三段（这一段被 #uniq 选中）</p>
  <p>第四段</p>
</div>""")

BODY = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p><b>选择器 = 「选中谁」</b>。CSS 的前半句。</p>
  <p>下面每一条都是<b>一句话 + 代码 + 示例展示</b>，
  示例框里的高亮段落就是被选中的那个。</p>
  <p><b>本页所有示例共用同一段 HTML</b>，方便对照不同选择器的作用范围：</p>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">&lt;div class="box"&gt;
  &lt;p&gt;第一段&lt;/p&gt;
  &lt;p class="hi"&gt;第二段（class="hi"）&lt;/p&gt;
  &lt;p data-t="uniq"&gt;第三段&lt;/p&gt;
  &lt;p&gt;第四段&lt;/p&gt;
&lt;/div&gt;</pre>
</div>

<h2 id="s1"><span class="n">1</span>选择器是什么</h2>

<p>CSS 规则的形状固定为 <b>选择器 + 声明块</b>：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">结构</span><span class="cp">复制</span></div><pre><span class="hl-p">选择器</span> {
    属性: 值;
}</pre></div>

<p>选择器写错了，CSS <b>不报错</b> —— 那条规则只是不生效。所以这一篇值得记牢。</p>

<h2 id="s2"><span class="n">2</span>基本选择器</h2>

<h4>标签选择器 —— 选中所有该标签</h4>
%(p1)s

<h4>类选择器 <code>.名字</code> —— 选中 class 含它的元素（最常用）</h4>
%(p2)s

<h4>id 选择器 <code>#名字</code> —— 选中唯一那一个</h4>
%(p3)s

<h4>通配符 <code>*</code> —— 选中所有元素</h4>
%(p4)s

<h2 id="s3"><span class="n">3</span>组合：并集与后代</h4>

<h4>并集：逗号 —— 同时选中多种</h4>
%(p5)s

<h4>后代：空格 —— 里面的所有层级</h4>
%(p6)s

<h4>直接子元素：<code>&gt;</code> —— 只要亲儿子，不含孙子</h4>
%(p7)s

<h4>相邻兄弟：<code>+</code> —— 紧跟在后面的那一个</h4>
%(p8)s

<h4>通用兄弟：<code>~</code> —— 后面所有同级</h4>
%(p9)s

<h2 id="s4"><span class="n">4</span>属性限定 <code>[href=""]</code></h2>

<p>这一节很实用 —— <b>按属性挑元素</b>，尤其是链接。</p>

<h4>有某个属性</h4>
%(p10)s

<h4>属性等于某值</h4>
%(p11)s

<h4>属性以某串开头 <code>^=</code></h4>
%(p12)s

<h4>属性以某串结尾 <code>$=</code> —— 常用于挑文件类型</h4>
%(p13)s

<h4>属性包含某串 <code>*=</code></h4>
%(p14)s

<h4>更实用的例子：区分外链和锚点</h4>
%(p15)s

<h2 id="s5"><span class="n">5</span>伪类</h2>

<p>伪类选中「<b>处在某种状态</b>」的元素，写法是 <code>:</code> + 状态名。</p>

<h4>悬停 / 按下 / 聚焦</h4>
%(p16)s
<p><b>把鼠标移到上面试试。</b></p>

<h4>结构伪类：第一个、最后一个、第 n 个</h4>
%(p17)s

<h4>表格斑马纹 —— <code>:nth-child(2n)</code> 最典型的用处</h4>
%(p18)s

<h4>取反 <code>:not()</code></h4>
%(p19)s

<h2 id="s6"><span class="n">6</span>伪元素</h2>

<p>伪元素用 <code>::</code>（两个冒号），选中的是<b>元素的一部分</b>，
或者<b>凭空造一个</b>。</p>

<h4>首字放大 / 首行</h4>
%(p20)s

<h4>前后插入内容 <code>::before</code> / <code>::after</code></h4>
%(p21)s
<p><b><code>content</code> 不能省</b>，哪怕写空字符串。忘了它伪元素就不出现。</p>

<h4>选中文字的颜色 <code>::selection</code></h4>
%(p22)s

<h2 id="s7"><span class="n">7</span>优先级速查</h4>

<table>
<thead><tr><th style="width:34%">选择器</th><th style="width:16%">权重</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">行内 style=""</td><td>最高</td><td>几乎总能赢</td></tr>
<tr><td class="c">#id</td><td>100</td><td>越具体越赢</td></tr>
<tr><td class="c">.class　:hover　[attr]</td><td>10</td><td>同一档</td></tr>
<tr><td class="c">标签名　::before</td><td>1</td><td>最低</td></tr>
<tr><td class="c">*</td><td>0</td><td>不增加权重</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">只用两句话</div>
  <ol>
    <li><b>越具体越赢</b>：<code>#id</code> &gt; <code>.class</code> &gt; <code>标签</code></li>
    <li><b>同样具体时，后写的赢</b></li>
  </ol>
  <p>不要为了「赢」而把选择器堆得又长又深 ——
  <b>把 class 用对，就不需要斗优先级。</b></p>
</div>

<h2 id="s8"><span class="n">8</span>一页速查</h2>

%(p23)s

<table>
<thead><tr><th style="width:34%">写法</th><th>选中</th></tr></thead>
<tbody>
<tr><td class="c">p</td><td>所有 <code>&lt;p&gt;</code></td></tr>
<tr><td class="c">.hi</td><td>class 含 hi 的</td></tr>
<tr><td class="c">#uniq</td><td>id 是 uniq 的那一个</td></tr>
<tr><td class="c">*</td><td>所有元素</td></tr>
<tr><td class="c">.a, .b</td><td>a <b>或</b> b</td></tr>
<tr><td class="c">.box p</td><td>.box 里的所有后代 p</td></tr>
<tr><td class="c">.box &gt; p</td><td>.box 的直接子元素 p</td></tr>
<tr><td class="c">p + p</td><td>紧跟在 p 后面的那个 p</td></tr>
<tr><td class="c">p ~ p</td><td>p 后面所有同级 p</td></tr>
<tr><td class="c">[href]</td><td>带 href 属性的</td></tr>
<tr><td class="c">[href="a.html"]</td><td>href 正好等于 a.html</td></tr>
<tr><td class="c">[href^="https"]</td><td>href 以 https 开头</td></tr>
<tr><td class="c">[href$=".pdf"]</td><td>href 以 .pdf 结尾</td></tr>
<tr><td class="c">[href*="ume"]</td><td>href 里含 ume</td></tr>
<tr><td class="c">a:hover</td><td>鼠标悬停时的 a</td></tr>
<tr><td class="c">a:active</td><td>正被按下的 a</td></tr>
<tr><td class="c">input:focus</td><td>获得焦点的输入框</td></tr>
<tr><td class="c">li:first-child</td><td>第一个 li</td></tr>
<tr><td class="c">li:last-child</td><td>最后一个 li</td></tr>
<tr><td class="c">tr:nth-child(2n)</td><td>偶数行</td></tr>
<tr><td class="c">li:not(.on)</td><td>不是 .on 的 li</td></tr>
<tr><td class="c">p::before</td><td>在 p 内容前插入</td></tr>
<tr><td class="c">p::after</td><td>在 p 内容后插入</td></tr>
<tr><td class="c">::selection</td><td>被选中的文字</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的四句话</div>
  <ol>
    <li><b>日常九成时间用 <code>.class</code></b>；<code>#id</code> 留给唯一锚点。</li>
    <li><b>空格是「后代」，<code>&gt;</code> 是「亲儿子」</b>，
      <code>+</code>/<code>~</code> 是「兄弟」—— 别混。</li>
    <li><b><code>[href^="https"]</code> / <code>[href$=".pdf"]</code> 能按属性挑元素</b>，
      做外链标记、文件类型图标非常好用。</li>
    <li><b>优先级：越具体越赢；同样具体时后写的赢</b>。
      与其堆选择器，不如把 class 起好名字。</li>
  </ol>
</div>"""

# ---------------------------------------------------------------------
# 各示例：同一段 HTML 在不同选择器下的效果
# ---------------------------------------------------------------------
BOX = r"""<div class="box">
  <p>第一段</p>
  <p class="hi">第二段（class="hi"）</p>
  <p data-t="uniq">第三段（这一段被 #uniq 选中）</p>
  <p>第四段</p>
</div>"""

# 让被选中的段落一目了然：统一给 .box 一点基础样式
MARK = (".box{border:1px dashed #ccd5e3;border-radius:8px;padding:10px 14px;"
        "background:#fafbfd}\n"
        ".box p{margin:4px 0;padding:3px 8px;border-radius:5px}\n")

def uni_id(html, n):
    """把示例里的 id="uniq" 换成 id="uniq<N>"。

    同一页有十几个示例，每个都用 demo 里的 id="uniq" 的话，
    整页就会出现十几个重复 id —— HTML 不允许，检查器也会报。
    CSS 示例里写的 #uniq 由 pv() 的 id 替换逻辑同步改掉。
    """
    return html.replace('id="uniq"', 'id="uniq%d"' % n)


def css_code(rule, note=""):
    body = MARK + rule
    if note:
        body = body + "\n\n" + note
    return body


PVS = {}
PVS["p1"] = pv(1, "标签选择器",
               "/* 选中上面那 4 个 p */\np{background:#ffe9a8}",
               demo=BOX)
PVS["p2"] = pv(2, "类选择器",
               '/* 只有 class="hi" 的那一个 */\n.hi{background:#c9f0d8}',
               demo=BOX)
PVS["p3"] = pv(3, "id 选择器",
               '/* 只有带这个标记的那一个 */\n[data-t="uniq"]{background:#d8e6ff}',
               demo=BOX)
PVS["p4"] = pv(4, "通配符",
               "/* 框里所有元素加一圈虚线 */\n*{outline:1px dashed #e08a2e;"
               "outline-offset:1px}",
               demo=BOX)
PVS["p5"] = pv(5, "并集（逗号）",
               '/* 逗号 = 或。这里两个都中 */\n'
               '.hi, [data-t="uniq"]{background:#e6d8ff}',
               demo=BOX)
PVS["p6"] = pv(6, "后代（空格）",
               "/* .box 里面的所有 p（含更深层级） */\n"
               ".box p{background:#ffd9d4}",
               demo=BOX)
PVS["p7"] = pv(7, "直接子元素（&gt;）",
               ".box > p{background:#cfe9ff;border-left:3px solid #1f6feb}",
               demo=(r"""<div class="box">
  <p>直接子元素（中）</p>
  <div>
    <p>孙子元素（不中，因为不是直接子元素）</p>
  </div>
</div>"""))
PVS["p8"] = pv(8, "相邻兄弟（+）",
               "/* 紧跟在另一个 p 后面的 p（即第 2、3、4 个） */\n"
               "p + p{background:#ffe0b3}",
               demo=BOX)
PVS["p9"] = pv(9, "通用兄弟（~）",
               "/* .hi 后面所有同级 p */\n.hi ~ p{background:#c9f0d8}",
               demo=BOX)

LINKBOX = (r"""<div class="box">
  <a href="/local/page.html">站内链接</a><br>
  <a href="https://example.com">外站链接 https</a><br>
  <a href="report.pdf">PDF 文件</a><br>
  <a href="#top">本页锚点</a><br>
  <a>没有 href 的 a</a>
</div>""")

def linkcss(rule):
    """把要演示的规则提权一层，保证它压过示例框的基础样式。

    坑：基础规则 `.box a` 的权重是 (0,1,1)，而 `[href]` 只有 (0,1,0) ——
    基础样式会反过来压住「要演示的规则」，示例就看不出效果。
    所以给要演示的规则加一层 `.box`：`.box [href]` = (0,2,0)，保证它赢。
    括号里的选择器本身没改，讲的还是同一个知识点。
    """
    bumped = []
    for line in rule.split("\n"):
        s = line.strip()
        if (not s) or s.startswith("/*") or s.startswith(".") or s.startswith(".box"):
            bumped.append(line)          # 注释、以及已带类名前缀的原样保留
        else:
            bumped.append(".box " + line)
    return "\n".join(bumped)

PVS["p10"] = pv(10, '有某属性：[href]',
                linkcss('/* 只要带 href 就中 */\n[href]{background:#ffe0b3}'),
                demo=LINKBOX)
PVS["p11"] = pv(11, '属性等于：[href="report.pdf"]',
                linkcss('/* 正好等于这个值 */\n[href="report.pdf"]'
                        '{background:#ffd9d4;font-weight:700}'),
                demo=LINKBOX)
PVS["p12"] = pv(12, '以某串开头：[href^="https"]',
                linkcss('/* ^= 开头 */\n[href^="https"]'
                        '{background:#c9f0d8;font-weight:700}'),
                demo=LINKBOX)
PVS["p13"] = pv(13, '以某串结尾：[href$=".pdf"]',
                linkcss('/* $= 结尾 */\n[href$=".pdf"]'
                        '{background:#e6d8ff;font-weight:700}'),
                demo=LINKBOX)
PVS["p14"] = pv(14, '包含某串：[href*="ume"]',
                linkcss('/* *= 包含 */\n[href*="ume"]'
                        '{background:#cfe9ff;font-weight:700}'),
                demo=(r"""<div class="box">
  <a href="/ume/about.html">/ume/about.html</a><br>
  <a href="/other/about.html">/other/about.html</a>
</div>"""))
PVS["p15"] = pv(15, "实战：外链自动加标记",
                linkcss('/* 外链后面自动加一个 ↗ */\n'
                        '[href^="http"]::after{content:" ↗";color:#1f6feb;font-weight:700}\n'
                        '/* 锚点链接换个底色 */\n'
                        '[href^="#"]{background:#e6d8ff}'),
                demo=LINKBOX)

PVS["p16"] = pv(16, "悬停 / 按下 / 聚焦",
                (".btn:hover{background:#1558b8}\n"
                 ".btn:active{transform:scale(.95)}\n"
                 ".inp:focus{box-shadow:0 0 0 3px rgba(31,111,235,.3)}"),
                demo=(r"""<span class="btn">鼠标移上来</span>
<span class="btn">按下去试试</span>
<div><input class="inp" placeholder="点这里获得焦点"></div>"""))

NUMLIST = (r"""<ul class="nl">
  <li>第 1 项</li><li>第 2 项</li><li>第 3 项</li>
  <li>第 4 项</li><li>第 5 项</li><li>第 6 项</li>
</ul>""")

PVS["p17"] = pv(17, ":first-child / :last-child / :nth-child(3)",
                (".nl li:first-child{background:#c9f0d8;font-weight:700}\n"
                 ".nl li:last-child{background:#ffd9d4;font-weight:700}\n"
                 ".nl li:nth-child(3){background:#ffe0b3;font-weight:700}"),
                demo=NUMLIST)

TBL = (r"""<table class="zt">
  <tr><th>名字</th><th>血量</th></tr>
  <tr><td>Archer</td><td>100</td></tr>
  <tr><td>Mage</td><td>80</td></tr>
  <tr><td>Knight</td><td>150</td></tr>
  <tr><td>Rogue</td><td>90</td></tr>
</table>""")

PVS["p18"] = pv(18, "斑马纹：tr:nth-child(2n)",
                "/* 偶数行上浅灰底 */\n.zt tr:nth-child(2n){background:#f7f9fc}",
                demo=TBL)

PVS["p19"] = pv(19, "取反：li:not(.on)",
                (".nl li:not(.on){color:#8b95a5;text-decoration:line-through}\n"
                 ".nl li.on{background:#c9f0d8;font-weight:700}"),
                demo=(r"""<ul class="nl">
  <li class="on">这一项是 .on（保留）</li>
  <li>没有 .on，被划掉</li>
  <li>没有 .on，被划掉</li>
</ul>"""))

PVS["p20"] = pv(20, "首字放大：p::first-letter",
                (".fx::first-letter{font-size:34px;font-weight:700;color:#1f6feb;"
                 "float:left;line-height:1;margin:2px 8px 0 0}"),
                demo='<p class="fx">这一段的第一个字会被放大。首字下沉是排版里很常见的手法，'
                     '用一条 ::first-letter 就能做到。</p>')

PVS["p21"] = pv(21, "前后插入：::before / ::after",
                (".tagp::before{content:\"● \";color:#17864a}\n"
                 ".li2::after{content:\"（已完成）\";color:#17864a;font-size:12px;"
                 "margin-left:6px}"),
                demo=('<span class="tagp">带圆点的标签</span>\n'
                      '<div class="li2">任务一</div>\n'
                      '<div class="li2">任务二</div>'))

PVS["p22"] = pv(22, "选中文字的颜色：::selection",
                ("/* 用鼠标拖选下面这段文字 */\n"
                 ".sel::selection{background:#ffe0b3;color:#8a5e0c}"),
                demo='<p class="sel">用鼠标拖选这一段文字，看到选中背景变成了暖黄色。'
                     '::selection 就是干这个的。</p>')

PVS["p23"] = pv(23, "一页速查的现场版",
                (".s8 p:nth-child(2n){background:#f2f6fb}\n"
                 ".s8 p:first-child{background:#c9f0d8}\n"
                 ".s8 p:last-child{background:#ffd9d4}\n"
                 ".s8 p:hover{background:#ffe0b3}"),
                demo=('<div class="s8">'
                      '<p>第一个（:first-child 绿）</p>'
                      '<p>第二个（偶数行 :nth-child(2n) 灰）</p>'
                      '<p>第三个</p>'
                      '<p>第四个（偶数行）</p>'
                      '<p>最后一个（:last-child 红）</p>'
                      '<p>鼠标移到任意一行会变黄（:hover）</p>'
                      '</div>'))

if __name__ == "__main__":
    # 注意：BODY 里有 CSS 的 %（比如 width:50%），绝不能用 % 格式化 —— 用 replace
    body = BODY
    for k, v in PVS.items():
        body = body.replace("%(" + k + ")s", v)
    left = [ln for ln in body.split("\n") if "%(" in ln and ")s" in ln]
    if left:
        print("!! 还有未替换的占位符:")
        for ln in left[:8]:
            print("   " + ln.strip()[:80])
        raise SystemExit(1)
    print(build("fe-04.html", "FE-04", "CSS 选择器语法", body, TOC))
