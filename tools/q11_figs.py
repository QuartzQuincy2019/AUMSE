# -*- coding: utf-8 -*-
"""把六张 mermaid 甘特图接进 Q11 正文。

图本身由 tools/render_gantt.js 预渲染成静态 SVG（明暗两套），
页面只 <img> 引用 —— 运行时不加载 mermaid，也不需要 JS。

六张的落点
    §2 上下文切换   两张：① CPU 交给谁（轮流）  ② 切换本身的空隙
    §4 必要性       一张：单线程 vs 8 条线程（示意）
    §6 竞态         一张：读—改—写交错
    §7 临界区       一张：加锁后两段不重叠
    §8 死锁         一张：两条都停在「等」
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSS = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\q11.css"
BODY = r"E:\QKMansion\CSX10\w\UME\tools\_q11_body.html"

FIG_CSS = '''

/* =====================================================================
   甘特图（mermaid 预渲染成静态 SVG）
   ---------------------------------------------------------------------
   · 明暗两套图各一张，用 prefers-color-scheme 切换；隐藏的那张是
     display:none，不会被读屏软件读到。
   · SVG 本身没有背景，所以直接坐在卡片的 --bg-soft 上，两个主题都不打架。
   · 窄屏：容器横向滚动，图保底 560px，不压成看不清。
   ================================================================== */
.tlfig{margin:18px 0 22px;padding:12px 12px 8px;border:1px solid var(--line);
  border-radius:12px;background:var(--bg-soft);overflow-x:auto}
.tlfig img{display:block;width:100%;min-width:560px;height:auto;margin:0 auto}
.tlfig .tld{display:none}
.tlfig .tlcap{margin:8px 0 2px;font-size:12.5px;line-height:1.75;color:var(--fg-3)}
.tlfig .tlcap b{color:var(--fg-2)}
.tlfig .tlcap code{font-size:12px}

@media (prefers-color-scheme: dark){
  .tlfig .tll{display:none}
  .tlfig .tld{display:block}
}

@media (max-width:980px){
  .tlfig{padding:10px 10px 6px;border-radius:10px}
  .tlfig img{min-width:520px}
}
'''

css = io.open(CSS, encoding="utf-8").read()
if ".tlfig" not in css:
    io.open(CSS, "w", encoding="utf-8", newline="").write(css.rstrip() + FIG_CSS)
    print("  ① q11.css 已加入甘特图样式")
else:
    print("  ① 甘特图样式已存在，跳过")

t = io.open(BODY, encoding="utf-8").read()


def fig(n, alt, cap):
    return (
        '<div class="tlfig">\n'
        '  <img class="tll" src="assets/q11-tl%d-light.svg" alt="%s">\n'
        '  <img class="tld" src="assets/q11-tl%d-dark.svg" alt="%s">\n'
        '  <p class="tlcap">%s</p>\n'
        '</div>\n' % (n, alt, n, alt, cap))


F1 = fig(1, "甘特图：线程 A 在 0–4、线程 B 在 4–9、线程 A 又在 9–12 占用 CPU",
         "<b>任何时刻只有一条线程真正占着 CPU。</b>"
         "线程 A 在时间片 0–3 跑，4 起换成线程 B，9 又换回来 —— "
         "「同时」是靠这样来回换出来的，不是两条真的一起在算。")
F2 = fig(2, "甘特图：执行—切换—执行—切换—执行，橙红色是切换本身",
         "中间那两条橙红色窄块就是<b>切换本身</b>：保存现场 → 挑人 → 恢复现场。"
         "这段时间没有任何计算产出。线程开得越多，这种空隙越密，"
         "总时间反而可能更长。")
F3 = fig(3, "甘特图：单线程一整条 vs 八条线程一小段",
         "<b>示意图，不是实测。</b>同一批计算，一条线程顺着做完；"
         "切成几份交给多个核，墙钟时间大致按份数缩短。"
         "这就是第 4 节说「算得太多」才值得多线程的理由。")
F4 = fig(4, "甘特图：线程 A 读、线程 B 读、线程 A 写、线程 B 写",
         "两条线程都<b>在对方写回之前读到了 100</b>，各自加 1 得到 101，"
         "然后先后写回 101 —— <b>加了两次，值只涨了 1。</b>"
         "第二次写回把第一次覆盖掉了。")
F5 = fig(5, "甘特图：线程 B 等锁，线程 A 在临界区，之后线程 B 才进",
         "加了锁之后，两段临界区<b>完全不重叠</b>：B 在等锁的整段时间里进不来，"
         "A 退出（<code>g</code> 析构）的那一刻 B 才拿到。"
         "这就是「串行化」在时间轴上的样子。")
F6 = fig(6, "甘特图：两条线程各持有锁后互相等待，右边再无进展",
         "两条线程各拿到一把锁，然后都在等对方手里那把。"
         "<b>横条右边没有任何「继续」的块</b> —— 不是变慢，是永远不动了。"
         "死锁不报错、不崩溃，只是程序不再前进。")

INSERTS = [
    ('<h3>什么时候会切</h3>', F1, "§2 图一 · CPU 交给谁", True),
    ('<div class="card warn">\n  <div class="card-t">切换不是免费的</div>', F2,
     "§2 图二 · 切换的空隙", True),
    ('<div class="card warn">\n  <div class="card-t">多线程的代价是真实的</div>', F3,
     "§4 图 · 必要性（示意）", True),
    ('<p>8 个线程，每个把同一个计数器加 5 万次，应该得到 40 万：</p>', F4,
     "§6 图 · 竞态交错", True),
    ('<div class="out-wrap"><div class="cap">运行结果（已核对）</div><pre>lock_guard: total = 2000000</pre></div>',
     F5, "§7 图 · 临界区串行", False),
    ('<div class="out-wrap"><div class="cap">运行结果（已核对：8 线程 × 2000 次，没有卡死）</div><pre>scoped_lock : a=16000 b=16000</pre></div>',
     F6, "§8 图 · 死锁", False),
]

for anchor, f, name, before in INSERTS:
    if anchor not in t:
        print("  !! 锚点未匹配：%s" % name)
        continue
    if f in t:
        print("  = 已存在，跳过：%s" % name)
        continue
    t = t.replace(anchor, (f + "\n" + anchor) if before else (anchor + "\n\n" + f), 1)
    print("  ② 已插入 %s" % name)

io.open(BODY, "w", encoding="utf-8", newline="").write(t)
print()
print("  自检：图容器 =", t.count('<div class="tlfig">'))
