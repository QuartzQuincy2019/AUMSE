# -*- coding: utf-8 -*-
"""F02 最终重排。

目标顺序：
    1 2 3 4 5 6 7（坑 1~6）→ 8（VS 宏）→ 总结卡 → 下一步 → footer

原来 s8 被插在了 7 前面，且「总结卡 / 下一步」两张卡在 7 的末尾。
按标记精确定位，而不是靠猜索引。
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F02_相对文件路径与宏.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)

# ---- 定位 ----
i8 = t.index('<h2 id="s8">')
i7 = t.index('<h2 id="s7">')
i_sum = t.index('<div class="card key">\n  <div class="card-t">这一篇要记住的四件事</div>')
i_next = t.index('<div class="card note">\n  <div class="card-t">下一步</div>')
i_footer = t.index('<footer>')

assert i8 < i7 < i_sum < i_next < i_footer, "元素顺序与预期不符，先人工检查"

# ---- 切块 ----
s7_div = t.rfind('<!-- =', 0, i7)          # s7 的分隔注释
assert s7_div > i8

block8 = t[i8:s7_div]                       # 第 8 节（含尾随空行）
middle = t[s7_div:i_sum]                    # s7 的分隔注释 + 7 全部内容
tailcards = t[i_sum:i_footer]               # 总结卡 + 下一步

# ---- 重组 ----
new = t[:i8] + middle + block8.rstrip() + "\n\n" + tailcards.rstrip() + "\n\n" + t[i_footer:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(new)

print("重排：%d → %d 字符" % (orig, len(new)))
print("")
import re
print("h2 顺序：")
for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', new):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
print("")
print("h3 顺序：")
for m in re.finditer(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', new):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
print("")
ids = re.findall(r'id="([^"]+)"', new)
dups = sorted({i for i in ids if ids.count(i) > 1})
print("重复 id: %s" % (", ".join(dups) if dups else "无"))
print("footer 在 </main> 之前: %s" % (new.index('<footer>') < new.index('</main>')))
