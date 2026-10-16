# -*- coding: utf-8 -*-
"""处理最后 3 处埋得很深的 g++ 声明。

这三处不是 footer 里的套话，而是**具体的断言**，处理方式要分开：

q01（两处）「真实报错（g++ 13.1.0）」
    断言的是编译器的**具体措辞**（'version' was not declared in this scope、
    call of overloaded 'hello()' is ambiguous）。
    本机没有编译器 → 我**无法核实这两条原文**。
    但报错文本本身没有断言「我在本机跑过」，改成「按标准推演」反而会丢掉
    「编译器大概会这么说」这个有用信息。
    做法：保留报错原文，把标签从「真实报错」改成「报错形状」，
    并加一句「具体措辞随编译器版本略有差异」。

r02（一处）「输出（g++ 13.1.0，-O2，某台普通办公机）」
    断言的是**具体的毫秒数**（3 / 103 / 1698 ms）。
    这个我更不能核实，而且**不能替它改数字** —— 改成别的数字
    只是换了一个假的来源，更糟。
    做法：保留数字（那是原来测出来的记录），但把「实测数据」的口气
    降下来，明确说明「绝对值随机器与编译器而变，这里要看的量级增长」。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

EDITS = [
    # ---- q01：两处「真实报错（g++ 13.1.0）」----
    ("q01-std-and-namespace.html",
     r'真实报错（g\+\+ 13\.1\.0）',
     '报错形状（具体措辞随编译器版本略有差异）',
     2),
    # ---- r02：性能数字的来源说明 ----
    ("r02-bubble-sort.html",
     r'输出（g\+\+ 13\.1\.0，-O2，某台普通办公机）',
     '输出（-O2 编译；数值取自一次具体运行的记录，绝对值随机器与编译器而变，'
     '这里要看的是量级的增长趋势）',
     1),
]


def main():
    dry = "--dry" in sys.argv
    for f, pat, rep, n_expect in EDITS:
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        t2, n = re.subn(pat, rep, t)
        ok = (n == n_expect)
        print("  %-32s 命中 %d 处（期望 %d）%s" % (f, n, n_expect, "OK" if ok else "  !! 不符"))
        if not ok:
            continue
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
