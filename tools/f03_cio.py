# -*- coding: utf-8 -*-
"""F03 第 8 节：把示例代码统一成 C 风格 I/O（printf / stdio.h）。

理由：教程 01~08 教的是 C 的输入输出，成员没见过 cout。
第 8 节讲的是「VS 里做静态库」这件事，没必要顺带引入 iostream。
改用 printf 之后，第 8 节里唯一的 C++ 元素就只剩 inline ——
而那正是第 9 节要讲的，边界反而更清楚。

（注意：PowerShell 5.1 的 String.Replace 没有三参重载，
 之前用 PS 改写失败，所以这里用 Python 精确替换。）
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F03_编译与链接、头文件与库.html"
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


# ---------------------------------------------------------------------
# 1) 头文件示例：去掉 cout，保留 inline（那是第 9 节的主题）
# ---------------------------------------------------------------------
sub('''<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;''',
    '''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>''',
    "头文件/实现里的 iostream → stdio.h")

t = t.replace('<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>',
              '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>')
t = t.replace('<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>',
              '<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>')
t = t.replace('<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n', '')

# ---------------------------------------------------------------------
# 2) 各种 cout 语句 → printf
# ---------------------------------------------------------------------
COUT_MAP = [
    ('    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_add(2, 3)      = "</span> &lt;&lt; <span class="hl-f">ume_add</span>(<span class="hl-n">2</span>, <span class="hl-n">3</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"ume_add(2, 3)      = %d\\n"</span>, <span class="hl-f">ume_add</span>(<span class="hl-n">2</span>, <span class="hl-n">3</span>));'),
    ('    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_mul(4, 5)      = "</span> &lt;&lt; <span class="hl-f">ume_mul</span>(<span class="hl-n">4</span>, <span class="hl-n">5</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"ume_mul(4, 5)      = %d\\n"</span>, <span class="hl-f">ume_mul</span>(<span class="hl-n">4</span>, <span class="hl-n">5</span>));'),
    ('    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_clamp(99,0,10) = "</span> &lt;&lt; <span class="hl-f">ume_clamp</span>(<span class="hl-n">99</span>, <span class="hl-n">0</span>, <span class="hl-n">10</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"ume_clamp(99,0,10) = %d\\n"</span>, <span class="hl-f">ume_clamp</span>(<span class="hl-n">99</span>, <span class="hl-n">0</span>, <span class="hl-n">10</span>));'),
    ('    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_max(7, 9)      = "</span> &lt;&lt; <span class="hl-f">ume_max</span>(<span class="hl-n">7</span>, <span class="hl-n">9</span>) &lt;&lt; <span class="hl-s">"\\n"</span>;  <span class="hl-c">// inline 的</span>',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"ume_max(7, 9)      = %d\\n"</span>, <span class="hl-f">ume_max</span>(<span class="hl-n">7</span>, <span class="hl-n">9</span>));  <span class="hl-c">// 用的是 inline 函数</span>'),
    ('    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"kUmeVersion        = "</span> &lt;&lt; kUmeVersion &lt;&lt; <span class="hl-s">"\\n"</span>;',
     '    <span class="hl-f">printf</span>(<span class="hl-s">"kUmeVersion        = %d\\n"</span>, kUmeVersion);'),
]
for old, new in COUT_MAP:
    if old in t:
        t = t.replace(old, new)
        done.append("cout → printf")
    else:
        print("  · 未匹配（可能已改）: %s" % old[:56])

# main 签名
t = t.replace('<span class="hl-k">int</span> <span class="hl-f">main</span>() {',
              '<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {')

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("")
print("F03：%d → %d 字符" % (orig, len(t)))
for d in set(done):
    print("  ✓ " + d)
print("")
print("剩余 cout: %d   iostream: %d   std::: %d"
      % (len(re.findall(r'cout', t)), len(re.findall(r'iostream', t)), len(re.findall(r'std::', t))))
for m in re.finditer(r'.{0,60}(cout|iostream|std::).{0,60}', t):
    print("   ..." + m.group(0).replace("\n", " ").strip()[:110])
