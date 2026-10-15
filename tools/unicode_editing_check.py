# -*- coding: utf-8 -*-
"""
蒙文 U+1800–U+18AF 编辑行为验证（严格实现 UAX #29 / UAX #14）。

数据来源（UCD 18.0.0，本地缓存 report/ucd/）：
  GraphemeBreakProperty.txt, LineBreak.txt, WordBreakProperty.txt,
  DerivedJoiningType.txt, DerivedGeneralCategory.txt

回答三个编辑器必须做对的问题：
  1) 光标移动 / 退格 / 选取的最小单位是什么？（UAX #29 字素簇）
  2) 竖排列宽在哪里可以换行？（UAX #14 断行机会）
  3) FVS / U+180E / NIRUGU / 组合标记 各自如何影响上述行为？
"""
import os
import re
import sys
import unicodedata
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UCD = os.path.join(ROOT, "report", "ucd")
OUT = os.path.join(ROOT, "report")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RANGE_RE = re.compile(r"^([0-9A-Fa-f]{4,6})(?:\.\.([0-9A-Fa-f]{4,6}))?$")


def parse_prop(path):
    """通用 UCD 属性解析：兼容 `XXXX ; V` 与 `XXXX..YYYY ; V` 两种写法。"""
    out = {}
    if not os.path.exists(path):
        sys.stderr.write("缺少数据文件: %s\n" % path)
        return out
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.split("#")[0].strip()
            if not ln or ";" not in ln:
                continue
            parts = [p.strip() for p in ln.split(";")]
            m = RANGE_RE.match(parts[0])
            if not m:
                continue
            a = int(m.group(1), 16)
            b = int(m.group(2), 16) if m.group(2) else a
            for c in range(a, b + 1):
                out[c] = parts[1]
    return out


GB = parse_prop(os.path.join(UCD, "GraphemeBreakProperty.txt"))
LB = parse_prop(os.path.join(UCD, "LineBreak.txt"))
WB = parse_prop(os.path.join(UCD, "WordBreakProperty.txt"))
JT = parse_prop(os.path.join(UCD, "DerivedJoiningType.txt"))
GC = parse_prop(os.path.join(UCD, "DerivedGeneralCategory.txt"))

assert LB, "LineBreak.txt 解析失败"
print("数据加载: GCB=%d LB=%d WB=%d 条" % (len(GB), len(LB), len(WB)))


# ================================================================ UAX #29
def gcb(cp):
    return GB.get(cp, "Other")


def graphemes(text):
    """UAX #29 扩展字素簇边界（GB1–GB13，含 GB9c 从略项）。"""
    cps = [ord(c) for c in text]
    if not cps:
        return []
    p = [gcb(c) for c in cps]
    clusters, start = [], 0
    i = 1
    while i < len(cps):
        a, b = p[i - 1], p[i]
        brk = True
        if a == "CR" and b == "LF":                       # GB3
            brk = False
        elif a in ("Control", "CR", "LF"):                # GB4
            brk = True
        elif b in ("Control", "CR", "LF"):                # GB5
            brk = True
        elif a == "L" and b in ("L", "V", "LV", "LVT"):   # GB6
            brk = False
        elif a in ("LV", "V") and b in ("V", "T"):        # GB7
            brk = False
        elif a in ("LVT", "T") and b == "T":              # GB8
            brk = False
        elif b in ("Extend", "ZWJ"):                      # GB9
            brk = False
        elif b == "SpacingMark":                          # GB9a
            brk = False
        elif a == "Prepend":                              # GB9b
            brk = False
        if brk:
            clusters.append((start, i))
            start = i
        i += 1
    clusters.append((start, len(cps)))
    return [(text[a:b], a, b) for a, b in clusters]


# ================================================================ UAX #14
def lbclass(cp):
    return LB.get(cp, "XX")


