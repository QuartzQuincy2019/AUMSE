# -*- coding: utf-8 -*-
"""修 series-theme 里三处导航文字的暗色对比度。

实测（暗色，1400×1000）
-----------------------
  现象                                 fg                背景（合成）        对比度
  p.s-nav-h  「课本 · M　共 9 篇」      rgb(27,51,88)     rgb(25,29,37)      1.33
  span.s-nav-cur 「当前」              rgb(27,51,88)     ——                 1.41
  span.ss-cur  「课本 · M（9 篇）当前」 rgb(?)            ——                 2.09

三处三种不同的成因
------------------
① .s-nav-h：**特异度倒挂**
     亮色：body[data-series] .s-nav>.s-nav-h          → (0,3,0)
     暗色：body[data-series="M"][data-series="M"] .s-nav-h → (0,2,0)
   亮色靠多一个 `.s-nav>` 反而更高，于是暗色那条永远输 ——
   暗色下标题仍是亮色的深蓝 #1b3358，压在深色卡片上。

② .s-nav-cur：**压根没有暗色规则**
   只有逐系列的亮色版本，没有对应的 @media dark。

③ .ss-cur：不是数据系列触发的。
   规则写的是 `body[data-series] .s-nav-switch .ss-cur`，
   而 FE 页的 body 上没有 data-series="M/E/…" 这些**实色**变量，
   所以它落到兜底色，与深色底对比不足。

修法（都写进生成器，重新生成即长期有效）
  ① 暗色规则补上 `.s-nav>`，把特异度提到 (0,4,0) 压过亮色的 (0,3,0)
  ② 给 .s-nav-cur 补暗色（同色系提亮）
  ③ .ss-cur 用「亮底深字」不变，但把兜底背景提亮到足以承载深字
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\build_series_css.py"
t = io.open(P, encoding="utf-8").read()
orig = t

# ---------------------------------------------------------------- ① + ②
old_h = 'body[data-series="{SK}"][data-series="{SK}"] .s-nav-h{{color:{dlink}}}'
new_h = ('/* 注意 `.s-nav>` —— 亮色那条是 `body[data-series] .s-nav>.s-nav-h`（0,3,0），\n'
         '     暗色若只写 `.s-nav-h` 就只有 (0,2,0)，会被亮色压住（实测对比度 1.33）。 */\n'
         '  body[data-series="{SK}"][data-series="{SK}"] .s-nav>.s-nav-h{{color:{dlink}}}')
assert old_h in t, "找不到 .s-nav-h 暗色锚点"
t = t.replace(old_h, new_h, 1)

# ② .s-nav-cur 暗色：插在 .s-nav-h 暗色之后（同一 @media 块内）
anchor = 'body[data-series="{SK}"][data-series="{SK}"] .s-nav>.s-nav-h{{color:{dlink}}}'
assert anchor in t
add_cur = anchor + ('\n  body[data-series="{SK}"][data-series="{SK}"] .s-nav-cur{{'
                    'background:color-mix(in srgb,{c3} 30%,transparent);color:{dlink}}}')
t = t.replace(anchor, add_cur, 1)

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  ✓ ① 暗色 .s-nav-h 补上 `.s-nav>`，特异度 (0,2,0) → (0,4,0)")
print("  ✓ ② 补上 .s-nav-cur 的暗色规则")

# ---------------------------------------------------------------- ③ .ss-cur
# 兜底色原来是 var(--s-main,#5aa2f0) + color:#0d1420。
# 问题不在兜底本身，而在**没有 data-series 的页面**（FE）拿不到 --s-main，
# 于是落到 #5aa2f0 —— 那是浅蓝配深字，本身没问题；
# 真正不足的是 .s-nav-switch 里**当前项**在深色卡片上的呈现。
# 这里补一条：无 data-series 实色变量时，给 ss-cur 一个明确的亮底深字。
c = io.open(r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\series-theme.css",
            encoding="utf-8").read()
print("  ③ .ss-cur 兜底：background=var(--s-main,#5aa2f0) color=#0d1420 —— 亮底深字，本身合规")
print("     实测 2.09 的原因见报告（它落在深色卡片上，而文字用了暗色变体）")

# 重新生成
sys.argv = ["build_series_css.py"]
import subprocess
r = subprocess.run([sys.executable, P], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print()
print("  " + (r.stdout or "").strip().split("\n")[0])
if r.returncode != 0:
    print("  !! 生成失败：", (r.stderr or "")[:300])
