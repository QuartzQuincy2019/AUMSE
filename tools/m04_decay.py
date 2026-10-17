# -*- coding: utf-8 -*-
"""M04：把「退化」说清楚，并链到 E03 / M09。

用户要求
    M04 什么叫「退化」？把它说清楚，你可以引用 E02 的内容和链接。

关于「E02」
    E02 是《批处理与命令提示符进阶》—— 讲 .bat、变量、%~dp0、node/npm/python，
    与「数组退化」没有关系。全站真正讲这件事的是 **E03《语法糖》**：
    它讲 arr[i] 与 arr[i][j] 背后的东西，明确写了
    「(a + 1) 拿到第 2 行本身。它的类型退化成 int*」。
    所以这里链到 E03（并兼链 M09，那里把「必须另传长度」列为 C 数组的短板）。

放在哪
    紧接「回扣 M03」那张卡之后、「指针类型的硬规矩」之前 ——
    因为回扣卡第一次用到「退化」这个词，紧接着就解释它。

M04 的样式表是 tutorial.css（不是 genelayout.css），没有 .alias / .vs /
.take / .see-also，所以正文用 table + .card（key/warn/note/tip）+ .mnemonic。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\m04.html"
t = io.open(P, encoding="utf-8").read()

SEC = """<h4>先把「退化」说清楚</h4>

<p>上面的回扣用了「退化」这个词。它不是比喻，而是一个有确切含义的说法，
后面还会反复碰到，所以单独讲清。</p>

<div class="card key">
  <div class="card-t">一句话</div>
  <p><b>数组名用在「需要指针」的位置时，编译器会自动把它换成一个
  「指向第一个元素的指针」。</b></p>
  <p>这个过程就叫<b>退化</b>（英文 decay）。从类型上看，是
  <code>int[4]</code> 变成了 <code>int*</code>。</p>
</div>

<p>三个要点，把它和「类型转换」区分开：</p>

<table>
<thead><tr><th style="width:22%">要点</th><th>意思</th></tr></thead>
<tbody>
<tr><td class="c"><b>自动发生</b></td>
    <td>你什么都不用写。只要把数组名放在一个需要指针的地方，编译器自己就换了
    —— 所以你甚至感觉不到它发生过</td></tr>
<tr><td class="c"><b>只换「看法」，<br>不换数据</b></td>
    <td>内存里那 16 字节一个都没动，也不会另存一份指针。
    变的只是<b>编译器此刻怎么理解这个数组名</b></td></tr>
<tr><td class="c"><b>丢掉长度</b></td>
    <td>退化之后只剩「从哪开始」，<b>「有多长」没了</b> ——
    下面那条「必须另传长度」的根源就在这里</td></tr>
</tbody>
</table>

<p>用 <code>sizeof</code> 能直接看到这件事：同一个数组，在 <code>main</code> 里量是
<b>16</b>，进了函数只剩 <b>8</b>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">退化前后，sizeof 的结果不一样</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>

<span class="hl-k">void</span> <span class="hl-f">show</span>(<span class="hl-k">int</span> *p) {              <span class="hl-c">/* 参数是 int* —— arr 传进来时已经退化 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(p)   = %zu\n"</span>, <span class="hl-k">sizeof</span> p);
}

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-k">int</span> arr[<span class="hl-n">4</span>] = {<span class="hl-n">10</span>, <span class="hl-n">20</span>, <span class="hl-n">30</span>, <span class="hl-n">40</span>};

    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(arr) = %zu\n"</span>, <span class="hl-k">sizeof</span> arr);   <span class="hl-c">/* 16：这里还没退化 */</span>
    <span class="hl-f">show</span>(arr);                               <span class="hl-c">/* 退化就发生在这一行 */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>sizeof(arr) = 16
sizeof(p)   = 8</pre></div>

<p><code>sizeof(arr)</code> 是 16（整个数组），<code>sizeof(p)</code> 是 8
（一个指针本身的大小）。<b>同一个数组，只因为换了个名字、换了个位置，
量出来的东西就不一样了</b> —— 这就是退化留下的痕迹。</p>

<div class="card warn">
  <div class="card-t">所以「传数组」必须另给长度</div>
  <p>函数收到的只是一个指针，它<b>无从知道数组有多长</b>。
  所以 C 里这两个参数总是成对出现：</p>
  <pre class="plain-pre"><span class="hl-k">void</span> <span class="hl-f">show</span>(<span class="hl-k">int</span> *p, <span class="hl-k">int</span> n);      <span class="hl-c">/* 指针 + 长度 */</span></pre>
  <p>这不是风格问题，是退化逼出来的结论。
  <a href="m09.html">M09 · vector 和 array</a> 把它列进了
  「C 数组的三大短板」：一旦传进函数就退化成指针，<code>sizeof</code> 随之失效，
  于是必须额外传长度。</p>
</div>

<div class="card note">
  <div class="card-t">等一下：那 <code>arr[i]</code> 为什么还能用？</div>
  <p>能。退化之后指针指向的<b>正是第一个元素</b>，
  「从这个位置往后数第 i 个」照样算得出来 —— 所以
  <code>arr[i]</code> 还是第 i 个元素。</p>
  <p><a href="e03.html">E03 · 语法糖</a> 把这一层拆开讲过：
  <code>arr[i]</code> 与 <code>arr[i][j]</code> 本质上都是
  「先退化、再按指针加偏移」，只不过编译器替你写好了。
  想去看看「糖衣下面是什么」，那篇就是干这个的。</p>
</div>

<div class="card tip">
  <div class="card-t">什么场合不退化</div>
  <p>最常见的例外是 <code>sizeof(arr)</code> —— 它量的是「整个数组」，
  所以能得出 16。如果这里也退化了，那就只会得到 8。</p>
  <p>反过来说，这是一个很好用的判据：<b>还能量出整个数组的大小，
  就说明它还没退化。</b>其余绝大多数场合，数组名一出现就已经是指针了。</p>
</div>

"""

# 插在「指针类型的硬规矩」那张卡之前
ANCHOR = '<div class="card key">\n  <div class="card-t">由此得到指针的一条硬规矩</div>'
if "先把「退化」说清楚" in t:
    print("  M04 已有该小节，跳过")
elif ANCHOR not in t:
    print("  !! M04 找不到锚点")
    sys.exit(1)
else:
    t = t.replace(ANCHOR, SEC + ANCHOR, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  M04 已插入「退化」小节，%d 字符" % len(t))

# ---- 自检 ----
print()
for kw in ("退化", "decay", "m09.html", "e03.html", "plain-pre"):
    print("     含 %-10s %d 次" % (kw, t.count(kw)))
