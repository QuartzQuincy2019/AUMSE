# -*- coding: utf-8 -*-
"""修：窄屏「目录」按钮被顶部常驻条盖住。

实测（375×667）
--------------
  顶部常驻条 body::before   z-index:80   高 23px（top 0 → 23）
  #tocToggle                z-index:70   top:9px → 36px

按钮的**上半截（9~23px）整个压在常驻条下面**，而且 z-index 更低，
所以既看不见也点不动。elementFromPoint 命中的是 body。

F 系的三篇为什么没事：它们的样式表里有一条 `body.fseries #tocToggle{top:34px}`
把按钮挪到了常驻条下方 —— 那是针对 F 的单点补丁，其余 15 篇没有。

修法（两件事，都不能少）
-----------------------
1. 层级：`#tocToggle` 的 z-index 从 70 提到 **90**，高于常驻条的 80。
   只挪位置不提层级的话，按钮和常驻条在垂直方向仍有微小重叠，
   一旦有任何像素交叠，点击还是会落到常驻条上。
2. 位置：在**窄屏**下把按钮的 top 让到常驻条下方（top:28px，
   常驻条 23px + 5px 余量），这样两者根本不重叠。

作用范围：所有教程页（含 FE）。选择器用 `#tocToggle` 本身，
不带父级限定 —— 由于写在每份样式表末尾，靠「后加载」赢过前面的规则。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"

PATCH = """
/* =====================================================================
   窄屏「目录」按钮：不能被顶部常驻条盖住
   ---------------------------------------------------------------------
   实测 375×667：常驻条 z-index:80 高 23px（0→23），
   #tocToggle z-index:70 且 top:9px（9→36）——
   按钮上半截整段压在常驻条下面，又因为层级更低，既看不见也点不动。

   两处一起改：
     ① z-index 70 → 90，高于常驻条的 80
     ② 窄屏把 top 让到常驻条下方（23px + 5px 余量 = 28px），
        从根上不重叠 —— 只提层级不够，交叠处仍会吃到点击
   ===================================================================== */
#tocToggle{z-index:90}
@media (max-width:980px){
  #tocToggle{top:28px}
}
"""

n = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "不能被顶部常驻条盖住" in c:
        continue
    if "#tocToggle" not in c:
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(c.rstrip() + "\n" + PATCH)
    n += 1
    print("  ✓ %-30s 已补" % f)
print("\n  共 %d 份样式表" % n)
