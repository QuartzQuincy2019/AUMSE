# -*- coding: utf-8 -*-
"""把每篇里的示例展示编号（data-pv="N"）重排成连续 1..n。

为什么需要：pv() 的编号是我手写的，插入顺序一变就会出现空洞
（fe-05 曾经是 1,2,3,4,5,7,30）。编号只用于 CSS 作用域隔离，
重排不影响任何效果，但**连续性**能让人一眼看出有没有漏插或重复插。

重排时必须同时改两处：
  * data-pv="N"        —— 作用域属性的值
  * [data-pv="N"]      —— 注入脚本会重新生成，不用管
另外检查重复：重复编号意味着同一个示例被插了两次。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"


def main():
    total = 0
    for fn in sorted(f for f in os.listdir(TUT)
                     if f.endswith(".html")):
        p = os.path.join(TUT, fn)
        t = io.open(p, encoding="utf-8").read()
        ids = re.findall(r'data-pv="(\d+)"', t)
        if not ids:
            continue

        dup = sorted({x for x in ids if ids.count(x) > 1})
        if dup:
            print("  !! %-34s 编号重复 %s —— 有示例被插了两次，需重建" % (fn, dup))
            continue

        want = [str(i) for i in range(1, len(ids) + 1)]
        if ids == want:
            print("  ·  %-34s 已连续 1..%d" % (fn, len(ids)))
            continue

        # 按出现顺序重排（从后往前替换，避免偏移失效）
        mapping = {}
        for old, new in zip(ids, want):
            mapping.setdefault(old, new)
        for old in sorted(mapping, key=lambda x: -int(x)):
            t = t.replace('data-pv="%s"' % old, 'data-pv="@@%s@@"' % mapping[old])
        t = t.replace("@@", "")
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        new_ids = re.findall(r'data-pv="(\d+)"', t)
        ok = new_ids == want
        print("  ✔  %-34s %s → 1..%d %s" % (fn, ids, len(ids),
                                            "OK" if ok else "仍有问题!"))
        total += 1
    print("\n  重排 %d 篇" % total)


if __name__ == "__main__":
    main()
