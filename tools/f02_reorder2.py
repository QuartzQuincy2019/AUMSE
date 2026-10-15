# -*- coding: utf-8 -*-
"""F02：把 s8 整块移到 s7 之后（正文末尾、footer 之前）。"""
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

i8 = t.index('<h2 id="s8">')
i7 = t.index('<h2 id="s7">')
assert i8 < i7, "顺序已经是对的"

# s8 整块：从 <h2 id="s8"> 本身开始（它前面没有自己的分隔注释），
# 到 s7 的分隔注释之前结束
start = i8

# s7 的分隔注释作为 s8 块的结束
end = t.rfind('<!-- =', 0, i7)
assert end > i8, "找不到 s7 的分隔注释"
assert '<h2' not in t[end:i7], "s7 分隔注释前夹了别的内容"

block8 = t[start:end]
t = t[:start] + t[end:]

# 插到 footer 之前。注意从 end 开始往回找 —— 否则会找到 s7 自己的分隔注释，
# 于是「删掉再插回原处」，顺序不变（这是上一版没生效的原因）。
fi = t.index('<footer>')
fpre = t.rfind('<!-- =', end, fi)
if fpre == -1:
    fpre = fi
assert fpre > end, "插入点仍在 s7 之前"
t = t[:fpre] + block8.rstrip() + "\n\n" + t[fpre:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("已重排：%d → %d 字符" % (orig, len(t)))
print("")
print("h2 顺序：")
import re
for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', t):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
print("")
print("h3 顺序：")
for m in re.finditer(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', t):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
print("")
ids = re.findall(r'id="([^"]+)"', t)
dups = sorted({i for i in ids if ids.count(i) > 1})
print("重复 id: %s" % (", ".join(dups) if dups else "无"))
