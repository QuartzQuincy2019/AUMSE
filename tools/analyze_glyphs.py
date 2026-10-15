# -*- coding: utf-8 -*-
"""
UME 字体深度分析：字形命名分布 + 上下文形位(GSUB)统计。
在 analyze_font.py 的字符级报告之上，回答"3715 个字形都是什么"。
"""
import os
import re
import sys
import json
from collections import Counter, OrderedDict, defaultdict

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "report")

# Noto 蒙文字形命名后缀 -> 形位
SUFFIX = {
    "isol": "isol  单独形",
    "init": "init  词首形",
    "medi": "medi  词中形",
    "fina": "fina  词尾形",
}


def glyph_family(gname):
    """把 `a.isol` / `a.medi` 归并到词干 `a`，识别形位。"""
    m = re.match(r"^(?P<stem>.+?)\.(?P<sfx>[a-zA-Z0-9_]+)$", gname)
    if m:
        return m.group("stem"), m.group("sfx")
    return gname, None


def dump_lookups(table, kind):
    """按 lookup 汇总引用它的特性。"""
    owners = defaultdict(set)
    for fr in table.FeatureList.FeatureRecord:
        for li in fr.Feature.LookupListIndex:
            owners[li].add(fr.FeatureTag)
    rows = []
    for i, lk in enumerate(table.LookupList.Lookup):
        tags = sorted(owners.get(i, []))
        if not tags:
            continue
        n = 0
        for st in lk.SubTable:
            for attr in ("mapping", "alternates", "ligatures", "substitute"):
                v = getattr(st, attr, None)
                if isinstance(v, dict):
                    n += len(v)
        rows.append({"index": i, "type": lk.LookupType, "features": tags, "entries": n,
                     "flags": lk.LookupFlag})
    return rows


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    f = TTFont(FONT)
    order = f.getGlyphOrder()
    best = f.getBestCmap()
    hmtx = f["hmtx"]

    L = []
    A = L.append
    A("=" * 78)
    A("UME 字形分布与上下文形位分析 (glyph-level)")
    A("=" * 78)

    # ---------- 1. 字形命名分布
    stems = Counter()
    sfx = Counter()
    plain = []
    for g in order:
        stem, s = glyph_family(g)
        stems[stem] += 1
        sfx[s if s else "(无后缀/基字形)"] += 1
        if s is None:
            plain.append(g)

    A("")
    A("-- 字形命名后缀分布 (共 %d 字形) --" % len(order))
    for k, v in sfx.most_common():
        A("  %-18s %5d  (%.1f%%)" % (k, v, 100.0 * v / len(order)))

    multi = [(s, c) for s, c in stems.items() if c > 1]
    multi.sort(key=lambda kv: -kv[1])
    A("")
    A("-- 同词干多形位字形 (即需要上下文选形的字母) --")
    A("  有多个形位的词干数 : %d" % len(multi))
    A("  形位字形合计       : %d" % sum(c for _, c in multi))
    A("  Top 30 形位最多的词干:")
    for s, c in multi[:30]:
        forms = [glyph_family(g)[1] for g in order if glyph_family(g)[0] == s]
        A("      %-16s %2d 形 -> %s" % (s, c, ", ".join(
            x for x in forms if x)))

    # ---------- 2. 未被 cmap 引用的字形（纯排版中间产物）
    referenced = set(best.values())
    unref = [g for g in order if g not in referenced]
    A("")
    A("-- 字形可达性 --")
    A("  被 cmap 直接引用的字形 : %d" % len(referenced))
    A("  仅由 GSUB 间接产生的字形: %d" % len(unref))
    A("  (后者即上下文形位/连字/变体，必须靠排版引擎生成)")

    # ---------- 3. 各 Unicode 区段的码位 -> 字形映射
    A("")
    A("-- 蒙文码位 -> 基础字形 (cmap 直接映射) --")
    A("  %-9s %-3s %-38s %s" % ("码位", "字", "名称", "字形名"))
    mong_cps = sorted(c for c in best if 0x1800 <= c <= 0x18AF)
    for cp in mong_cps:
        import unicodedata
        try:
            nm = unicodedata.name(chr(cp))
        except ValueError:
            nm = "?"
        A("  %-9s %-3s %-38s %s" % ("U+%04X" % cp, chr(cp), nm, best[cp]))

    # ---------- 4. GSUB 逐特性统计
    gsub = f["GSUB"].table
    A("")
    A("-- GSUB 特性按脚本 --")
    for sr in gsub.ScriptList.ScriptRecord:
        tag = sr.ScriptTag
        feats = []
        if sr.Script.DefaultLangSys:
            feats += [gsub.FeatureList.FeatureRecord[i].FeatureTag
                      for i in sr.Script.DefaultLangSys.FeatureIndex]
        for ls in sr.Script.LangSysRecord:
            feats += ["%s:%s" % (ls.LangSysTag, gsub.FeatureList.FeatureRecord[i].FeatureTag)
                      for i in ls.LangSys.FeatureIndex]
        A("  %-6s %s" % (tag, ", ".join(sorted(set(feats)))))

    A("")
    A("-- GSUB 特性总览 (特性 -> 引用 lookup 数 / 替换条目数) --")
    owners = defaultdict(list)
    for fr in gsub.FeatureList.FeatureRecord:
        owners[fr.FeatureTag] += list(fr.Feature.LookupListIndex)
    for tag in sorted(owners):
        idxs = owners[tag]
        n = 0
        for i in idxs:
            for st in gsub.LookupList.Lookup[i].SubTable:
                for attr in ("mapping", "alternates", "ligatures"):
                    v = getattr(st, attr, None)
                    if isinstance(v, dict):
                        n += len(v)
        A("  %-6s lookups=%-4d 替换条目=%d" % (tag, len(idxs), n))

    A("")
    A("-- GSUB lookup 类型分布 --")
    tcount = Counter(lk.LookupType for lk in gsub.LookupList.Lookup)
    TYPE_NAME = {1: "Single 单字替换", 2: "Multiple 一字拆多",
                 3: "Alternate 候选替换", 4: "Ligature 连字合并",
                 5: "Context 上下文", 6: "Chaining 链式上下文",
                 7: "Extension 扩展", 8: "ReverseChaining 反向链式"}
    for t, c in sorted(tcount.items()):
        A("  type %d  %-26s %d" % (t, TYPE_NAME.get(t, "?"), c))

    # ---------- 5. 形位替换：每个字母能变成哪些形式
    A("")
    A("-- 单字替换(glyph -> variants) 抽样：蒙文字母的形位体系 --")
    mapping_all = {}
    for i, lk in enumerate(gsub.LookupList.Lookup):
        if lk.LookupType != 1:
            continue
        for st in lk.SubTable:
            m = getattr(st, "mapping", None)
            if m:
                mapping_all.update(m)
    A("  单字替换映射总数: %d" % len(mapping_all))
    # 展示几个典型字母
    samples = ["a", "e", "i", "o", "u", "na", "ba", "ma", "sa", "da", "ga", "ra"]
    for s in samples:
        tgt = sorted({v for k, v in mapping_all.items()
                      if glyph_family(k)[0] == s or glyph_family(v)[0] == s})
        if tgt:
            A("  %-4s -> %s" % (s, ", ".join(tgt)))

    # ---------- 6. 连字（Ligature）数量：蒙文的"字尾相连"
    A("")
    A("-- 连字合并 (Ligature) --")
    lig_total = 0
    lig_examples = []
    for i, lk in enumerate(gsub.LookupList.Lookup):
        if lk.LookupType != 4:
            continue
        for st in lk.SubTable:
            ligs = getattr(st, "ligatures", None)
            if not ligs:
                continue
            for first, lst in ligs.items():
                for lg in lst:
                    lig_total += 1
                    if len(lig_examples) < 15:
                        lig_examples.append("%s + %s -> %s" % (
                            first, " + ".join(lg.Component), lg.LigGlyph))
    A("  连字总数: %d" % lig_total)
    for e in lig_examples:
        A("    " + e)

    # ---------- 7. 垂直排版
    has_vert = any(fr.FeatureTag == "vert"
                   for fr in gsub.FeatureList.FeatureRecord)
    A("")
    A("-- 垂直排版支持 --")
    A("  GSUB 'vert' 特性: %s" % ("有" if has_vert else "无"))
    A("  vhea/vmtx 表    : %s" % ("有" if "vhea" in f else "无"))
    A("  → 蒙文为竖排书写，若缺 vhea/vmtx，竖排需由排版引擎做 90° 旋转")

    # ---------- 8. 拉丁/西文覆盖（编辑器 UI 用）
    A("")
    A("-- 西文/符号覆盖（编辑器界面与混排需要） --")
    for lo, hi, nm in [(0x20, 0x7E, "ASCII 可打印"),
                       (0xA0, 0xFF, "Latin-1 补充"),
                       (0x100, 0x17F, "Latin 扩展-A"),
                       (0x300, 0x36F, "组合附加符号"),
                       (0x2000, 0x206F, "常用标点"),
                       (0x3000, 0x303F, "CJK 标点")]:
        have = [c for c in range(lo, hi + 1) if c in best]
        A("  %-16s %3d / %3d" % (nm, len(have), hi - lo + 1))

    text = "\n".join(L)
    print(text)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "NotoSansMongolian-Regular.glyphs.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(text)
    with open(os.path.join(OUT, "NotoSansMongolian-Regular.glyphs.json"), "w",
              encoding="utf-8") as fh:
        json.dump({
            "glyph_count": len(order),
            "suffix_distribution": dict(sfx),
            "stems_with_multiple_forms": len(multi),
            "cmap_referenced_glyphs": len(referenced),
            "gsub_only_glyphs": len(unref),
            "single_substitutions": len(mapping_all),
            "ligatures": lig_total,
            "gsub_lookup_types": {str(k): v for k, v in tcount.items()},
            "has_vert": has_vert,
            "has_vhea": "vhea" in f,
        }, fh, ensure_ascii=False, indent=2)
    print("\n已写出: %s" % os.path.join(OUT, "NotoSansMongolian-Regular.glyphs.txt"))


if __name__ == "__main__":
    main()
