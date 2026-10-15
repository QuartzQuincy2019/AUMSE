# -*- coding: utf-8 -*-
"""为 ttf-basics.html 提取真实数据：
   字体表结构、GSUB 特性清单、rclt 的链式上下文规则、UCD 断行属性。
"""
import sys
import os
import json
from collections import Counter, OrderedDict

from fontTools.ttLib import TTFont

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
UCD = os.path.join(ROOT, "report", "ucd")
OUT = os.path.join(ROOT, "report")

f = TTFont(FONT)
gsub = f["GSUB"].table
order = f.getGlyphOrder()
cmap = f.getBestCmap()

# ---------------------------------------------------------------- 1. 表结构
tables = []
for tag in sorted(f.reader.tables.keys()):
    tables.append({"tag": tag.strip(), "size": f.reader.tables[tag].length})
data = {"tables": tables, "numGlyphs": f["maxp"].numGlyphs,
        "upem": f["head"].unitsPerEm,
        "cmapCount": len(cmap)}

# ---------------------------------------------------------------- 2. 特性清单
owners = OrderedDict()
for fr in gsub.FeatureList.FeatureRecord:
    owners.setdefault(fr.FeatureTag, []).extend(fr.Feature.LookupListIndex)

FEATURE_DOC = {
    "rclt": ("Required Contextual Ligatures", "必需上下文连字",
             "蒙文连写的核心：按前后字符决定取哪个字形、是否合并。必须默认开启。"),
    "ccmp": ("Glyph Composition/Decomposition", "字形组合/分解",
             "在其它特性之前执行，用于展开变体选择符（FVS）等。"),
    "init": ("Initial Forms", "词首形", "把字母换成词首写法。"),
    "medi": ("Medial Forms", "词中形", "把字母换成词中写法。"),
    "fina": ("Final Forms", "词尾形", "把字母换成词尾写法。"),
    "isol": ("Isolated Forms", "单独形", "把字母换成独立写法。"),
    "calt": ("Contextual Alternates", "上下文替代", "一般性的上下文替换。"),
    "liga": ("Standard Ligatures", "标准连字", "常规连字合并。"),
    "aalt": ("Access All Alternates", "全部替代字形", "汇总所有候选字形，供用户选择。"),
    "locl": ("Localized Forms", "本地化形式", "按语言标签替换字形。"),
    "ordn": ("Ordinals", "序数", "序数词标记。"),
    "vert": ("Vertical Writing", "竖排形式", "把标点换成竖排字形（本字体只覆盖 25 个标点）。"),
    "mark": ("Mark Positioning", "标记定位", "GPOS：把组合标记放到基字形上。"),
    "mkmk": ("Mark to Mark", "标记间定位", "GPOS：标记叠标记。"),
    "kern": ("Kerning", "字距调整", "GPOS：调整字偶间距。"),
}

feats = []
for tag, idxs in owners.items():
    n = 0
    for i in idxs:
        for st in gsub.LookupList.Lookup[i].SubTable:
            for attr in ("mapping", "alternates", "ligatures"):
                v = getattr(st, attr, None)
                if isinstance(v, dict):
                    n += len(v)
    full, cn, desc = FEATURE_DOC.get(tag, ("", "", ""))
    feats.append({"tag": tag, "full": full, "cn": cn, "desc": desc,
                  "lookups": len(idxs), "entries": n})
feats.sort(key=lambda x: -x["entries"])
data["features"] = feats

# ---------------------------------------------------------------- 3. rclt 链式上下文示例
# 找到 rclt 引用里 type=6（Chaining Context）的 lookup，导出可读规则
rclt_idx = set()
for fr in gsub.FeatureList.FeatureRecord:
    if fr.FeatureTag == "rclt":
        rclt_idx |= set(fr.Feature.LookupListIndex)

CHAIN_TYPE = 6
examples = []


def cov_glyphs(sub, attr):
    """安全取 coverage 里的字形名；不同 format 属性名不同或缺省。"""
    v = getattr(sub, attr, None)
    if not v:
        return []
    out = []
    for cov in v:
        out.extend(getattr(cov, "glyphs", []) or [])
    return out[:4]