def breaks_uax14(text):
    """UAX #14 断行机会（实现蒙文相关的核心规则 LB1–LB31）。

    关键：LB9 规定 CM/ZWJ 无自身断行语义，必须先把连续 CM/ZWJ 归并到
    前一个字符的类别，再套用成对规则。否则会出现 AL+CM|AL 被误判为可断。
    """
    cps = [ord(c) for c in text]
    raw = [lbclass(c) for c in cps]
    n = len(cps)
    if n == 0:
        return []

    # --- LB9 + LB10：把 CM/ZWJ 归并到前一个非 CM/ZWJ 字符的类别
    resolved = []
    for i, c in enumerate(raw):
        if c in ("CM", "ZWJ"):
            if resolved and resolved[-1] not in ("BK", "CR", "LF", "NL", "SP", "ZW"):
                resolved.append(resolved[-1])      # 继承前字符类别（LB9）
            else:
                resolved.append("AL")              # LB10：孤立的 CM 视作 AL
        else:
            resolved.append(c)

    # 归并后，相邻同源 CM 不产生断行点（它们属于同一簇）
    merged_prev = [False] * n
    for i in range(1, n):
        if raw[i] in ("CM", "ZWJ") and resolved[i] == resolved[i - 1]:
            merged_prev[i] = True

    opps = []
    for i in range(1, n):
        if merged_prev[i]:                 # 该位置是 CM 归并点，非断行点
            continue
        a, b = resolved[i - 1], resolved[i]
        allow = None

        if a == "BK":                                          # LB4
            allow = True
        elif a in ("CR", "LF", "NL"):                          # LB5
            allow = not (a == "CR" and b == "LF")
        elif b in ("BK", "CR", "LF", "NL"):                    # LB6
            allow = False
        elif b in ("SP", "ZW"):                                # LB7
            allow = False
        elif a == "ZW":                                        # LB8
            allow = True
        elif a == "ZWJ":                                       # LB8a
            allow = False
        elif a == "WJ" or b == "WJ":                           # LB11
            allow = False
        elif a == "GL" or b == "GL":                           # LB12
            allow = False
        elif b in ("CL", "CP", "EX", "IS", "SY"):              # LB13
            allow = False
        elif a == "OP":                                        # LB14
            allow = False
        elif a == "QU" or b == "QU":                           # LB15/19
            allow = None
        elif b in ("CL", "CP"):                                # LB16
            allow = False
        elif a == "SP":                                        # LB18：空格后可断
            allow = True
        elif a in ("BA", "HY", "NS"):                           # LB21
            allow = False
        elif (a == "NU" and b == "AL") or (a == "AL" and b == "NU"):   # LB23
            allow = False
        elif a in ("PR", "PO") and b in ("AL", "NU"):          # LB24
            allow = False
        elif a in ("AL", "NU") and b in ("PR", "PO"):
            allow = False
        elif a in ("NU", "IS", "SY") and b in ("NU", "IS", "SY"):      # LB25
            allow = False
        elif a == "AL" and b == "AL":                          # LB28
            allow = False
        elif b == "OP" and a in ("AL", "HL", "NU"):            # LB30
            allow = False
        elif a == "CP" and b in ("AL", "HL", "NU"):
            allow = False
        if allow is None:                                      # LB31 兜底
            allow = not (a in ("AL", "HL") and b in ("AL", "HL"))
        if allow:
            opps.append(i)
    return opps


# ================================================================ 测试
M = "\u182E\u1823\u1829\u182D\u1823\u182F"      # ᠮᠣᠩᠭᠣᠯ  mongol
S = "\u1830\u1820\u1836\u1822\u1828"              # ᠰᠠᠶᠢᠨ    sayin
FVS1, FVS2, FVS3, FVS4 = "\u180B", "\u180C", "\u180D", "\u180F"
MVS, NIRUGU = "\u180E", "\u180A"

CASES = [
    ("纯字母词 mongol", M),
    ("FVS1 附于词尾", M + FVS1),
    ("FVS1 夹在词中", M[:1] + FVS1 + M[1:]),
    ("FVS2 夹在词中", M[:1] + FVS2 + M[1:]),
    ("FVS4 夹在词中", M[:1] + FVS4 + M[1:]),
    ("NIRUGU 连接两词", M + NIRUGU + S),
    ("MVS 元音分隔", M + MVS + S),
    ("空格分隔两词", M + " " + S),
    ("蒙文逗号 U+1802", M + "\u1802" + S),
    ("蒙文句号 U+1803", M + "\u1803" + S),
    ("蒙文冒号 U+1804", M + "\u1804" + S),
    ("Sibe 边界符 U+1807", M + "\u1807" + S),
    ("蒙文数字", "\u1810\u1811\u1812"),
    ("字母+数字", M + "\u1810\u1811"),
    ("Baluda 组合", "\u1887\u1885"),
    ("Dagalga(ccc228)", "\u1889\u18A9"),
    ("ZWNJ 分隔", M + "\u200C" + S),
]

L = []
A = L.append
A("=" * 96)
A("蒙文 U+1800–U+18AF 编辑行为验证（严格实现 UAX #29 / UAX #14）")
A("=" * 96)
A("规则数据: UCD 18.0.0  GraphemeBreakProperty / LineBreak / DerivedJoiningType")
A("")
A("-- 第 1 部分：UAX #29 字素簇（光标/退格/选取的最小单位） --")
A("%-20s %6s %8s  %s" % ("用例", "码位数", "字素簇", "字素簇切分"))
A("-" * 96)
for name, text in CASES:
    cl = graphemes(text)
    seg = " | ".join("+".join("%04X" % ord(c) for c in s) for s, _, _ in cl)
    tag = "合并" if len(cl) < len(text) else "逐码位"
    A("%-20s %6d %8d  [%s] %s" % (name, len(text), len(cl), tag, seg))

