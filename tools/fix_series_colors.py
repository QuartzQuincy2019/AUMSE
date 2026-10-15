# -*- coding: utf-8 -*-
"""重写 build_series_css.py 的配色策略。

问题：原来用 `color-mix(in srgb, {ink} 62%, transparent)` 派生文字色，
实际算出来是 **半透明文字**（如 rgba(...,0.66) 叠在深底上），
对比度掉到 1.09:1。而且透明底 + 渐变底让自动检查与肉眼都难判断。

新策略（照抄 T 那套，已验证 0 失败）：
  · 文字色一律用**不透明的实色**，不用 alpha 派生
  · 每个系列显式给出：链接色 / 副标题色 / 当前项配色 / 表格头配色
  · 代码块、输出块、返回按钮都给**不透明底色**
  · 顶部条保留渐变（好看），但同时给 background-color 兜底，
    这样即使渐变失效或自动检查读不到渐变，也可读
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\build_series_css.py"
t = io.open(P, encoding="utf-8").read()

# 在 series_data 的每个系列里补一组「实色」字段
PATCH = '''
# ---------------------------------------------------------------- 配色补丁
# 每个系列补一组**不透明**的实色。原来靠 color-mix 派生，
# 算出来是半透明文字，暗底上对比度只有 1.09 —— 读不出来。
FIXED = {
    #            亮色                                  暗色
    # link    副标题  当前项底 当前项字  表头底 表头字
    "M": ("#14539f", "#4a5b70", "#1f6feb", "#ffffff", "#dbe8f8", "#12447f",
          "#8cc0ff", "#9fb0c6", "#5aa2f0", "#0d1420", "#22304a", "#cfe0f5"),
    "Q": ("#0a7157", "#40584f", "#0f9d76", "#ffffff", "#d6efe6", "#075c46",
          "#7adfc4", "#9db8ae", "#3fc4a0", "#0a1614", "#1c3b33", "#c9ece1"),
    "E": ("#67289a", "#554067", "#8b3fbe", "#ffffff", "#eddcf6", "#541f80",
          "#d6a6f2", "#b9a6c8", "#b877e0", "#150d1c", "#33203f", "#ead9f5"),
    "F": ("#0f6b3a", "#46584f", "#17864a", "#ffffff", "#d9efe2", "#0b5730",
          "#7fd8a8", "#a2bbaa", "#4fc98d", "#0f1a14", "#24402f", "#d6f0e2"),
    "R": ("#a02b40", "#6b4550", "#d1435b", "#ffffff", "#f7dde0", "#8a2338",
          "#f7a8b6", "#c9a6ad", "#ef7288", "#1a0e11", "#3d2229", "#f5dae0"),
    "T": ("#8a6008", "#6f5c26", "#c8901a", "#3d2c05", "#fdf3dc", "#5c470f",
          "#f0cc72", "#a89871", "#e0b23f", "#16120a", "#3a2d10", "#f4e3b4"),
}
'''

if "FIXED = {" not in t:
    i = t.find("TPL = \"\"\"")
    t = t[:i] + PATCH + "\n" + t[i:]
    print("  ✓ 加入 FIXED 实色表")

# 生成时按 FIXED 覆盖有问题的规则
OLD = '''    txt = "".join(out)'''
NEW = '''    txt = "".join(out)

    # ---------- 用不透明实色覆盖掉所有 color-mix 派生出来的文字/底色 ----------
    # 这些是「算出来半透明、读不清」的地方，逐系列换成实色。
    for sk in ORDER:
        s = SERIES[sk]
        if sk == "T" or sk not in FIXED:
            continue
        (link, sub, curbg, curfg, thbg, thfg,
         dlink, dsub, dcurbg, dcurfg, dthbg, dthfg) = FIXED[sk]
        sel = 'body[data-series="%s"][data-series="%s"]' % (sk, sk)
        txt += f"""
/* ---- {sk} 系列：把 color-mix 派生色换成不透明实色 ---- */
{sel} a{{color:{link}}}
{sel} a:hover{{color:{s['c3']}}}
{sel} .sub-title{{color:{sub}}}
{sel} #toc a{{color:{sub}}}
{sel} table th{{background:{thbg};color:{thfg};border-color:{s['c3']}}}
{sel} .series-nav a.cur{{background:{curbg} !important;color:{curfg} !important;
  border-color:{curbg} !important}}
{sel} .s-nav-h{{color:{link}}}
{sel} .s-nav-grid a{{color:{link}}}
{sel} .s-nav-toc a{{color:{link}}}
{sel} .series-nav b{{color:{sub}}}
{sel} .series-nav a{{color:{link}}}

@media (prefers-color-scheme: dark){{
  {sel} a{{color:{dlink}}}
  {sel} a:hover{{color:{s['d3']}}}
  {sel} .sub-title{{color:{dsub}}}
  {sel} #toc a{{color:{dsub}}}
  {sel} table th{{background:{dthbg};color:{dthfg};border-color:{s['d3']}}}
  {sel} .series-nav a.cur{{background:{dcurbg} !important;color:{dcurfg} !important;
    border-color:{dcurbg} !important}}
  {sel} .s-nav-h{{color:{dlink}}}
  {sel} .s-nav-grid a{{color:{dsub}}}
  {sel} .s-nav-toc a{{color:{dlink}}}
  {sel} .series-nav b{{color:{dsub}}}
  {sel} .series-nav a{{color:{dsub}}}
  /* 返回 home：给不透明底，别让自动检查与低端浏览器读成「深字压深底」 */
  {sel} .home-fab{{background-color:{s['d3']};
    background-image:linear-gradient(140deg,{s['d4']},{s['d3']}) !important;
    color:{s['d1']} !important}}
  {sel} .home-fab:hover{{background-color:{s['d4']} !important;color:{s['d1']} !important}}
  {sel} .s-nav .s-nav-grid a{{background-color:#22262e}}
}}
{sel} .home-fab{{background-color:{s['c2']};
  background-image:linear-gradient(140deg,#fff,{s['c2']}) !important;
  color:{link} !important}}
'''
    for _sk in ORDER:
        if _sk != "T" and _sk in FIXED:
            s = SERIES[_sk]
            txt += f'body[data-series="{_sk}"][data-series="{_sk}"]::before{{background-color:{s["c3"]} !important;background-image:none}}\\n'
    io.open(OUT, "w", encoding="utf-8", newline="\\n").write(txt)
    print("  ✓ 已生成 %s（%d 字符，含实色覆盖）" % (os.path.basename(OUT), len(txt)))
    for sk in ORDER:
        s = SERIES[sk]
        print("      %-2s %-42s %s" % (sk, s["banner"],
                                       "保留原样式" if s.get("keep_legacy") else "生成主题"))
    return'''

assert OLD in t, "没找到写入点"
t = t.replace(OLD, NEW, 1)

# 去掉原来的写入与打印（避免重复写）
old_tail = '''    txt = "".join(out)
    io.open(OUT, "w", encoding="utf-8", newline="\\n").write(txt)
    print("  ✓ 已生成 %s（%d 字符）" % (os.path.basename(OUT), len(txt)))
    for sk in ORDER:
        s = SERIES[sk]
        print("      %-2s %-42s %s" % (sk, s["banner"],
                                       "保留原样式" if s.get("keep_legacy") else "生成主题"))'''
if old_tail in t:
    t = t.replace(old_tail, "", 1)
    print("  ✓ 去掉旧的写入段")

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  ✓ build_series_css.py 已改为实色策略")
