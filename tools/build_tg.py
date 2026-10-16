# -*- coding: utf-8 -*-
"""第一步 · A：生成 tg_L.css（全局亮色）与 tg_D.css（全局暗色）。

为什么要先生成、再删源
----------------------
「先删后加」如果中途出问题，页面会瞬间失去主题变量（白底黑字乱掉）。
反过来「先生成、再逐份删」的话，任何一刻删到一半，页面仍然是**正确的** ——
旧的块还在原位，新的文件只是多加载了一份等价定义。

这也让验证变简单：生成后先跑一遍全量检查，
确认 tg 两文件本身没问题，再动手删每份样式表里的副本。

本轮先收「28 份全都有的」那 4 个块（它们是最纯粹的重复）：
    ① :root{--sfc:…}                          亮色表面变量
    ② @media dark{ :root:root{--sfc:…} }       暗色表面变量
    ③ @media dark{ code/.hd/.k/.mnemonic/… }   暗色组件补丁
    ④ @media dark{ :root:root{--bg-soft:…} }   暗色语义色变量

tg_L.css 与 tg_D.css 都由 tools/series_data.py 驱动生成（配色不手写），
生成器随后补 —— 本轮先把「已存在于各页、逐字相同」的部分收进来，
保证零行为变化。
"""
import io
import os
import re
import sys
import collections

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
# 注意：必须把本脚本的**产物**也排除掉，否则第二次运行会把
# tg_L.css / tg_D.css 当成「参与求交的文件」，
# 而它们里没有那 4 个块 → 交集瞬间变成 0 个（第一次就踩了这个坑）。
SKIP = {"series-theme.css", "t-theme.css", "fe-dark.css",
        "tg_L.css", "tg_D.css"}


def blocks(css):
    out = []
    i, n = 0, len(css)
    while i < n:
        m = re.match(r'\s*(/\*.*?\*/\s*)*', css[i:], re.S)
        j = i + m.end()
        k = css.find("{", j)
        if k < 0:
            break
        depth, p = 0, k
        while p < n:
            if css[p] == "{":
                depth += 1
            elif css[p] == "}":
                depth -= 1
                if depth == 0:
                    p += 1
                    break
            p += 1
        out.append((j, k, p))          # (头部起点, '{' 位置, 块结束)
        i = p
    return out


def key(b):
    return re.sub(r'\s+', ' ', re.sub(r'/\*.*?\*/', '', b, flags=re.S)).strip()


files = sorted(f for f in os.listdir(A) if f.endswith(".css") and f not in SKIP)
src = {f: io.open(os.path.join(A, f), encoding="utf-8").read() for f in files}

# ---------- 可选：从某个 git 提交里取源 ----------
# 搬块脚本把各页里的公共块删掉之后，工作区就再也抽不出这些块了。
# 想**重新生成**（比如改了文件头注释）就得回到搬块前的版本取源。
#   python build_tg.py --from-rev HEAD
FROM_REV = None
if "--from-rev" in sys.argv:
    FROM_REV = sys.argv[sys.argv.index("--from-rev") + 1]