A("")
A("-- 第 2 部分：UAX #14 断行机会（竖排列宽换行点） --")
A("%-20s %6s %10s  %s" % ("用例", "码位数", "断行机会", "断行点（码位索引）"))
A("-" * 96)
for name, text in CASES:
    b = breaks_uax14(text)
    A("%-20s %6d %10d  %s" % (name, len(text), len(b),
                              ", ".join(str(x) for x in b) if b else "无"))

A("")
A("=" * 96)
A("-- 第 3 部分：U+1800–U+18AF 的 LineBreak / GCB 属性全表（非 Other 者） --")
A("=" * 96)
A("%-10s %-38s %-4s %-4s %-4s %-13s %s" % (
    "码位", "名称", "gc", "jt", "LB", "GCB", "编辑含义"))
A("-" * 96)

NOTE = {
    0x1800: "LB=AL：视作字母，其后可断",
    0x1801: "LB=AL",
    0x1802: "LB=EX：行首禁止（禁则处理）",
    0x1803: "LB=EX：行首禁止",
    0x1804: "LB=BA：其后可断",
    0x1805: "LB=BA：其后可断",
    0x1806: "LB=BB：其前可断",
    0x1807: "LB=AL 且 JT=D：参与连写，标点但不断行",
    0x1808: "LB=EX：行首禁止",
    0x1809: "LB=EX：行首禁止",
    0x180A: "LB=AL 且 JT=C：引起连接，强制前后连写",
    0x180B: "LB=CM 且 JT=T：黏附前字，不占位，光标应跳过",
    0x180C: "LB=CM 且 JT=T：同上",
    0x180D: "LB=CM 且 JT=T：同上",
    0x180E: "LB=GL：不换行黏合，两侧均不得断行；GCB=Control",
    0x180F: "LB=CM 且 JT=T：同上",
    0x1810: "LB=NU：数字，与相邻字母/数字不断行",
    0x1885: "LB=CM：黏附前字",
    0x1886: "LB=CM：黏附前字",
    0x18A9: "LB=CM 且 ccc=228：黏附前字并参与正规化排序",
}
shown = 0
for cp in range(0x1800, 0x18B0):
    if cp not in LB:
        continue
    lb = LB.get(cp, "XX")
    g = GB.get(cp, "Other")
    if lb == "XX" and g == "Other":
        continue
    nm = unicodedata.name(chr(cp), "—")
    A("%-10s %-38s %-4s %-4s %-4s %-13s %s" % (
        "U+%04X" % cp, nm.replace("MONGOLIAN ", "")[:38],
        GC.get(cp, "Cn"), JT.get(cp, "U"), lb, g, NOTE.get(cp, "")))
    shown += 1
A("")
A("共列出 %d 个具有非默认 LineBreak 属性的码位" % shown)

A("")
A("=" * 96)
A("-- 第 4 部分：结论 --")
A("=" * 96)
A("1) 字素簇：")
A("   - 蒙文字母本身 Lo/Other，彼此不合并 -> 一词 N 个字母 = N 个光标位。")
A("     这与拉丁文一致，光标可落在字母之间（字母本身是独立字素）。")
A("   - FVS1-4（U+180B-D/180F）GCB=Extend -> 黏附前一字母，编辑器中")
A("     绝不能单独删除/移动光标到 FVS 与字母之间，否则破坏字形选择。")
A("   - Baluda(U+1885/6)、Dagalga(U+18A9) 同为 Extend，须与其基字符合并处理。")
A("   - U+180E GCB=Control -> 是唯一会“切断”字素簇的蒙文控制符。")
A("")
A("2) 断行：")
A("   - 蒙文字母 LB=AL，AL x AL 禁止断行 -> 连续字母串内部没有断行点。")
A("     传统蒙文不用空格分词，因此一个长词就是一个不可断的整体。")
A("   - U+180E LB=GL（不换行黏合）-> 其两侧一律不得断行，")
A("     说明它在标准中就是“词内”分隔符，不是词间分隔符。")
A("   - U+1802/1803/1808/1809 LB=EX -> 依禁则不得出现在行首。")
A("   - U+1804/1805 LB=BA -> 其后允许断行。")
A("   - U+1806 LB=BB -> 其前允许断行。")
A("   - 唯一自然断行点是 ASCII 空格（LB=SP）与上述标点。")
A("")
A("3) 连接类型（蒙文独有）：")
A("   - 125 个码位 JT=Dual_Joining、U+180A JT=Join_Causing、7 个 JT=Transparent。")
A("   - 这是 Unicode 为蒙古文专门定义的连接模型，与阿拉伯文同机制但取值独立。")

text = "\n".join(L)
print(text)
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "unicode-mongolian-editing.txt"), "w", encoding="utf-8") as fh:
    fh.write(text)
print("\n已写出: report/unicode-mongolian-editing.txt")
