# -*- coding: utf-8 -*-
"""把 07《作用域、全局与局部变量》整体改写为 C 风格。

原有 C++ 特性处理：
  · cout/endl          → printf
  · iostream           → stdio.h
  · int &makeStatic()  → int *makeStatic()（用指针模拟「窄作用域长生存期」）
  · ::value            → 用一个存取函数 getGlobalValue()
  · bool / true        → int / 1
所有输出已用 gcc -std=c99 实跑核对。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_07_作用域、全局与局部变量.html"

with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()

orig = len(t)
done = []


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d 次" % (label, n))
        return
    t = t.replace(old, new, 1)
    done.append(label)


# ---------- 统一把头文件换掉 ----------
t = t.replace(
    '<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
    '<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n',
    '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n')
t = t.replace(
    '<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n',
    '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n')
t = t.replace(
    '<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n', '')

# ---------- 逐个把 cout 语句换成 printf ----------
PAIRS = [
    # 1. 第一个例子
    ('<span class="hl-k">void</span> <span class="hl-f">f</span>() {\n'
     '    <span class="hl-k">int</span> n = <span class="hl-n">100</span>;          <span class="hl-c">/* 这个 n 属于 f */</span>\n'
     '    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"f 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;\n'
     '}',
     '<span class="hl-k">void</span> <span class="hl-f">f</span>(<span class="hl-k">void</span>) {\n'
     '    <span class="hl-k">int</span> n = <span class="hl-n">100</span>;          <span class="hl-c">/* 这个 n 属于 f */</span>\n'
     '    <span class="hl-f">printf</span>(<span class="hl-s">"f 里的 n = %d\\n"</span>, n);\n'
     '}'),

    ('<span class="hl-k">int</span> <span class="hl-f">main</span>() {\n'
     '    <span class="hl-k">int</span> n = <span class="hl-n">1</span>;            <span class="hl-c">/* 这个 n 属于 main */</span>\n'
     '    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"main 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;\n\n'
     '    <span class="hl-f">f</span>();\n\n'
     '    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 f 之后 main 里的 n 还是 "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;\n'
     '    <span class="hl-k">return</span> <span class="hl-n">0</span>;\n'
     '}',
     '<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {\n'
     '    <span class="hl-k">int</span> n = <span class="hl-n">1</span>;            <span class="hl-c">/* 这个 n 属于 main */</span>\n'
     '    <span class="hl-f">printf</span>(<span class="hl-s">"main 里的 n = %d\\n"</span>, n);\n\n'
     '    <span class="hl-f">f</span>();\n\n'
     '    <span class="hl-f">printf</span>(<span class="hl-s">"调用 f 之后 main 里的 n 还是 %d\\n"</span>, n);\n'
     '    <span class="hl-k">return</span> <span class="hl-n">0</span>;\n'
     '}'),
]
for old, new in PAIRS:
    sub(old, new, "第一个例子 → C")

# 把剩下的 cout << 形式批量转换（简单模式）
def cout_to_printf(m):
    return m.group(0)

# 逐条精修：下方是文中全部剩余 cout 行，逐行映射
LINE_MAP = [
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"外层 a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"外层 a = %d\\n"</span>, a);'),
    ('        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"内层 看得到 a = "</span> &lt;&lt; a\n'
     '             &lt;&lt; <span class="hl-s">"，b = "</span> &lt;&lt; b &lt;&lt; <span class="hl-f">endl</span>;',
     '        <span class="hl-f">printf</span>(<span class="hl-s">"内层 看得到 a = %d，b = %d\\n"</span>, a, b);'),
    ('        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"内层改了 a，a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-f">endl</span>;',
     '        <span class="hl-f">printf</span>(<span class="hl-s">"内层改了 a，a = %d\\n"</span>, a);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"出了内层，a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-s">"（改动保留）"</span> &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"出了内层，a = %d（改动保留）\\n"</span>, a);'),
    ('    <span class="hl-c">/* cout &lt;&lt; b;   ← 取消注释就报错：b 已经不在了 */</span>',
     '    <span class="hl-c">/* printf("%d", b);   ← 取消注释就报错：b 已经不在了 */</span>'),
    ('        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"i="</span> &lt;&lt; i &lt;&lt; <span class="hl-s">" t="</span> &lt;&lt; t &lt;&lt; <span class="hl-f">endl</span>;',
     '        <span class="hl-f">printf</span>(<span class="hl-s">"i=%d t=%d\\n"</span>, i, t);'),
    ('    <span class="hl-c">/* cout &lt;&lt; i;   ← 报错：i 已经不在了 */</span>',
     '    <span class="hl-c">/* printf("%d", i);   ← 报错：i 已经不在了 */</span>'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"循环结束后 i 和 t 都不存在了"</span> &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"循环结束后 i 和 t 都不存在了\\n"</span>);'),
    ('    <span class="hl-k">if</span> (<span class="hl-k">true</span>) {',
     '    <span class="hl-k">if</span> (<span class="hl-n">1</span>) {'),
    ('        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"if 块里的 only = "</span> &lt;&lt; only &lt;&lt; <span class="hl-f">endl</span>;',
     '        <span class="hl-f">printf</span>(<span class="hl-s">"if 块里的 only = %d\\n"</span>, only);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"if 块结束后 only 也不存在了"</span> &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"if 块结束后 only 也不存在了\\n"</span>);'),
    ('        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"第二个循环 i = "</span> &lt;&lt; i &lt;&lt; <span class="hl-f">endl</span>;',
     '        <span class="hl-f">printf</span>(<span class="hl-s">"第二个循环 i = %d\\n"</span>, i);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  f 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"  f 里的 n = %d\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  f 里改过之后 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"  f 里改过之后 n = %d\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"main 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"main 里的 n = %d\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 f 之后 main 里的 n = "</span> &lt;&lt; n\n'
     '         &lt;&lt; <span class="hl-s">"（没变）"</span> &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"调用 f 之后 main 里的 n = %d（没变）\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"开始 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"开始 gCount = %d\\n"</span>, gCount);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 bump 三次后 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"调用 bump 三次后 gCount = %d\\n"</span>, gCount);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"reset 之后 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"reset 之后 gCount = %d\\n"</span>, gCount);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  普通局部   n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"  普通局部   n = %d\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  static局部 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"  static局部 n = %d\\n"</span>, n);'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"第一次读: "</span> &lt;&lt; <span class="hl-f">makeStatic</span>() &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"第一次读: %d\\n"</span>, *<span class="hl-f">makeStatic</span>());'),
    ('    <span class="hl-f">makeStatic</span>() = <span class="hl-n">77</span>;         <span class="hl-c">/* 还能改它 */</span>',
     '    *<span class="hl-f">makeStatic</span>() = <span class="hl-n">77</span>;        <span class="hl-c">/* 还能改它 */</span>'),
    ('    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"改成 77 后再读: "</span> &lt;&lt; <span class="hl-f">makeStatic</span>() &lt;&lt; <span class="hl-f">endl</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"改成 77 后再读: %d\\n"</span>, *<span class="hl-f">makeStatic</span>());'),
    ('<span class="hl-k">int</span> &amp;<span class="hl-f">makeStatic</span>() {\n'
     '    <span class="hl-k">static</span> <span class="hl-k">int</span> keep = <span class="hl-n">42</span>;     <span class="hl-c">/* 名字只在函数内可见 */</span>\n'
     '    <span class="hl-k">return</span> keep;               <span class="hl-c">/* 但它活到程序结束 */</span>\n'
     '}',
     '<span class="hl-k">int</span> *<span class="hl-f">makeStatic</span>(<span class="hl-k">void</span>) {\n'
     '    <span class="hl-k">static</span> <span class="hl-k">int</span> keep = <span class="hl-n">42</span>;     <span class="hl-c">/* 名字只在函数内可见 */</span>\n'
     '    <span class="hl-k">return</span> &amp;keep;              <span class="hl-c">/* 但它活到程序结束 */</span>\n'
     '}'),
    ('<span class="hl-k">int</span> <span class="hl-f">main</span>() {\n'
     '    <span class="hl-f">printf</span>(<span class="hl-s">"第一次读: %d\\n"</span>, *<span class="hl-f">makeStatic</span>());',
     '<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {\n'
     '    <span class="hl-f">printf</span>(<span class="hl-s">"第一次读: %d\\n"</span>, *<span class="hl-f">makeStatic</span>());'),
]
for old, new in LINE_MAP:
    if old in t:
        n = t.count(old)
        t = t.replace(old, new)
        done.append("cout → printf（%d 处）" % n)

# ---------- :: 改成存取函数 ----------
sub('''<h4><code>::</code> 是干什么的</h4>
<p><code>::value</code> 表示「<b>全局作用域里的 value</b>」，
用它可以绕过所有局部变量，直接指名全局那个。</p>

<table>
<thead><tr><th style="width:34%">写法</th><th>指的是</th></tr></thead>
<tbody>
<tr><td class="c">value</td><td>就近的那个（可能是局部）</td></tr>
<tr><td class="c">::value</td><td><b>全局</b>那个，不管中间遮了多少层</td></tr>
</tbody>
</table>''',
'''<h4>C 里怎么指名「被遮住的全局」</h4>
<p>这里有个重要差别：<b>C 语言没有 <code>::</code> 这个写法</b>
（那是 C++ 的）。在 C 里，一旦被遮住，
<b>同名的作用域内就没法直接提到全局那个了</b>。</p>

<p>实际做法有两种。<b>第一种是根本不去遮它</b> ——
给全局变量起个不会撞车的名字，这也是最省事的办法：</p>

<table>
<thead><tr><th style="width:38%">做法</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">int g_value = 100;</td>
    <td><b>推荐</b>：全局加 <code>g_</code> 前缀，局部怎么起名都不会撞</td></tr>
<tr><td class="c">int value = 100;</td>
    <td>容易和局部重名，撞上就只能靠下面的办法</td></tr>
</tbody>
</table>

<p><b>第二种：写一个只返回全局值的函数</b>，用函数名绕开重名：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">用函数拿到被遮住的全局值</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> value = <span class="hl-n">100</span>;                 <span class="hl-c">/* 全局 */</span>

<span class="hl-c">/* 这个函数体里的 value 指的是全局 —— 因为它自己没定义同名局部 */</span>
<span class="hl-k">int</span> <span class="hl-f">getGlobalValue</span>(<span class="hl-k">void</span>) {
    <span class="hl-k">return</span> value;
}

<span class="hl-k">void</span> <span class="hl-f">setGlobalValue</span>(<span class="hl-k">int</span> v) {
    value = v;
}</pre></div>

<p>于是在被遮住的函数里，用 <code>getGlobalValue()</code> 就能拿到全局那个值。
虽然比 C++ 的 <code>::value</code> 啰嗦，但意思一样清楚。</p>''',
    ":: 说明 → C 的做法")

# 把例子里的 ::value 用法改掉
sub('''    <span class="hl-c">/* 用 :: 访问被遮住的全局变量 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"::value = %d\\n"</span>, ::value);

    ::value = <span class="hl-n">555</span>;              <span class="hl-c">/* 改的是全局那个 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"::value = 555 之后，全局 value = %d\\n"</span>, ::value);''',
'''    <span class="hl-c">/* 在局部遮蔽的范围里，用函数拿到全局那个 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"全局 value = %d\\n"</span>, <span class="hl-f">getGlobalValue</span>());

    <span class="hl-f">setGlobalValue</span>(<span class="hl-n">555</span>);            <span class="hl-c">/* 改的是全局那个 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"改过之后全局 value = %d\\n"</span>, <span class="hl-f">getGlobalValue</span>());''',
    "例子里的 ::value → 存取函数")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("07：%d → %d 字符" % (orig, len(t)))
for d in done:
    print("  ✓ " + d)
print("")
print("剩余 cout：%d   iostream：%d   ::value：%d"
      % (len(re.findall(r'cout', t)), len(re.findall(r'iostream', t)),
         len(re.findall(r'::value', t))))
