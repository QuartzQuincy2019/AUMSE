# -*- coding: utf-8 -*-
"""生成 E03 的样式表：以 e01 的样式表为基底（E 系列、结构最接近）。"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SRC = os.path.join(A, "e01_recursion.css")
DST = os.path.join(A, "e03_syntactic_sugar.css")

EXTRA = """
/* =====================================================================
   E03 专属：语法糖的「脱糖」展示
   ===================================================================== */

/* 脱糖：一行糖 → 一行不加糖的等价写法 */
.sugar{margin:16px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden;background:var(--sfc)}
.sugar .ln{display:flex;align-items:stretch;border-bottom:1px solid var(--line-2)}
.sugar .ln:last-child{border-bottom:0}
.sugar .ln .t{flex:0 0 74px;padding:9px 11px;font-size:11.5px;font-weight:700;
  color:var(--fg-3);background:var(--bg-soft);
  border-right:1px solid var(--line-2);line-height:1.6}
.sugar .ln .c{flex:1;padding:9px 13px;font-family:var(--mono);font-size:13.5px;
  line-height:1.7;color:var(--fg-2);overflow-x:auto;white-space:nowrap}
.sugar .ln.s .c{color:var(--fg);font-weight:700}
.sugar .ln.d .c{color:var(--fg-2)}
.sugar .ln .c em{font-style:normal;color:var(--fg-3)}

/* 跨语言对照：同一件事的各种写法 */
.xlang{margin:16px 0;border:1px solid var(--line-2);border-radius:11px;overflow:hidden}
.xlang table{margin:0;width:100%;border-collapse:collapse}
.xlang th,.xlang td{padding:8px 12px;font-size:13px;text-align:left;
  border-bottom:1px solid var(--line-2)}
.xlang th{background:var(--bg-soft);font-weight:700}
.xlang tr:last-child td{border-bottom:0}
.xlang td.l{font-weight:700;color:var(--fg-2);white-space:nowrap}
.xlang td.c{font-family:var(--mono);font-size:12.5px}

/* 小节里的一句话结论 */
.take{margin:14px 0;padding:11px 15px;border-left:5px solid var(--s-main,#0f9d76);
  border-radius:0 9px 9px 0;background:var(--s-soft,var(--bg-soft));
  font-size:14px;line-height:1.75;color:var(--fg)}

/* 「键 → 说明」对照（§2 讲 a / a+1 / *(a+1) 各是什么） */
/* 同样是上面那个坑的第二个实例：Q02 里定义的块，E03 不能想当然直接引用。 */
.alias{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden;background:var(--sfc)}
.alias .row{display:flex;align-items:stretch;border-bottom:1px solid var(--line-2)}
.alias .row:last-child{border-bottom:0}
.alias .row .k{flex:0 0 148px;padding:10px 14px;font-family:var(--mono);
  font-size:13px;font-weight:700;color:var(--fg-2);
  background:var(--bg-soft);border-right:1px solid var(--line-2)}
.alias .row .v{padding:10px 14px;font-size:13.5px;color:var(--fg-2);line-height:1.7}
.alias .row .v code{font-size:12.5px}
@media (max-width:720px){
  .alias .row{display:block}
  .alias .row .k{flex:none;border-right:0;border-bottom:1px solid var(--line-2)}
}

/* 内存示意：一行小格子，标出 a[i][j] 与其中的值 */
/* 踩过的坑：这个块原先只在 Q02 的样式表里定义，E03 直接拿来用，
   结果它按普通 div 渲染 —— 每个格子的地址、名字、值各占一行，
   变成一竖列纯文字，完全看不出「连续 6 个 int」的意思。
   样式表按页面各自成篇，用到什么块就必须在**这一页**的样式表里定义。 */
.mem{margin:16px 0;display:flex;gap:0;flex-wrap:wrap;
  border:1px solid var(--line-2);border-radius:10px;overflow:hidden}
.mem .slot{flex:1 1 96px;padding:9px 11px;border-right:1px solid var(--line-2);
  background:var(--sfc);font-size:12.5px;line-height:1.6}
.mem .slot:last-child{border-right:0}
.mem .slot .a{font-family:var(--mono);color:var(--fg-3);font-size:11.5px}
.mem .slot .n{font-family:var(--mono);font-weight:700;color:var(--fg-2)}
@media (max-width:720px){
  .mem .slot{flex:1 1 50%;border-bottom:1px solid var(--line-2)}
}
"""


def main():
    src = io.open(SRC, encoding="utf-8").read()
    i = src.find("/* =====================================================================\n   E03 专属")
    if i > 0:
        src = src[:i].rstrip() + "\n"
    out = src.rstrip() + "\n" + EXTRA
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("  ✓ e03_syntactic_sugar.css  %d B（基底 e01 %d B）" % (len(out), len(src)))


if __name__ == "__main__":
    main()
