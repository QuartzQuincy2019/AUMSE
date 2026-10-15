# -*- coding: utf-8 -*-
"""F02 修正：第 8 节被插到了第 7 节前面，把它移到文档末尾（页脚之前）。

原因：旧「项目里的实际用处」那一节的结束位置正好在第 7 节之前，
我在那里插入新内容，结果顺序变成了 …6, 8, 7。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F02_相对文件路径与宏.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)

# 切出第 8 节（从它的分隔注释到 <footer>）
m8 = re.search(
    r'(?s)(<!-- =+\s*-->\s*)?<h2 id="s8">.*?(?=<footer>)', t)
if not m8:
    raise SystemExit("没找到第 8 节")

block8 = m8.group(0)
t = t[:m8.start()] + t[m8.end():]

# 插到 </main> 之前（也就是页脚之后、正文末尾）
i = t.index('<footer>')
t = t[:i] + block8.rstrip() + "\n\n" + t[i:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("已重排：%d → %d 字符" % (orig, len(t)))
print("")
print("=== 现在的 h2 顺序 ===")
for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', t):
    print("  " + (m.group(2) - re.sub(r'<[^>]+>', '', m.group(2))))
print("")
print("=== 现在的 h3 顺序 ===")
for m in re.finditer(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', t):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
