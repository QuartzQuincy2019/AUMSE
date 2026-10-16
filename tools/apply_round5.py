# -*- coding: utf-8 -*-
"""本轮五件事的批量处理。

1. Q03/Q04 示例名字换成抽象的：
     灰羽·夜行者  → 忘情牛肉面
     小灰         → 奶蛙
     北境·霜牙岭   → University of Naiwa
     灰羽         → 牛肉面        ← 单独出现的「灰羽」是简称，跟着全名走
   替换顺序：先长后短，否则「灰羽」会先把「灰羽·夜行者」拆坏。

2. T02 删掉「教程到这里就结束了」那张卡（整张，1081 字符）
   它是**全课程回顾**（列出 01~09 每一篇），而且写在 T02 里 ——
   系列还在长，这种回顾放哪里都会过期。用户要求删掉，就整张删。

3. 系列标签：Qt · Q → C++&Qt · Q ；File · F → 文件  ·  F
   改 series_data.py 的 label 字段（首页分组标题与系列导航都用它）。

4. T03 结尾加一条指向 R01 的「延伸阅读」链接，并给这类链接单独做样式

5. FE 的 div.series-nav 里 a（非 .cur）在暗色下背景是白的 —— 修 fe-dark.css

用法：
    python apply_round5.py --dry
    python apply_round5.py
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
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")
TOOLS = os.path.join(R, "tools")

# =====================================================================
# 1. 示例名字
# =====================================================================
RENAME = [
    ("灰羽·夜行者·第三形态", "忘情牛肉面·第三形态"),   # 先处理带后缀的
    ("北境霜牙岭的守望者", "Naiwa 大学城的守望者"),
    ("灰羽·夜行者", "忘情牛肉面"),
    ("北境·霜牙岭", "University of Naiwa"),
    ("小灰", "奶蛙"),
    ("灰羽", "牛肉面"),                                # 最后才是简称
]


def fix_names(dry):
    files = ["_q03_body.html", "_q04_body.html"]
    for f in files:
        p = os.path.join(TOOLS, f)
        t = io.open(p, encoding="utf-8").read()
        n = 0
        for old, new in RENAME:
            k = t.count(old)
            if k:
                t = t.replace(old, new)
                n += k
        print("  %-18s 换名 %2d 处" % (f, n))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)


# =====================================================================
# 2. T02 删掉「教程到这里就结束了」整张卡
# =====================================================================
def fix_t02(dry):
    p = os.path.join(T, "t02-unicode-and-encoding.html")
    t = io.open(p, encoding="utf-8").read()
    key = '<div class="card note">\n  <div class="card-t">教程到这里就结束了'
    i = t.find(key)
    if i < 0:
        print("  T02：没找到那张卡（可能已删）")
        return
    # 从 i 起配对 <div> / </div> 找到该卡的结束
    depth = 0
    k = i
    end = i
    while True:
        m = re.compile(r'<div\b|</div>').search(t, k)
        if not m:
            break
        if m.group(0).startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = m.end()
                break
        k = m.end()
    seg = t[i:end]
    t2 = t[:i] + t[end:]
    t2 = re.sub(r'\n{3,}', '\n\n', t2)
    print("  T02：删掉整张卡 %d 字符（%s …）" % (len(seg), seg[:46].replace("\n", " ")))
    if not dry:
        io.open(p, "w", encoding="utf-8", newline="").write(t2)


# =====================================================================
# 3. 系列标签
# ---------------------------------------------------------------------
# 标签共出现在三个地方，必须一起改，否则页尾「全部系列」与首页会对不上：
#   tools/series_data.py            首页分组数据（label 字段）
#   assets/series-common.js         SERIES 映射（非 FE 页尾的「全部系列」）
#   assets/fe-data.js               ALL_SERIES（FE 页尾的「全部系列」）
# 注意用**字面 &**，不要写 &amp; —— 三处都是 textContent / JSON，
# 不是 HTML 文本，写 &amp; 会原样显示出来。
# =====================================================================
LABELS = [
    ('"label": "Qt · Q"', '"label": "C++&Qt · Q"'),
    ('"label": "File · F"', '"label": "文件 · F"'),
    ("label: 'Qt · Q'", "label: 'C++&Qt · Q'"),
    ("label: 'File · F'", "label: '文件 · F'"),
    ("lab: 'Qt · Q'", "lab: 'C++&Qt · Q'"),
    ("lab: 'File · F'", "lab: '文件 · F'"),
]


def fix_labels(dry):
    targets = [os.path.join(TOOLS, "series_data.py"),
               os.path.join(A, "series-common.js"),
               os.path.join(A, "fe-data.js")]
    for p in targets:
        t = io.open(p, encoding="utf-8").read()
        n = 0
        for old, new in LABELS:
            if old in t:
                t = t.replace(old, new)
                n += 1
        print("  %-24s 改 %d 处" % (os.path.basename(p), n))
        if n and not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)


# =====================================================================
# 4. T03 结尾加 R01 的延伸链接（+ 样式）
# =====================================================================
SEE_ALSO_CSS = """
/* ---------- 延伸阅读（跨篇链接） ---------- */
/* 这类链接以后会经常加，所以单开一个样式，别用临时的行内写法。
   放在正文末尾、NAV-AUTO 之前。 */
