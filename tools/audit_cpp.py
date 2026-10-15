# -*- coding: utf-8 -*-
"""扫描 09 之前的文档，找出所有含 C++ 特征的地方。

C++ 特征（C 里没有或含义不同的）：
  · 头文件        <iostream> <string> <vector> <array> <fstream> <algorithm>
  · 流对象        cout cin cerr endl std::
  · 类            class / public: / private: / protected:
  · 访问控制与成员函数  类内函数定义、构造函数、析构函数
  · 引用          int& / const T&
  · 作用域解析    ::value
  · 关键字        bool true false nullptr new delete namespace using template
  · 重载 / 默认参数
  · 字符串类      std::string
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

# 这些文档不做 C++ 审查（本身就是 C++ 主题 / 09 及以后）
SKIP = ("_ds_09_vector和array.html", "_ds_09_F04_Unicode和编码.html")

FEATURES = [
    ("iostream 头",   r"&lt;iostream&gt;"),
    ("string 头",     r"&lt;string&gt;"),
    ("vector/array 头", r"&lt;vector&gt;|&lt;array&gt;"),
    ("fstream 头",    r"&lt;fstream&gt;"),
    ("algorithm 头",  r"&lt;algorithm&gt;"),
    ("cout/cin",      r"\bcout\b|\bcin\b|\bcerr\b"),
    ("std::",         r"std::"),
    ("endl",          r"\bendl\b"),
    ("class 定义",    r'<span class="hl-k">class</span>'),
    ("public/private", r'<span class="hl-k">public</span>|<span class="hl-k">private</span>|<span class="hl-k">protected</span>'),
    ("引用 &",        r'<span class="hl-k">int</span> &amp;|<span class="hl-k">const</span> [A-Za-z_]+ &amp;|&amp;[a-z]'),
    (":: 作用域",     r"::[a-zA-Z_]"),
    ("bool/true/false", r'<span class="hl-k">bool</span>|<span class="hl-k">true</span>|<span class="hl-k">false</span>'),
    ("nullptr",       r"nullptr"),
    ("new/delete",    r'<span class="hl-k">new</span>|<span class="hl-k">delete</span>'),
    ("namespace/using", r"namespace"),
    ("template",      r'<span class="hl-k">template</span>'),
    ("STL 容器用法",  r"\bvector&lt;|\barray&lt;|\bstring "),
    ("inline",        r'<span class="hl-k">inline</span>'),
]

print("=" * 96)
for name in sorted(os.listdir(ROOT)):
    if not name.endswith(".html") or name in SKIP:
        continue
    p = os.path.join(ROOT, name)
    with io.open(p, encoding="utf-8") as fh:
        t = fh.read()

    # 逐个代码块扫
    blocks = list(re.finditer(r'(?s)<div class="code-wrap">.*?</pre></div>', t))
    hit_blocks = []
    for i, b in enumerate(blocks, 1):
        seg = b.group(0)
        found = [label for label, pat in FEATURES if re.search(pat, seg)]
        if found:
            m = re.search(r'<span class="name">([^<]*)</span>', seg)
            title = m.group(1) if m else "(无标题)"
            hit_blocks.append((i, title, found))

    badges = len(re.findall(r'class="cpp-badge"', t))
    if hit_blocks or badges:
        print("\n### %s   （代码块 %d 个，现有 C++ 徽标 %d 个）" % (name, len(blocks), badges))
        for i, title, found in hit_blocks:
            print("   块%-3d %-30s  %s" % (i, title[:30], "、".join(found)))
        if not hit_blocks:
            print("   （无 C++ 代码块，但有徽标 → 可能徽标是加在散文/卡片上的）")