for i in sorted(rclt_idx):
    lk = gsub.LookupList.Lookup[i]
    if lk.LookupType != CHAIN_TYPE:
        continue
    for st in lk.SubTable:
        fmt = getattr(st, "Format", None)
        # format 3：用 coverage 表达前后文，最适合展示
        if fmt == 3:
            bt = cov_glyphs(st, "BacktrackCoverage")
            inp = cov_glyphs(st, "InputCoverage")
            la = cov_glyphs(st, "LookAheadCoverage")
            subs = []
            for ls in (getattr(st, "SubstLookupRecord", None) or [])[:3]:
                subs.append("lookup#%d @seq%d" % (ls.LookupListIndex,
                                                  ls.SequenceIndex))
            if inp and subs and len(examples) < 8:
                examples.append({"lookup": i, "format": 3,
                                 "backtrack": bt, "input": inp,
                                 "lookahead": la, "subst": subs})
            continue
        # format 1/2：用规则集表达
        rules = getattr(st, "ChainSubRuleSet", None) or getattr(
            st, "ChainSubClassSet", None)
        if not rules:
            continue
        for rs in rules:
            rl = (getattr(rs, "ChainSubRule", None)
                  or getattr(rs, "ChainSubClassRule", None) or [])
            for r in rl:
                if len(examples) >= 8:
                    break
                subs = []
                try:
                    for j in range(len(r.Substitute)):
                        subs.append("%s→%s" % (r.Input[j] if j < len(r.Input) else "?",
                                               r.Substitute[j]))
                except Exception:
                    subs = ["(规则 %d)" % getattr(r, "SubstCount", 0)]
                if subs:
                    examples.append({"lookup": i, "format": fmt,
                                     "backtrack": [], "input": list(r.Input)[:4],
                                     "lookahead": [], "subst": subs[:3]})
            if len(examples) >= 8:
                break
        if len(examples) >= 8:
            break
    if len(examples) >= 8:
        break

# format 3 的 coverage 型规则最完整（前后文 + 执行动作齐全）。
# 若不足 6 条，再用 format 1/2 的规则集补充（这类规则没有 coverage，
# 只能给出 Input/Substitute 的字形名）。
if len(examples) < 6:
    for i in sorted(rclt_idx):
        lk = gsub.LookupList.Lookup[i]
        if lk.LookupType != CHAIN_TYPE:
            continue
        for st in lk.SubTable:
            rules = getattr(st, "ChainSubRuleSet", None)
            if not rules:
                continue
            for rs in rules:
                for r in (getattr(rs, "ChainSubRule", None) or []):
                    if len(examples) >= 6:
                        break
                    inp = list(getattr(r, "Input", []) or [])[:4]
                    sub = list(getattr(r, "Substitute", []) or [])[:4]
                    if inp and sub:
                        examples.append({
                            "lookup": i, "format": 1,
                            "backtrack": [], "input": inp, "lookahead": [],
                            "subst": ["%s → %s" % (inp[j] if j < len(inp) else "?",
                                                   sub[j]) for j in range(len(sub))]})
                if len(examples) >= 6:
                    break
            if len(examples) >= 6:
                break
        if len(examples) >= 6:
            break

# 最终兜底：丢掉任何 input 或 subst 为空的条目，避免文档里出现空卡片
examples = [e for e in examples if e["input"] and e["subst"]]

data["rcltChainExamples"] = examples
data["rcltLookupCount"] = len(rclt_idx)
data["gsubLookupCount"] = gsub.LookupList.LookupCount
data["gsubLookupTypes"] = dict(Counter(
    lk.LookupType for lk in gsub.LookupList.Lookup))

# ---------------------------------------------------------------- 4. UCD 断行属性
def parse_prop(path):
    out = {}
    if not os.path.exists(path):
        return out
    import re
    R = re.compile(r"^([0-9A-Fa-f]{4,6})(?:\.\.([0-9A-Fa-f]{4,6}))?$")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.split("#")[0].strip()
            if not ln or ";" not in ln:
                continue
            p = [x.strip() for x in ln.split(";")]
            m = R.match(p[0])
            if not m:
                continue
            a = int(m.group(1), 16)
            b = int(m.group(2), 16) if m.group(2) else a
            for c in range(a, b + 1):
                out[c] = p[1]
    return out

LB = parse_prop(os.path.join(UCD, "LineBreak.txt"))

