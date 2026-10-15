# -*- coding: utf-8 -*-
"""
UME (Uyghur-Mongolian Editor / 回鹘蒙文编辑器)
字体字符分布分析工具 —— 解析目录内的 TTF/OTF 字体，输出字符覆盖率报告。

用法:
    python analyze_font.py <font-file> [...]
    python analyze_font.py font/NotoSansMongolian-Regular.ttf
"""
import sys
import os
import json
import unicodedata
from collections import Counter, OrderedDict

from fontTools.ttLib import TTFont

# ---------------------------------------------------------------- Unicode 区段
# 与蒙文排版直接相关的区段优先，其余为通用区段抽样
BLOCKS = [
    ("Mongolian",                 0x1800, 0x18AF),
    ("Mongolian Supplement",      0x11660, 0x1167F),
    ("CJK Symbols and Punctuation", 0x3000, 0x303F),
    ("General Punctuation",       0x2000, 0x206F),
    ("Basic Latin",               0x0000, 0x007F),
    ("Latin-1 Supplement",        0x0080, 0x00FF),
    ("Latin Extended-A",          0x0100, 0x017F),
    ("Latin Extended-B",          0x0180, 0x024F),
    ("IPA Extensions",            0x0250, 0x02AF),
    ("Spacing Modifier Letters",  0x02B0, 0x02FF),
    ("Combining Diacritical Marks", 0x0300, 0x036F),
    ("Cyrillic",                  0x0400, 0x04FF),
    ("Cyrillic Supplement",       0x0500, 0x052F),
    ("Greek and Coptic",          0x0370, 0x03FF),
    ("Arabic",                    0x0600, 0x06FF),
    ("Hebrew",                    0x0590, 0x05FF),
    ("Thai",                      0x0E00, 0x0E7F),
    ("Hangul Jamo",               0x1100, 0x11FF),
    ("Phonetic Extensions",       0x1D00, 0x1D7F),
    ("Combining Diacritical Marks Supplement", 0x1DC0, 0x1DFF),
    ("Latin Extended Additional", 0x1E00, 0x1EFF),
    ("General Punctuation Ext",   0x2070, 0x209F),
    ("Superscripts and Subscripts", 0x2070, 0x209F),
    ("Currency Symbols",          0x20A0, 0x20CF),
    ("Letterlike Symbols",        0x2100, 0x214F),
    ("Number Forms",              0x2150, 0x218F),
    ("Arrows",                    0x2190, 0x21FF),
    ("Mathematical Operators",    0x2200, 0x22FF),
    ("Miscellaneous Technical",   0x2300, 0x23FF),
    ("Box Drawing",               0x2500, 0x257F),
    ("Block Elements",            0x2580, 0x259F),
    ("Geometric Shapes",          0x25A0, 0x25FF),
    ("Miscellaneous Symbols",     0x2600, 0x26FF),
    ("Dingbats",                  0x2700, 0x27BF),
    ("Braille Patterns",          0x2800, 0x28FF),
    ("CJK Radicals Supplement",   0x2E80, 0x2EFF),
    ("Kangxi Radicals",           0x2F00, 0x2FDF),
    ("CJK Symbols and Punctuation", 0x3000, 0x303F),
    ("Hiragana",                  0x3040, 0x309F),
    ("Katakana",                  0x30A0, 0x30FF),
    ("Bopomofo",                  0x3100, 0x312F),
    ("CJK Unified Ideographs",    0x4E00, 0x9FFF),
    ("Hangul Syllables",          0xAC00, 0xD7AF),
    ("Private Use Area",          0xE000, 0xF8FF),
    ("Alphabetic Presentation Forms", 0xFB00, 0xFB4F),
    ("Arabic Presentation Forms-A", 0xFB50, 0xFDFF),
    ("Arabic Presentation Forms-B", 0xFE70, 0xFEFF),
    ("Halfwidth and Fullwidth Forms", 0xFF00, 0xFFEF),
    ("Specials",                  0xFFF0, 0xFFFF),
]


def block_of(cp):
    for name, lo, hi in BLOCKS:
        if lo <= cp <= hi:
            return name
    return "Other"


def char_name(cp):
    try:
        return unicodedata.name(chr(cp))
    except ValueError:
        return "<unnamed>"


