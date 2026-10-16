# -*- coding: utf-8 -*-
"""给 FE-09 的数据加一条按篇的页脚说明。

为什么需要
    FE 的页脚是 fe-data.js 统一生成的，固定写着
    「标着『示例展示』的代码块会把效果真的渲染出来」——
    这句话对 FE-01~FE-08 成立，但 FE-09《DOM 操作基础》里
    **没有**那种会渲染效果的示例块，笼统这么写就不准确了。

    同时 FE-09 有一处必须交代的诚实说明：
      三个 DOM 函数的行为在浏览器里逐条实测过；
      但 Qt 那侧本机没有 Qt 工具链，**没有编译过**，
      是按 Qt 文档语义写的对照。
    教程页的惯例是把这类话写进页脚（和文档页的「按标准推演」同一套做法）。
"""
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\fe-09.html"

NOTE = ("本篇的 DOM 示例与返回值均在浏览器中实际运行核对（Chromium 内核，21 项断言全过）；"
        "Qt 那段对照代码本机无 Qt 工具链，未编译，按 Qt 文档语义整理。")

t = io.open(P, encoding="utf-8").read()
if "footerNote" in t:
    print("  已有 footerNote，跳过")
    raise SystemExit(0)

m = re.search(r'window\.__FE_PAGE__\s*=\s*(\{.*?\});\s*\n', t, re.S)
if not m:
    print("  !! 找不到 __FE_PAGE__")
    raise SystemExit(1)
data = json.loads(m.group(1))
data["footerNote"] = NOTE
js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
js = js.replace("</", "<\\/")
t2 = t[:m.start(1)] + js + t[m.end(1):]
io.open(P, "w", encoding="utf-8", newline="").write(t2)
print("  已给 FE-09 加 footerNote（%d 字符）" % len(NOTE))

# 顺便让生成器也带上，重跑不会丢
b = r"E:\QKMansion\CSX10\w\UME\tools\build_fe09_page.py"
s = io.open(b, encoding="utf-8").read()
old = '''    data = {
        "file": FN, "num": NUM, "title": TITLE, "star": False,
        "body": body,'''
new = '''    data = {
        "file": FN, "num": NUM, "title": TITLE, "star": False,
        # 按篇的页脚补充（fe-data.js 会拼在公共那句之后）
        "footerNote": FOOTER_NOTE,
        "body": body,'''
if "FOOTER_NOTE" not in s:
    s = s.replace(old, new, 1)
    # 定义常量
    s = s.replace('DESC = "',
                  'FOOTER_NOTE = ("本篇的 DOM 示例与返回值均在浏览器中实际运行核对"\n'
                  '               "（Chromium 内核，21 项断言全过）；"\n'
                  '               "Qt 那段对照代码本机无 Qt 工具链，未编译，"\n'
                  '               "按 Qt 文档语义整理。")\n\nDESC = "', 1)
    io.open(b, "w", encoding="utf-8", newline="").write(s)
    print("  生成器 build_fe09_page.py 也带上了 FOOTER_NOTE")
