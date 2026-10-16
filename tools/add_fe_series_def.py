# -*- coding: utf-8 -*-
"""给 series_data.py 补上 FE 的系列定义（纯新增，不改现有语义）。

背景
    gen_series_tables.py 要生成 series-common.js 的 PAGES 与 fe-data.js 的
    SERIES_FILES，两者都**需要 FE 的篇目**。但 series_data.py 里：

        # 首页分组顺序（FE 单独处理）
        ORDER = ["T", "F", "M", "R", "Q", "E"]

    ORDER 不含 FE，而且 SERIES 里也没有 FE 的条目 ——
    原因是 FE 的外观自成一系（它不走 series-theme.css 那套生成），
    所以 make_pages.py 里 FE 的 banner/label 是**硬写**的。

    结果就是同一份 FE 元信息散在两处：series_data.py 的 FE_PAGES
    和 make_pages.py 的硬写字符串。

做法（加法，不动老语义）
    1. SERIES 里新增 "FE" 条目 —— 只给 make_pages / 生成器要用的字段
       （label / banner / desc）；主题色字段不写，并注明原因。
       **不把 FE 加进 ORDER** —— 有 6 个脚本依赖「ORDER 不含 FE」
       （build_series_css / fix_series_colors / reorder_fe_links 等），
       动它风险太大。
    2. 另加 PAGE_ORDER = ORDER + ["FE"]，专门给
       「要遍历全部系列（含 FE）」的地方用：
       make_pages.py（首页分组）与 gen_series_tables.py（生成篇目表）。
    3. make_pages.py 里那段硬写的 FE banner/label 改成从 SERIES 取，
       消掉那处重复。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
TOOLS = os.path.join(R, "tools")

FE_ENTRY = '''
    # FE：前端系列。外观自成一系（走 fe_base.css / fe-dark.css，
    # 不由 build_series_css.py 从本表生成主题），所以这里**只给
    # 页面与导航要用的字段**，不写 c1~d4 / ink / dink 那套主题色。
    "FE": {
        "name": "FrontEnd",
        "num": "FE",
        "banner": "FE 系列 · 前端基础",
        "label": "前端 · FE",
        "desc": "HTML 与 CSS：界面长什么样、怎么让它好看",
        "cls": "feseries",
    },
}
'''

PAGE_ORDER = '''
# 遍历**全部**系列（含 FE）时用这个。
# ORDER 不含 FE 是有意的 —— 主题生成那套脚本依赖它跳过 FE；
# 但首页分组与篇目表生成需要 FE，所以单列一个。
PAGE_ORDER = ORDER + ["FE"]
'''


def main():
    dry = "--dry" in sys.argv

    # ---------- 1. series_data.py ----------
    p = os.path.join(TOOLS, "series_data.py")
    t = io.open(p, encoding="utf-8").read()

    if '"FE": {' in t:
        print("  1. series_data.py 已有 FE 条目")
    else:
        # SERIES 字典的结尾：找到 "R" 条目的收尾 "},\n}" 再替换
        i = t.find('SERIES = {')
        j = t.find('\n}\n', i)
        if j < 0:
            print("  !! 找不到 SERIES 的结尾")
            return
        t = t[:j] + "\n" + FE_ENTRY.rstrip("\n") + t[j + 3:]
        print("  1. series_data.py 追加 FE 系列定义")

    if "PAGE_ORDER" in t:
        print("     已存在 PAGE_ORDER")
    else:
        old = 'ORDER = ["T", "F", "M", "R", "Q", "E"]\n'
        if old not in t:
            print("     !! 找不到 ORDER 那一行")
        else:
            t = t.replace(old, old + PAGE_ORDER, 1)
            print("     追加 PAGE_ORDER = ORDER + ['FE']")

    if not dry:
        io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---------- 2. make_pages.py：FE 的 banner/label 改成取 SERIES ----------
    p = os.path.join(TOOLS, "make_pages.py")
    t = io.open(p, encoding="utf-8").read()
    old = '''    fe_items = [(a, b, c, d, e, f) for a, b, c, d, e, f in FE_PAGES]
    groups.append({"key": "FE", "label": "前端 · FE",
                   "banner": "FE 系列 · 前端基础",
                   "desc": "HTML 与 CSS：界面长什么样、怎么让它好看",
                   "count": len(fe_items), "items": fe_items})'''
    new = '''    fe_items = [(a, b, c, d, e, f) for a, b, c, d, e, f in FE_PAGES]
    # FE 的 label / banner / desc 以前是**硬写**在这里的，与
    # series_data.py 的 FE_PAGES 分成两处。现在统一从 SERIES["FE"] 取 ——
    # 生成器 gen_series_tables.py 也依赖 SERIES 里有 FE。
    _fe = SERIES["FE"]
    groups.append({"key": "FE", "label": _fe["label"],
                   "banner": _fe["banner"], "desc": _fe["desc"],
                   "count": len(fe_items), "items": fe_items})'''
    if new in t:
        print("  2. make_pages.py 已改成取 SERIES['FE']")
    elif old in t:
        t = t.replace(old, new, 1)
        print("  2. make_pages.py FE 的元信息改为取 SERIES['FE']")
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)
    else:
        print("  !! 2. make_pages.py 里那段 FE 硬写未匹配")

    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))

    # ---------- 自检 ----------
    if not dry:
        sys.path.insert(0, TOOLS)
        import importlib
        import series_data as S
        importlib.reload(S)
        print()
        print("  自检：")
        print("     ORDER       = %s" % (S.ORDER,))
        print("     PAGE_ORDER  = %s" % (S.PAGE_ORDER,))
        print("     SERIES['FE'] = %s" % (S.SERIES.get("FE"),))
        n = sum(len(S.pages_of(k) if k != "FE" else S.FE_PAGES)
                for k in S.PAGE_ORDER)
        print("     PAGE_ORDER 下总篇数 = %d" % n)


if __name__ == "__main__":
    main()
