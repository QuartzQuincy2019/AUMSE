# -*- coding: utf-8 -*-
"""核对语言徽章：每页恰好 1 个，且样式表里真的有对应规则。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")

EXPECT = {
    "t01-mongolian-script-intro.html": "html", "t02-unicode-and-encoding.html": "html",
    "t03-font-file-anatomy.html": "html",
    "f01-command-prompt.html": "sh", "f02-paths-and-env.html": "sh",
    "f03-compile-and-link.html": "sh",
    "m01-c-arrays.html": "cpp", "m02-c-functions.html": "cpp", "m03-c-types.html": "cpp",
    "m04-c-pointers.html": "cpp", "m05-memory.html": "cpp", "m06-class-struct.html": "cpp",
    "m07-scope.html": "cpp", "m08-c-strings.html": "cpp", "m09-vector-and-array.html": "cpp",
    "q01-std-and-namespace.html": "cpp", "q02-references.html": "cpp",
    "r01-font-design-metrics.html": "css", "r02-bubble-sort.html": "cpp",
    "r03-collation.html": "cpp",
    "e01-recursion.html": "cpp", "e02-batch-and-cmd.html": "sh",
    "e03-syntactic-sugar.html": "cpp",
    "fe-01.html": "html", "fe-02.html": "html", "fe-03-F01.html": "css",
    "fe-03.html": "css", "fe-04.html": "css", "fe-05.html": "css",
    "fe-06.html": "css", "fe-07.html": "css", "fe-08.html": "js",
}

# 页面上「渲染后可见」的徽章形态：class="lang xx"
PAT = re.compile(r'class="lang ([a-z]+)"')

bad = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    # 文档页直接出现；FE 页在 JSON 里带反斜杠转义
    hits = re.findall(r'class=\\?"lang ([a-z]+)\\?"', t)
    want = EXPECT.get(f)
    if want is None:
        print("  %-34s （未登记，跳过）" % f)
        continue
    if len(hits) != 1:
        bad += 1
        print("  !! %-32s 徽章 %d 个 %s" % (f, len(hits), hits))
    elif hits[0] != want:
        bad += 1
        print("  !! %-32s 徽章是 %s，期望 %s" % (f, hits[0], want))
    else:
        print("  OK %-32s %s" % (f, hits[0]))
print()
print("  异常 %d 篇 %s" % (bad, "OK" if bad == 0 else "FAIL"))

# 样式表侧：tg_L / tg_D 里必须有每一条规则
print()
for fn in ("tg_L.css", "tg_D.css"):
    c = io.open(os.path.join(A, fn), encoding="utf-8").read()
    missing = [k for k in ("html", "css", "js", "cpp", "c", "sh", "py")
               if (".lang.%s{" % k) not in c.replace(" ", "")]
    print("  %-10s 缺规则: %s" % (fn, missing if missing else "无 OK"))
