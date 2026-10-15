# -*- coding: utf-8 -*-
"""
蒙文 Unicode 码区 U+1800–U+18AF 完整属性调查。

数据来源：Unicode Character Database (UCD) 最新版，本地缓存于 report/ucd/。
逐码位读取 Official 属性，输出可核对的完整表 + 结构分析。
"""
import os
import re
import sys
import json
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UCD = os.path.join(ROOT, "report", "ucd")
OUT = os.path.join(ROOT, "report")

LO, HI = 0x1800, 0x18AF

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ---------------------------------------------------------------- UCD 解析
def read_lines(name):
    p = os.path.join(UCD, name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return fh.read().splitlines()


def parse_ranges(name, want_default=True):
    """返回 {codepoint: value}；支持 `XXXX..YYYY; Value` 与 `XXXX ; Value`。"""
    out = {}
    for ln in read_lines(name):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        parts = [p.strip() for p in ln.split(";")]
        if len(parts) < 2:
            continue
        rng, val = parts[0], parts[1]
        m = re.match(r"^([0-9A-Fa-f]{4,6})(?:\.\.([0-9A-Fa-f]{4,6}))?$", rng)
        if not m:
            continue
        a = int(m.group(1), 16)
        b = int(m.group(2), 16) if m.group(2) else a
        for c in range(a, b + 1):
            out[c] = val
    return out


def parse_numeric(name):
    """数值型属性（如 ccc）。"""
    out = {}
    for ln in read_lines(name):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        parts = [p.strip() for p in ln.split(";")]
        if len(parts) < 2:
            continue
        m = re.match(r"^([0-9A-Fa-f]{4,6})(?:\.\.([0-9A-Fa-f]{4,6}))?$", parts[0])
        if not m:
            continue
        a = int(m.group(1), 16)
        b = int(m.group(2), 16) if m.group(2) else a
        for c in range(a, b + 1):
            out[c] = int(parts[1])
    return out


def parse_sets(name, props):
    """解析 DerivedCoreProperties.txt 里的多属性集合。"""
    res = {p: set() for p in props}
    for ln in read_lines(name):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        parts = [p.strip() for p in ln.split(";")]
        if len(parts) < 2:
            continue
        m = re.match(r"^([0-9A-Fa-f]{4,6})(?:\.\.([0-9A-Fa-f]{4,6}))?$", parts[0])
        if not m or parts[1] not in res:
            continue
        a = int(m.group(1), 16)
        b = int(m.group(2), 16) if m.group(2) else a
        for c in range(a, b + 1):
            res[parts[1]].add(c)
    return res


print("读取 UCD 数据 ...")
BLOCKS_RAW = read_lines("Blocks.txt")
BLOCK_VERSION = ""
for ln in BLOCKS_RAW:
    if ln.startswith("# Blocks-"):
        BLOCK_VERSION = ln.strip("# ").strip()
        break
# 检查 U+1800..U+18AF 是否完整属于 Mongolian 块
block_of = {}
for ln in BLOCKS_RAW:
    ln = ln.split("#")[0].strip()
    if not ln or ";" not in ln:
        continue
    rng, nm = [x.strip() for x in ln.split(";")]
    m = re.match(r"^([0-9A-Fa-f]{4,6})\.\.([0-9A-Fa-f]{4,6})$", rng)
    if not m:
        continue
    a, b = int(m.group(1), 16), int(m.group(2), 16)
    if a <= HI and b >= LO:
        for c in range(max(a, LO), min(b, HI) + 1):
            block_of[c] = nm

gc = parse_ranges("DerivedGeneralCategory.txt")
script = parse_ranges("Scripts.txt")
jt = parse_ranges("DerivedJoiningType.txt")
gcb = parse_ranges("GraphemeBreakProperty.txt")
wb = parse_ranges("WordBreakProperty.txt")
sb = parse_ranges("SentenceBreakProperty.txt")
ccc = parse_numeric("DerivedCombiningClass.txt")
mirror = parse_ranges("BidiMirroring.txt")

CORE_PROPS = ["Default_Ignorable_Code_Point", "Variation_Selector",
              "Grapheme_Extend", "Grapheme_Base", "Cased", "Alphabetic",
              "ID_Start", "ID_Continue", "XID_Start", "XID_Continue",
              "Case_Ignorable", "Math", "Lowercase", "Uppercase"]
sets = parse_sets("DerivedCoreProperties.txt", CORE_PROPS)

PROPLIST_PROPS = ["White_Space", "Bidi_Control", "Join_Control",
                  "Noncharacter_Code_Point", "Deprecated", "Variation_Selector"]
pl = parse_sets("PropList.txt", PROPLIST_PROPS)

# 通过 PropertyValueAliases.txt 确认属性值全称
pva = {}
for ln in read_lines("PropertyValueAliases.txt"):
    ln = ln.split("#")[0].strip()
    if not ln:
        continue
    parts = [p.strip() for p in ln.split(";")]
    if len(parts) >= 3:
        pva.setdefault(parts[0], {})[parts[1]] = parts[2]


def alias(prop, val):
    return pva.get(prop, {}).get(val, val)


# ---------------------------------------------------------------- 建表
rows = []
for c in range(LO, HI + 1):
    rows.append(OrderedDict([
        ("cp", c), ("code", "U+%04X" % c), ("char", chr(c)),
        ("gc", gc.get(c, "Cn")), ("script", script.get(c, "Unknown")),
        ("jt", jt.get(c, "U")), ("ccc", ccc.get(c, 0)),
        ("gcb", gcb.get(c, "Other")), ("wb", wb.get(c, "Other")),
        ("sb", sb.get(c, "Other")),
        ("block", block_of.get(c, "(不在本块)")),
        ("is_Cn", gc.get(c, "Cn") == "Cn"),
    ]))

assigned = [r for r in rows if not r["is_Cn"]]
unassigned = [r for r in rows if r["is_Cn"]]

# ---------------------------------------------------------------- 输出
L = []
A = L.append
A("=" * 100)
A("蒙文 Unicode 码区 U+1800–U+18AF 完整属性调查")
A("=" * 100)
A("UCD 版本(Blocks.txt) : %s" % BLOCK_VERSION)
A("码位总数             : %d" % len(rows))
A("已分配               : %d" % len(assigned))
A("未分配(保留)         : %d -> %s" % (
    len(unassigned), " ".join(r["code"] for r in unassigned)))
A("整块归属             : %s" % ", ".join(sorted(set(block_of.values()))))
A("")

A("-- 通用类别 (General_Category) 分布 --")
for k, v in Counter(r["gc"] for r in assigned).most_common():
    A("  %-4s %-26s %3d" % (k, alias("gc", k), v))
A("")
A("-- 文字属性 (Script) --")
for k, v in Counter(r["script"] for r in assigned).most_common():
    A("  %-14s %3d" % (k, v))
A("")
A("-- 连接类型 (Joining_Type) --")
jtname = {"U": "Non_Joining 不连接", "T": "Transparent 透明",
          "C": "Join_Causing 引起连接", "D": "Dual_Joining 双向连接",
          "L": "Left_Joining 左连接", "R": "Right_Joining 右连接"}
for k, v in Counter(r["jt"] for r in assigned).most_common():
    A("  %-3s %-28s %3d" % (k, jtname.get(k, k), v))
A("  注：%s 脚本在 UCD 中不使用阿拉伯式连接类型；蒙文连写由 "
  "OpenType 上下文特性实现。" % sorted(set(r["script"] for r in assigned)))
A("")
A("-- 字素簇断行属性 (Grapheme_Cluster_Break) --")
for k, v in Counter(r["gc"] and r["gcb"] for r in assigned).most_common():
    A("  %-16s %3d" % (k, v))
A("")
A("-- 组合类 (Canonical_Combining_Class) --")
for k, v in Counter(r["ccc"] for r in assigned).most_common():
    A("  ccc=%-3d %3d" % (k, v))
A("")

A("-- 关键派生属性（仅列命中的码位） --")
for prop in ["Default_Ignorable_Code_Point", "Variation_Selector",
             "Grapheme_Extend", "White_Space", "Deprecated",
             "Join_Control", "Bidi_Control", "Noncharacter_Code_Point",
             "Alphabetic", "Cased", "Case_Ignorable", "ID_Start",
             "ID_Continue", "Math"]:
    hit = [r["code"] for r in assigned if r["cp"] in sets.get(prop, set())
           or r["cp"] in pl.get(prop, set())]
    A("  %-28s %3d  %s" % (prop, len(hit),
                           " ".join(hit) if 0 < len(hit) <= 24 else
                           (" ".join(hit[:24]) + " …" if hit else "—")))
A("")

# ---------------------------------------------------------------- 完整表
A("=" * 100)
A("逐码位完整属性表（176 个码位）")
A("=" * 100)
hdr = "%-8s %-3s %-38s %-4s %-8s %-3s %-4s %-14s %-16s %s"
A(hdr % ("码位", "字", "Unicode 官方名称", "gc", "script", "jt", "ccc",
         "GCB", "WordBreak", "Flags"))
A("-" * 100)

# 官方名称：从 Python unicodedata（15.0）取，未分配则标注
import unicodedata
for r in rows:
    c = r["cp"]
    try:
        nm = unicodedata.name(chr(c))
    except ValueError:
        nm = "— 未分配 / 保留 —" if r["is_Cn"] else "<无名称>"
    flags = []
    if c in sets.get("Default_Ignorable_Code_Point", set()):
        flags.append("Default_Ignorable")
    if c in sets.get("Variation_Selector", set()) or c in pl.get("Variation_Selector", set()):
        flags.append("Variation_Selector")
    if c in pl.get("White_Space", set()):
        flags.append("White_Space")
    if c in pl.get("Deprecated", set()):
        flags.append("Deprecated")
    if c in sets.get("Case_Ignorable", set()):
        flags.append("Case_Ignorable")
    if c in sets.get("Grapheme_Extend", set()):
        flags.append("Grapheme_Extend")
    A(hdr % (r["code"], r["char"] if not r["is_Cn"] else "·", nm[:38],
             r["gc"], r["script"], r["jt"], r["ccc"], r["gcb"], r["wb"],
             ", ".join(flags)))

# ---------------------------------------------------------------- 结构分析
A("")
A("=" * 100)
A("结构分析")
A("=" * 100)

# 1) 命名空间连续性：找出每个命名段的起止
segments = []
cur = None
for r in assigned:
    try:
        nm = unicodedata.name(chr(r["cp"]))
    except ValueError:
        nm = "?"
    key = nm.split(" ")[0]
    if cur and cur["key"] == key:
        cur["end"] = r["cp"]
        cur["n"] += 1
    else:
        if cur:
            segments.append(cur)
        cur = {"key": key, "start": r["cp"], "end": r["cp"], "n": 1,
               "gc": r["gc"]}
if cur:
    segments.append(cur)
A("")
A("-- 按名称前缀分组的结构段 --")
for s in segments:
    A("  %-12s U+%04X–U+%04X  %3d 个  gc=%s" % (
        s["key"], s["start"], s["end"], s["n"], s["gc"]))

# 2) 阴阳性元音：蒙文正字法核心
A("")
A("-- 蒙文元音与性别(阳性/阴性)对应（编辑器正字法校验用） --")
VOWELS = {0x1820: ("A", "阳性"), 0x1821: ("E", "阴性"),
          0x1822: ("I", "中性"), 0x1823: ("O", "阳性"),
          0x1824: ("U", "阳性"), 0x1825: ("OE", "阴性"),
          0x1826: ("UE", "阴性"), 0x1827: ("EE", "阴性"),
          0x1843: ("TODO LONG VOWEL", "托忒长元音"),
          0x1844: ("TODO E", "托忒"), 0x1845: ("TODO I", "托忒"),
          0x1846: ("TODO O", "托忒"), 0x1847: ("TODO U", "托忒")}
for c, (nm, g) in VOWELS.items():
    A("  U+%04X %-18s %s" % (c, nm, g))

# 3) 未分配码位的分布（可用于扩展）
A("")
A("-- 未分配(保留)码位的连续段 --")
runs = []
cur = None
for r in unassigned:
    if cur and r["cp"] == cur[1] + 1:
        cur[1] = r["cp"]
    else:
        if cur:
            runs.append(cur)
        cur = [r["cp"], r["cp"]]
if cur:
    runs.append(cur)
for a, b in runs:
    A("  U+%04X–U+%04X  (%d 个)" % (a, b, b - a + 1))

# ---------------------------------------------------------------- 落盘
text = "\n".join(L)
print(text)
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "unicode-1800-18AF.txt"), "w", encoding="utf-8") as fh:
    fh.write(text)

summary = {
    "ucd_version_blocks": BLOCK_VERSION,
    "range": "U+1800..U+18AF",
    "total": len(rows),
    "assigned": len(assigned),
    "unassigned": ["U+%04X" % r["cp"] for r in unassigned],
    "general_category": dict(Counter(r["gc"] for r in assigned)),
    "script": dict(Counter(r["script"] for r in assigned)),
    "joining_type": dict(Counter(r["jt"] for r in assigned)),
    "grapheme_cluster_break": dict(Counter(r["gcb"] for r in assigned)),
    "ccc": {str(k): v for k, v in Counter(r["ccc"] for r in assigned).items()},
    "codepoints": [{k: v for k, v in r.items() if k != "is_Cn"} for r in rows],
}
with open(os.path.join(OUT, "unicode-1800-18AF.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)
print("\n已写出: report/unicode-1800-18AF.txt / .json")
