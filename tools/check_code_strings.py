# -*- coding: utf-8 -*-
"""检查代码块里的字符串字面量有没有被写成真换行。

为什么需要这个检查
    HTML 的 <pre> 会原样渲染换行。所以 `printf("%d\\n", x)` 里的 \\n
    必须是**两个字符**（反斜杠 + n）。如果源码里落了真换行，页面就会变成：

        printf("%d
        ", x);

    看起来像语法错误，而所有结构性检查（标签配平、溢出、暗色对比度）
    都发现不了它 —— 它只是「长得不对」。

    这个坑本会话撞了三次：
        ① Q07 的 C 示例
        ② M04 新增「退化」小节时
        ③ M04 与 M05 里本来就有的（m05 一次 24 处）

    所以做成固定检查，跟 check_docs / check_page_classes 一起跑。

检查范围
    · <pre> 内、<span class="hl-s">"…"</span> 这个字符串标签
    · 以及 <pre> 内任何 hl-s 标签里的真换行
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# 只找 <pre> 块；其它地方（正文、表格）的换行是正常的
PRE_RE = re.compile(r"<pre>(.*?)</pre>", re.S)
STR_RE = re.compile(r'<span class="hl-s">"([^"]*)"</span>')

bad_pages = 0
bad_total = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    p = os.path.join(T, f)
    try:
        t = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    hits = []
    for pm in PRE_RE.finditer(t):
        block = pm.group(1)
        for sm in STR_RE.finditer(block):
            if "\n" in sm.group(1):
                holes = sm.group(1).count("\n")
                bad_total += holes
                hits.append((holes, sm.group(1)[:40].replace("\n", "⏎")))
    if hits:
        bad_pages += 1
        print("  !! %-12s %d 处" % (f, sum(h[0] for h in hits)))
        for n, sample in hits[:3]:
            print("        %d 个换行：%s" % (n, sample))

print()
print("  字符串里含真换行：%d 页 / %d 处  %s"
      % (bad_pages, bad_total, "OK" if bad_total == 0 else "FAIL"))
