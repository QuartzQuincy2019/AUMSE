# -*- coding: utf-8 -*-
"""为 R01 / R02 / R03 生成样式表。

为什么不从零写
--------------
每篇教程的样式表是「一份合并后的完整样式表」（基础排版 + 本篇专属），
约 30 KB。从零写必然漏掉 .card / .code-wrap / .out-wrap / #toc 这些
基础块，页面会直接塌掉。

做法：以 q01_std_and_namespace.css 为**基底**（它与 R 同属非 T/F 系列，
基础块最全），只把「系列主色」替换成 R 的红色系，再追加 R 专属样式。

R 的配色（取自 tools/series_data.py 的 SERIES["R"]）：
    亮色  c3=#d1435b  c4=#a02b40
    暗色  d3=#ef7288  d4=#f7a8b6
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
BASE = os.path.join(A, "q01_std_and_namespace.css")

# 每篇自己的主色（同一系列里略有区别，避免三篇看着一模一样）
PAGES = {
    "r01_font_design_metrics.css": ("#d1435b", "#a02b40", "#ef7288", "#f7a8b6"),
    "r02_bubble_sort.css":         ("#c0392b", "#8e2a1f", "#e8705f", "#f5a598"),
    "r03_collation.css":           ("#b5304f", "#7d1f36", "#e06287", "#f4a0b8"),
}

EXTRA = """
/* =====================================================================
   R 系列专属：字体度量示意图
   ---------------------------------------------------------------------
   素材放在 assets/ 下的 .awebp 文件里，用 <img class="fig-img"> 直接引用。
   .awebp 不是浏览器认识的扩展名，但内容就是标准 WebP —— 靠
   Content-Type 嗅探能正常显示。**必须显式写 width/height**，
   否则加载前会把版面撑开（累积布局偏移）。
   ===================================================================== */
.fig{margin:20px 0;text-align:center}
.fig-img{max-width:100%;height:auto;border-radius:10px;
  border:1px solid var(--line-2);background:var(--sfc)}
.fig figcaption{margin-top:9px;font-size:13px;color:var(--fg-3);line-height:1.6}
.fig figcaption b{color:var(--fg-2)}

/* 八线对照表：把图上的每一条线单独拎出来讲 */
.lines{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;overflow:hidden}
.lines .row{display:flex;align-items:baseline;gap:12px;padding:9px 14px;
  border-bottom:1px solid var(--line-2)}
.lines .row:last-child{border-bottom:0}
.lines .row .sw{flex:0 0 auto;width:14px;height:14px;border-radius:3px;
  vertical-align:-2px;border:1px solid rgba(0,0,0,.12)}
.lines .row .k{flex:0 0 auto;width:172px;font-family:var(--mono);font-size:12.5px;
  color:var(--fg-2);font-weight:700}
.lines .row .v{font-size:13.5px;color:var(--fg-2);line-height:1.6}

/* 度量数值的小卡片 */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:10px;margin:16px 0}
.metrics .m{border:1px solid var(--line-2);border-radius:10px;padding:10px 13px;
  background:var(--sfc)}
/* 数字用深红而不是主色：主色 #d1435b 压在浅底上只有 3.71:1，不到 4.5 */
.metrics .m .n{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--r-deep)}
.metrics .m .l{font-size:12.5px;color:var(--fg-3);margin-top:3px}
@media (prefers-color-scheme: dark){
  /* 暗色下深红压深底同样不够，换亮红 */
  .metrics .m .n{color:var(--r-bright)}
}

/* 字重阶梯 */
.wgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));
  gap:10px;margin:16px 0}
.wgrid .w{border:1px solid var(--line-2);border-radius:10px;padding:10px 8px;
  text-align:center;background:var(--sfc)}
.wgrid .w .a{font-size:30px;line-height:1.1;color:var(--fg)}
.wgrid .w .c{font-family:var(--mono);font-size:12px;color:var(--fg-3);margin-top:5px}

