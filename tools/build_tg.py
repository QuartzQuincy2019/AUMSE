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

outL = HEAD_L + "\n".join(sorted(light)) + "\n"
outD = HEAD_D + "\n\n".join(d.strip() for d in sorted(dark)) + "\n"

# ---------- 防呆：抽不到块时**不要**覆盖已有产物 ----------
# 搬块脚本跑过之后，各页里那些块已经删掉了，再跑本脚本就会「抽到 0 个块」，
# 然后把好好的 tg_L/tg_D 覆盖成空壳 —— 第一次就踩了这个坑。
# 所以：抽不到就保留原文件，并明确提示。
if not light and not dark:
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
