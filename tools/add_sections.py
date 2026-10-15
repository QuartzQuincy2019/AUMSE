# -*- coding: utf-8 -*-
"""1) 08《C 风格字符串》第 6 节：把「宏与常量」那段改写为 C 的说法，
      并对涉及 C++ 的部分加显眼标识。
   2) 09-F04 增补「变长编码」的设计思路与历史（详解）。"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

CPP_CSS = """
/* ===== C++ 内容标识 ===== */
.cpp-badge{
  display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;
  font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.04em;
  background:#7c3aed;color:#fff;vertical-align:1px;
}
.cpp-note{
  border:1px solid #ded0f7;border-left:4px solid #7c3aed;background:var(--violet-soft);
  border-radius:0 9px 9px 0;padding:11px 16px;margin:14px 0;font-size:14px;
}
.cpp-note b{color:#7c3aed}
.cpp-note .t2{font-weight:700;color:#7c3aed;margin-bottom:4px}
.cpp-note p:last-child{margin-bottom:0}
"""

# =====================================================================
# 1) doc 08
# =====================================================================
p8 = os.path.join(ROOT, "_ds_08_C风格字符串.html")
with io.open(p8, encoding="utf-8") as fh:
    t = fh.read()

if "cpp-badge" not in t:
    t = t.replace("</head>", "<style>" + CPP_CSS + "</style>\n</head>", 1)

OLD = '''<h4>③ 避免头文件被重复包含</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">include guard</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifndef</span> UME_FONT_H
<span class="hl-p">#define</span> UME_FONT_H

<span class="hl-c">/* 头文件内容写在这里 */</span>

<span class="hl-p">#endif</span></pre></div>
<p>或者用更省事的 <code>#pragma once</code>。
这是每个头文件都该有的第一行和最后一行，08-F03 会讲为什么需要它。</p>

<h4>④ 构建模式判断</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">区分调试版与发布版</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifdef</span> QT_NO_DEBUG
    <span class="hl-c">/* 发布版：不做耗时检查 */</span>
<span class="hl-p">#else</span>
    <span class="hl-c">/* 调试版：加额外校验 */</span>
<span class="hl-p">#endif</span></pre></div>'''

NEW = '''<h4>③ 别用宏定义常量，用 <code>const</code></h4>
<p>新手常写 <code>#define MAX_LEN 100</code> 来表示「最大长度」。
在 C 里<b>更好的写法是 <code>const</code></b>：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> MAX_LEN <span class="hl-n">100</span>        <span class="hl-c">/* ⚠ 能跑，但没有类型、调试时看不到 */</span>

<span class="hl-k">const</span> <span class="hl-k">int</span> kMaxLen = <span class="hl-n">100</span>;   <span class="hl-c">/* ✅ C 里推荐：有类型、能调试、有作用域 */</span>

<span class="hl-k">char</span> buf[kMaxLen];</pre></div>

<table>
<thead><tr><th style="width:26%"></th><th><code>#define</code></th><th><code>const</code></th></tr></thead>
<tbody>
<tr><td><b>有没有类型</b></td><td><span class="tag r">没有</span></td><td><span class="tag g">有</span></td></tr>
<tr><td><b>调试能看到吗</b></td><td>看不到（编译前就没了）</td><td>能，是个真变量</td></tr>
<tr><td><b>有作用域吗</b></td><td>没有，从定义处管到文件尾</td><td>有，和普通变量一样</td></tr>
<tr><td><b>编译器会检查吗</b></td><td>基本不检查</td><td>会做类型检查</td></tr>
</tbody>
</table>

<div class="cpp-note">
  <div class="t2">关于宏：见 08-F02（那里讲的是环境变量）</div>
  <p>「宏」这个词在命令行和编译器里都出现，但指的是不同的东西。
  <b>配开发环境时说的「宏」是环境变量</b>（<code>%PATH%</code> 这类），
  已在 <b>08-F02《相对文件路径与宏》</b>里讲。</p>
  <p>编译器里的 <code>#define</code> 是预处理的文字替换，
  <b>不属于本讲范围</b>；用到它的场合（比如头文件保护）
  在 <b>08-F03《编译与链接》</b>里讲。</p>
</div>'''

if OLD in t:
    t = t.replace(OLD, NEW, 1)
    print("08：③④ 小节 → const 与说明框")
else:
    print("08：未匹配（检查）")

with io.open(p8, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

# =====================================================================
# 2) F04 增补「变长编码」的设计思路与历史
# =====================================================================
p4 = os.path.join(ROOT, "_ds_09_F04_Unicode和编码.html")
with io.open(p4, encoding="utf-8") as fh:
    t = fh.read()

# 目次补一条
t = t.replace('  <a href="#s3">3 · UTF-8 的字节规律</a>',
              '  <a href="#s3">3 · UTF-8 的字节规律</a>\n'
              '  <a href="#s3b" class="sub">3.5 为什么设计成变长（含历史）</a>',
              1)

ANCHOR = '<h4>自己打印出来看</h4>'
if ANCHOR not in t:
    # 退回用别的锚
    ANCHOR = '<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">自己打印出来看'

ADD = r'''<h3 id="s3b">3.5 为什么设计成变长？—— 设计思路与历史</h3>

<p>前面那张表里藏着一个「故意为之」的设计。这一节讲清它为什么这样做，
以及它是怎么从历史里长出来的。</p>

<h4>先看三种「朴素方案」各自的毛病</h4>

<div class="encs">
  <div class="c u8">
    <div class="h">方案 A：定长 4 字节</div>
    <div class="note">
      每个字符都用 4 字节（这就是 UTF-32）。<br>
      <b>好处</b>：定位极简单 —— 第 n 个字符就在第 4n 字节。<br>
      <b>毛病</b>：<b>太浪费</b>。一篇纯英文文档体积直接<b>变 4 倍</b>，
      而英文内容占互联网的绝大多数。
    </div>
  </div>
  <div class="c u16">
    <div class="h">方案 B：定长 2 字节</div>
    <div class="note">
      每个字符 2 字节（UTF-16 的早期想法）。<br>
      <b>好处</b>：比 4 字节省一半。<br>
      <b>毛病</b>：<b>装不下</b>。Unicode 有 100 多万个码位，
      2 字节最多 65536 个 —— 表情、古文字、罕用汉字全没地方放。
    </div>
  </div>
  <div class="c u32">
    <div class="h">方案 C：变长</div>
    <div class="note">
      按码位大小决定用几个字节（UTF-8 走的就是这条）。<br>
      <b>好处</b>：英文 1 字节、汉字 3 字节、表情 4 字节，
      <b>又省又能装</b>。<br>
      <b>毛病</b>：不能再用「第 n 个字符 = 第 k 字节」直接跳转，
      得从头数。
    </div>
  </div>
</div>

<div class="card key">
  <div class="card-t">变长编码的核心取舍</div>
  <p><b>用「随机访问变难」换「空间大幅节省」，并且能表示无限多的码位。</b></p>
  <p>这个取舍在当年是对的：网络传输和磁盘存储是瓶颈，
  而「从字符串开头数到第 n 个字符」这种操作相对少见。</p>
</div>

<h4>为什么是 1 / 2 / 3 / 4 字节，而不是别的分法</h4>

<p>关键在<b>「前面几个 1」当标志位</b>。先看 UTF-8 的字节形状：</p>

<table>
<thead><tr><th style="width:18%">字节数</th><th style="width:34%">字节的二进制形状</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">1</td><td class="c">0xxxxxxx</td>
    <td>最高位是 <b>0</b> → 说明「这是一个单字节字符」</td></tr>
<tr><td class="c">2</td><td class="c">110xxxxx 10xxxxxx</td>
    <td>开头 <b>110</b> → 两字节的第 1 个</td></tr>
<tr><td class="c">3</td><td class="c">1110xxxx 10xxxxxx 10xxxxxx</td>
    <td>开头 <b>1110</b> → 三字节的第 1 个</td></tr>
<tr><td class="c">4</td><td class="c">11110xxx 10xxxxxx 10xxxxxx 10xxxxxx</td>
    <td>开头 <b>11110</b> → 四字节的第 1 个</td></tr>
<tr><td class="c">后续</td><td class="c">10xxxxxx</td>
    <td><b>所有后续字节都以 10 开头</b>，用来看家</td></tr>
</tbody>
</table>

<p>这套形状带来三个非常实用的性质：</p>

<div class="flow">
  <div class="s"><div class="t">① 不会认错</div>
    <div class="d">看到 <code>10</code> 开头就知道「这是尾巴」，
      看到 <code>0</code> 开头就知道「这是新字符」</div></div>
  <div class="s"><div class="t">② 能自同步</div>
    <div class="d">就算从中间随便一个字节开始读，
      最多跳几个字节就能对上边界，<b>不会一直错下去</b></div></div>
  <div class="s"><div class="t">③ 英文完全兼容</div>
    <div class="d">ASCII 都是 <code>0xxxxxxx</code>，
      和 UTF-8 的单字节形式<b>一模一样</b></div></div>
</div>

<div class="card tip">
  <div class="card-t">性质③ 才是 UTF-8 赢的关键</div>
  <p>因为 <b>UTF-8 下的纯 ASCII 内容，字节和几十年前的 ASCII 完全相同</b>。</p>
  <p>这意味着：一个存英文的旧文件，用 UTF-8 打开<b>照样正确</b>。
  于是从旧编码迁移到 UTF-8 <b>不需要一次性转换所有文件</b> ——
  可以一个文件一个文件慢慢来，新旧混着用也不炸。</p>
  <p>对比一下 UTF-16：它在英文里会插入一堆 <code>00</code> 字节，
  旧程序读它会看到满屏乱码。<b>兼容性差，是 UTF-16 在文件与网络上输给
  UTF-8 的主要原因。</b></p>
</div>

<h4>来历：这一切是怎么发生的</h4>

<p>按时间线看，能明白为什么会有「变长」这个想法。</p>

<table>
<thead><tr><th style="width:20%">时期</th><th style="width:26%">方案</th><th>要解决的问题</th></tr></thead>
<tbody>
<tr><td><b>1960s</b></td><td class="c">ASCII（7 位）</td>
    <td>只有 128 个位置 —— <b>够英文用</b>，但装不下任何其他语言</td></tr>
<tr><td><b>1980s</b></td><td class="c">各种「代码页」</td>
    <td>每种语言各占一个 256 格的表（GBK、Shift-JIS、Latin-1…）。
      <b>毛病：同一个字节在不同代码页里是不同字</b> ——
      这就是「乱码」的来源</td></tr>
<tr><td><b>1988–1991</b></td><td class="c">Unicode 诞生</td>
    <td>提出「<b>给全世界所有字符统一编号</b>」，一个字符一个码位。
      但一开始倾向于「码位就是 16 位」（那时以为字符总数不到 65536）</td></tr>
<tr><td><b>1992</b></td><td class="c">UTF-8 出现</td>
    <td>在 Unix 社区设计出来，<b>目标很明确：既要能装全世界，
      又要和 ASCII 二进制兼容</b>，好让已有的英文系统平滑过渡</td></tr>
<tr><td><b>1996 起</b></td><td class="c">UTF-16 定型</td>
    <td>码位突破了 65536（发现了更多汉字和古文字），
      于是 UTF-16 改成「基本用 2 字节，超出范围时用 4 字节」——
      <b>也成了变长</b></td></tr>
<tr><td><b>2000s 之后</b></td><td class="c">UTF-8 成为主流</td>
    <td>网页、Linux、JSON、源码文件……<b>事实标准</b>。
      Windows 内部仍用 UTF-16，这正是 Qt 里 <code>QString</code>
      也是 UTF-16 的原因</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">三条能记住的结论</div>
  <ol>
    <li><b>变长是为了省空间：</b>不让英文为「全世界字符」买单。</li>
    <li><b>变长必须「自己认得出边界」：</b>
      靠 <code>0</code> / <code>110</code> / <code>1110</code> /
      <code>11110</code> 这些前缀，让程序不看上下文也能切分字符。</li>
    <li><b>兼容 ASCII 是它胜出的决定性因素：</b>
      能用最小的代价把旧世界接过来 ——
      技术方案能不能推广，常常取决于这一点，而不只是它「设计得多好」。</li>
  </ol>
</div>

<h4>回到我们的代码</h4>
<p>现在再看前面那三行输出，含义就清楚了：</p>
<div class="out-wrap"><div class="cap">再看一次这些字节</div><pre>ASCII 里的 A (1 字节): 41                     ← 0x41 = 01000001，最高位 0
e 带音标 (2 字节): C3 A9                      ← C3 = 11000011，开头 110
中 (3 字节): E4 B8 AD                         ← E4 = 11100100，开头 1110
蒙文 MA (3 字节): E1 A0 AE                     ← E1 = 11100001，开头 1110
笑脸 (4 字节): F0 9F 98 80                     ← F0 = 11110000，开头 11110</pre></div>
<p>每个字符的<b>第一个字节</b>都在告诉你「后面还有几个字节」——
这就是变长编码能工作起来的全部秘密。</p>

'''

if ANCHOR in t:
    t = t.replace(ANCHOR, ADD + ANCHOR, 1)
    print("F04：已加入 3.5 变长编码（设计思路与历史）")
else:
    print("F04：未找到插入锚点（检查）")

t = t.replace('文中所有字节值均使用 gcc 13.1.0',
              '文中所有字节值与二进制形状均使用 gcc 13.1.0', 1)

with io.open(p4, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("")
print("08 字符数 %d    F04 字符数 %d" % (len(t if False else ""), len(t)))
