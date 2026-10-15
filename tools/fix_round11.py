# -*- coding: utf-8 -*-
"""第 11 轮：4 个问题。

① 暗色下表格偶数行 hover 变白看不清
   各篇样式表里有一条 `tbody tr:hover{background:#f4f8fd}`（写死的浅色）。
   暗色下它把行刷成浅蓝，而文字是浅色 → 看不见。
   这是内联在 25 份样式表里的，逐份加一条暗色覆盖即可。
   （FE 用的是 rgba(124,58,237,.05)，半透明、不影响，无需改。）

② F01 的 div.c 不支持暗色
   F01 用的是 `<div class="c">`，而样式表里只定义了
   `.cmds .c` / `.stages .c`（带父级限定）—— 所以这些 div 本来就**没有**背景样式，
   亮色下靠页面底色、暗色下就露馅。
   给 `div.c` 补一套独立样式（亮/暗两套）。

③ F / Q / E 的「返回 home」样式丢失
   实测：series-theme.css 里的 30 条 .home-fab 规则**全部**写成
   `body[data-series="M"] .home-fab` 这种带系列名的形式 —— 那是
   build_series_css.py 按 SERIES 逐系列生成的；而实色覆盖段又跳过 keep_legacy。
   结果 F / Q / E 三篇**没有任何 .home-fab 规则**命中。
   修法：在公共段（不带具体系列名）补一套 .home-fab。

④ FE 样式表里主题与页面专属规则重复
   sync_fe_theme.py 把主题**前置**进每篇 fe_*.css，而页面专属段里
   原本也有一份同样的基础设计系统 → 83 组选择器各出现两次。
   修法：同步时删掉页面专属段里「选择器已在主题段出现过」的规则。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")

# ------------------------------------------------------------------ ①
HOVER = """
/* ---------- 表格行 hover 的暗色适配 ----------
   本文件里有一条 tbody tr:hover{background:#f4f8fd}（写死的浅色）。
   暗色模式下它会把整行刷成浅蓝，而文字是浅色 —— 直接看不见。
   这里在暗色下换成深底亮字。 */
@media (prefers-color-scheme: dark){
  tbody tr:hover{background:#1e2836}
  tbody tr:hover td{color:#e6ecf4}
}
"""
n1 = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "tbody tr:hover{background:#f4f8fd}" not in c:
        continue
    if "表格行 hover 的暗色适配" in c:
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(c.rstrip() + "\n" + HOVER)
    n1 += 1
print("  ✓ ① 为 %d 份样式表补上表格 hover 的暗色" % n1)

# ------------------------------------------------------------------ ②
DIVC = """
/* ---------- 命令卡片（div.c） ----------
   F01 / F03 用 `<div class="c">` 排命令卡片，但样式表里只定义了
   `.cmds .c` 与 `.stages .c`（都带父级限定）—— 页面里的 div.c
   其实**没有**背景，亮色下靠页面底色撑着，暗色下就露馅了。
   这里给 div.c 一套独立样式（亮/暗两套）。 */
div.c{
  margin:10px 0;padding:11px 13px;
  border:1px solid var(--line-2,#ccd5e3);border-radius:10px;
  background:#fff;
}
div.c > .cn{font-weight:700;color:var(--fg,#1a1f28)}
div.c code{font-family:var(--mono,Consolas,monospace)}
@media (prefers-color-scheme: dark){
  div.c{
    background:#161d26;border-color:#374556;color:#e6ecf4;
  }
  div.c > .cn{color:#e6ecf4}
}
"""
n2 = 0
for f in ("f01_command_prompt.css", "f03_compile_and_link.css"):
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "命令卡片（div.c）" in c:
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(c.rstrip() + "\n" + DIVC)
    n2 += 1
print("  ✓ ② 为 %d 份 F 样式表补上 div.c（亮/暗两套）" % n2)

# ------------------------------------------------------------------ ③
# 在 build_series_css.py 的公共段里补一套 .home-fab
P = r"E:\QKMansion\CSX10\w\UME\tools\build_series_css.py"
t = io.open(P, encoding="utf-8").read()
if "返回 home 按钮：公共样式" not in t:
    anchor = "body[data-series]{box-sizing:border-box}"
    add = '''/* ---------- 返回 home 按钮：公共样式 ----------
   注意：下面那些 body[data-series="M"] .home-fab 是**逐系列**生成的，
   写死了系列名。F 走 keep_legacy 分支、Q/E 的实色覆盖段又被跳过，
   结果这几篇一条 .home-fab 规则都命中不到 —— 按钮成了裸链接。
   所以这里在公共段补一套（不带系列名，谁都能用）。 */
.home-fab{
  position:fixed;left:12px;bottom:12px;z-index:65;
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 15px;border-radius:999px;
  font:650 13.5px/1 var(--sans,system-ui,"Microsoft YaHei",sans-serif);
  text-decoration:none;
  background:linear-gradient(140deg,#ffffff,#eef3f9);
  border:1px solid var(--line-2,#ccd5e3);
  color:var(--fg-2,#4b5563);
  box-shadow:0 3px 12px rgba(20,40,80,.16);
  transition:transform .16s ease,box-shadow .16s ease,color .16s ease;
}
.home-fab::before{content:"\\2302";font-size:15px;line-height:1}
.home-fab:hover{transform:translateY(-2px);
  box-shadow:0 6px 18px rgba(20,40,80,.24)}
.home-fab:focus-visible{outline:3px solid #1f6feb;outline-offset:2px}
body.toc-open .home-fab{display:none}
@media (min-width:561px) and (max-width:980px){
  .home-fab{left:auto;right:12px}
}
@media (prefers-color-scheme: dark){
  .home-fab{
    background:linear-gradient(140deg,#2b313b,#1e242e);
    border-color:#3a414c;color:#dbe6f5;
    box-shadow:0 4px 16px rgba(0,0,0,.45);
  }
  .home-fab:hover{color:#9db8dc;box-shadow:0 8px 22px rgba(0,0,0,.55)}
}

body[data-series]{box-sizing:border-box}'''
    assert anchor in t
    t = t.replace(anchor, add, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  ✓ ③ series-theme.css 公共段补上 .home-fab（含暗色）")
else:
    print("  · ③ 已有公共 .home-fab")

io.open(os.path.join(T, "_r11"), "w").write("1")
