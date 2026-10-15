# -*- coding: utf-8 -*-
"""从 _ds_04 提取可复用的 CSS（含移动端增强）与末尾脚本，
   生成 _ds_05 / _ds_06 / _ds_07 三份新教程的公共外壳。

这样三份新文档的视觉与交互（Consolas 代码、悬停反馈、目录抽屉、
手机适配）与前面四讲完全一致，不必手抄 15KB 的 CSS。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
SRC = os.path.join(ROOT, "_ds_04_C指针初步.html")

with io.open(SRC, encoding="utf-8") as fh:
    src = fh.read()

i0 = src.index("<style>")
i1 = src.index("</style>") + len("</style>")
CSS = src[i0:i1]

j0 = src.rindex("<script>")
j1 = src.rindex("</script>") + len("</script>")
# 末尾脚本 = 移动端目录按钮那段；目录高亮 + 复制按钮那两段在它前面
k0 = src.index("<script>")           # 第一段 script（目录高亮 + 复制按钮）
k1 = src.index("</script>", k0) + len("</script>")
SCRIPTS = src[k0:k1] + "\n" + src[j0:j1]

OUT = os.path.join(ROOT, "_shell_parts")
os.makedirs(OUT, exist_ok=True)

with io.open(os.path.join(OUT, "css.html"), "w", encoding="utf-8") as fh:
    fh.write(CSS)
with io.open(os.path.join(OUT, "scripts.html"), "w", encoding="utf-8") as fh:
    fh.write(SCRIPTS)

print("CSS      : %d 字符 -> _shell_parts/css.html" % len(CSS))
print("SCRIPTS  : %d 字符 -> _shell_parts/scripts.html" % len(SCRIPTS))
print("含移动端增强: %s" % ("是" if "移动端增强" in CSS else "否"))
print("含目录按钮JS: %s" % ("是" if "tocToggle" in SCRIPTS else "否"))
print("含复制按钮JS: %s" % ("是" if "navigator.clipboard" in SCRIPTS else "否"))
print("含目录高亮JS: %s" % ("是" if "IntersectionObserver" in SCRIPTS else "否"))
