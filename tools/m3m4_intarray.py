# -*- coding: utf-8 -*-
"""M03 新增「数组的类型是 int[n]」一节；M04 开头回扣。

用户要求
    M03 和 M04 的衔接不良。要提及：数组的类型不是「int」，而是「int[n]」，
    这才是完整的类型，并在 M04 中回扣。

做法
    M03：在「地址与数组」（s10）之后插入 11 · 数组的类型是 int[n]
        原「常见错误」11→12、「一页速查」12→13。
        TOC 只插一行、顺延最后两条 —— 不整份重建，否则会丢掉
        <div class="sep"> 分组线，也会把目录文案换成标题原文。
    M04：第 1 节末尾加两张卡：回扣（arr 退化）+ 指针类型的硬规矩。

幂等：已有标记就直接跳过，重复运行不会重复插入。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

NEW_SEC = """<h2 id="s11"><span class="n">11</span>数组的类型是 <code>int[n]</code></h2>

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

<h4>① 它解释了「步长」</h4>

<p>上一节说「地址加 1 前进多少，由类型决定」。现在可以精确说了：</p>

<div class="vs">
<table>
<thead><tr><th style="width:26%">表达式</th><th style="width:22%">类型</th>
<th>加 1 前进</th></tr></thead>
<tbody>
<tr><td class="c"><code>arr</code></td><td class="c"><code>int[4]</code></td>
    <td class="c"><b>16 字节</b>（跨过整个数组）</td></tr>
<tr><td class="c"><code>&amp;arr[0]</code></td><td class="c"><code>int*</code></td>
    <td class="c"><b>4 字节</b>（跨过一个 int）</td></tr>
</tbody>
</table>
</div>

<p>同样是「加 1」，一个前进 16 字节、一个前进 4 字节 —— 因为
<b>两个东西的类型不一样</b>。</p>

<h4>② 它解释了为什么不能把数组塞给 int</h4>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">类型不匹配，编译不过</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> arr[<span class="hl-n">4</span>];
<span class="hl-k">int</span> x = arr;      <span class="hl-c">/* 错：int[4] 不能塞进 int */</span></pre></div>

<p>编译器会直接报错。这不是「规矩多」，而是<b>真的放不下</b>：
<code>arr</code> 是 16 字节，<code>x</code> 只有 4 字节。</p>

<h4>③ 它是 M04 讲指针的入口</h4>

<p>还有一个细节：<b>数组名在多数场合会「退化」成指向首元素的指针</b>，
也就是从 <code>int[4]</code> 变成 <code>int*</code>。这件事
M04 讲指针时会正面用到 —— 那里会回扣本节。</p>

<div class="take">
  <b>记住这一条：</b>看到 <code>int arr[4]</code>，把它的类型读成
  <b><code>int[4]</code></b>，不要读成 <code>int</code>。<br>
  类型不同，<code>sizeof</code> 不同，步长不同，能不能赋值也不同。
</div>

"""

M04_BACK = """
<div class="card tip">
  <div class="card-t">回扣 M03：数组的类型是 <code>int[n]</code></div>
  <p>M03 最后一节说过：<code>int arr[4]</code> 里 <code>arr</code> 的类型是
  <b><code>int[4]</code></b>，不是 <code>int</code>。现在有了指针，可以接着往下说：</p>
  <div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">数组名会「退化」成指针</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span>  arr[<span class="hl-n">4</span>] = {<span class="hl-n">10</span>, <span class="hl-n">20</span>, <span class="hl-n">30</span>, <span class="hl-n">40</span>};
<span class="hl-k">int</span> *p = arr;        <span class="hl-c">/* arr 原类型 int[4] → 这里退化成 int* */</span></pre></div>
  <p><code>arr</code> 原本是 <code>int[4]</code>；一旦要赋给指针，
  它就<b>退化</b>成「指向第一个元素的指针」，类型变成 <code>int*</code>。</p>
  <p>所以 <code>p</code> 指向的是 <code>arr[0]</code>，
  <code>*p</code> 取到的是 <b>10</b>。</p>
