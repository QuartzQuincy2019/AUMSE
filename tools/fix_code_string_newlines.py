# -*- coding: utf-8 -*-
"""修 M04 代码块里「字符串字面量中的真换行」。

问题
    HTML 的 <pre> 里，`printf("%d\n", ...)` 中的 `\\n` 必须是**两个字符**
    （反斜杠 + n）。一旦源码里写成了真换行，浏览器就按 <pre> 断行渲染：

        printf("sizeof(p)   = %zu
        ", sizeof p);

    看起来像语法错误。

    这个坑本轮已经踩了第三次：
        ① 写 Q07 的 C 示例时
        ② 本轮给 M04 加「退化」小节时（生成脚本里用了普通字符串，
           而不是 \\\\n 转义）
        ③ M04 里本来就有两处（"%d\\n"）—— 一直没被发现

    所以除了修，还要把检查做成固定脚本：tools/check_code_strings.py

修法
    只在 <pre> 内、且 <span class="hl-s">"…"</span> 这个字符串标签里，
    把真换行换成字面的 \\n。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

STR_RE = re.compile(r'(<span class="hl-s">")([^"]*)("</span>)')

total = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    p = os.path.join(T, f)
    t = io.open(p, encoding="utf-8").read()
    n = [0]

    def fix(m):
        inner = m.group(2)
        if "\n" not in inner:
            return m.group(0)
        n[0] += inner.count("\n")
        return m.group(1) + inner.replace("\n", "\\n") + m.group(3)

    t2 = STR_RE.sub(fix, t)
    if t2 != t:
        io.open(p, "w", encoding="utf-8", newline="").write(t2)
        total += n[0]
        print("  %-10s 修了 %d 处字符串里的真换行" % (f, n[0]))

print()
print("  合计修 %d 处" % total)
