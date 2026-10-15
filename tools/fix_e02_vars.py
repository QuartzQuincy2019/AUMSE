# -*- coding: utf-8 -*-
"""给 e02 补上表面变量（它当初被跳过了）。

为什么 e02 是唯一漏网的
-----------------------
svc_vars3.py 有一道「语法自检」：花括号不配平就整体放弃、保留原文件。
e02 里那条 `max-width:980px` 的媒体查询缺一个 `}`（我刚刚在
fix_bad_comment.py / 手工补上），所以它当时**被安全跳过了** ——
于是它至今没有 --sfc / --sfc-2 这些表面变量，11 处背景仍写死 #fff。

结构修好之后，现在可以补上了。

顺带说明：之前这些 #fff **没有暴露出来**，是因为那时它们被关在
「未闭合的窄屏媒体查询」里，只在窄屏生效；结构一修好，它们就在
所有宽度下生效了 —— 所以 e02 暗色下冒出 6 处浅底（.bflow、.tools3 .c 等）。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
P = A + r"\e02_batch_and_cmd.css"

LIGHT_VARS = """/* =====================================================================
   表面变量（亮色）
   ---------------------------------------------------------------------
   本文件当初因为花括号不配平被自动检查跳过，所以一直没有这套变量，
   背景仍写死 #fff —— 暗色下就是一块白。
   （不配平的根因是一条未闭合的 `max-width:980px` 媒体查询，已修。）
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
/* 暗色：只改变量，所有引用处一起变 */
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

c = io.open(P, encoding="utf-8").read()
orig = c

# 1) 把写死的 #fff 换成变量（跳过注释与渐变色标）
def fix(m):
    prop, val = m.group(1), m.group(2)
    if not re.match(r'\s*background(-color)?\s*$', prop, re.I):
        return m.group(0)
    return prop + ":" + re.sub(r'#(?:fff|ffffff)\b', 'var(--sfc)', val)

c = re.sub(r'([-a-zA-Z]+)\s*:\s*([^;{}]+)', fix, c)
n = c.count('var(--sfc)')

# 2) 插变量：亮色在最前，暗色在最后（后加载赢）
c = LIGHT_VARS + "\n" + c.lstrip() + "\n" + DARK_VARS

# 3) 结构自检（跳过注释）
def check(s):
    depth = 0; i = 0
    while i < len(s):
        if s[i:i+2] == '/*':
            j = s.find('*/', i+2)
            if j < 0:
                return False, "未闭合注释"
            i = j + 2; continue
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth < 0:
                return False, "负深度"
        i += 1
    return depth == 0, "剩余深度 %+d" % depth

ok, why = check(c)
if not ok:
    print("  !! 自检不过（%s），保持原样" % why)
    sys.exit(1)

io.open(P, "w", encoding="utf-8", newline="\n").write(c)
print("  ✓ e02 补上表面变量：%d 处改用 var(--sfc)" % n)
print("  ✓ 结构自检: %s" % why)
