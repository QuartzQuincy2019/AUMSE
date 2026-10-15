# -*- coding: utf-8 -*-
"""把 08-E01《递归》改写为 C 风格（cout → printf，iostream → stdio.h，
   const char* 递归保持不变，g++ 相关字样改为 gcc）。"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_E01_递归.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)
done = []


def sub(old, new, label, count=1):
    global t
    n = t.count(old)
    if n != count:
        print("  !! %s：命中 %d（期望 %d）" % (label, n, count))
        return
    t = t.replace(old, new)
    done.append("%s ×%d" % (label, n))


def rep_all(old, new, label):
    global t
    n = t.count(old)
    if not n:
        print("  !! %s：未命中" % label)
        return
    t = t.replace(old, new)
    done.append("%s ×%d" % (label, n))


# 头文件
rep_all('<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
        '<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n',
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n',
        "头文件 → stdio.h")
rep_all('<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n',
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n',
        "头文件残留")
rep_all('<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n', '', "去 using")

# 缩进打印
rep_all('<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; depth; i++) <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  "</span>;   <span class="hl-c">/* 缩进表示层数 */</span>',
        '<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; depth; i++) <span class="hl-f">printf</span>(<span class="hl-s">"  "</span>);   <span class="hl-c">/* 缩进表示层数 */</span>',
        "缩进打印")
rep_all('        <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; depth; i++) <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  "</span>;',
        '        <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; depth; i++) <span class="hl-f">printf</span>(<span class="hl-s">"  "</span>);',
        "缩进打印2")

rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"countdown("</span> &lt;&lt; n &lt;&lt; <span class="hl-s">")"</span> &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"countdown(%d)\\n"</span>, n);', "countdown 打印")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"到底了，开始返回"</span> &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"到底了，开始返回\\n"</span>);', "到底了")
rep_all('<span class="hl-f">cout</span> &lt;&lt; n &lt;&lt; <span class="hl-s">" "</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"%d "</span>, n);', "countdown 一行版")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);', "换行")
rep_all('<span class="hl-f">cout</span> &lt;&lt; (n % <span class="hl-n">2</span>);',
        '<span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, n % <span class="hl-n">2</span>);', "打印位")
rep_all('<span class="hl-f">cout</span> &lt;&lt; *s;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"%c"</span>, *s);', "打印字符")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"10 -&gt; "</span>;  <span class="hl-f">toBinary</span>(<span class="hl-n">10</span>);  <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"10 -&gt; "</span>);  <span class="hl-f">toBinary</span>(<span class="hl-n">10</span>);  <span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);', "10 ->")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"255 -&gt; "</span>; <span class="hl-f">toBinary</span>(<span class="hl-n">255</span>); <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"255 -&gt; "</span>); <span class="hl-f">toBinary</span>(<span class="hl-n">255</span>); <span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);', "255 ->")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"Mongol 倒过来: "</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"Mongol 倒过来: "</span>);', "Mongol")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">" max = "</span> &lt;&lt; <span class="hl-f">maxInArray</span>(a, <span class="hl-n">6</span>) &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"max = %d\\n"</span>, <span class="hl-f">maxInArray</span>(a, <span class="hl-n">6</span>));', "max")

# 示例 ①：整段重写（含 main）
sub('''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>

<span class="hl-k">void</span> <span class="hl-f">countdown</span>(<span class="hl-k">int</span> n) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%d "</span>, n);

    <span class="hl-k">if</span> (n == <span class="hl-n">0</span>) <span class="hl-k">return</span>;      <span class="hl-c">/* ① 停下来的条件 */</span>

    <span class="hl-f">countdown</span>(n - <span class="hl-n">1</span>);           <span class="hl-c">/* ② 调用自己，但问题变小了 */</span>
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">countdown</span>(<span class="hl-n">5</span>);
    <span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''',
'''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>

<span class="hl-k">void</span> <span class="hl-f">countdown</span>(<span class="hl-k">int</span> n) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%d "</span>, n);

    <span class="hl-k">if</span> (n == <span class="hl-n">0</span>) <span class="hl-k">return</span>;      <span class="hl-c">/* ① 停下来的条件 */</span>

    <span class="hl-f">countdown</span>(n - <span class="hl-n">1</span>);           <span class="hl-c">/* ② 调用自己，但问题变小了 */</span>
}

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">countdown</span>(<span class="hl-n">5</span>);
    <span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''', "示例① main")

# 阶乘 / fib / sumTo / toBinary 的 main 调用行
rep_all('<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">1</span>; i &lt;= <span class="hl-n">6</span>; i++) <span class="hl-f">cout</span> &lt;&lt; i &lt;&lt; <span class="hl-s">"! = "</span> &lt;&lt; <span class="hl-f">fact</span>(i) &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">1</span>; i &lt;= <span class="hl-n">6</span>; i++) <span class="hl-f">printf</span>(<span class="hl-s">"%d! = %lld\\n"</span>, i, <span class="hl-f">fact</span>(i));', "阶乘打印")
rep_all('<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt;= <span class="hl-n">8</span>; i++) <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">fib</span>(i) &lt;&lt; <span class="hl-s">" "</span>;',
        '<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt;= <span class="hl-n">8</span>; i++) <span class="hl-f">printf</span>(<span class="hl-s">"%d "</span>, <span class="hl-f">fib</span>(i));', "fib 打印")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"1+2+...+10 = "</span> &lt;&lt; <span class="hl-f">sumTo</span>(<span class="hl-n">10</span>) &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"1+2+...+10 = %d\\n"</span>, <span class="hl-f">sumTo</span>(<span class="hl-n">10</span>));', "sumTo 打印")
rep_all('<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"max = "</span> &lt;&lt; <span class="hl-f">maxInArray</span>(a, <span class="hl-n">6</span>) &lt;&lt; <span class="hl-f">endl</span>;',
        '<span class="hl-f">printf</span>(<span class="hl-s">"max = %d\\n"</span>, <span class="hl-f">maxInArray</span>(a, <span class="hl-n">6</span>));', "max 打印2")

# main 签名与 const char* 递归
rep_all('<span class="hl-k">int</span> <span class="hl-f">main</span>() {', '<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {', "main 签名")

# g++ → gcc 字样
rep_all('（<code>-std=c++17</code>）', '（<code>-std=c99</code>）', "标准字样")
rep_all('g++ 13.1.0', 'gcc 13.1.0', "编译器字样")
rep_all('std::cout', 'printf', "std::cout 残留")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("E01：%d → %d 字符" % (orig, len(t)))
for d in done:
    print("  ✓ " + d)
print("")
print("剩余 cout：%d   iostream：%d   g++：%d"
      % (len(re.findall(r'cout', t)), len(re.findall(r'iostream', t)), len(re.findall(r'g\+\+', t))))
for m in re.finditer(r'.{0,45}cout.{0,45}', t):
    print("   ..." + m.group(0).replace("\n", " ").strip()[:95])
