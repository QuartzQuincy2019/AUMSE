# -*- coding: utf-8 -*-
"""M03 §11 去掉取址运算符；M04 回扣处补「多维数组为什么只有第一维可省」。

用户要求
    1. M03 第 11 节不要涉及取址运算符。
    2. M04 在对数组的类型名方面进行回扣时，添加
       「为什么多维数组在声明时，只有第一维的大小可以不指定」的小话题。

M03 的改法
    原 §11 里有一张表对比 `arr` 与 `&arr[0]` 的步长 —— 那用到了 &。
    改成完全不碰 &：讲清楚
        ① sizeof 为什么是 16（而不是 4）
        ② 为什么不能 int x = arr;
        ③ 它是 M04 的入口（数组名会退化）
    步长那一点本来 §10 已经讲过（那里用的是 &，属于 §10 的内容，不动）。

M04 的补充
    在回扣的两张卡之后加一个小话题：
    为什么 int a[][3] 合法、int a[][] 不合法、int a[2][] 也不合法。
    原因是编译器必须知道「一个元素有多大」才能算出 a[i] 在哪；
    第一维是「有几个」，可以由初始化列表推出来，所以能省。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

NEW_S11 = """<h2 id="s11"><span class="n">11</span>数组的类型是 <code>int[n]</code></h2>

<p>前面一直写 <code>int arr[4]</code>。很容易以为 <code>arr</code> 的类型就是
<code>int</code> —— <b>不是。</b></p>

<div class="card key">
  <div class="card-t">完整类型</div>
  <p><code>int arr[4];</code> 里，<code>arr</code> 的完整类型是
  <b><code>int[4]</code></b>，读作「<b>4 个 int 组成的数组</b>」。</p>
  <p>它不是一个 <code>int</code>，而是<b>4 个 int 挨在一起</b>构成的
  <b>一个新东西</b>。方括号里的数字是类型的一部分，不能省。</p>
</div>

<p>用 <code>sizeof</code> 一验就清楚：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">sizeof 看的是「类型」，不是「里面的值」</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-k">int</span>  arr[<span class="hl-n">4</span>];      <span class="hl-c">/* arr 的类型是 int[4] */</span>
    <span class="hl-k">int</span>  x;            <span class="hl-c">/* x   的类型是 int    */</span>

    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(arr)    = %zu\\n"</span>, <span class="hl-k">sizeof</span> arr);      <span class="hl-c">/* 16 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(arr[0]) = %zu\\n"</span>, <span class="hl-k">sizeof</span> arr[<span class="hl-n">0</span>]);   <span class="hl-c">/* 4  */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(x)      = %zu\\n"</span>, <span class="hl-k">sizeof</span> x);        <span class="hl-c">/* 4  */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>sizeof(arr)    = 16
sizeof(arr[0]) = 4
sizeof(x)      = 4</pre></div>

<p><code>sizeof(arr)</code> 是 <b>16</b> 而不是 4 —— 因为
<code>arr</code> 是「4 个 int」，4 × 4 = 16。<code>sizeof</code> 量的始终是
<b>类型占多大</b>。</p>

<div class="card note">
  <div class="card-t">一句话</div>
  <p><b><code>arr</code> 是数组，<code>arr[0]</code> 才是 int。</b>
  加一个下标，类型就从 <code>int[4]</code> 变成了 <code>int</code>。</p>
</div>

<h3>为什么这件事重要</h3>

<h4>① 它解释了 sizeof 为什么是 16</h4>

<p>如果 <code>arr</code> 的类型真是 <code>int</code>，<code>sizeof(arr)</code>
就该是 4。它是 16，正说明<b>量到的是一个「4 个 int」的整体</b>。</p>

<p>这也解释了一件容易被忽略的事：<b><code>sizeof</code> 不需要真的去数内存，
它在编译期就算好了</b> —— 因为它只需要知道类型。</p>

<h4>② 它解释了为什么不能把数组塞给 int</h4>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">类型不匹配，编译不过</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> arr[<span class="hl-n">4</span>];
<span class="hl-k">int</span> x = arr;      <span class="hl-c">/* 错：int[4] 不能塞进 int */</span></pre></div>

<p>编译器会直接报错。这不是「规矩多」，而是<b>真的放不下</b>：
<code>arr</code> 是 16 字节，<code>x</code> 只有 4 字节。</p>

<h4>③ 它是 M04 讲指针的入口</h4>

<p>还有一个细节：<b>数组名在多数场合会「退化」成指向首元素的指针</b>，
也就是从 <code>int[4]</code> 变成 <code>int*</code>。这件事
M04 讲指针时会正面用到 —— 那里会回扣本节，还会顺带说清
<b>多维数组为什么能省掉第一维</b>。</p>

