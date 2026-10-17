# -*- coding: utf-8 -*-
"""缩写第一次出现时补上中文全称（用户规则）。

已合规的不用动：
    m09  RAII（资源获取即初始化）           ✓ 已有中文
    q05  单一职责原则（SRP）/ 开闭原则（OCP） ✓ 本轮已补
    q08  接口隔离原则（ISP）                ✓ 本轮已补

要补的：
    fe-09  DOM 树（Document Object Model）  → 补中文「文档对象模型」
    t01    表（GSUB）/ 表（GPOS）           → 补「字形替换表 / 字形定位表」
    t03    GSUB / GPOS 的正文首次出现       → 同上

t03 的表格行里已经有「字形替换：连字、位置变体」「位置微调：kern」，
语义上已给出中文含义，但没有正式表名 —— 这里补在正文首次提到处。
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# ---------------------------------------------------------------- fe-09（JSON 页）
p = os.path.join(T, "fe-09.html")
t = io.open(p, encoding="utf-8").read()
RE = re.compile(r'(window\.__FE_PAGE__\s*=\s*)(\{.*?\})(;\s*\n</script>)', re.S)
m = RE.search(t)
if not m:
    print("  !! fe-09 找不到 __FE_PAGE__")
else:
    d = json.loads(m.group(2))
    body = d["body"]
    old = "这套结构就叫 DOM 树（Document Object Model）。"
    new = "这套结构就叫 DOM 树（<b>文档对象模型</b>，Document Object Model）。"
    if old in body:
        d["body"] = body.replace(old, new, 1)
        js = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        js = js.replace("</", "<\\/")
        io.open(p, "w", encoding="utf-8", newline="").write(
            t[:m.start(2)] + js + t[m.end(2):])
        print("  fe-09 已补 DOM 的中文名")
    elif "文档对象模型" in body:
        print("  fe-09 已有中文名，跳过")
    else:
        print("  !! fe-09 锚点未匹配")

# ---------------------------------------------------------------- t01
p = os.path.join(T, "t01.html")
t = io.open(p, encoding="utf-8").read()
OLD1 = "「换字形」的表（GSUB）比「摆位置」的表（GPOS）大得多"
NEW1 = "「换字形」的表（<b>字形替换表</b>，GSUB）比「摆位置」的表（<b>字形定位表</b>，GPOS）大得多"
if OLD1 in t:
    t = t.replace(OLD1, NEW1, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("  t01 已补 GSUB / GPOS 的中文名")
elif "字形替换表" in t:
    print("  t01 已有中文名，跳过")
else:
    print("  !! t01 锚点未匹配")

# ---------------------------------------------------------------- t03
p = os.path.join(T, "t03.html")
t = io.open(p, encoding="utf-8").read()
OLD3 = "GSUB 占 15% 排第二，\n  而且比 GPOS 大 5.5 倍"
if OLD3 not in t:
    # 换一种可能的换行写法
    m3 = re.search(r'GSUB 占 15% 排第二，\s*而且比 GPOS 大 5\.5 倍', t)
    OLD3 = m3.group(0) if m3 else None

if "字形替换表" in t:
    print("  t03 已有中文名，跳过")
elif OLD3:
    NEW3 = ("GSUB（<b>字形替换表</b>）占 15% 排第二，\n"
            "  而且比 GPOS（<b>字形定位表</b>）大 5.5 倍")
    t = t.replace(OLD3, NEW3, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("  t03 已补 GSUB / GPOS 的中文名")
else:
    print("  !! t03 锚点未匹配")
