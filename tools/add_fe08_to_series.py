# -*- coding: utf-8 -*-
"""把 FE-08 补进 fe-01 ~ fe-07 的 window.__FE_PAGE__.series。

问题
----
fe-08.html 的 series 里有 9 条（含自己），但 fe-01 ~ fe-07 只有 8 条 ——
它们的 __FE_PAGE__ 是 FE-08 建出来**之前**生成的，之后没人补。
后果有两个：
  ① 这七页的「本系列」小目录里看不到 FE-08；
  ② 页尾「全部系列」里 FE 那一格的篇数取自本页 P.series，
     于是同一系列在不同页上显示 8 篇 / 9 篇。
第二个是上一轮才暴露的（那时我把篇数改成现算，取的就是 P.series.length）。

为什么不用 make_fe_shells.py 重生成
    那个脚本会在转换过程中调用 add_fe_demos 之前的构建流程，
    **后补的示例会丢**（build_fe08_page.py 的注释里已经写明）。
    所以这里只做最小侵入：往 series 数组末尾插一条。

做法
    1. 括号配平定位 window.__FE_PAGE__ 里的 "series":[ ... ]；
    2. 已经含 fe-08 就跳过；
    3. 否则在数组的 ']' 之前插入 FE-08 那一条（与现有条目同格式）。
    正文（body 字符串）一个字都不动。

用法：
    python add_fe08_to_series.py --dry
    python add_fe08_to_series.py
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

ENTRY = ('{"file":"fe-08.html","num":"FE-08",'
         '"title":"JavaScript 语法初步","star":false}')

# 各页 series 数组里最后一条的“样式”：
#   fe-01..07 的数组以 }, 结尾，直接插在 ] 前要补逗号
TAIL = re.compile(r'(\})\s*\]')


def bracket_span(s, start):
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "[":
            depth += 1
        elif s[i] == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def main():
    dry = "--dry" in sys.argv
    for f in sorted(os.listdir(T)):
        # fe-01 … fe-08，外加 fe-03-F01 —— 它也是 FE 系列的一篇。
        # 第一版只写了 fe-0[1-7]，把它漏了（正则里的 [1-7] 后面
        # 直接跟 \.html，而 fe-03-F01.html 中间还有 -F01）。
        if not re.match(r"^fe-0[1-8](-F\d+)?\.html$", f):
            continue
        if f == "fe-08.html":
            continue          # 它自己本来就有
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()

        m = re.search(r'"series"\s*:\s*\[', t)
        if not m:
            print("  %-22s 无 series，跳过" % f)
            continue
        b = t.index("[", m.start())
        e = bracket_span(t, b)
        seg = t[b:e + 1]

        if '"fe-08.html"' in seg:
            print("  %-22s 已含 FE-08，跳过" % f)
            continue

        # 在数组的 ']' 之前插入
        inner = seg[:-1].rstrip()
        newseg = inner + "," + ENTRY + "]"
        t2 = t[:b] + newseg + t[e + 1:]

        n_before = len(re.findall(r'"file"\s*:', seg))
        n_after = len(re.findall(r'"file"\s*:', newseg))
        ok = (n_after == n_before + 1)
        print("  %-22s series %d → %d 条 %s"
              % (f, n_before, n_after, "OK" if ok else "!! 数量不对"))
        if not dry and ok:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
