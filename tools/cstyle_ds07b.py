# -*- coding: utf-8 -*-
"""07 收尾：把剩余 cout / ::value 处全部改成 C。"""
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
done = []


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d 次" % (label, n))
        return
    t = t.replace(old, new, 1)
    done.append(label)


# ---------- 遮蔽示例整块换成 C ----------
sub('''<span class="hl-k">int</span> value = <span class="hl-n">100</span>;              <span class="hl-c">/* 全局 */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"全局 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-k">int</span> value = <span class="hl-n">20</span>;            <span class="hl-c">/* 局部把全局遮住了 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"局部 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;

    {
        <span class="hl-k">int</span> value = <span class="hl-n">3</span>;         <span class="hl-c">/* 又遮一层 */</span>
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"最内层 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;
    }

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"出了内层 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-c">/* 用 :: 访问被遮住的全局变量 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"::value = "</span> &lt;&lt; ::value &lt;&lt; <span class="hl-f">endl</span>;

    ::value = <span class="hl-n">555</span>;              <span class="hl-c">/* 改的是全局那个 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"::value = 555 之后，全局 value = "</span> &lt;&lt; ::value &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"局部 value 还是 "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''',
'''<span class="hl-k">int</span> value = <span class="hl-n">100</span>;              <span class="hl-c">/* 全局 */</span>

<span class="hl-c">/* 这个函数自己的函数体里没有同名变量，所以 value 指全局 */</span>
<span class="hl-k">int</span>  <span class="hl-f">getGlobalValue</span>(<span class="hl-k">void</span>) { <span class="hl-k">return</span> value; }
<span class="hl-k">void</span> <span class="hl-f">setGlobalValue</span>(<span class="hl-k">int</span> v)  { value = v; }

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">printf</span>(<span class="hl-s">"全局 value = %d\\n"</span>, <span class="hl-f">getGlobalValue</span>());

    <span class="hl-k">int</span> value = <span class="hl-n">20</span>;            <span class="hl-c">/* 局部把全局遮住了 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"局部 value = %d\\n"</span>, value);

    {
        <span class="hl-k">int</span> value = <span class="hl-n">3</span>;         <span class="hl-c">/* 又遮一层 */</span>
        <span class="hl-f">printf</span>(<span class="hl-s">"最内层 value = %d\\n"</span>, value);
    }

    <span class="hl-f">printf</span>(<span class="hl-s">"出了内层 value = %d\\n"</span>, value);

    <span class="hl-c">/* 在自己被遮住的范围里，只有靠函数名才能碰到全局那个 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"全局 value = %d\\n"</span>, <span class="hl-f">getGlobalValue</span>());

    <span class="hl-f">setGlobalValue</span>(<span class="hl-n">555</span>);           <span class="hl-c">/* 改的是全局那个 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"改过之后全局 value = %d\\n"</span>, <span class="hl-f">getGlobalValue</span>());
    <span class="hl-f">printf</span>(<span class="hl-s">"局部 value 还是 %d\\n"</span>, value);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''', "遮蔽示例 → C")

# ---------- 两处编译器原始报错：改成 C 的报错 ----------
sub('''<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'b' was not declared in this scope
    7 |     std::cout &lt;&lt; b &lt;&lt; std::endl;
      |                  ^</pre></div>''',
'''<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'b' undeclared (first use in this function)
    7 |     printf("%d", b);
      |                  ^</pre></div>''', "块作用域报错 → C")

sub('''<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'i' was not declared in this scope
    5 |     std::cout &lt;&lt; i &lt;&lt; std::endl;
      |                  ^</pre></div>''',
'''<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'i' undeclared (first use in this function)
    5 |     printf("%d", i);
      |                  ^</pre></div>''', "循环变量报错 → C")

# 正文里解释这句报错的地方
sub('''<p><code>was not declared in this scope</code> 直译就是
<b>「这个名字在本作用域里没有声明」</b>。以后看到这句报错，
第一反应应该是：<b>我是不是在块外面用了块里面的变量？</b></p>''',
'''<p><code>undeclared (first use in this function)</code> 直译就是
<b>「这个名字没声明过（在本函数里第一次用到）」</b>。以后看到它，
第一反应应该是：<b>我是不是在块外面用了块里面的变量？</b></p>''',
    "报错解释文字 → C")

# ---------- 常见错误里的 cout 片段 ----------
sub('''<pre><span class="hl-c">/* ❌ 数据全公开…… */</span>''', '''<pre><span class="hl-c">/* ❌ 数据全公开…… */</span>''', "占位")
for old, new, lab in [
    ('<span class="hl-f">cout</span> &lt;&lt; b;         <span class="hl-c">/* ❌ error: \'b\' was not declared in this scope */</span>',
     '<span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, b);   <span class="hl-c">/* ❌ error: \'b\' undeclared */</span>',
     "错误 1 的 cout → printf"),
    ('<span class="hl-f">cout</span> &lt;&lt; b;         <span class="hl-c">/* ✅ */</span>',
     '<span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, b);   <span class="hl-c">/* ✅ */</span>',
     "错误 1 的 ✅ cout → printf"),
    ('<span class="hl-f">cout</span> &lt;&lt; i;         <span class="hl-c">/* ❌ i 已经不在了 */</span>',
     '<span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, i);   <span class="hl-c">/* ❌ i 已经不在了 */</span>',
     "错误 2 的 cout → printf"),
    ('<span class="hl-f">cout</span> &lt;&lt; i;         <span class="hl-c">/* ✅ */</span>',
     '<span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, i);   <span class="hl-c">/* ✅ */</span>',
     "错误 2 的 ✅ cout → printf"),
    ('<span class="hl-k">void</span> <span class="hl-f">g</span>() { <span class="hl-f">cout</span> &lt;&lt; gResult; }   <span class="hl-c">/* 必须 f 先调用过才对 */</span>',
     '<span class="hl-k">void</span> <span class="hl-f">g</span>(<span class="hl-k">void</span>) { <span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, gResult); }   <span class="hl-c">/* 必须 f 先调用过才对 */</span>',
     "错误 4 的 cout → printf（❌ 行）"),
    ('<span class="hl-k">void</span> <span class="hl-f">g</span>(<span class="hl-k">int</span> v) { <span class="hl-f">cout</span> &lt;&lt; v; }',
     '<span class="hl-k">void</span> <span class="hl-f">g</span>(<span class="hl-k">int</span> v) { <span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, v); }',
     "错误 4 的 cout → printf（✅ 行）"),
]:
    sub(old, new, lab)

# ---------- 速查表那一行 ----------
sub('<tr><td>指名被遮住的全局</td><td class="c">::value</td></tr>',
    '<tr><td>拿到被遮住的全局值</td><td class="c">写个 getGlobalValue() 存取函数</td></tr>',
    "速查表行 → C")

sub('<tr><td>全局变量</td><td class="c">写在所有函数外面</td></tr>',
    '<tr><td>全局变量</td><td class="c">写在所有函数外面（建议加 <code>g_</code> 前缀防撞名）</td></tr>',
    "速查表全局变量行")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("07 收尾：")
for d in done:
    print("  ✓ " + d)
print("")
print("剩余 cout：%d   ::value：%d" % (len(re.findall(r'cout', t)), len(re.findall(r'::value', t))))
for m in re.finditer(r'.{0,50}(cout|::value).{0,40}', t):
    print("   ..." + m.group(0).replace("\n", " ").strip()[:98])