def cat_label(cp):
    ch = chr(cp)
    c = unicodedata.category(ch)
    return {
        "Lu": "大写字母", "Ll": "小写字母", "Lo": "字母(其它)", "Lm": "修饰字母",
        "Mn": "组合标记(非间距)", "Mc": "组合标记(间距)", "Me": "组合标记(包围)",
        "Nd": "十进制数字", "Nl": "字母数字", "No": "其它数字",
        "Po": "标点(其它)", "Pd": "标点(横线)", "Ps": "标点(左括号)",
        "Pe": "标点(右括号)", "Pi": "标点(左引号)", "Pf": "标点(右引号)",
        "Sm": "数学符号", "Sc": "货币符号", "Sk": "修饰符号", "So": "其它符号",
        "Zs": "空格", "Zl": "行分隔", "Zp": "段分隔", "Cc": "控制字符", "Cf": "格式字符",
        "Cs": "代理项", "Co": "私用", "Cn": "未分配",
    }.get(c, c)


# ---------------------------------------------------------------- 分析主体
def analyze(path):
    f = TTFont(path, lazy=False)
    info = OrderedDict()
    info["file"] = os.path.abspath(path)
    info["size_bytes"] = os.path.getsize(path)

    # ---- sfnt 版本 / 表清单
    info["sfnt_version"] = "0x%08X" % int.from_bytes(
        str(f.sfntVersion).encode("latin1")[:4], "big")
    info["flavor"] = f.flavor or "TTF (glyf outlines)"
    tables = sorted(f.reader.tables.keys())
    info["tables"] = tables
    info["table_sizes"] = {t: f.reader.tables[t].length for t in tables}

    # ---- head
    head = f["head"]
    info["units_per_em"] = head.unitsPerEm
    info["created"] = str(head.created)
    info["modified"] = str(head.modified)
    info["mac_style_flags"] = head.macStyle

    # ---- OS/2
    if "OS/2" in f:
        os2 = f["OS/2"]
        info["os2_version"] = os2.version
        info["weight_class"] = os2.usWeightClass
        info["width_class"] = os2.usWidthClass
        info["fsSelection"] = os2.fsSelection
        info["fsType"] = os2.fsType
        info["vendor_id"] = os2.achVendID
        info["typo_ascender"] = os2.sTypoAscender
        info["typo_descender"] = os2.sTypoDescender
        info["typo_line_gap"] = os2.sTypoLineGap
        info["win_ascent"] = os2.usWinAscent
        info["win_descent"] = os2.usWinDescent
        info["x_height"] = getattr(os2, "sxHeight", None)
        info["cap_height"] = getattr(os2, "sCapHeight", None)
        info["default_char"] = getattr(os2, "usDefaultChar", None)
        info["break_char"] = getattr(os2, "usBreakChar", None)
        info["unicode_ranges"] = "0x%08X 0x%08X 0x%08X 0x%08X" % (
            os2.ulUnicodeRange1, os2.ulUnicodeRange2,
            os2.ulUnicodeRange3, os2.ulUnicodeRange4)
        info["codepage_ranges"] = "0x%08X 0x%08X" % (
            os2.ulCodePageRange1, os2.ulCodePageRange2)

    # ---- name
    names = OrderedDict()
    for rec in f["name"].names:
        key = rec.nameID
        try:
            val = rec.toUnicode()
        except Exception:
            val = repr(rec.string)
        plat = {0: "Unicode", 1: "Mac", 3: "Windows"}.get(rec.platformID, str(rec.platformID))
        names.setdefault(key, {})["%s/%s/%s" % (plat, rec.platEncID, rec.langID)] = val
    NAME_IDS = {
        0: "Copyright", 1: "Family", 2: "Subfamily", 3: "Unique ID",
        4: "Full name", 5: "Version", 6: "PostScript name", 7: "Trademark",
        8: "Manufacturer", 9: "Designer", 10: "Description", 11: "Vendor URL",
        12: "Designer URL", 13: "License", 14: "License URL",
        16: "Typographic Family", 17: "Typographic Subfamily",
        18: "Compatible Full", 19: "Sample text", 20: "PostScript CID",
        21: "WWS Family", 22: "WWS Subfamily", 25: "Variations PS Prefix",
    }
    info["name_records"] = OrderedDict(
        (NAME_IDS.get(k, "nameID %d" % k), v) for k, v in sorted(names.items()))

    # ---- maxp
    maxp = f["maxp"]
    info["num_glyphs"] = maxp.numGlyphs
    info["maxp_version"] = "0x%08X" % maxp.tableVersion

    # ---- hmtx
    hmtx = f["hmtx"]
    widths = [hmtx[g][0] for g in f.getGlyphOrder()]
    info["advance_width"] = {
        "min": min(widths), "max": max(widths),
        "distinct": len(set(widths)),
        "most_common": Counter(widths).most_common(8),
    }
    hhea = f["hhea"]
    info["hhea"] = {
        "ascender": hhea.ascent, "descender": hhea.descent, "lineGap": hhea.lineGap,
        "advanceWidthMax": hhea.advanceWidthMax,
        "numOfLongHorMetrics": hhea.numberOfHMetrics,
    }

    # ---- cmap
    cmap_tables = OrderedDict()
    for st in f["cmap"].tables:
        plat = {0: "Unicode", 1: "Macintosh", 3: "Windows"}.get(st.platformID, str(st.platformID))
        key = "%s/%d (format %d)" % (plat, st.platEncID, st.format)
        cmap_tables[key] = len(st.cmap)
    info["cmap_subtables"] = cmap_tables

    best = f.getBestCmap()               # 最佳 Unicode cmap
    all_uni = set()
    for st in f["cmap"].tables:
        if st.platformID == 0 or (st.platformID == 3 and st.platEncID in (1, 10)):
            all_uni |= set(st.cmap.keys())
    info["unicode_codepoints_best_cmap"] = len(best)
    info["unicode_codepoints_all_subtables"] = len(all_uni)

    # ---- 按 Unicode 区段统计
    by_block = Counter(block_of(cp) for cp in best)
    info["coverage_by_block"] = OrderedDict(
        sorted(by_block.items(), key=lambda kv: -kv[1]))

    # ---- 按类别统计
    by_cat = Counter(cat_label(cp) for cp in best)
    info["coverage_by_category"] = OrderedDict(
        sorted(by_cat.items(), key=lambda kv: -kv[1]))

    # ---- 蒙文主区段逐字符明细
    mong = []
    for cp in sorted(c for c in best if 0x1800 <= c <= 0x18AF):
        g = best[cp]
        w = hmtx[g][0] if g in hmtx.metrics else None
        mong.append(OrderedDict([
            ("codepoint", "U+%04X" % cp),
            ("char", chr(cp)),
            ("name", char_name(cp)),
            ("category", cat_label(cp)),
            ("glyph", g),
            ("advance_width", w),
        ]))
    info["mongolian_block_detail"] = mong
    info["mongolian_block_coverage"] = {
        "assigned_in_unicode": sum(
            1 for c in range(0x1800, 0x18B0)
            if unicodedata.category(chr(c)) != "Cn"),
        "present_in_font": len(mong),
        "missing_in_font": [
            "U+%04X %s" % (c, char_name(c))
            for c in range(0x1800, 0x18B0)
            if unicodedata.category(chr(c)) != "Cn" and c not in best
        ],
    }

    # ---- 蒙文补充区段
    supp = []
    for cp in sorted(c for c in best if 0x11660 <= c <= 0x1167F):
        supp.append(OrderedDict([
            ("codepoint", "U+%04X" % cp), ("char", chr(cp)),
            ("name", char_name(cp)), ("glyph", best[cp]),
            ("advance_width", hmtx[best[cp]][0]),
        ]))
    info["mongolian_supplement_detail"] = supp

    # ---- 自由变体选择符 FVS
    fvs = [c for c in best if 0x180B <= c <= 0x180D or c in (0x180F,)]
    info["free_variation_selectors"] = [
        "U+%04X %s" % (c, char_name(c)) for c in sorted(fvs)]

    # ---- GSUB
    gsub = OrderedDict()
    if "GSUB" in f:
        t = f["GSUB"].table
        scripts = OrderedDict()
        for sr in t.ScriptList.ScriptRecord:
            scripts[sr.ScriptTag] = {
                "default_lang_sys": bool(sr.Script.DefaultLangSys),
                "lang_sys": [ls.LangSysTag for ls in sr.Script.LangSysRecord],
            }
        gsub["scripts"] = scripts
        gsub["features"] = OrderedDict()
        for fr in t.FeatureList.FeatureRecord:
            gsub["features"].setdefault(fr.FeatureTag, 0)
            gsub["features"][fr.FeatureTag] += len(fr.Feature.LookupListIndex)
        gsub["lookup_count"] = t.LookupList.LookupCount
        gsub["lookup_types"] = OrderedDict(
            (str(i), sum(1 for lk in t.LookupList.Lookup if lk.LookupType == i))
            for i in sorted({lk.LookupType for lk in t.LookupList.Lookup}))
        # 变体字形数量（GSUB type 1/3 产生的替换总数）
        nsub = 0
        for lk in t.LookupList.Lookup:
            for st in lk.SubTable:
                if lk.LookupType == 1:
                    nsub += len(getattr(st, "mapping", {}) or {})
                elif lk.LookupType == 3:
                    nsub += len(getattr(st, "alternates", {}) or {})
        gsub["total_substitutions"] = nsub
    info["GSUB"] = gsub

    # ---- GPOS
    gpos = OrderedDict()
    if "GPOS" in f:
        t = f["GPOS"].table
        gpos["scripts"] = list(
            OrderedDict.fromkeys(sr.ScriptTag for sr in t.ScriptList.ScriptRecord))
        gpos["features"] = OrderedDict()
        for fr in t.FeatureList.FeatureRecord:
            gpos["features"].setdefault(fr.FeatureTag, 0)
            gpos["features"][fr.FeatureTag] += len(fr.Feature.LookupListIndex)
        gpos["lookup_types"] = OrderedDict(
            (str(i), sum(1 for lk in t.LookupList.Lookup if lk.LookupType == i))
            for i in sorted({lk.LookupType for lk in t.LookupList.Lookup}))
    info["GPOS"] = gpos

    # ---- GDEF 类别统计
    gdef = OrderedDict()
    if "GDEF" in f:
        t = f["GDEF"].table
        try:
            cls = t.GlyphClassDef.classDefs
            c = Counter(cls.values())
            gdef["glyph_class_defs"] = {
                {1: "Base(基字形)", 2: "Ligature(连字)", 3: "Mark(标记)",
                 4: "Component(部件)"}.get(k, str(k)): v for k, v in sorted(c.items())}
        except Exception:
            pass
        if getattr(t, "MarkAttachClassDef", None):
            gdef["mark_attach_classes"] = len(t.MarkAttachClassDef.classDefs)
        if getattr(t, "MarkGlyphSetsDef", None):
            gdef["mark_glyph_sets"] = t.MarkGlyphSetsDef.MarkSetCount
    info["GDEF"] = gdef

    # ---- glyf 轮廓统计（轮廓复杂度 → 判断装饰/字形密度）
    if "glyf" in f:
        glyf = f["glyf"]
        n_empty = sum(1 for g in f.getGlyphOrder()
                      if glyf[g].numberOfContours == 0)
        info["glyf"] = {
            "glyphs_with_outlines": maxp.numGlyphs - n_empty,
            "empty_glyphs": n_empty,
        }

    info["glyph_order_sample"] = list(f.getGlyphOrder())[:40]
    return info


