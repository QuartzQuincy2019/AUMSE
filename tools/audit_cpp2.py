# -*- coding: utf-8 -*-
"""精确审计：只找 C 里**确实没有**的 C++ 构造。

排除误报：
  · &x 取地址        —— C 也有（第三、四讲讲过）
  · -> 成员访问      —— C 也有
  · struct 定义      —— C 也有
  · // 注释          —— C99 起合法
真正的 C++ 特征只有下面这些。
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
SKIP = ("_ds_09_vector和array.html", "_ds_09_F04_Unicode和编码.html")

TRUE_CPP = [
    ("iostream 头",  r"&lt;iostream&gt;"),
    ("string 头",    r"&lt;string&gt;"),
    ("STL 头",       r"&lt;vector&gt;|&lt;array&gt;|&lt;algorithm&gt;|&lt;fstream&gt;"),
    ("cout/cin/cerr", r'<span class="hl-f">cout</span>|\bcout\b|<span class="hl-f">cin</span>|\bcin\b'),
    ("std::",        r"std::"),
    ("class 关键字", r'<span class="hl-k">class</span>'),
    ("public/private/protected", r'<span class="hl-k">public</span>|<span class="hl-k">private</span>|<span class="hl-k">protected</span>'),
    ("引用类型 T&",  r'<span class="hl-k">int</span> &amp;[a-z]|<span class="hl-k">const</span> [A-Za-z_:]+ &amp;[a-z]|<span class="hl-k">int</span> &amp;<span class="hl-f">'),
    (":: 作用域解析", r"::[a-zA-Z_]"),
    ("bool/true/false", r'<span class="hl-k">bool</span>|<span class="hl-k">true</span>|<span class="hl-k">false</span>'),
    ("nullptr",      r"nullptr"),
    ("new/delete",   r'<span class="hl-k">new</span>|<span class="hl-k">delete</span>'),
    ("namespace/using", r"namespace"),
    ("template",     r'<span class="hl-k">template</span>'),
    ("inline",       r'<span class="hl-k">inline</span>'),
    ("std::string",  r'<span class="hl-k">string</span> [a-z]|string name|QString'),
]

print("=" * 100)
total = 0
for name in sorted(os.listdir(ROOT)):
    if not name.endswith(".html") or name in SKIP:
        continue
    p = os.path.join(ROOT, name)
    with io.open(p, encoding="utf-8") as fh:
        t = fh.read()

    blocks = list(re.finditer(r'(?s)<div class="code-wrap">.*?</pre></div>', t))
    rows = []
    for i, b in enumerate(blocks, 1):
        seg = b.group(0)
        found = [lab for lab, pat in TRUE_CPP if re.search(pat, seg)]
        if found:
            m = re.search(r'<span class="name">([^<]*)</span>', seg)
            title = (m.group(1) if m else "(无标题)")
            badged = 'cpp-badge' in seg
            rows.append((i, title, found, badged))

    # 非代码块里的 C++ 痕迹（散文、卡片内嵌 pre）
    inline_pres = [m for m in re.finditer(r'(?s)<pre[^>]*>(.*?)</pre>', t)
                   if 'code-wrap' not in t[max(0, m.start() - 200):m.start()]]
    prose_cpp = 0
    for m in inline_pres:
        if re.search(r'cout|std::|&lt;iostream&gt;|hl-k">class</span>|hl-k">inline</span>', m.group(1)):
            prose_cpp += 1

    badges = len(re.findall(r'class="cpp-badge"', t))
    if rows or prose_cpp or badges:
        total += 1
        print("\n### %s" % name)
        print("    代码块 %d 个 | C++ 徽标 %d 个 | 卡片内嵌 pre 含 C++ %d 处"
              % (len(blocks), badges, prose_cpp))
        for i, title, found, badged in rows:
            mark = "✔已标" if badged else "✘未标"
            print("    %s  块%-3d %-28s %s" % (mark, i, title[:28], "、".join(found)))

print("\n" + "=" * 100)
print("涉及 C++ 的文档数：%d" % total)