</div>

<div class="card key">
  <div class="card-t">由此得到指针的一条硬规矩</div>
  <p><b>指针的类型，必须与它指向的东西对得上。</b></p>
  <p><code>int *p</code> 只能指向 <code>int</code>；
  要指向 <code>char</code> 就用 <code>char *</code>，
  要指向 <code>double</code> 就用 <code>double *</code>。</p>
  <p>原因 M03 已经讲过：<b>类型决定步长</b>。
  <code>int *</code> 加 1 前进 4 字节，<code>char *</code> 加 1 只前进 1 字节。
  类型写错了，指针就会在内存里走错格。</p>
</div>

"""

# ---------------- M03 ----------------
p3 = T + r"\m03.html"
t = io.open(p3, encoding="utf-8").read()

if "数组的类型是 <code>int[n]</code>" in t:
    print("  M03 已有本节，跳过")
else:
    a = t.find('<h2 id="s11">')
    if a < 0:
        print("  !! M03 找不到 s11")
        sys.exit(1)
    t = t[:a] + NEW_SEC + t[a:]

    # 新节先给临时 id，再把旧的 s11/s12 顺延，最后落位
    t = t.replace('<h2 id="s11"><span class="n">11</span>数组的类型是',
                  '<h2 id="NEW11"><span class="n">11</span>数组的类型是', 1)
    t = t.replace('<h2 id="s12">', '<h2 id="sTMP13">', 1)
    t = t.replace('<h2 id="s11">', '<h2 id="sTMP12">', 1)
    t = t.replace('<h2 id="sTMP12">', '<h2 id="s12">', 1)
    t = t.replace('<h2 id="sTMP13">', '<h2 id="s13">', 1)
    t = t.replace('<h2 id="NEW11">', '<h2 id="s11">', 1)

    n = [0]

    def renum(m):
        n[0] += 1
        return '<h2 id="%s"><span class="n">%d</span>' % (m.group(1), n[0])

    t = re.sub(r'<h2 id="(s\d+)"><span class="n">\d+</span>', renum, t)
    print("  M03 小节数 %d" % n[0])

    NEW_ROW = '  <a href="#s11">11 · 数组的类型是 int[n]</a>\n'
    ANCHOR = '  <a href="#s10">10 · 地址与数组</a>\n'
    if ANCHOR in t:
        t = t.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
        t = t.replace('  <a href="#s11">11 · 常见错误</a>',
                      '  <a href="#s12">12 · 常见错误</a>', 1)
        t = t.replace('  <a href="#s12">12 · 一页速查</a>',
                      '  <a href="#s13">13 · 一页速查</a>', 1)
        print("  M03 TOC 已插入并顺延")
    else:
        print("  !! M03 TOC 锚点未匹配")

    io.open(p3, "w", encoding="utf-8", newline="").write(t)
    print("  M03 已写入 %d 字符" % len(t))

# ---------------- M04 ----------------
p4 = T + r"\m04.html"
t4 = io.open(p4, encoding="utf-8").read()

if "回扣 M03" in t4:
    print("  M04 已有回扣，跳过")
else:
    ANCHOR4 = ('<div class="mnemonic">\n'
               '  <b>记住这个比喻：</b>\n'
               '  <code>x</code> 是一间房，<code>42</code> 是房里住的人。<br>\n'
               '  <code>p</code> 是一张<b>纸条</b>，上面写着「x 的房间号」。<br>\n'
               '  纸条上写的不是「42」，而是「<b>去哪里找 42</b>」。\n'
               '</div>\n')
    if ANCHOR4 not in t4:
        print("  !! M04 找不到插入锚点")
        sys.exit(1)
    t4 = t4.replace(ANCHOR4, ANCHOR4 + M04_BACK, 1)
    io.open(p4, "w", encoding="utf-8", newline="").write(t4)
    print("  M04 已写入 %d 字符" % len(t4))
