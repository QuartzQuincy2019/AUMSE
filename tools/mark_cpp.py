# -*- coding: utf-8 -*-
"""给 06 / F02 / F03 补齐 C++ 标识。

06：错误 2「忘把数据放 private」那个对比块是 C++，漏标了 → 补上。
    并把第 4 节那个 C++ 说明框扩写，明确「哪些块是 C++、哪些是 C」。
F02：附加包含目录那个例子用了 QString（Qt/C++）→ 在块里加一行 C++ 提示。
F03：inline 相关块、class 块、App.cpp → 补 C++ 徽标；
     并把 App.cpp 改成 C 风格 I/O（printf），与全系列一致。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"


def load(n):
    with io.open(ROOT + "\\" + n, encoding="utf-8") as fh:
        return fh.read()


def save(n, t):
    with io.open(ROOT + "\\" + n, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)


done = []

# =====================================================================
# 06
# =====================================================================
n = "_ds_06_类、结构体.html"
t = load(n)

# ---- 1) 补上漏标的 C++ 对比块 ----
old = ('<span class="name">对比</span><span class="cp">复制</span></div>'
       '<pre><span class="hl-c">/* ❌ 数据全公开，保护形同虚设 */</span>\n'
       '<span class="hl-k">class</span> Player {')
new = ('<span class="name">对比</span><span class="cpp-badge">C++</span>'
       '<span class="cp">复制</span></div>'
       '<pre><span class="hl-c">/* ❌ 数据全公开，保护形同虚设 */</span>\n'
       '<span class="hl-k">class</span> Player {')
if old in t:
    t = t.replace(old, new, 1)
    done.append("06 块12（忘放 private 的对比）→ 补 C++ 徽标")
else:
    print("  !! 06 块12 未匹配")

# ---- 2) 扩写 C++ 说明框 ----
oldnote = '''<div class="cpp-note">
  <div class="t2">本节开始出现 C++ —— 已用紫色「C++」徽标标出</div>
  <p>本文档其余部分是 <b>C</b>。但「把函数放进结构体里」这件事
  <b>C 语言做不到</b>，它是 C++ 的特性，所以接下来几段代码是 C++。</p>
  <p>看到<b>紫色 C++ 徽标</b>就说明：这段代码需要 <code>g++</code>
  而不是 <code>gcc</code> 来编译。</p>
</div>'''

newnote = '''<div class="cpp-note">
  <div class="t2">从这里开始会出现 C++ —— 带紫色「C++」徽标的才是</div>
  <p>本文档<b>大部分是 C</b>。「把函数放进结构体里」这件事
  <b>C 语言做不到</b>，它是 C++ 的特性，所以接下来有几段代码是 C++。</p>
  <p><b>怎么区分</b>：代码块标题栏上带<b>紫色「C++」徽标</b>的，就是 C++；
  没有徽标的一律是 C。</p>
  <table style="margin:10px 0 8px">
  <thead><tr><th style="width:22%">本文档</th><th>语言</th></tr></thead>
  <tbody>
  <tr><td>第 2~3 节</td><td><b>C</b> —— <code>struct</code> 定义、用 <code>.</code> 读写成员</td></tr>
  <tr><td>第 4 节「成员函数」起</td><td><b>C++</b> <span class="cpp-badge">C++</span> —— 把函数放进结构体</td></tr>
  <tr><td>第 5 节「私有与共享成员」</td><td><b>C++</b> <span class="cpp-badge">C++</span> —— <code>class</code> / <code>private</code></td></tr>
  <tr><td>第 7 节「对象的生与死」</td><td><b>C</b> —— 用 <code>xxx_init</code> / <code>xxx_destroy</code> 约定代替构造函数</td></tr>
  <tr><td>第 8 节常见错误</td><td>两种都有，<b>看徽标</b></td></tr>
  </tbody></table>
  <p><b>编译方式也不同</b>：带徽标的用 <code>g++</code>（或 Visual Studio 的
  <code>.cpp</code>），没徽标的用 <code>gcc</code>（或 <code>.c</code>）。</p>
</div>'''

if oldnote in t:
    t = t.replace(oldnote, newnote, 1)
    done.append("06 → 扩写 C++ 说明框（含逐节对照表）")
else:
    print("  !! 06 说明框未匹配")

save(n, t)
print("06：%d 字符，C++ 徽标 %d 个"
      % (len(t), len(re.findall(r'class="cpp-badge"', t)) - 1))

# =====================================================================
# F03
# =====================================================================
n = "_ds_08_F03_编译与链接、头文件与库.html"
t = load(n)

# ---- 1) App.cpp 改成 C 风格 I/O，并加 C++ 徽标 ----
oldapp = '''<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">App.cpp</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>       <span class="hl-c">// 只用引号：这是「自己写的头文件」</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_add(2, 3)      = "</span> &lt;&lt; <span class="hl-f">ume_add</span>(<span class="hl-n">2</span>, <span class="hl-n">3</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_mul(4, 5)      = "</span> &lt;&lt; <span class="hl-f">ume_mul</span>(<span class="hl-n">4</span>, <span class="hl-n">5</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_clamp(99,0,10) = "</span> &lt;&lt; <span class="hl-f">ume_clamp</span>(<span class="hl-n">99</span>, <span class="hl-n">0</span>, <span class="hl-n">10</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_max(7, 9)      = "</span> &lt;&lt; <span class="hl-f">ume_max</span>(<span class="hl-n">7</span>, <span class="hl-n">9</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;  <span class="hl-c">// inline 的</span>
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"kUmeVersion        = "</span> &lt;&lt; kUmeVersion &lt;&lt; <span class="hl-s">"\\n"</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>'''

newapp = '''<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">App.cpp</span><span class="cpp-badge">C++</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>          <span class="hl-c">// 用 C 的输入输出，和前面几讲一致</span>
<span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>       <span class="hl-c">// 只用引号：这是「自己写的头文件」</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">printf</span>(<span class="hl-s">"ume_add(2, 3)      = %d\\n"</span>, <span class="hl-f">ume_add</span>(<span class="hl-n">2</span>, <span class="hl-n">3</span>));
    <span class="hl-f">printf</span>(<span class="hl-s">"ume_mul(4, 5)      = %d\\n"</span>, <span class="hl-f">ume_mul</span>(<span class="hl-n">4</span>, <span class="hl-n">5</span>));
    <span class="hl-f">printf</span>(<span class="hl-s">"ume_clamp(99,0,10) = %d\\n"</span>, <span class="hl-f">ume_clamp</span>(<span class="hl-n">99</span>, <span class="hl-n">0</span>, <span class="hl-n">10</span>));
    <span class="hl-f">printf</span>(<span class="hl-s">"ume_max(7, 9)      = %d\\n"</span>, <span class="hl-f">ume_max</span>(<span class="hl-n">7</span>, <span class="hl-n">9</span>));  <span class="hl-c">// 这个是 inline 的</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"kUmeVersion        = %d\\n"</span>, kUmeVersion);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>'''

if oldapp in t:
    t = t.replace(oldapp, newapp, 1)
    done.append("F03 App.cpp → 改用 printf，并加 C++ 徽标")
else:
    print("  !! F03 App.cpp 未匹配")

# ---- 2) 给 inline / class 相关块补徽标 ----
badge_targets = [
    ("ume_math.h —— 对外公开的头文件", "ume_math.h —— 对外公开的头文件"),
    ("类内直接写函数体 = 自动 inline", "类内直接写函数体 = 自动 inline"),
]
for name, label in badge_targets:
    old = '<span class="name">%s</span>' % name
    new = '<span class="name">%s</span><span class="cpp-badge">C++</span>' % name
    if old in t and new not in t:
        t = t.replace(old, new, 1)
        done.append("F03 「%s」→ 补 C++ 徽标" % label)

# 「对比」块里含 inline 的两处（第 10 节错误 1、错误 3 附近）单独处理：
# 用「内容特征」定位，避免误伤其他「对比」块
def badge_compare(anchor_snippet, label):
    global t
    i = t.find(anchor_snippet)
    if i < 0:
        print("  !! F03 未找到：%s" % label)
        return
    # 往前找这个块的 <span class="name">对比</span>
    j = t.rfind('<span class="name">对比</span>', 0, i)
    if j < 0:
        print("  !! F03 未找到块标题：%s" % label)
        return
    seg = t[j:j + 200]
    if 'cpp-badge' in seg:
        return
    t = t[:j] + '<span class="name">对比</span><span class="cpp-badge">C++</span>' + t[j + len('<span class="name">对比</span>'):]
    done.append("F03 「%s」所在对比块 → 补 C++ 徽标" % label)

badge_compare('<span class="hl-c">// ❌ 被两个 .cpp 包含就报 LNK2005</span>', "头文件忘加 inline")
badge_compare('<span class="hl-c">// ❌ 只写名字，不写在哪</span>', "附加依赖项对比")

save(n, t)
print("F03：%d 字符，C++ 徽标 %d 个"
      % (len(t), len(re.findall(r'class="cpp-badge"', t)) - 1))
print("    剩余 cout/iosteam: %d" % len(re.findall(r'cout|iostream', t)))

# =====================================================================
# F02：QString 那一处
# =====================================================================
n = "_ds_08_F02_相对文件路径与宏.html"
t = load(n)
old = '<span class="hl-c">/* ✅ 明确从 exe 所在目录找（Qt 里用 applicationDirPath） */</span>'
new = ('<span class="hl-c">/* ✅ 明确从 exe 所在目录找（下面这行是 Qt / C++） */</span>')
if old in t:
    t = t.replace(old, new, 1)
    # 找到该块的标题并补一个「含 C++」提示
    i = t.find(new)
    j = t.rfind('<span class="name">对比</span>', 0, i)
    if j >= 0 and 'cpp-badge' not in t[j:j + 200]:
        t = t[:j] + '<span class="name">对比</span><span class="cpp-badge">含 C++</span>' + t[j + len('<span class="name">对比</span>'):]
        done.append("F02 坑1 对比块 → 标「含 C++」（用了 QString）")
save(n, t)
print("F02：%d 字符" % len(t))

print("")
print("完成项：")
for d in done:
    print("  ✓ " + d)
