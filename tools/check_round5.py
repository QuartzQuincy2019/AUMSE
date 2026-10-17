# -*- coding: utf-8 -*-
"""核对本轮五件事是否都生效。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")

ok = bad = 0


def chk(cond, msg):
    global ok, bad
    if cond:
        ok += 1
        print("  OK   %s" % msg)
    else:
        bad += 1
        print("  !!   %s" % msg)


print("1. 示例名字已换成抽象的")
q3 = io.open(os.path.join(A, "..", "q03.html"),
             encoding="utf-8").read()
q4 = io.open(os.path.join(T, "q04.html"), encoding="utf-8").read()
old_names = ["灰羽", "小灰", "北境"]
for f, t in (("q03", q3), ("q04", q4)):
    left = [n for n in old_names if n in t]
    chk(not left, "%s 里没有旧名字（残留：%s）" % (f, left or "无"))
chk("忘情牛肉面" in q3 and "忘情牛肉面" in q4, "两页都出现「忘情牛肉面」")
chk("奶蛙" in q3 and "奶蛙" in q4, "两页都出现「奶蛙」")
chk("University of Naiwa" in q3 and "University of Naiwa" in q4,
    "两页都出现「University of Naiwa」")

print()
print("2. T02 的收尾卡已删")
t02 = io.open(os.path.join(T, "t02.html"),
              encoding="utf-8").read()
chk("教程到这里就结束了" not in t02, "T02 里没有「教程到这里就结束了」")
chk("七讲正文" not in t02, "T02 里那张回顾卡已整张删除")

print()
print("3. 系列标签")
for f in ("series_data.py",):
    t = io.open(os.path.join(R, "tools", f), encoding="utf-8").read()
    chk("C++&Qt · Q" in t, "%s 有「C++&Qt · Q」" % f)
    chk("文件 · F" in t, "%s 有「文件 · F」" % f)
for f in ("series-common.js", "fe-data.js"):
    t = io.open(os.path.join(A, f), encoding="utf-8").read()
    chk("C++&Qt · Q" in t, "%s 有「C++&Qt · Q」" % f)
    chk("文件 · F" in t, "%s 有「文件 · F」" % f)
    chk("&amp;Qt" not in t, "%s 没有误写成 &amp;" % f)

print()
print("4. T03 的 R01 延伸链接 + 样式")
t03 = io.open(os.path.join(T, "t03.html"),
              encoding="utf-8").read()
chk('class="see-also"' in t03, "T03 有 .see-also 块")
chk('href="r01.html"' in t03, "T03 链到 R01")
gl = io.open(os.path.join(A, "genelayout.css"), encoding="utf-8").read()
chk(".see-also{" in gl, "genelayout.css 有 .see-also 样式")
chk(".see-also a{" in gl, "样式里有 .see-also a")
# 位置：应在 <footer> 之前
chk(t03.find('class="see-also"') < t03.find("<footer>"),
    "链接块在 <footer> 之前")

print()
print("5. FE series-nav 暗色覆盖")
fd = io.open(os.path.join(A, "fe-dark.css"), encoding="utf-8").read()
chk('body[data-series="FE"] .series-nav a:not(.cur)' in fd,
    "fe-dark.css 有非 .cur 的暗色覆盖")
chk("#1e242e" in fd, "覆盖里用了深底（不是白色）")

print()
print("  通过 %d 项，未过 %d 项 %s" % (ok, bad, "OK" if bad == 0 else "FAIL"))
