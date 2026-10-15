# -*- coding: utf-8 -*-
"""F01 / F03 / F04 的 C 化与修正：

F01：编译错误示例改用 C 的报错（原来是 C++ 的 cout）
F03：三处报错信息全部换成 gcc 的 C 版本
F04：字节打印示例从 cout 改成 printf
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"


def load(n):
    with io.open(os.path.join(ROOT, n), encoding="utf-8") as fh:
        return fh.read()


def save(n, t):
    with io.open(os.path.join(ROOT, n), "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


# =====================================================================
# F01：把 C++ 的编译错误示例换成 C 的
# =====================================================================
n = "_ds_08_F01_命令提示符初步.html"
t = load(n)
old = '''<span class="pr">E:\\Path\\To\\demo&gt;</span><span class="cmd">g++ -std=c++17 main.cpp -o main.exe</span>
<span class="err">main.cpp: In function 'int main()':</span>
<span class="err">main.cpp:5:12: error: 'cout' was not declared in this scope</span>
<span class="err">    5 |     cout &lt;&lt; "Hello";</span>
<span class="err">      |     ^~~~</span>'''
new = '''<span class="pr">D:\\Path\\To\\demo&gt;</span><span class="cmd">gcc -std=c99 main.c -o main.exe</span>
<span class="err">main.c: In function 'main':</span>
<span class="err">main.c:5:12: error: 'count' undeclared (first use in this function)</span>
<span class="err">    5 |     printf("%d", count);</span>
<span class="err">      |                ^~~~~</span>'''
if old in t:
    t = t.replace(old, new, 1)
    print("F01：编译错误示例 → C 报错")
else:
    print("F01：未匹配（检查）")
# 其余 g++/-std=c++17 也统一成 C
t = t.replace('g++ -std=c++17 main.cpp -o main.exe', 'gcc -std=c99 main.c -o main.exe')
t = t.replace('main.cpp', 'main.c')
t = t.replace('main.o', 'main.o')
t = t.replace('一个 C++ 源文件', '一个 C 源文件')
save(n, t)


# =====================================================================
# F03：三处报错换成 gcc 的 C 版本
# =====================================================================
n = "_ds_08_F03_编译与链接、头文件与库.html"
t = load(n)
pairs = [
    # 语法错误
    ('''<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>syn.cpp:1:22: error: expected primary-expression before ';' token
    1 | int main() { int x = ; return 0; }
      |                      ^</pre></div>''',
     '''<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>syn.c:1:26: error: expected expression before ';' token
    1 | int main(void) { int x = ; return 0; }
      |                          ^</pre></div>'''),
    # 链接错误
    ('''<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>ld.exe: lk1.cpp:(.text+0x18): undefined reference to `add(int, int)'
collect2.exe: error: ld returned 1 exit status</pre></div>''',
     '''<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>ld.exe: lk1.c:(.text+0x6c): undefined reference to `add'
collect2.exe: error: ld returned 1 exit status</pre></div>'''),
]
for old, new in pairs:
    if old in t:
        t = t.replace(old, new, 1)
        print("F03：报错 → C 版")
    else:
        print("F03：未匹配一处（检查）")

# 代码示例里的 iostream/cout 换掉
t = t.replace('''<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() { <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"hi"</span>; }''',
'''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) { <span class="hl-f">printf</span>(<span class="hl-s">"hi"</span>); }''')
t = t.replace('''<span class="hl-c">/* ...iostream 的全部内容粘在这里... */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() { <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"hi"</span>; }''',
'''<span class="hl-c">/* ...stdio.h 的全部内容粘在这里... */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) { <span class="hl-f">printf</span>(<span class="hl-s">"hi"</span>); }''')
t = t.replace('''<span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);      <span class="hl-c">/* 声明了，但没人实现它 */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>) &lt;&lt; <span class="hl-f">endl</span>;   <span class="hl-c">/* 编译能过，链接会失败 */</span>
}''',
'''<span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);      <span class="hl-c">/* 声明了，但没人实现它 */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%d\\n"</span>, <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>));   <span class="hl-c">/* 编译能过，链接会失败 */</span>
}''')
t = t.replace('''<span class="hl-c">/* main.cpp —— 编译 main.cpp 时，编译器不知道 add 长什么样 */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>);        <span class="hl-c">/* ❌ 编译器：add 是什么？ */</span>
}

<span class="hl-c">/* tools.cpp —— 定义在这里，但编译 main.cpp 时看不到它 */</span>''',
'''<span class="hl-c">/* main.c —— 编译 main.c 时，编译器不知道 add 长什么样 */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%d"</span>, <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>));   <span class="hl-c">/* ❌ 编译器：add 是什么？ */</span>
}

<span class="hl-c">/* tools.c —— 定义在这里，但编译 main.c 时看不到它 */</span>''')
t = t.replace('''<span class="hl-c">/* main.cpp（使用） */</span>''', '''<span class="hl-c">/* main.c（使用） */</span>''')
t = t.replace('<code>main.cpp</code>', '<code>main.c</code>')
t = t.replace('<code>tools.cpp</code>', '<code>tools.c</code>')
t = t.replace('main.cpp', 'main.c')
t = t.replace('tools.cpp', 'tools.c')
t = t.replace('font.cpp', 'font.c')
t = t.replace('-std=c++17', '-std=c99')
t = t.replace('g++', 'gcc')
t = t.replace('C++ 源代码', 'C 源代码')
t = t.replace('把 C++ 翻译成机器指令', '把 C 翻译成机器指令')
t = t.replace('为什么要写头文件、C++ 怎么', '为什么要写头文件、C 怎么')
t = t.replace('用哪个 C++ 标准', '用哪个 C 标准')
t = t.replace('C/C++ 混编没写 <code>extern "C"</code>', 'C++ 与 C 混编时没写 <code>extern "C"</code>')
t = t.replace('C++ 会对函数名做修饰，C 不会', 'C++ 会对函数名做「名字修饰」，C 不会 —— 链接时名字对不上')
save(n, t)
print("F03：已 C 化")


# =====================================================================
# F04：字节打印示例 cout → printf
# =====================================================================
n = "_ds_09_F04_Unicode和编码.html"
t = load(n)
old_start = '<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>'
i0 = t.find(old_start)
if i0 >= 0:
    i1 = t.find('</pre></div>', i0)
    seg = t[i0:i1]
    new_seg = '''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>

<span class="hl-k">void</span> <span class="hl-f">dump_bytes</span>(<span class="hl-k">const</span> <span class="hl-k">char</span> *s, <span class="hl-k">const</span> <span class="hl-k">char</span> *label) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%s (%d 字节): "</span>, label, (<span class="hl-k">int</span>)<span class="hl-f">strlen</span>(s));
    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; (<span class="hl-k">int</span>)<span class="hl-f">strlen</span>(s); i++) {
        <span class="hl-f">printf</span>(<span class="hl-s">"%02X "</span>, (<span class="hl-k">unsigned</span> <span class="hl-k">char</span>)s[i]);
    }
    <span class="hl-f">printf</span>(<span class="hl-s">"\\n"</span>);
}

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">dump_bytes</span>(<span class="hl-s">"A"</span>, <span class="hl-s">"ASCII 里的 A"</span>);
    <span class="hl-f">dump_bytes</span>(<span class="hl-s">"\\xC3\\xA9"</span>, <span class="hl-s">"e 带音标 U+00E9"</span>);
    <span class="hl-f">dump_bytes</span>(<span class="hl-s">"\\xE4\\xB8\\xAD"</span>, <span class="hl-s">"中 U+4E2D"</span>);
    <span class="hl-f">dump_bytes</span>(<span class="hl-s">"\\xE1\\xA0\\xAE"</span>, <span class="hl-s">"蒙文 MA U+182E"</span>);
    <span class="hl-f">dump_bytes</span>(<span class="hl-s">"\\xF0\\x9F\\x98\\x80"</span>, <span class="hl-s">"笑脸 U+1F600"</span>);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}'''
    t = t[:i0] + new_seg + t[i1:]
    print("F04：字节打印 → C")

# 那段 cout 的 size() 示例
t = t.replace('''string mongol = <span class="hl-s">"\\u182E\\u1823\\u1829\\u182D\\u1823\\u182F"</span>;   <span class="hl-c">/* ᠮᠣᠩᠭᠣᠯ */</span>

<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"size() = "</span> &lt;&lt; mongol.<span class="hl-f">size</span>() &lt;&lt; <span class="hl-s">" 字节"</span> &lt;&lt; <span class="hl-f">endl</span>;''',
'''<span class="hl-c">/* ᠮᠣᠩᠭᠣᠯ：6 个蒙文字母，每个 3 字节 */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *mongol =
    <span class="hl-s">"\\xE1\\xA0\\xAE\\xE1\\xA0\\xA3\\xE1\\xA0\\xA9"</span>
    <span class="hl-s">"\\xE1\\xA0\\xAD\\xE1\\xA0\\xA3\\xE1\\xA0\\xAF"</span>;

<span class="hl-f">printf</span>(<span class="hl-s">"strlen = %d 字节\\n"</span>, (<span class="hl-k">int</span>)<span class="hl-f">strlen</span>(mongol));''')
t = t.replace('''<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"sizeof(char)    = "</span> &lt;&lt; <span class="hl-k">sizeof</span>(<span class="hl-k">char</span>) &lt;&lt; <span class="hl-f">endl</span>;
<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"sizeof(wchar_t) = "</span> &lt;&lt; <span class="hl-k">sizeof</span>(<span class="hl-k">wchar_t</span>) &lt;&lt; <span class="hl-f">endl</span>;''',
'''<span class="hl-f">printf</span>(<span class="hl-s">"sizeof(char)    = %d\\n"</span>, (<span class="hl-k">int</span>)<span class="hl-k">sizeof</span>(<span class="hl-k">char</span>));
<span class="hl-f">printf</span>(<span class="hl-s">"sizeof(wchar_t) = %d\\n"</span>, (<span class="hl-k">int</span>)<span class="hl-k">sizeof</span>(<span class="hl-k">wchar_t</span>));''')
t = t.replace('g++ 13.1.0（<code>-std=c++17 -fexec-charset=UTF-8</code>）',
              'gcc 13.1.0（<code>-std=c99</code>）')
t = t.replace('g++ 13.1.0', 'gcc 13.1.0')
save(n, t)
print("F04：已 C 化")
print("")
for f in ["_ds_08_F01_命令提示符初步.html", "_ds_08_F03_编译与链接、头文件与库.html",
          "_ds_09_F04_Unicode和编码.html"]:
    tt = load(f)
    print("%-46s cout=%d iostream=%d g++=%d"
          % (f, len(re.findall(r'cout', tt)), len(re.findall(r'iostream', tt)),
             len(re.findall(r'g\+\+', tt))))
