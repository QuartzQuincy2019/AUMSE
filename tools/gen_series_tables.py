# -*- coding: utf-8 -*-
"""从 tools/series_data.py 生成 assets/series-common.js 与 assets/fe-data.js 里的篇目表。

为什么要有这个生成器
    同一份篇目数据原来散在**三处**手写副本里：
        tools/series_data.py          权威来源
        assets/series-common.js       PAGES（非 FE 页尾的「本系列」「全部系列」）
        assets/fe-data.js             SERIES_FILES（FE 页尾的「全部系列」）
    于是每次加篇目都要改好几处，漏一处就出问题。本会话已经栽过三次：
        · FE 页尾的「相关 · R」一直点不动（fe-data.js 里 f: null）
        · 各 FE 页 series 条数 8 / 9 不一致
        · FE-09 标为重点后只有它自己带星
    前两次的补救是「再加一个同步脚本」，等于把副本数又加了一层。
    这次直接把副本**生成**掉 —— 加篇目只改 series_data.py，然后重跑本脚本。

生成什么
    series-common.js 里的
        var PAGES = [ … ];          （按 ORDER 分组的全部篇目）
    fe-data.js 里的
        var SERIES_FILES = [ … ];   （只给「数篇数 / 取首篇做跳转目标」用）
    两处都只替换对应数组的内容，**其余代码原样保留** ——
    这两个文件里还有大量手写的运行逻辑，不能被生成器碰。

SERIES_FILES 与 PAGES 的区别
    PAGES 含 FE 各篇（FE 页尾的「本系列」要用到）；
    SERIES_FILES **不含** FE 各篇 —— FE 的篇数取自每页自己的 P.__series，
    那边是运行时的权威来源。这个差异是有意的，别「顺手统一」。

用法：
    python gen_series_tables.py --check    只比对，不写（CI/自检用）
    python gen_series_tables.py            写入
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
A = os.path.join(R, "SharingGroup", "tutorials", "assets")

sys.path.insert(0, TOOLS)
import series_data as S  # noqa: E402


# ----------------------------------------------------------------------
# 组装 SERIES_FILES：只含**非 FE** 的篇目（见文件头说明）
# ----------------------------------------------------------------------
def series_files():
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
    return out


# ----------------------------------------------------------------------
# 渲染 PAGES（series-common.js）
# ----------------------------------------------------------------------
def render_pages():
    lines = ["  var PAGES = ["]
    for ki, key in enumerate(S.PAGE_ORDER):
        pages = S.pages_of(key) if key != "FE" else S.FE_PAGES
        lines.append("    /* ---- %s：%s ---- */"
                     % (key, S.SERIES[key]["banner"]))
        for i, p in enumerate(pages):
            # PAGES 与 FE_PAGES 的字段顺序不同，必须分开取：
            #   PAGES    = (当前名, 新文件名, 系列, 编号, 标题, 说明, 星标)
            #   FE_PAGES = (文件名, 编号, 标题, 说明, 语言, 星标)
            if key == "FE":
                fn, num, title = p[0], p[1], p[2]
            else:
                fn, num, title = p[1], p[3], p[4]
            lines.append("    { f: %-34s n: %-12s t: %s, s: '%s' },"
                         % ("'%s'," % fn, "'%s'," % num, "'%s'" % title, key))
        if ki < len(S.PAGE_ORDER) - 1:
            lines.append("")
    lines.append("  ];")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 渲染 SERIES_FILES（fe-data.js）
# ----------------------------------------------------------------------
def render_series_files():
    files = series_files()
    lines = ["  var SERIES_FILES = ["]
    row = []
    for f in files:
        row.append("'%s'," % f)
        if len(row) == 3:
            lines.append("    " + "".join(row))
            row = []
    if row:
        lines.append("    " + "".join(row))
    # 去掉最后一行的尾逗号，保持与原文件一致的写法
    if lines[-1].rstrip().endswith(","):
        lines[-1] = lines[-1].rstrip()[:-1]
    lines.append("  ];")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 替换
# ----------------------------------------------------------------------
def splice(text, name, new_block, indent_anchor):
    """把 `var NAME = [ … ];` 整块换成 new_block，其余原样。"""
    pat = re.compile(r"(?s)( *var " + re.escape(name) + r"\s*=\s*\[).*?(\n"
                     + indent_anchor + r"\];)")
    m = pat.search(text)
    if not m:
        return None, None
    old = m.group(0)
    # new_block 已自带缩进与结尾的 "  ];"
    out = text[:m.start()] + new_block + text[m.end():]
    return out, old


def main():
    check = "--check" in sys.argv

    # ---------- series-common.js 的 PAGES ----------
    p1 = os.path.join(A, "series-common.js")
    t1 = io.open(p1, encoding="utf-8").read()
    new1 = render_pages()
    out1, old1 = splice(t1, "PAGES", new1, "  ")
    if out1 is None:
        print("  !! series-common.js 里找不到 PAGES 数组")
        return

    # ---------- fe-data.js 的 SERIES_FILES ----------
    p2 = os.path.join(A, "fe-data.js")
    t2 = io.open(p2, encoding="utf-8").read()
    new2 = render_series_files()
    out2, old2 = splice(t2, "SERIES_FILES", new2, "  ")
    if out2 is None:
        print("  !! fe-data.js 里找不到 SERIES_FILES 数组")
        return

    def n_items(block):
        return len(re.findall(r"\{ f:", block)) or len(re.findall(r"'[^']+\.html'", block))

    print("  series-common.js  PAGES        %d 条 → %d 条"
          % (n_items(old1), n_items(new1)))
    print("  fe-data.js        SERIES_FILES %d 条 → %d 条"
          % (n_items(old2), n_items(new2)))

    same1 = (old1 == new1)
    same2 = (old2 == new2)
    print("  内容是否已一致：PAGES=%s  SERIES_FILES=%s" % (same1, same2))

    if check:
        print()
        print("  --check：未写入")
        return

    if not same1:
        io.open(p1, "w", encoding="utf-8", newline="").write(out1)
        print("  已写入 series-common.js")
    if not same2:
        io.open(p2, "w", encoding="utf-8", newline="").write(out2)
        print("  已写入 fe-data.js")
    if same1 and same2:
        print("  两个文件都是最新的，无需改动")


if __name__ == "__main__":
    main()
