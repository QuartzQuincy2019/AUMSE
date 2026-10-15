# -*- coding: utf-8 -*-
"""把 FE 各篇的内嵌 <style> 抽成 assets/<stem>.css，与其它教程一致。

注意顺序：这一步必须在「重建 → 插示例 → 标注重点」**之后**做，
因为标注会往 <style> 里加 .key-mark 规则。
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
AS = os.path.join(TUT, "assets")


def main():
    docs = sorted(f for f in os.listdir(TUT)
                  if f.startswith("fe-") and f.endswith(".html"))
    n = 0
    for fn in docs:
        p = os.path.join(TUT, fn)
        t = io.open(p, encoding="utf-8").read()
        m = re.search(r'(?s)<style>(.*?)</style>', t)
        if not m:
            print("  · %-18s 已经是外部样式表" % fn)
            continue
        stem = re.sub(r'[^A-Za-z0-9]+', '_', os.path.splitext(fn)[0]).strip('_')
        target = stem + ".css"
        css = ("/* ==== %s\n"
               "       前端系列样式：共用设计系统 + 示例展示 + 颜色拾取器\n"
               "       （每篇自带一份，保证层叠顺序与内嵌时完全一致）==== */\n\n"
               % fn) + m.group(1).strip() + "\n"
        io.open(os.path.join(AS, target), "w",
                encoding="utf-8", newline="\n").write(css)
        t = t.replace(m.group(0),
                      '<link rel="stylesheet" href="assets/%s">' % target, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        n += 1
        print("  ✔ %-18s → assets/%-22s (%d 字符)" % (fn, target, len(css)))
    print("\n  抽出 %d 篇" % n)


if __name__ == "__main__":
    main()
