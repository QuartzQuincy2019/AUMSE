# -*- coding: utf-8 -*-
"""修 FE 窄屏：目录抽屉**打不开也收不起**，且把正文挤成 86px。

实测（360×800，点不动按钮也测过）
---------------------------------
  FE 8 篇     main 宽 86px    toc.left = 0    → 抽屉常驻展开
  后端 18 篇  main 宽 360px   toc.left = -306 → 抽屉在画面外，正文满宽

根因
----
后端样式表在 @media (max-width:980px) 里有**两条**：

    #toc{ display:block !important; position:fixed; top:0;left:0;bottom:0;
          z-index:60; width:min(80vw,308px); transform:translateX(-100%); ... }
    #toc.open{ transform:translateX(0) }

而 FE 的样式表里**只有 .open 那条**，缺了默认态：

    （缺）  #toc{ position:fixed; ...; transform:translateX(-100%) }
    ✓      #toc.open{ transform:translateX(0) }

于是 FE 的 #toc 仍是基础样式 `position:sticky; flex:0 0 274px` ——
它在 flex 里**占据 274px 的真实宽度**（sticky 元素照样占位），
360 − 274 = 86px 留给 main；又因为没有 translateX(-100%)，
它一开始就显示在屏幕左边，看起来像「抽屉默认展开」。
按钮点下去只切换 .open，而基础态本来就是「可见」，所以看起来没反应。

修法
----
给 FE 补上缺失的默认态（与后端对齐）：
    position:fixed + translateX(-100%)  → 移出画面，且不再占 flex 宽度
    #toc.open 时 translateX(0)          → 滑入
同时补上遮罩（body.toc-open::before）与 560px 断点的宽度，行为与后端一致。
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
   FE 窄屏目录抽屉：补上缺失的「默认收起」态
   ---------------------------------------------------------------------
   本文件原来只有 `#toc.open{transform:translateX(0)}`，
   缺了默认态 —— 于是 @media(max-width:980px) 下 #toc 仍是基础样式
   `position:sticky; flex:0 0 274px`：
     · sticky 元素照样占 flex 宽度 → 360px 视口只剩 86px 给正文
     · 没有 translateX(-100%)        → 它一开始就停在屏幕左边，像抽屉默认展开
   下面补齐，行为与后端系列一致。
   ===================================================================== */
@media (max-width:980px){
  /* 默认：移出画面。position:fixed 很关键 —— 脱离 flex 流，
     否则它仍占 274px，把正文挤扁。 */
  #toc{
    display:block;
    position:fixed;top:0;left:0;bottom:0;z-index:60;
    width:min(80vw,308px);height:100vh;max-height:100vh;
    transform:translateX(-100%);
    transition:transform .26s ease;
    padding-top:58px;
  }
  /* 打开：滑入 */
  #toc.open{transform:translateX(0)}
  /* 遮罩 */
  body.toc-open::before{
    content:"";position:fixed;inset:0;z-index:55;
    background:rgba(18,26,40,.42);
  }
}
@media (max-width:560px){
  #toc{width:min(86vw,300px)}
}
"""

n = 0
for f in sorted(os.listdir(A)):
    if not (f.startswith("fe_") and f.endswith(".css")):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "补上缺失的「默认收起」态" in c:
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(c.rstrip() + "\n" + PATCH)
    n += 1
    print("  ✓ %-18s 已补" % f)
print("\n  共 %d 份 FE 样式表" % n)