if FROM_REV:
    import subprocess
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel = os.path.relpath(A, repo).replace("\\", "/")
    n = 0
    for f in files:
        r = subprocess.run(["git", "show", "%s:%s/%s" % (FROM_REV, rel, f)],
                           cwd=repo, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0 and r.stdout:
            src[f] = r.stdout
            n += 1
    print("  已从 %s 取到 %d/%d 份源文件" % (FROM_REV, n, len(files)))

cnt = collections.Counter()
for f, c in src.items():
    for (_, k, p) in blocks(c):
        cnt[key(c[:p].split("{", 1)[-1] if False else c[0:p])] += 1   # 占位，下面重算

# 正确做法：按块文本统计
cnt = collections.Counter()
for f, c in src.items():
    for (_, k, p) in blocks(c):
        st = c.rfind("\n", 0, k) + 1
        cnt[key(c[st:p])] += 1

ALL = len(files)
exact = [k for k, n in cnt.items() if n == ALL]
print("  全部 %d 份都有的块：%d 个" % (ALL, len(exact)))

# ---------- 分类：亮色 / 暗色 ----------
light, dark = [], []
for k in exact:
    if re.match(r'\s*@media\s*\(\s*prefers-color-scheme\s*:\s*dark', k):
        dark.append(k)
    else:
        light.append(k)

print("     亮色 %d 个，暗色 %d 个" % (len(light), len(dark)))

HEAD_L = """/* =====================================================================
   tg_L.css —— 全局亮色主题层（theme global · Light）
   ---------------------------------------------------------------------
   由 tools/build_tg.py 生成，**不要手改**。
   配色数据在 tools/series_data.py 与 build_tg.py 的 LIGHT 段里。

   这一层装的是「所有页面都一样」的亮色定义：
     · --sfc / --sfc-2 / --sfc-3 / --sfc-hover / --sfc-glass  表面变量
     · 各系列的亮色主题（见 series-theme.css）
   加载顺序：genelayout.css → tg_L.css → tg_D.css → sp_<page>.css
   ===================================================================== */

"""

HEAD_D = """/* =====================================================================
   tg_D.css —— 全局暗色主题层（theme global · Dark）
   ---------------------------------------------------------------------
   由 tools/build_tg.py 生成，**不要手改**。

   为什么暗色要单独一层
     之前每份样式表末尾都追加了一段暗色补丁，追加了 28~30 遍 ——
     同一批规则（code / .mnemonic / .k / --bg-soft …）在 30 个文件里
     逐字重复。这一层把它们收成一份。

   放在 tg_L.css **之后**加载，所以能覆盖亮色；
   页面自己的 sp_<page>.css 再放在最后，个别例外仍可覆盖这里。

   注意：下面每个块**自带** `@media (prefers-color-scheme: dark)`，
   不再套一层外壳 —— 嵌两层虽然合法，但纯属冗余。

   这些规则原先散在 28 份页面样式表里逐字重复（每份末尾追加一段），
   合并时把原来的行内说明也一并收在这里，免得理由丢失：
     code      行内代码 —— 全站最多的一块，暗色下必须是深底亮字
     .hd       小标题条
     .k        紫色小标记
     .mnemonic 助记块（e02 那份当初漏了暗色，是「逐份打补丁」漏掉的典型）
     .cpp-note C++ 备注块
     .lv.l0/1/2 作用域层级
     .ch.end   字符串内存图的结尾格
     .ptr-demo 指针演示区
   ===================================================================== */

"""

TAIL_D = ""

# =====================================================================
# 语言标注（.lang）—— 每个语言一个专属色
# ---------------------------------------------------------------------
# 需求（用户指定，浅色模式）：
#     CSS  天蓝色底 + 白字        HTML 橙红色底 + 白字
#     C++  深蓝色底 + 白字        C    蓝紫色底 + 白字
#     JS   黄底 + 深字 —— 见下面「为什么 JS 是唯一深字的」
#
# 为什么多数色值比「标准色」暗
#     纯正的黄（#eab308）配白字只有 1.92:1，天蓝（#0ea5e9）配白字只有 2.77:1 ——
#     都远低于 WCAG 的 4.5:1。所以往同色调的深处压，压到刚好达标为止
#     （CSS 压到 #0478ab 得 4.91:1）。下面每个色值都标了实测对比度，
#     改动前请重新验算。
#
# 为什么 JS 是唯一「深字」的
#     黄不能用「压暗 + 白字」来解决 —— 压到 #8a5f05 虽然达标（5.65:1），
#     但那时它已经不像黄了。用户给的方案更对：
#         底 #FFD400 + 字 #0D1110  →  13.28:1
#     保留真正的黄色，靠**换成深字**拿到对比度。这比压暗底色好得多，
#     所以 JS 单独走这一套，其余四个语言维持「实色底 + 白字」。
#
# 为什么不用 .tag.X
#     .tag.b/.g/.r/.v 这套已经被「本讲：…」「可以/不要这样写」等
#     语义标签用掉了，M06 还用它做权限标记（.tag.pub/.pri/.pro）。
#     语言标注单开一个 .lang.X 命名空间，避免和它们抢颜色。
LANG_CSS = """/* ---------- 语言标注（.lang）---------- */
/* 浅色：实色底 + 白字（JS 例外，用深字）。括号内是实测对比度，均 ≥ 4.5:1 */
.lang{display:inline-block;font-family:var(--mono);font-size:11.5px;
  font-weight:700;padding:1.5px 9px;border-radius:999px;
  color:#fff;border:1px solid transparent;vertical-align:2px;
  letter-spacing:.02em}
.lang.html{background:#cf4520}          /* 橙红 + 白字 4.64 */
.lang.css{background:#0478ab}           /* 天蓝 + 白字 4.91 */
.lang.cpp{background:#2456c4}           /* 深蓝 + 白字 6.56 */
.lang.c{background:#7d5cd6}             /* 蓝紫 + 白字 4.80 */
.lang.sh{background:#3f6212}            /* Shell：用户未指定，橄榄绿 + 白字 7.34 */
.lang.py{background:#1f6f5c}            /* Python：用户未指定，松绿 + 白字 5.73 */
/* JS 单独一套：保留正黄，改用深字 —— 比压暗底色好看得多 */
.lang.js{background:#ffd400;color:#0d1110}   /* 正黄 + 深字 13.28 */"""

LANG_DARK_CSS = """@media (prefers-color-scheme: dark){
  /* 暗色：除了 JS，其余反过来 —— 浅底 + 深字，在深色卡片上更跳也更好读 */
  .lang{color:#12161d;border-color:transparent}
  .lang.html{background:#ffb4a2}        /* 10.62 */
  .lang.css{background:#7dd3fc}         /* 10.87 */
  .lang.cpp{background:#a5c8ff}         /* 10.62 */
  .lang.c{background:#c4b5fd}           /* 9.03 */
  .lang.sh{background:#bef264}          /* 12.44 */
  .lang.py{background:#7dd3b0}          /* 9.29 */
  /* JS 在暗色下**沿用同一个正黄底 + 深字** —— 不改成浅黄。
     理由：① 正黄配深字无论明暗都达标（13.28 对底、对深色页面一样清晰）；
           ② 语言色卡在两种模式下保持同一个黄，认起来更稳。 */
  .lang.js{background:#ffd400;color:#0d1110}
}"""

outL = HEAD_L + "\n".join(sorted(light)) + "\n\n" + LANG_CSS + "\n"
outD = (HEAD_D + "\n\n".join(d.strip() for d in sorted(dark))
        + "\n\n" + LANG_DARK_CSS + "\n")

# ---------- 防呆：抽不到块时**不要**覆盖已有产物 ----------
# 搬块脚本跑过之后，各页里那些块已经删掉了，再跑本脚本就会「抽到 0 个块」，
# 然后把好好的 tg_L/tg_D 覆盖成空壳 —— 第一次就踩了这个坑。
# 所以：抽不到就保留原文件，并明确提示。
if not light and not dark:
    # 注意：即使「没有可抽的块」，语言标注（.lang）这一段也要保证是**最新**的 ——
    # 它不是从页面里抽出来的，而是这里直接定义的。
    #
    # 关键：不能「已经有 .lang 就跳过」—— 那样改了 LANG_CSS 以后永远写不进去。
    # 正确做法是**先剪掉旧的 .lang 段，再追加新的**（幂等：内容相同则原样保留）。
    LANGS = {
        "tg_L.css": (LANG_CSS, True),
        "tg_D.css": (LANG_DARK_CSS, False),
    }
    for fn, (seg, is_light) in LANGS.items():
        p0 = os.path.join(A, fn)
        if not os.path.exists(p0):
            continue
        raw = io.open(p0, encoding="utf-8").read()
        c0 = raw
        # 剪掉旧的 .lang 段。
        # 别用「固定的注释文字」当标记 —— 一改注释就对不上，
        # 于是切不掉旧段、每跑一次就在末尾再追加一份（踩过这个坑：
        # tg_D.css 尾部堆了 6 个空 @media 壳）。
        # 改为按**结构**定位：找到 `.lang` 规则，再回退到包着它的
        # @media / 注释起点，从那里截断到文件末尾。
        i = c0.find(".lang")
        if i >= 0:
            if is_light:
                # 亮色段是平铺规则，回退到它上面的注释块起点
                j = c0.rfind("/* ---------- 语言标注", 0, i)
                if j < 0:
                    j = c0.rfind("/*", 0, i)
                cut = j if j >= 0 else i
            else:
                # 暗色段外面包着 @media，回退到该 @media 的起点
                j = c0.rfind("@media (prefers-color-scheme: dark){", 0, i)
                cut = j if j >= 0 else i
            c0 = c0[:cut].rstrip() + "\n"
        # 与「剪掉旧段后的内容」比较，而不是与原文件比较 ——
        # 原文件带着旧段，拿它比永远不会相等，于是每跑一次都报「已更新」。
        new = c0.rstrip() + "\n\n" + seg + "\n"
        if new == raw:
            print("  = %s 的语言标注已是最新" % fn)
        else:
            io.open(p0, "w", encoding="utf-8", newline="\n").write(new)
            print("  + 已更新 %s 的语言标注（.lang）" % fn)
    keep = []
    for fn, _ in (("tg_L.css", light), ("tg_D.css", dark)):
        p0 = os.path.join(A, fn)
        if os.path.exists(p0) and os.path.getsize(p0) > 200:
            keep.append(fn)
    print()
    print("  ⚠ 这次没有抽到任何块（各页可能已经搬过了）。")
    if keep:
        print("    已保留现有产物不动：%s" % "、".join(keep))
        print("    （若要重新抽取，请从搬块前的提交里取源文件，"
              "或用 git stash / git checkout 还原后再跑）")
    raise SystemExit(0)

io.open(os.path.join(A, "tg_L.css"), "w", encoding="utf-8", newline="\n").write(outL)
io.open(os.path.join(A, "tg_D.css"), "w", encoding="utf-8", newline="\n").write(outD)
print()
print("  ✓ tg_L.css  %6d B  （%d 个块）" % (len(outL), len(light)))
print("  ✓ tg_D.css  %6d B  （%d 个块）" % (len(outD), len(dark)))

# ---------- 结构自检 ----------
for fn in ("tg_L.css", "tg_D.css"):
    c = io.open(os.path.join(A, fn), encoding="utf-8").read()
    d = 0
    i = 0
    unc = 0
    while i < len(c):
        if c[i:i + 2] == '/*':
            j = c.find('*/', i + 2)
            if j < 0:
                unc += 1
                break
            i = j + 2
            continue
        if c[i] == '{':
            d += 1
        elif c[i] == '}':
            d -= 1
        i += 1
    print("     %s 花括号余 %+d，未闭合注释 %d %s"
          % (fn, d, unc, "✅" if d == 0 and unc == 0 else "❌"))
