# -*- coding: utf-8 -*-
"""重建导航页（index.html / home.html）。

**篇目数据不在这个文件里** —— 唯一数据源是 tools/series_data.py。
改编号、加篇目、调系列说明，只改那一个文件，然后跑：

    python tools/apply_series.py        # 改名 / 改正文编号（新篇目才需要）
    python tools/build_series_css.py    # 重生成系列主题
    python tools/rebuild_series_nav.py  # 重生成页尾小目录
    python tools/make_pages.py          # 重生成首页

首页卡片按「系列」分组，分组顺序与标题都取自 series_data.py。
R 系列目前为空，会渲染成一个「暂空」的占位块，加篇目后自动出现。
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import (SERIES, PAGES, ORDER, FE_PAGES,  # noqa: E402
                         pages_of, LANG_OF, LANG_CLS)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(REPO, "SharingGroup", "tutorials")
ASSETS = os.path.join(TUT, "assets")
_HOME_TPL = os.path.join(REPO, "tools", "home_template.html")
_HOME_JS = os.path.join(REPO, "tools", "home-cards.js")

# 首页卡片用 (文件, 编号, 标题, 说明, 类别, 星标)
# 类别即系列 key，home-cards.js 据此上徽标颜色
META = [(p[1], p[3], p[4], p[5], p[2], bool(p[6])) for p in PAGES]
FE = [(a, b, c, d, e, f) for a, b, c, d, e, f in FE_PAGES]

# 非 FE 系列每篇的「语言标注」。
#   按系列给即可 —— 这几组的主线语言各自统一：
#     T  理论三篇：示例都是 HTML
#     F  F01/F02 是命令提示符、F03 是编译与链接 → Shell
#     M  C++（M08 讲 C 字符串，但通篇用 C++ 的 iostream 演示）
#     Q  C++
#     R  R01 只讲字体度量、R02/R03 是 C++ → 归 C++
#     E  E01/E03 是 C++，E02 是批处理 → 见下面的单篇覆盖
#   以后某篇换了主线语言，加一条 PAGE_LANG 覆盖即可。
SERIES_LANG = {"T": "HTML", "F": "Shell", "M": "C++",
               "Q": "C++", "R": "C++", "E": "C++"}
PAGE_LANG = {
    "e02.html": "Shell",
    # R01 讲的是字体度量（EM Square / x 字高 / 行高），里面一个编程语言例子
    # 都没有 —— 归到 R 系列的默认 C++ 会误导。它讲的东西是 CSS 关心的，
    # 而且教程页自己的语言徽章也是 CSS，这里必须与之一致。
    "r01.html": "CSS",
}


# ---------------------------------------------------------------- 组长留言
# 原文一字不动。日期单独一行，右对齐。
LEAD_MSG = ("回鹘蒙文输入法 (UME) 的技术难点是【利用Qt进行回鹘文字排版】，"
            "除了 Qt 之外，还涉及回鹘文字书写系统、字体文件等领域知识。"
            "后者将是项目组内部交流时最频繁使用的术语，"
            "请大家务必认真考察这方面的理论。")
LEAD_DATE = "2026年10月16日"

STYLE = """<style>
:root{
  --bg:#ffffff; --bg-soft:#f7f9fc; --line:#e3e8f0; --line-2:#ccd5e3;
  --fg:#1a1f28; --fg-2:#4b5563; --fg-3:#6b7684;
  --blue:#1f6feb; --blue-soft:#e8f1fe;
  --green:#17864a; --green-soft:#e7f6ee;
  --violet:#6b46c1; --violet-soft:#f2ecfd;
  --amber:#a4690d; --amber-soft:#fdf4e3;
  --teal:#0d7d7d; --teal-soft:#e4f5f5;
  --gold:#c8901a; --gold-line:#e8c877;
  --code-bg:#eef2f8;
  --mono:"Consolas","Cascadia Mono","Courier New",monospace;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",system-ui,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.8 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:48px 24px 80px}

header h1{font-size:29px;margin:0 0 6px}
header .sub{color:var(--fg-3);font-size:14px;margin:0 0 4px}
header .meta{color:var(--fg-3);font-size:13px;margin:0}

h2{font-size:15px;letter-spacing:.10em;text-transform:uppercase;
  color:var(--fg-3);margin:42px 0 14px;padding-bottom:8px;
  border-bottom:1px solid var(--line)}
h2 .h2note{float:right;text-transform:none;letter-spacing:0;
  font-size:12.5px;color:var(--fg-3);font-weight:400}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:14px}