.see-also{margin:26px 0 0;padding:14px 18px;border:1px solid var(--line-2);
  border-left:5px solid var(--s-main,var(--blue));border-radius:0 10px 10px 0;
  background:var(--bg-soft)}
.see-also .hd{font-weight:700;font-size:13.5px;color:var(--fg-2);
  margin-bottom:8px}
.see-also ul{margin:0;padding-left:20px}
.see-also li{font-size:14px;line-height:1.85;margin:4px 0}
.see-also a{font-weight:700}
.see-also .why{color:var(--fg-3);font-size:13px}
"""

T03_LINK = """
<div class="see-also">
  <div class="hd">延伸阅读</div>
  <ul>
    <li><a href="r01-font-design-metrics.html">R01 · 字体设计里的几个基本概念</a>
      <span class="why">—— 本篇量出来的 ascender / descender / x 字高 / 行高，
      在那一篇里讲清了各自的定义与相互关系。看完就知道这些数字为什么必须实测。</span></li>
  </ul>
</div>
"""


def fix_t03(dry):
    p = os.path.join(T, "t03-font-file-anatomy.html")
    t = io.open(p, encoding="utf-8").read()
    if 'class="see-also"' in t:
        print("  T03：已有延伸阅读块，跳过")
    else:
        # T03 是早期页面，**没有** <!-- NAV-AUTO --> 锚点
        # （返回 home 是直接写在 HTML 里的）。所以插在 <footer> 之前 ——
        # 正文结束、页脚开始的交界处，正是「延伸阅读」该在的位置。
        i = t.find("<footer>")
        if i < 0:
            print("  !! T03 找不到 <footer>")
        else:
            t2 = t[:i] + T03_LINK.strip("\n") + "\n\n" + t[i:]
            print("  T03：在 <footer> 前插入 R01 延伸链接（%d 字符）" % len(T03_LINK))
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)

    # 样式放 genelayout.css —— 那是所有页面都加载的公共层，
    # 「延伸阅读」以后每篇都可能加，属于通用的跨篇链接样式。
    # 不要放进某一篇的样式表（T03 根本没有自己的样式表，它用 t-theme.css）。
    gp = os.path.join(A, "genelayout.css")
    c = io.open(gp, encoding="utf-8").read()
    if ".see-also{" in c:
        print("  genelayout.css 已有 .see-also")
        return
    if not dry:
        io.open(gp, "a", encoding="utf-8", newline="\n").write(SEE_ALSO_CSS)
    print("  genelayout.css：追加 .see-also（%d 字符）" % len(SEE_ALSO_CSS))



# =====================================================================
# 5. FE series-nav 暗色下的 a 背景
# =====================================================================
def fix_fe_nav(dry):
    p = os.path.join(A, "fe-dark.css")
    c = io.open(p, encoding="utf-8").read()
    # 先看现状：series-nav 的 a 有没有被单独设成白底
    hits = [m.group(0) for m in re.finditer(r'[^\n{}]*series-nav[^\n{}]*\{[^}]*\}', c)]
    print("  fe-dark.css 现有 series-nav 规则 %d 条：" % len(hits))
    for h in hits:
        print("      " + re.sub(r'\s+', ' ', h).strip()[:150])
    add = """
/* ---------- 系列导航：暗色下的链接底色 ---------- */
/* 问题：div.series-nav 里的 a（非 .cur）在暗色模式下背景是白的。
   浅色主题给它们留了 var(--sfc-2) 之类的浅底，fe-dark.css 没有覆盖到，
   于是浅色值漏了过来。这里把非当前项统一压成深底。 */
body[data-series="FE"] .series-nav a:not(.cur){
  background:#1e242e;border-color:#374556;color:#c3cfdd;
}
body[data-series="FE"] .series-nav a:not(.cur):hover{
  background:#26303c;border-color:#4a586f;color:#e6ecf4;
}
body[data-series="FE"] .series-nav .ss-cur{
  background:#2456c4;border-color:#2456c4;color:#fff;
}
body[data-series="FE"] .series-nav .ss-empty{
  background:transparent;border-color:#374556;color:#95a0b0;
}
"""
    if "series-nav" in c and "#1e242e" in c:
        print("  已有暗色覆盖，跳过")
        return
    if not dry:
        io.open(p, "a", encoding="utf-8", newline="\n").write(add)
    print("  已向 fe-dark.css 追加 series-nav 暗色覆盖（%d 字符）" % len(add))


def main():
    dry = "--dry" in sys.argv
    print("1. 示例名字")
    fix_names(dry)
    print()
    print("2. T02 删卡")
    fix_t02(dry)
    print()
    print("3. 系列标签")
    fix_labels(dry)
    print()
    print("4. T03 延伸阅读")
    fix_t03(dry)
    print()
    print("5. FE series-nav 暗色")
    fix_fe_nav(dry)
    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
