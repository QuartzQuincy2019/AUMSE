# -*- coding: utf-8 -*-
"""把颜色拾取器的 JS 从 fe-data.js 抽成独立文件，供 r04.html 加载。

问题
    R04 原来是 FE 系列的数据驱动页（fe-03-F01），拾取器的逻辑写在
    assets/js/fe-data.js 里（FE 页面的运行时）。改成 R 系列的文档页后，
    r04.html 只加载 tutorial.css / series-theme.css，**不再加载 fe-data.js**，
    于是滑块拖不动 —— 这正是用户报告的「颜色拾取器停止工作」。

做法
    1. 从 fe-data.js 里抠出拾取器相关的三个函数：
           h2(n)            两位十六进制
           hue(r,g,b,...)   算色相
           initPicker()     全部交互
       以及它依赖的 copyText()
    2. 写成 assets/r04-picker.js —— 自带 DOMContentLoaded 触发，
       不依赖 FE 的任何其它代码
    3. 在 r04.html 里加一行 <script src="assets/r04-picker.js" defer>
       (放在 series-common.js 之前)

    为什么不直接让 r04 加载 fe-data.js：那份是 FE 系列的运行时，
    里面还有 buildSeriesNav / P 页面数据等一大堆 FE 专属逻辑，
    会去读 window.__FE_PAGE__（r04 现在没有），反而出错。
"""
import io
import re
import sys

R = r"E:\QKMansion\CSX10\w\UME"
FE = R + r"\SharingGroup\tutorials\assets\fe-data.js"
OUT = R + r"\SharingGroup\tutorials\assets\r04-picker.js"
PAGE = R + r"\SharingGroup\tutorials\r04.html"

src = io.open(FE, encoding="utf-8").read()

# ---------------- 1. 抠 h2 / hue ----------------
a = src.find("  function h2(n) {")
b = src.find("  function initPicker() {")
if a < 0 or b < 0:
    print("  !! 找不到 h2 / initPicker 的位置")
    sys.exit(1)
helpers = src[a:b].rstrip()
print("  h2 + hue：%d 字符" % len(helpers))

# ---------------- 2. 抠 initPicker（到下一个 /* ==== 段）----------------
c = src.find("  /* =====", b)
if c < 0:
    print("  !! 找不到 initPicker 的结尾")
    sys.exit(1)
picker = src[b:c].rstrip()
print("  initPicker：%d 字符" % len(picker))

# ---------------- 3. 抠 copyText ----------------
d = src.find("  function copyText(s) {")
if d < 0:
    print("  !! 找不到 copyText")
    sys.exit(1)
# 到「  /* ================= 2.」之前
e = src.find("  /* ================= 2.", d)
copytext = src[d:e].rstrip()
print("  copyText：%d 字符" % len(copytext))

# 把顶层缩进 2 格改成 0（原文在 IIFE 里）
def dedent(s):
    return "\n".join(l[2:] if l.startswith("  ") else l for l in s.split("\n"))

header = """/* =====================================================================
   r04-picker.js —— R04《十六进制颜色模型、HSV 与 Alpha》的「颜色拾取器」
   ---------------------------------------------------------------------
   这一段逻辑原来住在 assets/js/fe-data.js 里（FE 系列页面的运行时）。
   R04 原本是 FE 的 fe-03-F01，改成 R 系列的文档页后就不再加载
   fe-data.js，滑块因此拖不动 —— 所以把它抽成独立文件单独加载。

   依赖（全在本文件内，不引用 FE 的任何其它代码）：
       h2()         两位十六进制
       hue()        算色相
       copyText()   复制到剪贴板（带 execCommand 兜底）
       initPicker() 全部交互

   页面侧约定：body 里要有 id="picker"，以及 pkR / pkG / pkB / pkA、
   pkSwatch / pkHex / pkRgb / pkHsl / pkRgba / pkPresets 这些元素。
   样式在 assets/css/r04.css 的「颜色拾取器」一节。
   ===================================================================== */
(function () {
  'use strict';

"""

footer = """
  /* 等 DOM 就绪再挂 —— 本文件用 defer 加载，但保险起见再包一层 */
  function boot() { initPicker(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
"""

body = "\n\n".join([dedent(copytext), dedent(helpers), dedent(picker)])
js = header + body + "\n" + footer

io.open(OUT, "w", encoding="utf-8", newline="").write(js)
print("  已写入 r04-picker.js（%d 字符）" % len(js))

# ---------------- 4. 在 r04.html 里加 <script> ----------------
t = io.open(PAGE, encoding="utf-8").read()
if "r04-picker.js" in t:
    print("  r04.html 已引用 r04-picker.js")
else:
    anchor = '<script src="assets/js/series-common.js"></script>'
    if anchor not in t:
        print("  !! r04.html 找不到 series-common.js 的引用")
        sys.exit(1)
    t = t.replace(anchor, '<script src="assets/r04-picker.js" defer></script>\n' + anchor, 1)
    io.open(PAGE, "w", encoding="utf-8", newline="").write(t)
    print("  r04.html 已加 <script src=\"assets/r04-picker.js\" defer>")

# ---------------- 5. 语法自检 ----------------
print()
print("  生成的骨架：")
for l in js.split("\n")[:6]:
    print("      " + l)
print("      ...")
for kw in ("function h2", "function hue", "function copyText", "function initPicker",
           "initPicker()"):
    print("      含 %-18s %s" % (kw, kw in js))