<div class="take">
  <b>记住这一条：</b>看到 <code>int arr[4]</code>，把它的类型读成
  <b><code>int[4]</code></b>，不要读成 <code>int</code>。<br>
  类型不同，<code>sizeof</code> 不同，能不能赋值也不同。
</div>

"""

# ---------------- M03：替换整节 ----------------
p3 = T + r"\m03.html"
t = io.open(p3, encoding="utf-8").read()
a = t.find('<h2 id="s11"')
b = t.find('<h2 id="s12"')
if a < 0 or b < 0:
    print("  !! 找不到 M03 的 s11/s12")
    sys.exit(1)
t = t[:a] + NEW_S11 + t[b:]
# 校验：本节内不该再有 &amp;（& 的转义）
seg = t[a:t.find('<h2 id="s12"')]
n_amp = seg.count("&amp;")
print("  M03 §11 已替换；节内 & 的出现次数 = %d（应为 0）" % n_amp)
io.open(p3, "w", encoding="utf-8", newline="").write(t)
print("  M03 已写入 %d 字符" % len(t))

# ---------------- M04：补多维数组小话题 ----------------
EXTRA = """
<h4>附：为什么多维数组只有第一维可以省</h4>

<p>写二维数组时有个常被问的问题：下面三种声明，为什么只有中间那个能过？</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三种写法</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> a1[<span class="hl-n">2</span>][<span class="hl-n">3</span>];   <span class="hl-c">/* ✓ 合法 */</span>
<span class="hl-k">int</span> a2[][<span class="hl-n">3</span>];    <span class="hl-c">/* ✓ 合法：第一维省掉 */</span>
<span class="hl-k">int</span> a3[<span class="hl-n">2</span>][];    <span class="hl-c">/* ✗ 非法：第二维不能省 */</span></pre></div>

<p>关键在于<b>编译器要能算出一个元素占多大</b>。</p>

<p><code>int[2][3]</code> 可以理解成「<b>2 个 <code>int[3]</code></b>」——
它的一层元素是 <code>int[3]</code>，占 12 字节。所以：</p>

<div class="mnemonic">
  <code>a[i]</code> 的地址 = 起始地址 + <b>i × 12</b><br>
  —— 每跨一行，正好跳过 12 字节
</div>

<p>这个「12」必须由<b>第二维</b>算出来。所以：</p>

<table>
<thead><tr><th style="width:22%">写法</th><th style="width:22%">每行多大</th>
<th>行不行</th></tr></thead>
<tbody>
<tr><td class="c"><code>int a[2][3]</code></td><td class="c">3 × 4 = 12</td>
    <td class="c">行 —— 两个都说了</td></tr>
<tr><td class="c"><code>int a[][3]</code></td><td class="c">3 × 4 = 12</td>
    <td class="c"><b>行</b> —— 行宽有了，「几行」以后再补也行</td></tr>
<tr><td class="c"><code>int a[2][]</code></td><td class="c"><b>算不出来</b></td>
    <td class="c"><b>不行</b> —— 不知道一行多宽，<code>a[1]</code> 就找不到</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">一句话</div>
  <p><b>第一维是「有几行」，第二维是「一行多宽」。</b></p>
  <p>「几行」可以临时不知道 —— 有时能由初始化列表数出来；
  但<b>「一行多宽」必须知道</b>，否则连第二行从哪开始都算不出来。</p>
</div>

<p>顺带一个推论：<code>sizeof(int[2][3])</code> 是 <b>24</b>
（2 × 12）—— 和多维无关，仍然是「整个类型占多大」。</p>

<div class="card tip">
  <div class="card-t">和这一节的回扣连起来看</div>
  <p>回扣说的是「<code>arr</code> 的类型是 <code>int[4]</code> 而不是 <code>int</code>」；
  这里说的是「<code>a</code> 的类型是 <code>int[2][3]</code>，
  它的一层元素是 <code>int[3]</code>」。</p>
  <p><b>同一个道理：数组的类型里带着「每一维多大」，这是编译器算地址的依据。</b>
  省掉第一维还有救，省掉后面任何一维就断了这条依据。</p>
</div>

"""

p4 = T + r"\m04.html"
t4 = io.open(p4, encoding="utf-8").read()
if "为什么多维数组只有第一维可以省" in t4:
    print("  M04 已有该话题，跳过")
else:
    ANCHOR = """  <p>原因 M03 已经讲过：<b>类型决定步长</b>。
  <code>int *</code> 加 1 前进 4 字节，<code>char *</code> 加 1 只前进 1 字节。
  类型写错了，指针就会在内存里走错格。</p>
</div>
"""
    if ANCHOR not in t4:
        print("  !! M04 找不到锚点")
        sys.exit(1)
    t4 = t4.replace(ANCHOR, ANCHOR + EXTRA, 1)
    io.open(p4, "w", encoding="utf-8", newline="").write(t4)
    print("  M04 已补多维数组话题，%d 字符" % len(t4))
