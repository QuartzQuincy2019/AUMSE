# -*- coding: utf-8 -*-
"""把「FE-09 是重点项目」这件事同步到每个 FE 页面的 series 列表里。

为什么需要单独做
    build_fe09_page.py 重写 fe-09.html 时会把 star:true 写进**它自己**的
    __FE_PAGE__（顶层）和 series。但其它 9 个 FE 页面的 series 里也各有一条
    FE-09，那几条是历史遗留的副本，不会跟着变 ——
    于是 fe-09 页上「本系列」里 FE-09 带星，别的页上不带。

    这类「同一份数据散在多个页面里」的漂移本会话已经遇到两次
    （R 按钮点不动、FE 篇数 8/9 不一致），所以照旧写个脚本统一下来。
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

# 页面数据里的 series 条目（JSON 被转义，所以 \" 和 <\/ 都要照原样匹配）
PAT = re.compile(r'\{"file":"fe-09\.html","num":"FE-09",'
                 r'"title":"DOM 操作基础","star":(true|false)\}')


def main():
    dry = "--dry" in sys.argv
    n = 0
    for f in sorted(os.listdir(T)):
        if not re.match(r"^fe-0\d(-F\d+)?\.html$", f):
            continue
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        hits = PAT.findall(t)
        if not hits:
            print("  %-18s 没有 FE-09 条目" % f)
            continue
        if all(h == "true" for h in hits):
            print("  %-18s 已是 star:true" % f)
            continue
        t2 = PAT.sub(lambda m: m.group(0).replace('"star":false', '"star":true'), t)
        print("  %-18s 改 %d 处 → star:true" % (f, len(hits)))
        n += len(hits)
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  合计 %d 处  %s" % (n, "[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