a.card{display:block;padding:15px 17px 14px;border:1px solid var(--line);
  border-left:4px solid var(--line-2);border-radius:12px;background:var(--bg-soft);
  text-decoration:none;color:inherit;
  transition:transform .14s,box-shadow .14s,border-color .14s,background .14s}
a.card:hover{transform:translateY(-2px);border-color:var(--blue);
  background:#fff;box-shadow:0 6px 20px rgba(20,40,80,.10)}
a.card .no{display:inline-block;font:700 12px/1.6 var(--mono);
  color:var(--fg-2);background:#fff;border:1px solid var(--line-2);
  border-radius:6px;padding:1px 8px;margin-right:7px}
a.card .k{display:inline-block;font:600 11px/1.7 var(--sans);
  border-radius:999px;padding:0 9px;vertical-align:1px}
a.card .tt{display:block;margin:9px 0 4px;font-weight:650;font-size:15.5px}
a.card .ds{display:block;color:var(--fg-3);font-size:13px;line-height:1.65}
a.card.star{border-left-color:var(--gold);
  background:linear-gradient(96deg,#fffdf5,#fdf3dc)}
a.card.star:hover{background:linear-gradient(96deg,#fffdf5,#fbe9c4)}
/* 带题干图的卡片（.has-bg 由 home-cards.js 加上）：
   background-image 的两层写在行内，其中**遮罩那一层是 var(--card-veil)**。
   所以 hover 只需要换这个变量 —— 千万不要在这里写 background-image，
   那会把第二层的图一起覆盖掉（图会整个消失）。 */
a.card.has-bg{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,1) 16%,
  rgba(255,253,245,.58) 46%, rgba(253,243,220,.58) 54%,
  rgba(253,243,220,1) 84%, rgba(253,243,220,1) 100%)}
a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
  rgba(255,253,245,1) 0%, rgba(255,253,245,.99) 16%,
  rgba(255,253,245,.50) 46%, rgba(251,233,196,.50) 54%,
  rgba(251,233,196,.96) 84%, rgba(251,233,196,1) 100%)}
a.card .sb{display:inline-block;margin-top:8px;font:700 10.5px/1.8 var(--sans);
  letter-spacing:.04em;color:#fff;background:var(--gold);
  border-radius:999px;padding:0 9px}
.k-c{background:#e8f1fe;color:#14539f;border:1px solid #c9dcf7}
.k-cpp{background:#f2ecfd;color:#5b21b6;border:1px solid #ddd0f7}
.k-extra{background:#fdf4e3;color:#8a5a06;border:1px solid #f0dcb4}
.k-file{background:#e7f6ee;color:#0f6b3a;border:1px solid #c3e6d3}
.k-html{background:#fdeceb;color:#b74a1f;border:1px solid #f0c8c2}
.k-css{background:#e4f5f5;color:#0a6666;border:1px solid #bfe6e6}
.k-th{background:#eee9fd;color:#5b21b6;border:1px solid #d6cbf7}
.k-M{background:#e8f1fe;color:#14539f;border:1px solid #c9dcf7}
.k-Q{background:#dff2ec;color:#0a7157;border:1px solid #bde4d7}
.k-E{background:#f3e4f7;color:#67289a;border:1px solid #e0c8ee}
.k-F{background:#e7f6ee;color:#0f6b3a;border:1px solid #c3e6d3}
.k-T{background:#fdf3dc;color:#8a6008;border:1px solid #f0dcb4}
.k-R{background:#fbdfe0;color:#a02b40;border:1px solid #f2c6c9}
.k-empty{background:#f1f3f6;color:#6b7684;border:1px dashed #ccd5e3}

@@HOME_LANG_LIGHT@@

.note{margin-top:46px;padding:18px 20px;border:1px solid var(--line);
  border-radius:12px;background:var(--bg-soft)}
.note h3{margin:0 0 10px;font-size:14px}
.note table{width:100%;border-collapse:collapse;font-size:13.5px}
.note td{padding:5px 8px;border-bottom:1px solid var(--line)}
.note code{font-family:var(--mono);font-size:12.5px;background:var(--code-bg);
  border:1px solid var(--line);border-radius:4px;padding:1px 5px}
.empty-slot{padding:15px 17px;border:1px dashed var(--line-2);border-radius:12px;
  color:var(--fg-3);font-size:13.5px;background:transparent}

/* ================= 项目组长留言 =================
   要足够醒目。用「最粗的宋体」：
   SimSun 本身没有真正的粗体，所以靠三层叠出来 ——
     ① font-weight:900 请求最粗
     ② -webkit-text-stroke 描边加粗笔画
     ③ text-shadow 极小的同色阴影再补一点厚度
   text-rendering:optimizeLegibility 让笔画交接处更实。 */
.lead-msg{
  margin:22px 0 6px;padding:20px 22px 22px;
  border:2px solid #b8860b;border-left:9px solid #a8760f;border-radius:14px;
  background:linear-gradient(135deg,#fffdf3,#fdf3dc 52%,#fbe9c4);
  box-shadow:0 5px 20px rgba(168,118,15,.20),
             inset 0 1px 0 rgba(255,255,255,.9);
  position:relative;
}
.lead-msg-t{
  margin:0 0 12px;display:inline-block;
  padding:4px 14px;border-radius:999px;
  font:700 13px/1.6 var(--sans);
  letter-spacing:.10em;color:#fffdf3;
  background:linear-gradient(135deg,#c8901a,#8a6208);
  box-shadow:0 2px 7px rgba(138,98,8,.35);
}
.lead-msg-t::before{content:"📌 "}
.lead-msg-b{
  margin:0;
  font-family:SimSun,"Songti SC","Noto Serif CJK SC","Source Han Serif SC",serif;
  font-weight:900;
  font-size:clamp(17px,2.1vw,21px);
  line-height:2.0;
  letter-spacing:.02em;
  color:#2b1d02;
  -webkit-text-stroke:.55px #2b1d02;
  text-shadow:0 0 .35px #2b1d02,0 .5px 0 rgba(43,29,2,.20);
  text-rendering:optimizeLegibility;
}
@media (max-width:560px){
  .lead-msg{padding:15px 16px 17px;border-left-width:7px}
  .lead-msg-b{line-height:1.95;letter-spacing:0}
}

/* =====================================================================
   整页暗色模式
   ---------------------------------------------------------------------
   首页的样式全部建立在上面的 CSS 变量上，所以暗色只需要换变量值，
   规则一条都不用重写。

   ⚠ 曾经只给「项目组长留言」那一块写了暗色规则 ——
   结果是暗色模式下整页纯白，只有留言块变成深色，
   里面的浅色文字压在深底上（对比度 1.18），而周围全是白的，非常突兀。
   现在改成整页统一处理。
   ===================================================================== */
@media (prefers-color-scheme: dark){
  :root{
    --bg:#15171c;      --bg-soft:#1b1e25;
    --line:#2b3038;    --line-2:#3a414c;
    --fg:#e8ecf2;      --fg-2:#b6bfcc;   --fg-3:#95a0b0;
    --blue:#63a2ff;    --blue-soft:#1b2740;
    --green:#4fc98d;   --green-soft:#15291f;
    --violet:#b18cff;  --violet-soft:#241d38;
    --amber:#e0a94a;   --amber-soft:#2c2415;
    --teal:#45c4c4;    --teal-soft:#132a2a;
    --gold:#e0b23f;    --gold-line:#6b5518;
    --code-bg:#252a33;
  }
  a.card{background:var(--bg-soft)}
  a.card:hover{background:#22262e;box-shadow:0 6px 20px rgba(0,0,0,.40)}
  a.card .no{background:#22262e;border-color:var(--line-2);color:var(--fg-2)}
  a.card.star{border-left-color:var(--gold);
    background:linear-gradient(96deg,#241d0c,#2b2210)}
  a.card.star:hover{background:linear-gradient(96deg,#2b2210,#3a2d10)}
  a.card.has-bg:hover{--card-veil:linear-gradient(100deg,
    rgba(43,34,16,1) 0%, rgba(43,34,16,.99) 16%,
    rgba(43,34,16,.54) 46%, rgba(58,45,16,.54) 54%,
    rgba(58,45,16,.98) 84%, rgba(58,45,16,1) 100%)}
  .k-c,.k-M{background:#1b2740;color:#a9c8f5;border-color:#2e4265}
  .k-cpp{background:#241d38;color:#c9b0ff;border-color:#3d3160}
  .k-extra{background:#2c2415;color:#e6c078;border-color:#4a3c1c}
  .k-file,.k-F{background:#15291f;color:#7fd8a8;border-color:#25452f}
  .k-html{background:#33201c;color:#f0a48b;border-color:#57332b}
  .k-css{background:#132a2a;color:#7fd8d8;border-color:#234747}
  .k-th,.k-T{background:#2b2210;color:#f0cc72;border-color:#4a3a15}
  .k-Q{background:#12231f;color:#7adfc4;border-color:#1f4239}
  .k-E{background:#22152c;color:#d6a6f2;border-color:#3d2a4d}
  .k-R{background:#291619;color:#f7a8b6;border-color:#4a2830}
  .k-empty{background:#1b1e25;color:#95a0b0;border-color:#3a414c}
  @@HOME_LANG_DARK@@
  .note table td{border-bottom-color:var(--line)}
  .lead-msg{
    border-color:var(--gold-line);border-left-color:var(--gold);
    background:linear-gradient(135deg,#241d0c,#2b2210 52%,#1e1809);
    box-shadow:0 5px 22px rgba(0,0,0,.50);
  }
  .lead-msg-t{background:linear-gradient(135deg,#e0b23f,#a8760f);color:#241a03}
  .lead-msg-b{
    color:#f6ecd2;
    -webkit-text-stroke:.55px #f6ecd2;
    text-shadow:0 0 .35px #f6ecd2,0 .5px 0 rgba(0,0,0,.5);
  }
}

/* 留言的日期：单独一行，右对齐 */
.lead-msg-d{
  margin:14px 0 0;
  text-align:right;
  font-family:SimSun,"Songti SC","Noto Serif CJK SC",serif;
  font-weight:700;
  font-size:clamp(14px,1.7vw,16px);
  letter-spacing:.06em;
  color:#7a5a12;
  -webkit-text-stroke:.3px #7a5a12;
}

/* ================= 页尾「全部系列」跳转 =================
   这一块原来完全没有样式 —— 它只继承了 <a> 的默认外观，
   在一排胶囊按钮旁边显得像「裸链接」，用户反馈「样式丢失」。
   现在给它和「本系列」一致的胶囊样式。 */
.series-switch{
  margin-top:14px;padding-top:12px;
  border-top:1px dashed var(--line-2,#ccd5e3);
  font:500 12.5px/2 var(--sans,system-ui,sans-serif);
  color:var(--fg-3,#8b95a5);
}
.series-switch b{color:var(--fg-2,#4b5563);margin-right:2px}
.series-switch a{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;background:#fff;
  border:1px solid var(--line-2,#ccd5e3);
  color:var(--fg-2,#4b5563);text-decoration:none;
  transition:border-color .14s,color .14s,background .14s;
}
.series-switch a:hover{border-color:var(--blue,#1f6feb);color:var(--blue,#1f6feb);
  background:var(--blue-soft,#e8f1fe)}
.series-switch .ss-cur{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;font-weight:700;
  background:var(--fg-2,#4b5563);border:1px solid var(--fg-2,#4b5563);color:#fff;
}
.series-switch .ss-empty{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;opacity:.62;
  border:1px dashed var(--line-2,#ccd5e3);
}
@media (max-width:560px){
  .series-switch{font-size:12px}
  .series-switch a,.series-switch .ss-cur,.series-switch .ss-empty{
    margin:2px 5px 2px 0;padding:1px 9px}
}
</style>"""


def card(fn, num, title, desc, kind, star):
    # 首页卡片上的「语言标注」—— 配色类与教程页的 .lang 是同一套。
    # 参数 kind 现在传的是**语言**（HTML / CSS / JS / C / C++ / Shell），
    # 不再是系列 key。原先这里传的是系列 key，于是八篇 FE 全显示「FE」，
    # 浏览器里根本看不出哪篇讲 HTML、哪篇讲 CSS、哪篇讲 JS。
    lcls = {"HTML": "lang html", "CSS": "lang css", "JS": "lang js",
            "C": "lang c", "C++": "lang cpp",
            "Shell": "lang sh", "Python": "lang py"}.get(kind)
    lang_chip = ('<span class="%s">%s</span>' % (lcls, kind)) if lcls else ''
    return ('<a class="card%s" href="SharingGroup/tutorials/%s" '
            'target="_blank" rel="noopener">'
            '<span class="no">%s</span>'
            '%s'
            '<span class="tt">%s</span>'
            '<span class="ds">%s</span>%s</a>'
            % (" star" if star else "", fn, num, lang_chip, title, desc,
               '<br><span class="sb">&#9733; 重点</span>' if star else ""))


# 给某张首页卡片叠一层题干图。
# 值是**相对 index.html 的路径**（首页在仓库根，教程页在 SharingGroup/tutorials/）。
# home-cards.js 把它当成 background-image 的第二层，上面压一层
# 「半透明白 → 完全透明」的线性渐变：左侧留给文字，图推向右侧。
# 只放真正需要「一眼认出题面」的卡片；不在表里的就用普通卡片样式。
# ---------------------------------------------------------------- 语言徽章
# 首页是全内联样式（加载不到 assets/tg_L.css / tg_D.css），所以语言徽章的
# 规则要在这里再写一份。但**色值不手写** —— 由 tools/gen_home_lang_css.py
# 从 build_tg.py 的 LANG_CSS / LANG_DARK_CSS 里读出来，
# 保证首页与 38 篇教程页用的是同一套颜色。
# （这是本会话第 4 次「把散在多处的副本换成派生」。）
import gen_home_lang_css as _LANGCSS

STYLE = STYLE.replace("@@HOME_LANG_LIGHT@@", _LANGCSS.build_light())
# 暗色那几行在 @media 内部，逐行补两格缩进
STYLE = STYLE.replace(
    "@@HOME_LANG_DARK@@",
    "\n".join(("  " + l) if l.strip() else l
              for l in _LANGCSS.build_dark().split("\n")))


CARD_BG = {
    "q07.html": "SharingGroup/tutorials/assets/第04次作业第1题.png",
}


def pack(items):
    """items 里第 5 项现在是 [(显示名, class), …]。

    同时导出两个字段：
        kind   语言**显示名**用「 / 」连起来（如 "Qt / JS"）——人读、比对用
        kinds  原样的 [(名, class), …] —— home-cards.js 按它逐个画徽章
    保留 kind 是因为若干检查脚本还在按字符串比对；两者同源，不会漂。
    """
    out = []
    for a, b, c, d, e, f in items:
        specs = list(e or [])
        rec = {"file": a, "num": b, "title": c, "desc": d,
               "kind": " / ".join(n for n, _ in specs),
               "kinds": [[n, cls] for n, cls in specs],
               "star": bool(f)}
        if a in CARD_BG:
            rec["bg"] = CARD_BG[a]
        out.append(rec)
    return out


def build_html():
    """首页数据驱动 —— 数据来自 series_data.py。

    数据内联在页面里（不 fetch），所以本地双击也能看。
    同时输出一份 noscript 静态列表兜底。
    """
    groups = []
    for sk in ORDER:
        s = SERIES[sk]
        ps = pages_of(sk)
        # 第 5 个字段必须是**语言显示名**（p[2] 是系列 key，不是语言）。
        # 语言一律从 LANG_OF 取 —— 那是唯一权威来源（M01-M08→C、
        # R03/FE-09→Qt、T01-T03→不显示徽章）。原先这里自己算
        # PAGE_LANG.get(...) or SERIES_LANG.get(sk)，等于把派生逻辑抄了第二遍，
        # 结果首页与教程页会不一致（实测：M01-M08 首页显示 C++、页面显示 C）。
        items = [(p[1], p[3], p[4], p[5],
                  LANG_OF.get(p[1]) or [],
                  bool(p[6])) for p in ps]
        groups.append({"key": sk, "label": s["label"], "banner": s["banner"],
                       "desc": s["desc"], "count": len(items),
                       "items": items})
    # FE_PAGES 的第 5 项现在是**语言显示名的列表**（如 ['Qt','JS']）。
    # pack() 要的是 [(显示名, class), …]，所以在这里补上 class。
    fe_items = [(a, b, c, d, [(n, LANG_CLS[n]) for n in e], f)
                for a, b, c, d, e, f in FE_PAGES]
    # FE 的 label / banner / desc 以前是**硬写**在这里的，与
    # series_data.py 的 FE_PAGES 分成两处。现在统一从 SERIES["FE"] 取 ——
    # 生成器 gen_series_tables.py 也依赖 SERIES 里有 FE。
    _fe = SERIES["FE"]
    groups.append({"key": "FE", "label": _fe["label"],
                   "banner": _fe["banner"], "desc": _fe["desc"],
                   "count": len(fe_items), "items": fe_items})

    total = sum(g["count"] for g in groups)
    n_star = sum(1 for g in groups for it in g["items"] if it[5])

    # count 必须一起序列化 —— 漏了它，前端 group.count 就是 undefined，
    # 页面右上角会一律显示「暂空」（不管这个系列有几篇）。
    data = {"groups": [{"key": g["key"], "label": g["label"],
                        "banner": g["banner"], "desc": g["desc"],
                        "count": g["count"],
                        "cards": pack(g["items"])} for g in groups],
            "total": total, "star": n_star,
            # 语言 → class。首页卡片的 .lang 需要它；原来这张表手写在
            # home-cards.js 的 LCLS 里，加 Qt 时漏了更新，结果首页的 Qt
            # 徽章没有 class、样式整个丢掉。改成从 series_data 派生。
            # LANG_OF 的值现在是列表；展平后去重，得到「有哪些语言」
            "langs": {name: "lang " + cls
                      for v in LANG_OF.values() for name, cls in v}}
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    def plain(items):
        out = ["<ul>"]
        # noscript 兜底列表要把颜色**内联**写上去（禁用 JS 时只剩静态
        # HTML，内联最稳）。色值同样不手写 —— 由 gen_home_lang_css.py 从
        # build_tg.py 的 LANG_CSS 解析出来，连「哪些语言用深字」也一并读出。
        INLINE, DARK_INK = _LANGCSS.chip_colors()
        for a, b, c, d, e, f in items:
            s = " <b>&#9733;</b>" if f else ""
            chip = ""
            # 一篇可以有**多个**语言（FE-09 = Qt + JS），逐个画
            for _name, _cls in e:
                bg = INLINE.get(_name)
                if not bg:
                    continue
                fg = DARK_INK.get(_name, "#fff")
                # bg 有两种形态：实色字符串（绝大多数），或
                # {"image": "linear-gradient(…)"}（Qt 这类渐变底）——
                # 后者要写 background-image 而不是 background。
                if isinstance(bg, dict):
                    fill = "background-image:%s;" % bg["image"]
                else:
                    fill = "background:%s;" % bg
                chip += ('<span style="display:inline-block;font:700 11px/1.7 '
                         'Consolas,monospace;border-radius:999px;padding:0 8px;'
                         'margin-right:6px;%scolor:%s">%s</span>'
                         % (fill, fg, _name))
            out.append('<li>%s<a href="SharingGroup/tutorials/%s">%s %s</a>%s</li>'
                       % (chip, a, b, c, s))
        out.append("</ul>")
        return "".join(out)

    ns = ['<noscript><div class="note"><h3>请开启 JavaScript</h3>',
          '<p>上面的卡片列表由脚本生成。你也可以用这份静态列表进入各篇：</p>']
    for g in groups:
        ns.append("<h3>%s</h3>" % g["banner"])
        ns.append(plain(g["items"]) if g["items"]
                  else "<p>（暂空，待补）</p>")
    ns.append("</div></noscript>")
    noscript = "".join(ns)

    tpl = io.open(_HOME_TPL, encoding="utf-8").read()
    cardjs = io.open(_HOME_JS, encoding="utf-8").read()

    # 顶部系列索引（一行说明各系列是什么）
    idx = ['<div class="note"><h3>系列一览</h3><table>']
    for g in groups:
        # 介绍为空的系列就只显示名字与篇数 ——
        # 这几个系列将来会大量补充，写死的介绍很快会过时。
        desc = g["desc"]
        body = ("%s<br>" % desc) if desc else ""
        idx.append("<tr><td style='width:30%%'><b>%s</b></td>"
                   "<td>%s<span style='color:var(--fg-3);font-size:12.5px'>"
                   "共 %d 篇%s</span></td></tr>"
                   % (g["banner"], body,
                      g["count"], "，暂空" if g["count"] == 0 else ""))
    idx.append("</table></div>")
    index_html = "".join(idx)

    out = (tpl.replace("@@STYLE@@", STYLE)
              .replace("@@DATA@@", js)
              .replace("@@TOTAL@@", str(total))
              .replace("@@NSTAR@@", str(n_star))
              .replace("@@NOSCRIPT@@", noscript)
              .replace("@@SERIES_INDEX@@", index_html)
              .replace("@@LEAD_MSG@@", LEAD_MSG)
              .replace("@@LEAD_DATE@@", LEAD_DATE)
              .replace("@@CARDS_JS@@", cardjs))
    # 自检：占位符必须全部替换干净。
    # 曾经漏过 —— home-cards.js 的注释里写了 @@NSTAR@@，
    # 被内联进页面后替换成数字，反而把那段脚本弄成了意外语句。
    left = re.findall(r"@@[A-Z_]+@@", out)
    if left:
        raise SystemExit("  !! 输出里还有未替换的占位符: %s" % sorted(set(left)))
    return out


def main():
    html = build_html()
    for name in ("index.html", "home.html"):
        io.open(os.path.join(REPO, name), "w",
                encoding="utf-8", newline="").write(html)
    n_star = sum(1 for g in [pages_of(k) for k in ORDER] for p in g if p[6]) \
        + sum(1 for f in FE_PAGES if f[5])
    print("  已生成 index.html / home.html（%d 字符）" % len(html))
    print("  共 %d 篇（%s），其中星标 %d 篇"
          % (len(PAGES) + len(FE_PAGES),
             " + ".join("%s %d" % (SERIES[k]["num"], len(pages_of(k)))
                        for k in ORDER) + " + FE %d" % len(FE_PAGES),
             n_star))
    # 链接检查
    bad = []
    for p in PAGES + [(a, a, "", "", "", "", False) for a in [f[0] for f in FE_PAGES]]:
        fp = os.path.join(TUT, p[1])
        if not os.path.exists(fp):
            bad.append(p[1])
    if bad:
        print("  !! 缺文件: %s" % bad)
    else:
        print("  链接检查：全部有效")


if __name__ == "__main__":
    main()
