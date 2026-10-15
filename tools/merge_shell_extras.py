# -*- coding: utf-8 -*-
"""把「移动端长串断行」与「星标」这两条全局增强合并进共享外壳缓存。

这两条之前是以独立 <style> 块附在各个文档末尾的。新文档应当直接从
外壳继承，不必每篇再带一次，所以这里把它们并进 _shell_parts/css.html。

顺带确认移动端目录抽屉那部分已经在基础样式里（它是更早合进去的）。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
PARTS = os.path.join(ROOT, "_shell_parts")
SRC = os.path.join(ROOT, "_ds_08_F02_相对文件路径与宏.html")

WRAP = """
/* ===== 移动端：长路径字符串断行 ===== */
/* 长且无空格的串（路径、命令、变量名）在窄屏上必须允许内部断行，
   否则会把表格和终端块撑得比视口还宽。 */
@media (max-width:980px){
  main table th,
  main table td,
  main table td code,
  main table th code,
  main table td .c,
  main td,
  main th{
    overflow-wrap:anywhere;
    word-break:break-word;
  }
  main table th{white-space:normal}
  .term pre,
  .term .pr,
  .term .cmd,
  .term .out,
  .term .warn,
  .term .err{
    overflow-wrap:anywhere;
    word-break:break-word;
    white-space:pre-wrap;
  }
  main p code,
  main li code,
  main td code,
  .card code{
    overflow-wrap:anywhere;
    word-break:break-word;
  }
}
"""

STAR = """
/* ===== 星标：标记与本项目施行密切相关的篇目 ===== */
h1 .star{color:#e0a800;font-size:.62em;vertical-align:super;margin-left:6px;
  font-weight:700;cursor:help}
"""

css_path = os.path.join(PARTS, "css.html")
with io.open(css_path, encoding="utf-8") as fh:
    css = fh.read()

added = []
if "移动端：长路径字符串断行" not in css:
    css = css.rstrip()
    assert css.endswith("</style>"), "css.html 结构异常"
    css = css[: -len("</style>")] + WRAP + STAR + "</style>"
    added.append("移动端断行 + 星标")

with io.open(css_path, "w", encoding="utf-8", newline="") as fh:
    fh.write(css)

print("css.html 现在 %d 字符" % len(css))
print("已合并: %s" % ("、".join(added) if added else "无需改动"))
for k, label in [("max-width:980px", "移动端断点"),
                 ("tocToggle", "目录抽屉按钮"),
                 ("overflow-wrap:anywhere", "长串断行"),
                 ("h1 .star", "星标样式"),
                 ("background-size:26px", "F 系列网格(应为否)"),
                 ("fseries", "F 系列主题(应为否)")]:
    print("  含 %-22s : %s" % (label, "是" if k in css else "否"))
