# -*- coding: utf-8 -*-
"""把「写死的浅色背景」换成语义化表面变量 —— 第三版（前两版都出过事）。

出过的两次事故
--------------
第 1 版：连金色渐变的色标（#fffdf5/#fdf3dc/#fbe9c4）也换了 → 亮色下
         .key-h 的金色渐变变成灰色渐变。
第 2 版：替换时用 `re.sub(r'#fff\\b', 'var(--sfc)', v)`，
         但 `#` 不在匹配里 —— 于是产出 `background:#var(--sfc)`，
         **# 后面的 var() 不是合法颜色，整条声明失效**。
         实测 303 处非法声明（`background:--sfc`），全站浅色底全没了。

本版的三个保险
--------------
1. 颜色模式**连 # 一起匹配**：r'#fff\\b' → 替换成 'var(--sfc)'，
   但匹配里包含 '#'，所以要写成 r'#fff\\b' 并把 '#' 吃进去 ——
   先用 r'(#fff)\\b' 捕获再整体替换。
2. 只动 background / background-color，**不碰 border-color**。
3. 替换完做**语法自检**：
     · 不允许出现 `:#`、`:#`、`:--`、`:#var(`、`:#`
     · 花括号必须配平
     · `var(--` 后面必须紧跟合法变量名
   任何一条不过，就整体放弃、保留原文件。
"""
import io
import os
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
BAK = os.path.join(os.environ["TEMP"], "svc-backup")

# ---------- 0. 从备份恢复（备份是替换前的干净版本） ----------
n = 0
for f in sorted(os.listdir(BAK)):
    if f.endswith(".css"):
        shutil.copy2(os.path.join(BAK, f), os.path.join(A, f))
        n += 1
print("  从备份恢复 %d 份样式表（回到替换前的干净状态）" % n)

# ---------- 1. 哪些色标不能动 ----------
# (原色, 替换成的**完整 CSS 值**) —— 值必须带 var(...)，
# 否则会产出 `background:--sfc-hover` 这种非法声明（上一版就是这么翻车的）
NEUTRAL = [
    ("#f4f8fd", "var(--sfc-hover)"),
    ("#f2f4f8", "var(--sfc-2)"),
    ("#f7f9fc", "var(--sfc-2)"),
    ("#fbfcfe", "var(--sfc-3)"),
    ("#ffffff", "var(--sfc)"),
    ("#fff",    "var(--sfc)"),      # 放最后
]
# 与 #fff 同处渐变的非中性色标 → 不动
grad_exclude = set()
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    c = io.open(os.path.join(A, f), encoding="utf-8").read()
    for m in re.finditer(r'gradient\([^;{}]*\)', c):
        g = m.group(0).lower()
        if "#fff" in g:
            for col in re.findall(r'#[0-9a-f]{3,8}', g):
                if col not in ("#fff", "#ffffff"):
                    grad_exclude.add(col)
print("  渐变色标（不动）：%s" % sorted(grad_exclude))


LIGHT_VARS = """
/* =====================================================================
   表面变量（亮色）
   ---------------------------------------------------------------------
   样式表里原来到处写死 #fff / #f2f4f8 这类浅色，暗色模式只能一个个
   选择器去补 —— 补不完。现在统一走这几个变量：暗色只改变量值，
   所有引用处一起生效。

   ⚠ 金色渐变的色标（#fffdf5 / #fdf3dc / #fbe9c4 …）**不在**这套变量里 ——
     它们是主题色，不是中性表面。
   ===================================================================== */
:root{
  --sfc:#ffffff;
  --sfc-2:#f2f4f8;
  --sfc-3:#fbfcfe;
  --sfc-hover:#f4f8fd;
  --sfc-glass:rgba(255,255,255,.74);
}
"""

DARK_VARS = """
@media (prefers-color-scheme: dark){
  :root:root{
    --sfc:#1b1e25;
    --sfc-2:#161d26;
    --sfc-3:#1e242e;
    --sfc-hover:#1e2836;
    --sfc-glass:rgba(38,44,54,.72);
  }
}
"""

GLASS = re.compile(r'rgba\(255,\s*255,\s*255,\s*(?:0?\.\d+)\)')


def fix_value(v):
    """只替换「整体作为颜色值」的中性色；渐变色标不动。"""
    cnt = 0
    # 半透明白
    v2, k = GLASS.subn('var(--sfc-glass)', v)
    cnt += k
    v = v2
    for col, var in NEUTRAL:
        # 关键：把 '#' 一起匹配进去；负向断言避免吃掉更长的十六进制
        pat = re.escape(col) + r'(?![0-9a-fA-F])'
        def repl(m):
            nonlocal cnt
            # 位于渐变的色标里且属于排除集合 → 不换
            seg_start = v.rfind('gradient(', 0, m.start())
            seg_end = v.find(')', m.start())
            in_grad = seg_start >= 0 and (seg_end < 0 or seg_start < m.start())
            if in_grad and col in grad_exclude:
                return m.group(0)
            cnt += 1
            return var
        v = re.sub(pat, repl, v, flags=re.I)
    return v, cnt


def check(css):
    """语法自检：返回问题列表。"""
    probs = []
    if css.count("{") != css.count("}"):
        probs.append("花括号不配平 %d/%d" % (css.count("{"), css.count("}")))
    # 注意：不能把 `--sfc:#fff` 这种**变量定义**当成错误。
    # 要抓的是「普通属性被写成了 :--x」——前面那个属性名不以 -- 开头。
    for pat, why in ((r':\s*#\s*var\(', "出现 #var( （# 没被吃掉）"),
                     (r'(?<!-)\b[a-z-]+\s*:\s*--[a-z]', "出现 属性:--xxx（缺 var()）"),
                     (r'var\(--\s*\)', "空变量名"),
                     (r'#' + r'#', "双 #")):
        if re.search(pat, css):
            probs.append(why)
    return probs


done = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "--sfc-glass" in c:
        continue
    total = [0]

    def fix_decl(m):
        prop, val = m.group(1), m.group(2)
        if not re.match(r'\s*background(-color)?\s*$', prop, re.I):
            return m.group(0)
        nv, k = fix_value(val)
        total[0] += k
        return prop + ":" + nv

    c2 = re.sub(r'([-a-zA-Z]+)\s*:\s*([^;{}]+)', fix_decl, c)
    if total[0] == 0:
        continue
    probs = check(c2)
    if probs:
        print("  !! %-30s 自检不过：%s —— 保持原样" % (f, "；".join(probs)))
        continue
    # 变量定义：亮色放最前，暗色放最后（后加载赢）
    out = LIGHT_VARS + "\n" + c2.lstrip() + "\n" + DARK_VARS
    probs2 = check(out)
    if probs2:
        print("  !! %-30s 加变量后自检不过：%s" % (f, "；".join(probs2)))
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(out)
    done += 1
    print("  ✓ %-30s 替换 %3d 处" % (f, total[0]))
print("\n  共 %d 份" % done)


def final_audit():
    """全站最终自检：非法声明必须为 0。"""
    bad = 0
    for f in sorted(os.listdir(A)):
        if not f.endswith(".css"):
            continue
        c = io.open(os.path.join(A, f), encoding="utf-8").read()
        for m in re.finditer(r'(?<!-)\b[a-z-]+\s*:\s*(#\s*var\(|--[a-z])', c):
            bad += 1
            if bad <= 5:
                print("     !! %s → %s" % (f, m.group(0)[:40]))
    print("  最终自检：非法声明 %d 处 %s" % (bad, "✅" if bad == 0 else "❌"))

if __name__ == "__main__":
    final_audit()