def render_text(info):
    L = []
    A = L.append
    A("=" * 78)
    A("UME 字体字符分布分析报告")
    A("=" * 78)
    A("文件      : %s" % info["file"])
    A("大小      : %s 字节 (%.1f KB)" % (info["size_bytes"], info["size_bytes"] / 1024))
    A("轮廓格式  : %s   sfntVersion=%s" % (info["flavor"], info["sfnt_version"]))
    A("em 单位   : %d" % info["units_per_em"])
    A("字形总数  : %d" % info["num_glyphs"])
    A("表数量    : %d -> %s" % (len(info["tables"]), ", ".join(info["tables"])))
    A("")
    A("-- 名称表 --")
    for k, v in info.get("name_records", {}).items():
        for kk, vv in v.items():
            A("  %-22s [%s] %s" % (k, kk, vv))
    A("")
    A("-- 度量 --")
    for k, v in info.get("hhea", {}).items():
        A("  hhea.%-18s %s" % (k, v))
    if "OS/2" in info or True:
        for k in ("typo_ascender", "typo_descender", "typo_line_gap",
                  "win_ascent", "win_descent", "x_height", "cap_height",
                  "weight_class", "width_class", "unicode_ranges"):
            if k in info:
                A("  OS/2.%-18s %s" % (k, info[k]))
    A("  横向 advance  : min=%s max=%s 不同值=%s" % (
        info["advance_width"]["min"], info["advance_width"]["max"],
        info["advance_width"]["distinct"]))
    A("  最常见 advance: %s" % info["advance_width"]["most_common"])
    A("")
    A("-- cmap 子表 --")
    for k, v in info["cmap_subtables"].items():
        A("  %-28s %d 个映射" % (k, v))
    A("  Unicode 码位数(最佳 cmap) : %d" % info["unicode_codepoints_best_cmap"])
    A("  Unicode 码位数(全部子表) : %d" % info["unicode_codepoints_all_subtables"])
    A("")
    A("-- 按 Unicode 区段分布 --")
    for k, v in info["coverage_by_block"].items():
        A("  %-38s %4d" % (k, v))
    A("")
    A("-- 按字符类别分布 --")
    for k, v in info["coverage_by_category"].items():
        A("  %-24s %4d" % (k, v))
    A("")
    mb = info["mongolian_block_coverage"]
    A("-- 蒙文主区段 U+1800..U+18AF --")
    A("  Unicode 已分配 : %d" % mb["assigned_in_unicode"])
    A("  字体已收录     : %d" % mb["present_in_font"])
    A("  覆盖率         : %.1f%%" % (
        100.0 * mb["present_in_font"] / mb["assigned_in_unicode"]))
    if mb["missing_in_font"]:
        A("  未收录         : %s" % ", ".join(mb["missing_in_font"]))
    else:
        A("  未收录         : 无")
    A("")
    A("  %-9s %-3s %-40s %-14s %s" % ("码位", "字", "Unicode 名称", "类别", "advance"))
    for r in info["mongolian_block_detail"]:
        A("  %-9s %-3s %-40s %-14s %s" % (
            r["codepoint"], r["char"], r["name"], r["category"], r["advance_width"]))
    A("")
    if info["mongolian_supplement_detail"]:
        A("-- 蒙文补充区段 U+11660..U+1167F --")
        for r in info["mongolian_supplement_detail"]:
            A("  %-9s %-3s %-40s adv=%s" % (
                r["codepoint"], r["char"], r["name"], r["advance_width"]))
        A("")
    if info["free_variation_selectors"]:
        A("-- 自由变体选择符 (FVS) --")
        for s in info["free_variation_selectors"]:
            A("  " + s)
        A("")
    A("-- OpenType 排版特性 --")
    if info.get("GSUB"):
        g = info["GSUB"]
        A("  GSUB 脚本   : %s" % ", ".join(g["scripts"].keys()))
        A("  GSUB lookup : %d 个, 类型分布 %s" % (
            g["lookup_count"], dict(g["lookup_types"])))
        A("  GSUB 替换总数: %d" % g["total_substitutions"])
        A("  GSUB 特性   :")
        for k, v in sorted(g["features"].items()):
            A("      %-6s lookups=%d" % (k, v))
    if info.get("GPOS"):
        g = info["GPOS"]
        A("  GPOS 脚本   : %s" % ", ".join(g["scripts"]))
        A("  GPOS lookup 类型分布: %s" % dict(g["lookup_types"]))
        A("  GPOS 特性   : %s" % ", ".join(sorted(g["features"])))
    if info.get("GDEF"):
        A("  GDEF        : %s" % json.dumps(info["GDEF"], ensure_ascii=False))
    A("")
    return "\n".join(L)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = sys.argv[1:]
    if not args:
        args = [os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "font", "NotoSansMongolian-Regular.ttf")]
    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "report")
    os.makedirs(outdir, exist_ok=True)
    for path in args:
        if not os.path.isfile(path):
            print("跳过（不是文件）: %s" % path)
            continue
        info = analyze(path)
        text = render_text(info)
        print(text)
        base = os.path.splitext(os.path.basename(path))[0]
        with open(os.path.join(outdir, base + ".report.txt"), "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, base + ".report.json"), "w", encoding="utf-8") as fh:
            json.dump(info, fh, ensure_ascii=False, indent=2)
        print("已写出: %s" % os.path.join(outdir, base + ".report.txt"))


if __name__ == "__main__":
    main()
