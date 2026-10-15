# -*- coding: utf-8 -*-
"""中国—蒙古国联合蒙文转写：蒙文 ⇄ 拉丁 双向换算工具。

数据来源：tools/_cnmn_table.json
  （由 tools/_cnmn_wikitext.txt 解析而来，
    原始出处 https://www.qiuwenbaike.cn/wiki/中国—蒙古国联合蒙文转写）

用途：
  · 写文档时用它把拉丁转写**机械地**换成蒙文码位，避免手写蒙文出错
  · 反过来把蒙文码位换成转写，便于核对
  · 可以做一致性自检：a→b→a 是否还原
"""
import io
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "_cnmn_table.json")

# 多字符转写优先匹配（长的排前面），避免 "ng" 被拆成 "n"+"g"
_COL = {"generic": "generic", "khudum": "khudum",
        "todo": "todo", "sibe": "sibe", "manchu": "manchu"}


def load():
    rows = json.loads(io.open(TABLE, encoding="utf-8").read())
    by_cp, by_tr = {}, {}
    for r in rows:
        if not r["cp"]:
            continue          # FVS / MVS 单独处理
        cp = int(r["cp"][2:], 16)
        by_cp[cp] = r
        for col, key in _COL.items():
            v = r.get(key) or ""
            if v and not v.startswith("("):      # (y') 这类是备注，不当正式转写
                by_tr.setdefault(col, {}).setdefault(v, []).append(cp)
    fvs = {r["label"]: r["generic"] for r in rows if r["label"]}
    return rows, by_cp, by_tr, fvs


ROWS, BY_CP, BY_TR, FVS = load()


def tr_to_cps(s, scheme="generic"):
    """拉丁转写 → 码位列表。不认识的字符原样保留（返回为 None 占位）。"""
    table = BY_TR.get(scheme, {})
    keys = sorted(table, key=len, reverse=True)
    out, i = [], 0
    while i < len(s):
        for k in keys:
            if s.startswith(k, i):
                out.append((k, table[k][0]))
                i += len(k)
                break
        else:
            out.append((s[i], None))
            i += 1
    return out


def cps_to_str(cps):
    return "".join(chr(c) for c in cps if c)


def escapes(cps, style="js"):
    r"""生成 \uXXXX 转义串 —— 写进 HTML/JS 时不依赖编辑器能否输入蒙文。

    注意这个 docstring 必须是 raw 字符串：里面写了 \uXXXX 字面量，
    普通字符串会被 Python 当成 Unicode 转义去解码而报错。
    """
    out = []
    for c in cps:
        if c is None:
            continue
        if c > 0xFFFF:
            hi = 0xD800 + ((c - 0x10000) >> 10)
            lo = 0xDC00 + ((c - 0x10000) & 0x3FF)
            out.append("\\u%04X\\u%04X" % (hi, lo))
        else:
            out.append("\\u%04X" % c)
    return "".join(out)


def cps_to_tr(cps, scheme="generic"):
    """码位 → 转写（用于反向核对）。"""
    out = []
    for c in cps:
        r = BY_CP.get(c)
        if not r:
            out.append("?")
            continue
        v = r.get(scheme) or ""
        out.append(v if v else "·")
    return " ".join(out)


def show(word, scheme="generic"):
    cps = [c for _, c in tr_to_cps(word, scheme)]
    print("  %-22s → %-14s  %s" % (
        word, repr(cps_to_str(cps)),
        " ".join("U+%04X" % c for c in cps if c)))
    print("      JS 转义: \"%s\"" % escapes(cps))
    print("      回读:    %s" % cps_to_tr(cps, scheme))
    return cps


if __name__ == "__main__":
    print("=== 换算示例（通用转写 → 蒙文码位）===")
    for w in ("monggul", "bicig", "sain", "baina", "uu", "nigen", "gurban",
              "tngri", "nutug", "kele"):
        show(w)
    print()
    print("=== 按转写查码位 ===")
    for w in ("a", "e", "i", "o", "u", "ö", "ü", "ë", "ng", "š", "č", "ǰ", "x", "g"):
        table = BY_TR["generic"]
        if w in table:
            print("  %-4s → %s" % (w, " ".join("U+%04X" % c for c in table[w])))
    print()
    print("=== FVS / MVS ===")
    for k, v in FVS.items():
        print("  %-6s 转写作 %r" % (k, v))
