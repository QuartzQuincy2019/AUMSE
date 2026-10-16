# -*- coding: utf-8 -*-
"""修 gen_series_tables.py 的两处字段索引错误。

错在哪（两处都是我照经验猜的，没先看数据）
    ① PAGES 与 FE_PAGES 的字段顺序**不一样**：
         PAGES     = (当前名, 新文件名, 系列, 编号, 标题, 说明, 星标)
                      0        1         2     3     4     5     6
         FE_PAGES  = (文件名, 编号, 标题, 说明, 语言, 星标)
                      0       1     2     3     4     5
       我两处都按 p[1]/p[3]/p[4] 取，于是 FE 那 10 条全错位
       （把「说明」当标题、「语言」当说明）。

    ② SERIES_FILES **是含 FE 的**。
       fe-data.js 里 filesOfSeries() 只用它筛**非 FE** 系列；
       而 FE 那一格的**跳转目标**也取自它（取首篇）。
       所以正确的清单是「全部篇目」37 条，不是 27 条。
       （我先前以为它不含 FE，是因为注释写着「除 FE 自己」——
        那句话说的是 FE 的**篇数**来自 P.series，不是这个清单不含 FE。）
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\gen_series_tables.py"
t = io.open(P, encoding="utf-8").read()

# ---------- 修 ①：字段索引 ----------
old_sf = '''def series_files():
    out = []
    for key in S.PAGE_ORDER:
        if key == "FE":
            continue
        for p in S.pages_of(key):
            out.append(p[1])          # p[1] 是"对外文件名"
    return out'''
new_sf = '''def series_files():
    """「全部系列」的篇目清单 —— **含 FE**。

    用途有两个：
      · 非 FE 系列：数篇数、取首篇做跳转目标
      · FE 那一格：取首篇做跳转目标（篇数不取这里，见下）
    fe-data.js 的 filesOfSeries() 用文件名首字母筛出各系列；
    fe- 开头的都算 FE。

    注意 FE 的**篇数**不来自这个清单 —— 它取每页自己的 P.series
    （那是运行时的权威来源）。清单里保留 FE 只是为了拿到跳转目标。
    """
    out = []
    for key in S.PAGE_ORDER:
        for p in (S.pages_of(key) if key != "FE" else S.FE_PAGES):
            out.append(p[1] if key != "FE" else p[0])
    return out'''
assert old_sf in t, "series_files 锚点未匹配"
t = t.replace(old_sf, new_sf, 1)

# ---------- 修 ②：FE 的字段顺序 ----------
old_rp = '''        for i, p in enumerate(pages):
            fn, num, title = p[1], p[3], p[4]'''
new_rp = '''        for i, p in enumerate(pages):
            # PAGES 与 FE_PAGES 的字段顺序不同，必须分开取：
            #   PAGES    = (当前名, 新文件名, 系列, 编号, 标题, 说明, 星标)
            #   FE_PAGES = (文件名, 编号, 标题, 说明, 语言, 星标)
            if key == "FE":
                fn, num, title = p[0], p[1], p[2]
            else:
                fn, num, title = p[1], p[3], p[4]'''
assert old_rp in t, "render_pages 锚点未匹配"
t = t.replace(old_rp, new_rp, 1)

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  gen_series_tables.py 已修正两处字段索引")
print("     · series_files() 现在含 FE（共全部篇目）")
print("     · render_pages() 对 FE 用 p[0]/p[1]/p[2]")
