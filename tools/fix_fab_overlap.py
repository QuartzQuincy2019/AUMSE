# -*- coding: utf-8 -*-
"""修「窄屏侧边抽屉底部被『返回 home』悬浮按钮压住」的问题。

实测（375x640，m04.html，抽屉已打开）：
    home 按钮  z-index=65  rect=(9,600)-(121,631)
    抽屉      z-index=60  rect=(0,0)-(300,640)
    目录第 ⑧ 项 y=615 → 命中 a.home-fab，点不动
按钮比抽屉层级高、又压在左下角，所以抽屉底部的目录项点不到。

修法（两处，前后端都要）：
  1) 抽屉打开时把按钮藏起来 —— 抽屉里有它自己的入口，按钮不该抢层级
  2) 中等宽度下按钮右移到底部右侧 —— 抽屉宽度是 min(86vw,300px)，
     375px 屏上就是 300px，左侧放任何悬浮控件都会落到抽屉上面；
     右移 320px 之后，抽屉开到 300px 也不重叠
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
AS = os.path.join(REPO, "SharingGroup", "tutorials", "assets")

RULE = """
/* ---------- 悬浮「返回 home」按钮的避让 ----------
   窄屏下抽屉宽 min(86vw,300px)，而按钮固定在左下角、z-index 又高于抽屉，
   会把抽屉底部的目录项压住导致点击无效。所以：
     * 抽屉打开时直接藏起按钮
     * 中等宽度把按钮移到底部右侧（320px 之外就不与抽屉重叠） */
body.toc-open .home-fab{display:none}
@media (min-width:561px) and (max-width:980px){
  .home-fab{left:auto;right:12px}
}
"""


def patch(path, must_have):
    t = io.open(path, encoding="utf-8").read()
    if "悬浮「返回 home」按钮的避让" in t:
        print("  ·  %-30s 已有" % os.path.basename(path))
        return False
    if must_have not in t:
        print("  !! %-30s 没有 %s，跳过" % (os.path.basename(path), must_have))
        return False
    t = t.rstrip() + "\n" + RULE
    io.open(path, "w", encoding="utf-8", newline="\n").write(t)
    print("  ✔  %-30s 已加避让规则" % os.path.basename(path))
    return True


def main():
    n = 0
    # 前端：悬浮按钮的样式在每篇的 fe_*.css 里
    for f in sorted(os.listdir(AS)):
        if f.startswith("fe_") and f.endswith(".css"):
            if patch(os.path.join(AS, f), ".home-fab"):
                n += 1
    # 后端：注入的样式块在每篇 html 的 <style> 里
    TUT = os.path.join(REPO, "SharingGroup", "tutorials")
    for f in sorted(os.listdir(TUT)):
        if not f.endswith(".html") or f.startswith("fe_"):
            continue
        p = os.path.join(TUT, f)
        t = io.open(p, encoding="utf-8").read()
        if ".home-fab" not in t:
            continue
        if "悬浮「返回 home」按钮的避让" in t:
            print("  ·  %-30s 已有" % f)
            continue
        i = t.rfind("</style>")
        if i < 0:
            print("  !! %s 没有 </style>" % f)
            continue
        t = t[:i] + RULE + t[i:]
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("  ✔  %-30s 已加避让规则" % f)
        n += 1
    print("\n  处理 %d 处" % n)


if __name__ == "__main__":
    main()
