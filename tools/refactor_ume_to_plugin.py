# -*- coding: utf-8 -*-
"""让 web/UME.html 引用 UMCompos —— 逐步来，每次只删一小块、每块都断言。

教训（上一版）：锚点行前面是 `const PROPS` 的**注释头**，而注释头的上一行
是 `const isMong = …`。脚本往前吞注释时把 isMong、cpHex、S、raw、insert
一起删掉了，导致 sync/insert 直接 ReferenceError。
所以这里：
  · 起始锚点用唯一的 ASCII 行（`const PROPS = {`、`function prop(` …）
  · 结束点靠**数花括号**配平，不靠「顶格 }」这种巧合
  · 每删一块都断言关键符号仍在，不满足就中止、不写文件

本次只删「字符属性 / 字素簇 / 断行机会」这三块（纯分类逻辑，最值得复用）；
测量那一段（initMeasure / measureLine / measureText / layoutDoc）**先留着不动** ——
它和编辑器耦合更深，等 T01 那边验证充分再统一，避免一次改太多。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\web\UME.html"
t = io.open(P, encoding="utf-8").read()
before = len(t)

KEEP = ("const S =", "const raw", "const cpHex", "const isMong",
        "function insert", "function sync", "function buildSVGText",
        "function boot", "function layoutDoc", "function measureLine",
        "function initMeasure", "function escXml")


def find_fn(src, header):
    """从 header 开始，按花括号配平找函数结束位置（跳过字符串里的括号）。"""
    i = src.find(header)
    if i < 0:
        return None
    b = src.find("{", i)
    if b < 0:
        return None
    depth, k, n, q = 0, b, len(src), None
    while k < n:
        ch = src[k]
        if q:
            if ch == q and src[k - 1] != "\\":
                q = None
        elif ch in "\"'`":
            q = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return (i, k + 1)
        k += 1
    return None


def cut(src, start, end):
    """删掉 [start,end)，顺带清掉紧邻其前的**纯注释行**（只吃注释，绝不吃代码）。"""
    j = start
    while True:
        prev_nl = src.rfind("\n", 0, max(0, j - 1))
        line = src[prev_nl + 1:j].strip() if prev_nl >= 0 else src[:j].strip()
        if line.startswith("/*") or line.startswith("*") or line.startswith("//"):
            j = prev_nl + 1 if prev_nl >= 0 else 0
        elif line == "":
            prev = src.rfind("\n", 0, max(0, j - 1))
            j = prev + 1 if prev >= 0 else 0
            break
        else:
            break
    return src[:j] + src[end:]


# ---------- 1. 删 const PROPS = { … }; ----------
i = t.find("\nconst PROPS = {")
assert i > 0, "找不到 const PROPS"
i += 1
j = t.find("\n};", i)
assert j > 0, "找不到 PROPS 结尾"
j += len("\n};")
t = cut(t, i, j)
print("  ✓ 删除 PROPS 常量")

# ---------- 2. 删三个函数 ----------
for header in ("function prop(c){", "function graphemes(cps){", "function breakOpps(cps){"):
    r = find_fn(t, header)
    assert r, "找不到 " + header
    t = cut(t, r[0], r[1])
    print("  ✓ 删除 %-26s （%d 字符）" % (header, r[1] - r[0]))

# ---------- 3. 插入转发层 ----------
SHIM = '''/* ==================================================================
   字符分类与断行：改用外部插件 UMCompos（web/UMCompos.js）
   ------------------------------------------------------------------
   原来这三块（字符属性表 / 字素簇切分 / 断行机会）在本文件里各有一份实现。
   它们与界面完全无关、纯粹是 Unicode 规则，已抽成 UMCompos.js 组件化，
   这里只留一层同名转发 —— 下方代码仍在调 prop / graphemes / breakOpps，
   这样改动面最小，行为与重构前一致。
   ================================================================== */
function prop(c){ return UMCompos.properties(c); }
function graphemes(cps){ return UMCompos.graphemes(cps); }
function breakOpps(cps){ return UMCompos.breakOpportunities(cps); }

'''
k = t.find("function sync(){")
assert k > 0, "找不到插入点"
# 插在 sync 之前的那个注释块之前
kb = t.rfind("/* =", 0, k)
t = t[:kb] + SHIM + t[kb:]
print("  ✓ 插入转发层")

# ---------- 4. head 加载插件 ----------
if '<script src="UMCompos.js"></script>' not in t:
    k = t.find("</head>")
    assert k > 0
    t = t[:k] + '<script src="UMCompos.js"></script>\n' + t[k:]
    print("  ✓ <head> 加载 UMCompos.js")

# ---------- 5. 自检 ----------
for must in KEEP:
    assert must in t, "删除过多：%s 不见了" % must
assert t.count("function prop(") == 1, "prop 定义重复"
assert t.count("function graphemes(") == 1, "graphemes 定义重复"
assert t.count("function breakOpps(") == 1, "breakOpps 定义重复"
print("  ✓ 自检通过")

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  ✓ %d → %d 字符（少 %d）" % (before, len(t), before - len(t)))
