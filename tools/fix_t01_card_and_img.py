# -*- coding: utf-8 -*-
"""改 build_t01.py：
   ① 删掉「这些蒙文是怎么打出来的」那张 card
   ② 用 zhaocaijinbao.webp 图片替换 ASCII 招财进宝
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\build_t01.py"
t = io.open(P, encoding="utf-8").read()
n = 0

# ---------- ① 删掉那张 card ----------
start_mark = '<div class="card note">\n  <div class="card-t">这些蒙文是怎么打出来的</div>'
i = t.find(start_mark)
if i >= 0:
    # 找这张 card 的收尾 </div>（靠层数配平）
    k = t.find(">", i) + 1
    depth = 0
    j = i
    while j < len(t):
        if t.startswith("<div", j):
            depth += 1
            j += 4
        elif t.startswith("</div>", j):
            depth -= 1
            if depth == 0:
                j += len("</div>")
                break
            j += 6
        else:
            j += 1
    # 连带前面的空行一起删
    a = i
    while a > 0 and t[a - 1] in "\r\n":
        a -= 1
    t = t[:a] + "\n\n" + t[j:].lstrip("\r\n")
    n += 1
    print("  ✓ 删掉「这些蒙文是怎么打出来的」card")
else:
    print("  ! 没找到那张 card")

# ---------- ② ASCII 招财进宝 → 图片 ----------
old = '''<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">招财进宝合体字</span><span class="cp">复制</span></div><pre>正常写：  招  财  进  宝        （四个字，四个位置）

合体字：  招
         财 宝        （四个字共用一个字形的空间，
          进            借笔画、共用偏旁）
          ↑
     这是个「装饰性」连字：
     只有过年贴的福字、春联上才这么写，
     正文里绝不会用 —— 因为没人能一眼读出来。</pre></div>'''
if old in t:
    new = '''<figure class="fig">
  <img src="assets/img/zhaocaijinbao.webp"
       alt="招财进宝合体字：把「招财进宝」四个字挤进一个字的位置，笔画相互借用、偏旁共用"
       width="715" height="800" loading="lazy" decoding="async">
  <figcaption><b>招财进宝</b>合体字 —— 四个字共用一个字形的空间，
    借笔画、共用偏旁。它只在过年的福字、春联上出现，
    <b>正文里绝不会用</b>，因为没人能一眼读出来。</figcaption>
</figure>'''
    t = t.replace(old, new, 1)
    n += 1
    print("  ✓ ASCII 招财进宝 → zhaocaijinbao.webp 图片")
else:
    print("  ! 没找到 ASCII 招财进宝 段")

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("\n  改 %d 处" % n)
