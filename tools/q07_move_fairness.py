# -*- coding: utf-8 -*-
"""Q07：把「说句公道话」的第一行改成醒目强调，并移到第 3 节最后。

用户要求
    1. 将「说句公道话」的**第一行**改为醒目强调的格式，放在第 3 节最后
    2. （第 3 节 = 「直接实现：题面数据内嵌于主函数」）

做法
    · 第 3 节末尾插一个 .take 强调块（与小结里那个同一个样式类，
      是页面上最醒目的结论样式），内容就是那一行：
      「如果这道题只交一次、永不再改，写死在 main 里是完全合理的」
    · 原来那张 .card.warn「说句公道话」整张删掉 —— 第一行已经搬走，
      剩下的两句在第 12 节（改造前后的对照）之后本来也是重复论述。
      若用户还要那两句，可以单独再加回第 3 节。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\_q07_body.html"
t = io.open(P, encoding="utf-8").read()

CARD_START = '<div class="card warn">\n  <div class="card-t">说句公道话</div>'
i = t.find(CARD_START)
if i < 0:
    print("  !! 找不到「说句公道话」卡片")
    sys.exit(1)
# 卡片结尾：从卡片起点往后，第 3 个 </div> 之后
j = i
for _ in range(3):
    j = t.find("</div>", j) + 6
card = t[i:j]
print("  原卡片 %d 字符" % len(card))

# 移除卡片，并把后面多余的空行收掉
t2 = t[:i] + t[j:]
t2 = re.sub(r"\n{3,}(<h2 id=\"s12\")", r"\n\n\1", t2)

# 强调块
TAKE = """
<div class="take">
  <b>说句公道话：</b>如果这道题<b>只交一次、永不再改</b>，
  写死在 <code>main</code> 里是 <b>完全合理的</b> ——
  更快、更短、也没有什么可维护的。
  拆成类型是为了「<b>会变</b>」；真实的项目里需求永远在变，
  所以这个投入是值的。
</div>
"""

# 插到第 3 节最后（第 4 节开始之前）
i4 = t2.find('<h2 id="s4">')
if i4 < 0:
    print("  !! 找不到 s4，无法定位第 3 节结尾")
    sys.exit(1)
t2 = t2[:i4].rstrip() + "\n" + TAKE + "\n" + t2[i4:]

# ---- 自检 ----
print()
print("  「说句公道话」出现次数：%d（原卡片已删）" % t2.count("说句公道话"))
print("  第 3 节末尾 260 字符：")
print(repr(t2[i4 - 400:i4]))
print()
hs = re.findall(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                t2, re.S)
print("  小节 %d 个：" % len(hs))
for sid, no, ttl in hs:
    print("      %-4s %-3s %s" % (sid, no, re.sub(r"<[^>]+>", "", ttl).strip()))
print()
print("  .take 块数：%d" % t2.count('class="take"'))
print("  正文 %d 字符" % len(t2))
print("  markdown ** 残留：%d" % t2.count("**"))

io.open(P, "w", encoding="utf-8", newline="").write(t2)
print("  已写入")