LB_DOC = {
    "AL": ("Alphabetic", "字母", "普通字母：两个 AL 相邻时不允许断行。"),
    "EX": ("Exclamation/Interrogation", "叹/问号类",
           "不允许在它之前断行 —— 即它不能出现在行首（禁则）。"),
    "BA": ("Break After", "其后可断", "它之后可以断行。"),
    "BB": ("Break Before", "其前可断", "它之前可以断行，且它本身移到下一行。"),
    "GL": ("Non-breaking Glue", "不换行黏合", "前后都不允许断行。"),
    "CM": ("Combining Mark", "组合标记", "无自身断行语义，黏附前一字符。"),
    "NU": ("Numeric", "数字", "与相邻字母/数字之间不允许断行。"),
    "SP": ("Space", "空格", "允许在其后断行。"),
    "OP": ("Open Punctuation", "左括号", "不允许在它之后断行。"),
    "CP": ("Close Parenthesis", "右括号", "不允许在它之前断行。"),
    "CL": ("Close Punctuation", "闭标点", "不允许在它之前断行。"),
    "WJ": ("Word Joiner", "词连接符", "前后都不允许断行。"),
    "ZW": ("Zero Width Space", "零宽空格", "提供一个断行机会。"),
    "ZWJ": ("Zero Width Joiner", "零宽连接符", "连接符序列内不允许断行。"),
    "QU": ("Quotation", "引号", "行为取决于开引号还是闭引号。"),
    "IS": ("Infix Numeric Separator", "数字内分隔符", "数字表达式内部使用。"),
    "B2": ("Break Opportunity Before and After", "前后可断",
           "字符前后都可以断行（如 EM DASH）。"),
}

# 蒙古文块 + 几个对照字符
rows = []
for c in range(0x1800, 0x18AB):
    lb = LB.get(c)
    if not lb:
        continue
    rows.append({"cp": "U+%04X" % c, "ch": chr(c), "lb": lb})
data["lbMongolian"] = rows
data["lbDoc"] = LB_DOC

CONTRAST = [(0x0020, " ", "空格"), (0x0041, "A", "拉丁字母"),
            (0x0030, "0", "数字"), (0x0021, "!", "感叹号"),
            (0x0028, "(", "左括号"), (0x0029, ")", "右括号"),
            (0x00A0, "\u00a0", "不换行空格"), (0x200B, "\u200b", "零宽空格"),
            (0x2060, "\u2060", "词连接符"), (0x200D, "\u200d", "零宽连接符")]
data["lbContrast"] = [{"cp": "U+%04X" % c, "ch": ch, "lb": LB.get(c, "?"), "note": n}
                      for c, ch, n in CONTRAST]

# ---------------------------------------------------------------- 5. 一个真实字形链
data["sampleChain"] = {
    "text": "\u182E\u1823\u1829\u182D\u1823\u182F",
    "codepoints": ["U+182E", "U+1823", "U+1829", "U+182D", "U+1823", "U+182F"],
    "glyphs": ["u182E.M.init", "u1823.O.medi", "u1829.AG.medi",
               "u182D_u1823.GO.medi", "u182F.L.fina"],
}

# ---------------------------------------------------------------- 6. GSUB 16 种 lookup 类型
LOOKUP_TYPES = {
    1: ("Single Substitution", "单字替换", "一个字形换成另一个。"),
    2: ("Multiple Substitution", "一字拆多", "一个字形拆成多个。"),
    3: ("Alternate Substitution", "候选替换", "提供若干候选字形供选择。"),
    4: ("Ligature Substitution", "连字合并", "多个字形合并成一个。"),
    5: ("Contextual Substitution", "上下文替换", "在给定上下文中做替换。"),
    6: ("Chained Contextual Substitution", "链式上下文替换",
        "考察前文/后文再决定替换 —— 蒙文连写的主力。"),
    7: ("Extension Substitution", "扩展替换", "间接寻址，用于突破 64K 偏移限制。"),
    8: ("Reverse Chained Contextual", "反向链式替换", "由后向前做上下文替换。"),
}
data["lookupTypeDoc"] = {str(k): {"full": v[0], "cn": v[1], "desc": v[2]}
                         for k, v in LOOKUP_TYPES.items()}

jspath = os.path.join(OUT, "ttf-basics-data.js")
with open(jspath, "w", encoding="utf-8") as fh:
    fh.write("/* 由 tools/extract_ttf_basics.py 生成，请勿手改。 */\n")
    fh.write("window.UME_TTF_BASICS = ")
    json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    fh.write(";\n")

print("表 %d 个，字形 %d，cmap %d 个码位" % (len(tables), data["numGlyphs"], data["cmapCount"]))
print("GSUB lookup %d 个，rclt 引用 %d 个" % (data["gsubLookupCount"], data["rcltLookupCount"]))
print("rclt 链式规则示例 %d 条" % len(examples))
for e in examples[:3]:
    print("  back=%s input=%s look=%s  ->  %s" % (
        e["backtrack"], e["input"], e["lookahead"], e["subst"]))
print("蒙文断行属性行 %d 条" % len(rows))
print("已写出:", jspath, "(%d 字节)" % os.path.getsize(jspath))