/* 排序动画/表格里的小格子 */
.bars{display:flex;align-items:flex-end;gap:5px;height:132px;margin:16px 0;
  padding:10px 12px;border:1px solid var(--line-2);border-radius:10px;background:var(--sfc)}
.bars .b{flex:1;background:var(--r-main);border-radius:3px 3px 0 0;
  display:flex;align-items:flex-start;justify-content:center;
  color:#fff;font:700 11px/1.4 var(--mono);padding-top:3px;transition:height .25s}
.bars .b.on{background:var(--r-deep)}
.bars .b.done{background:var(--r-soft-strong)}

/* 比较次数统计表 */
.stat{margin:16px 0;border:1px solid var(--line-2);border-radius:11px;overflow:hidden}
.stat table{margin:0;width:100%;border-collapse:collapse}
.stat th,.stat td{padding:8px 12px;font-size:13.5px;border-bottom:1px solid var(--line-2)}
.stat th{background:var(--r-chiplight);font-weight:700;color:var(--r-deep)}
.stat tr:last-child td{border-bottom:0}
.stat td.num{font-family:var(--mono);text-align:right}
"""


def main():
    base = io.open(BASE, encoding="utf-8").read()
    # 去掉基底里 Q 专属的一段注释标题（避免误导）
    base = base.replace("本篇专属样式", "本篇专属样式")

    for fn, (c1, c2, c3, c4) in PAGES.items():
        c = base

        # 把主色变量换成 R 的（基底里 Q 用 --q-* 或直接写色值）
        # 1) 变量重命名：q- -> r-
        c = re.sub(r'--q-([\w-]+)', r'--r-\1', c)
        # 2) 把 Q 的绿色主色值映射到 R 的红色
        QCOL = {
            "#0f9d76": c1, "#0a7157": c2, "#7adfc4": c3, "#d6f2ea": c4,
            "#0d7a5c": c1, "#0b5f48": c2,
        }
        for k, v in QCOL.items():
            c = re.sub(re.escape(k), v, c, flags=re.I)

        # 3) 补上 R 自己的变量（供追加块使用）。
        #    基底 q01 用的强调色是 --violet（.card.key / 行内 .k / .tag.v），
        #    把「紫色强调」整体改成 R 的红色 —— 这样三篇一眼就是 R 系列。
        #    不动语义色（--green 提示 / --red 警告 / --blue 说明），
        #    否则「警告卡」和「强调卡」会撞色。
        vars_block = (
            "\n/* ---------- R 系列主色 ---------- */\n"
            ":root{\n"
            "  --r-main:%s;\n  --r-deep:%s;\n  --r-bright:%s;\n  --r-pale:%s;\n"
            "  --r-soft-strong:%s;\n  --r-chiplight:color-mix(in srgb, %s 12%%, #fff);\n"
            "  /* 强调色改用红：.card.key 的标题、行内 .k、.tag.v */\n"
            "  --violet:%s;\n"
            "  --violet-soft:color-mix(in srgb, %s 12%%, #fff);\n"
            "}\n" % (c1, c2, c3, c4, c3, c1, c2, c1)
        )
        c = vars_block + c + "\n" + EXTRA

        p = os.path.join(A, fn)
        io.open(p, "w", encoding="utf-8", newline="\n").write(c)
        print("  ✓ %-32s %6d 字符" % (fn, len(c)))

    # 结构自检
    print()
    bad = 0
    for fn in PAGES:
        e = io.open(os.path.join(A, fn), encoding="utf-8").read()
        depth = 0; i = 0; unc = 0
        while i < len(e):
            if e[i:i+2] == '/*':
                j = e.find('*/', i+2)
                if j < 0:
                    unc += 1; break
                i = j + 2; continue
            if e[i] == '{':
                depth += 1
            elif e[i] == '}':
                depth -= 1
            i += 1
        if depth or unc:
            bad += 1
            print("  !! %s 剩余深度 %+d 未闭合注释 %d" % (fn, depth, unc))
    print("  结构自检: %d 个文件有问题 %s" % (bad, "✅" if bad == 0 else "❌"))


if __name__ == "__main__":
    main()
