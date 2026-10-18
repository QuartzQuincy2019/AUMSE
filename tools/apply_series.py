# -*- coding: utf-8 -*-
"""按 series_data.py 完成改名与改编号，并给每篇挂上系列属性。

顺序很关键（避免连锁误改）：
  第 1 步  改**文件名**（15 个）
  第 2 步  全仓替换**文件名引用**（href / link / 脚本里的输出路径）
           —— 先做这一步，后面的「改数字」就不会碰到 href
  第 3 步  改**显示编号**，且只改可枚举的确定位置：
             a. <title>            「C 风格 · X」 → 「M02 · X」 这类
             b. <p class="sub-title">  统一成「… · <编号> · <副题>」
             c. 页尾「本系列」小目录里的 `<a href="新名">旧号 标题`
             d. 正文里的「第 N 讲」→ 编号
  第 4 步  给 <body> 加 data-series，并把系列主题与共用脚本挂上

为什么不直接全局替换 "01"→"M01"：
     正文里到处都是「第 1 个元素」「a[4]」这种数字，
     全局替换会把它们毁掉。所以只动可枚举的结构化位置。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import SERIES, PAGES, RENAME, OLD_NUM  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")

# 只处理这 18 篇（FE 那 8 篇外观独立，不动）
TARGETS = [p[1] for p in PAGES]
NEW_BY_OLD = {p[0]: p[1] for p in PAGES}
META = {p[1]: p for p in PAGES}          # 新名 → (旧名,新名,系列,编号,标题,说明,星标)

ZH = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
      6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}


def step1_rename_files():
    n = 0
    for old, new in RENAME.items():
        s, d = os.path.join(T, old), os.path.join(T, new)
        if os.path.exists(d):
            continue
        if os.path.exists(s):
            os.rename(s, d)
            n += 1
    print("  第 1 步：改名 %d 个文件" % n)


def step2_fix_refs():
    """全仓替换文件名引用（长的先替，避免 08-e01 被 08-e0 之类截断）。"""
    pairs = sorted([(o, n) for o, n in RENAME.items()],
                   key=lambda x: -len(x[0]))
    # 同时处理去掉 .html 的写法（脚本里的 DST 常量等）
    ext = [(o[:-5], n[:-5]) for o, n in pairs]
    hits = 0
    for root, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs
                   if d not in (".git", "node_modules", "__pycache__", ".vs")]
        for f in files:
            if not re.search(r'\.(html|css|js|py|md|json)$', f):
                continue
            p = os.path.join(root, f)
            if os.path.basename(p) in ("apply_series.py", "series_data.py"):
                continue                     # 这两个文件里出现旧名是正常的
            try:
                t = io.open(p, encoding="utf-8").read()
            except Exception:
                continue
            o0 = t
            for a, b in pairs:
                t = t.replace(a, b)
            for a, b in ext:
                # 只替「像文件名」的位置：前后不是字母数字
                t = re.sub(r'(?<![0-9A-Za-z_\-])' + re.escape(a) + r'(?![0-9A-Za-z_\-])',
                           b, t)
            if t != o0:
                io.open(p, "w", encoding="utf-8", newline="").write(t)
                hits += 1
    print("  第 2 步：改了 %d 个文件的文件名引用" % hits)


def series_of_num(num):
    return num[0] if num[0] in "MQEFTR" else None


def step3_fix_display():
    """改显示编号（title / sub-title / 页尾目录项）。"""
    n = 0
    for fn in TARGETS:
        p = os.path.join(T, fn)
        if not os.path.exists(p):
            print("      ! 找不到 %s" % fn)
            continue
        t = io.open(p, encoding="utf-8").read()
        meta = META[fn]
        old, new, sk, num, title, desc, star = meta
        s = SERIES[sk]

        # a. <title>
        mt = re.search(r'<title>([^<]*)</title>', t)
        if mt:
            # 去掉原来的「C 风格 · 」「实用 · 」这类前缀，换成编号
            core = re.split(r'\s*·\s*', mt.group(1), maxsplit=1)
            core = core[-1].strip() if len(core) > 1 else mt.group(1).strip()
            core = re.sub(r'^[A-Za-z0-9\-]+\s*·\s*', '', core)
            t = t[:mt.start()] + "<title>%s · %s</title>" % (num, core) + t[mt.end():]

        # b. sub-title：统一成「… · <编号> · <原副题>」
        ms = re.search(r'<p class="sub-title">([^<]*)</p>', t)
        if ms:
            old_sub = ms.group(1)
            parts = [x.strip() for x in old_sub.split("·")]
            # 去掉「UME 项目组内部教程」与旧编号/旧「第 N 讲」段
            rest = [x for x in parts
                    if x and "UME 项目组内部教程" not in x
                    and not re.fullmatch(r'(第[一二三四五六七八九十]+讲|'
                                         r'[0-9]{2}(-[A-Z][0-9]{2})?|'
                                         r'(Extra|File|C/C\+\+|C 风格|C\+\+|实用))'
                                         r'(（[^）]*）)?', x)]
            newsub = "UME 项目组内部教程 · %s（%s）" % (num, s["name"])
            if rest:
                newsub += " · " + " · ".join(rest)
            t = t[:ms.start()] + '<p class="sub-title">%s</p>' % newsub + t[ms.end():]

        # c. 页尾「本系列」小目录：<a href="X">…</a> 把编号换成新编号
        nav = re.search(r'(?s)<div class="series-nav">(.*?)</div>', t)
        if nav:
            def fix_a(m):
                href, text = m.group(1), m.group(2)
                mm = META.get(os.path.basename(href))
                if not mm:
                    return m.group(0)
                # 去掉开头的旧编号（01 / 08-E01 / 09-E03 …）与多余空白
                tt = re.sub(r'^\s*(?:\d{2}(?:-[A-Za-z]\d{2})?|\d{1,2})\s*', '',
                            text).strip()
                # 星标在 <span> 里，text 不含它；这里只重建纯文字部分
                return '<a href="%s">%s %s</a>' % (href, mm[3], tt)
            seg = re.sub(r'<a href="([^"]+)">([^<]*)</a>', fix_a, nav.group(1))
            t = t[:nav.start(1)] + seg + t[nav.end(1):]

        # d. 正文里的「第 N 讲」→ 编号
        t = re.sub(r'第\s*([一二三四五六七八九十]+)\s*讲',
                   lambda m: zh_to_num(m.group(1)), t)

        io.open(p, "w", encoding="utf-8", newline="").write(t)
        n += 1
    print("  第 3 步：改了 %d 篇的显示编号" % n)


def zh_to_num(z):
    mp = {v: k for k, v in ZH.items()}
    v = mp.get(z)
    if not v:
        return "第%s讲" % z
    return OLD_NUM.get("%02d" % v, "第%s讲" % z)


def step4_attach_theme():
    """给 <body> 加 data-series，挂系列主题与共用脚本。"""
    n = 0
    for fn in TARGETS:
        p = os.path.join(T, fn)
        t = io.open(p, encoding="utf-8").read()
        meta = META[fn]
        sk = meta[2]
        cls = SERIES[sk]["cls"]

        # body：加 data-series，并把旧的 tseries/fseries class 归一
        mb = re.search(r'<body([^>]*)>', t)
        attrs = mb.group(1)
        mc = re.search(r'class="([^"]*)"', attrs)
        classes = (mc.group(1).split() if mc else [])
        classes = [c for c in classes if c not in
                   ("tseries", "fseries", "mseries", "qseries",
                    "eseries", "rseries")]
        if cls not in classes:
            classes.insert(0, cls)
        newattrs = re.sub(r'\s*class="[^"]*"', '', attrs)
        newbody = '<body%s class="%s" data-series="%s">' % (
            newattrs.rstrip(), " ".join(classes), sk)
        t = t[:mb.start()] + newbody + t[mb.end():]

        # 主题样式表：加在最后一个 stylesheet link 之后
        if sk == "T":
            need = '<link rel="stylesheet" href="assets/css/t-theme.css">'
        else:
            need = '<link rel="stylesheet" href="assets/css/series-theme.css">'
        if need not in t:
            links = list(re.finditer(r'<link[^>]*rel="stylesheet"[^>]*>', t))
            last = links[-1]
            t = t[:last.end()] + "\n" + need + t[last.end():]

        # 共用脚本（内含文末系列跳转 + 当前页小目录）
        if "assets/js/series-common.js" not in t:
            t = t.replace("</body>",
                          '<script src="assets/js/series-common.js"></script>\n</body>', 1)

        # 旧的 .t-nav 由 t-common.js 生成，改用统一的 series-common.js
        t = re.sub(r'\s*<script src="assets/t-common\.js"></script>', '', t)

        io.open(p, "w", encoding="utf-8", newline="").write(t)
        n += 1
    print("  第 4 步：%d 篇挂上系列主题" % n)


if __name__ == "__main__":
    step1_rename_files()
    step2_fix_refs()
    step3_fix_display()
    step4_attach_theme()
