# -*- coding: utf-8 -*-
"""按 series_data.py 生成 assets/series-theme.css。

设计：一套模板，按系列替换颜色与文案。
  · T 的规则由 assets/t-theme.css 提供（我手写的那份，含两轮对比度修正），
    本文件**不再重复**，只在末尾做少量补充，以免两处定义打架。
  · M / Q / E / R 用同一套模板生成，只是配色不同。
  · F 保留原有样式（08_f03 里的蓝色皮肤），本文件只改顶部常驻条的**文字**，
    并按用户要求把顶部条统一成「吸顶」行为。

顶部常驻条（banner）：
  原来 F / T 是用 body::before 做的固定条，一直在视口顶上。
  用户要求保留这个「sticky 到视口顶部」的行为，只改文字。
  这里统一由 body[data-series]::before 生成，文案取自 SERIES[*].banner。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import SERIES, ORDER  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
OUT = os.path.join(TUT, "assets", "series-theme.css")

# 每个系列一段：变量 + 顶部条 + 侧栏 + 卡片
TPL = """
/* ============================ {SK} · {NAME} ============================
   {BANNER}
   ==================================================================== */
body[data-series="{SK}"][data-series="{SK}"]{{
  --s-bg:{c1};
  --s-bg2:{c2};
  --s-main:{c3};
  --s-main-deep:{c4};
  --s-ink:{ink};
  --s-line:color-mix(in srgb, {c3} 32%, transparent);
  --s-card:rgba(255,255,255,.82);
  --s-toc:rgba(255,255,255,.90);
  --s-soft:color-mix(in srgb, {c3} 10%, transparent);
  color:var(--s-ink);
  background-color:{c1};
  background-image:
    radial-gradient(circle at 12% 8%,  rgba(255,255,255,.90) 0, transparent 42%),
    radial-gradient(circle at 88% 4%,  {c2} 0, transparent 38%),
    radial-gradient(circle at 70% 96%, {c2} 0, transparent 46%),
    linear-gradient(135deg,
      rgba(255,255,255,.40) 0 6px,
      {c2} 6px 12px,
      rgba(255,255,255,.40) 12px 18px);
  background-size:auto, auto, auto, 18px 18px;
  background-attachment:fixed;
}}

/* 顶部常驻条：固定在视口顶端（原来就有，保留行为、换文字） */
body[data-series="{SK}"][data-series="{SK}"]::before{{
  content:"{BANNER}";
  position:fixed;top:0;left:0;right:0;z-index:80;
  padding:5px 14px;
  font:700 12px/1.5 var(--sans,system-ui,sans-serif);
  letter-spacing:.06em;
  color:#fff;background:{c3};
  box-shadow:0 1px 8px color-mix(in srgb, {c3} 42%, transparent);
}}
body[data-series="{SK}"][data-series="{SK}"] main{{padding-top:52px}}

/* 侧栏目录 */
body[data-series="{SK}"][data-series="{SK}"] #toc{{
  background:var(--s-toc);border-right:1px solid var(--s-line);
  backdrop-filter:blur(6px);
}}
body[data-series="{SK}"][data-series="{SK}"] #toc h5{{color:var(--s-main-deep)}}
body[data-series="{SK}"][data-series="{SK}"] #toc a{{color:color-mix(in srgb, {ink} 78%, transparent)}}
body[data-series="{SK}"][data-series="{SK}"] #toc a:hover{{background:var(--s-soft)}}
body[data-series="{SK}"][data-series="{SK}"] #toc a.on{{
  background:linear-gradient(90deg,
    color-mix(in srgb, {c3} 26%, transparent),
    color-mix(in srgb, {c3} 8%, transparent));
  color:var(--s-main-deep);font-weight:650;
}}

/* 正文层级 */
body[data-series="{SK}"][data-series="{SK}"] h1{{color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] h2{{border-bottom:1px solid var(--s-line);color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] h2 .n{{background:{c3};color:#fff;
  box-shadow:0 1px 4px color-mix(in srgb, {c3} 40%, transparent)}}
body[data-series="{SK}"][data-series="{SK}"] h3,
body[data-series="{SK}"][data-series="{SK}"] h4{{color:var(--s-main-deep)}}
body[data-series="{SK}"][data-series="{SK}"] .sub-title{{color:color-mix(in srgb, {ink} 62%, transparent)}}
body[data-series="{SK}"][data-series="{SK}"] a{{color:var(--s-main-deep)}}
body[data-series="{SK}"][data-series="{SK}"] a:hover{{color:{c3}}}

/* 卡片 / 代码 / 表格 */
body[data-series="{SK}"][data-series="{SK}"] main > .card,
body[data-series="{SK}"][data-series="{SK}"] main > .code-wrap,
body[data-series="{SK}"][data-series="{SK}"] main > .out-wrap,
body[data-series="{SK}"][data-series="{SK}"] main > table,
body[data-series="{SK}"][data-series="{SK}"] main > .fig,
body[data-series="{SK}"][data-series="{SK}"] main > .umc-demo,
body[data-series="{SK}"][data-series="{SK}"] main > .s-nav{{
  background:var(--s-card);border-color:var(--s-line);
  box-shadow:0 2px 10px color-mix(in srgb, {c3} 12%, transparent);
  backdrop-filter:blur(4px);
}}
body[data-series="{SK}"][data-series="{SK}"] table th{{
  background:color-mix(in srgb, {c3} 14%, #fff);
  color:{c4};border-color:var(--s-line);
}}
body[data-series="{SK}"][data-series="{SK}"] table td{{border-color:var(--s-line)}}
body[data-series="{SK}"][data-series="{SK}"] table tbody tr:nth-child(even){{
  background:color-mix(in srgb, {c3} 5%, transparent);
}}
/* 代码块与输出块：底色必须不透明，而且要压过各篇自带样式表。
   08_f03 里有 body.fseries main>.code-wrap{{background-color:#fff}}（0,2,2），
   只写 body[data-series] 是压不过的 —— 代码块会被刷成白底而文字仍是浅色，
   对比度掉到 1.2:1，等于看不见。所以这里写两遍属性提权重，再兜一个 !important。 */
body[data-series="{SK}"][data-series="{SK}"] main>.code-wrap,
body[data-series="{SK}"][data-series="{SK}"] .code-wrap{{
  background-color:#1d1530 !important;
}}
body[data-series="{SK}"][data-series="{SK}"] .code-wrap>pre{{
  background:transparent !important;color:#e8e3f5;
}}
body[data-series="{SK}"][data-series="{SK}"] .code-wrap .bar{{
  background-color:#191233 !important;
  background-image:linear-gradient(180deg,#241b3d,#191233) !important;
  border-bottom:1px solid rgba(255,255,255,.10) !important;
  color:#c3b8e0;
}}
body[data-series="{SK}"][data-series="{SK}"] .code-wrap .bar .cp{{
  background-color:#241b3d;border-color:rgba(255,255,255,.22);color:#cfc6ea;
}}
body[data-series="{SK}"][data-series="{SK}"] main>.out-wrap,
body[data-series="{SK}"][data-series="{SK}"] .out-wrap{{
  background-color:#0c2523 !important;
}}
body[data-series="{SK}"][data-series="{SK}"] .out-wrap>pre{{
  background:transparent !important;color:#c9ece6;
}}
body[data-series="{SK}"][data-series="{SK}"] .out-wrap .cap{{color:#7fc7bb}}
body[data-series="{SK}"][data-series="{SK}"] .card.key{{
  background:linear-gradient(96deg,{c2},#fff 55%,{c2});
  border-left:6px solid {c3};
}}
body[data-series="{SK}"][data-series="{SK}"] .key-mark{{color:{c3}}}
body[data-series="{SK}"][data-series="{SK}"] .card-t{{color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] .card.note>.card-t{{color:#175fd0}}
body[data-series="{SK}"][data-series="{SK}"] .card.tip>.card-t{{color:#0f6b3a}}
body[data-series="{SK}"][data-series="{SK}"] .card.warn>.card-t{{color:#a82a1c}}
body[data-series="{SK}"][data-series="{SK}"] .card.teal>.card-t{{color:#0a6666}}
body[data-series="{SK}"][data-series="{SK}"] .tag{{
  background:color-mix(in srgb, {c3} 12%, #fff);
  border-color:var(--s-line);color:{c4};
}}

/* 「返回 home」：与顶条同色系 */
body[data-series="{SK}"][data-series="{SK}"] .home-fab{{
  background:linear-gradient(140deg,#fff,{c2});
  border-color:var(--s-line);color:{c4};
  box-shadow:0 3px 12px color-mix(in srgb, {c3} 26%, transparent);
}}
body[data-series="{SK}"][data-series="{SK}"] .home-fab:hover{{
  background:linear-gradient(140deg,{c2},{c1});color:{c4};
}}

/* 文末系列内跳转 */
body[data-series="{SK}"][data-series="{SK}"] .s-nav{{
  background:linear-gradient(135deg,{c2},#fff);
}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav > .s-nav-h{{color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-cur{{background:color-mix(in srgb,{c3} 20%,transparent);color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a{{
  background:#fff;border-color:var(--s-line);color:{c4};
}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a:hover{{
  background:{c2};border-color:{c3};
}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a .s-no{{background:{c3};color:#fff}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a[aria-current="page"]{{
  background:linear-gradient(96deg,{c2},{c1});border-color:{c3};
}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-cur{{background:color-mix(in srgb,{c3} 20%,transparent);color:{c4}}}
body[data-series="{SK}"][data-series="{SK}"] .s-nav-toc a{{color:var(--s-main-deep)}}

/* 暗色 */
@media (prefers-color-scheme: dark){{
  body[data-series="{SK}"][data-series="{SK}"]{{
    --s-bg:{d1};
    --s-ink:{dink};
    --s-line:color-mix(in srgb, {d3} 30%, transparent);
    --s-card:rgba(30,34,42,.74);
    --s-toc:rgba(18,21,26,.90);
    --s-soft:color-mix(in srgb, {d3} 14%, transparent);
    background-color:{d1};
    background-image:
      radial-gradient(circle at 12% 8%,  color-mix(in srgb,{d3} 10%,transparent) 0, transparent 44%),
      radial-gradient(circle at 88% 4%,  color-mix(in srgb,{d3} 8%,transparent) 0, transparent 40%),
      radial-gradient(circle at 70% 96%, color-mix(in srgb,{d4} 8%,transparent) 0, transparent 48%),
      linear-gradient(135deg,
        color-mix(in srgb,{d3} 4%,transparent) 0 6px,
        transparent 6px 12px,
        color-mix(in srgb,{d3} 4%,transparent) 12px 18px);
    background-size:auto, auto, auto, 18px 18px;
    color:{dink};
  }}
  body[data-series="{SK}"][data-series="{SK}"]::before{{
    color:{d1};background:{d3};
  }}
  body[data-series="{SK}"][data-series="{SK}"] main > .card,
  body[data-series="{SK}"][data-series="{SK}"] main > .code-wrap,
  body[data-series="{SK}"][data-series="{SK}"] main > .out-wrap,
  body[data-series="{SK}"][data-series="{SK}"] main > table,
  body[data-series="{SK}"][data-series="{SK}"] main > .fig,
  body[data-series="{SK}"][data-series="{SK}"] main > .umc-demo,
  body[data-series="{SK}"][data-series="{SK}"] main > .s-nav{{background:var(--s-card)}}
  body[data-series="{SK}"][data-series="{SK}"] h1{{color:{d4}}}
  body[data-series="{SK}"][data-series="{SK}"] h2{{color:{dink};border-bottom-color:var(--s-line)}}
  body[data-series="{SK}"][data-series="{SK}"] h3,
  body[data-series="{SK}"][data-series="{SK}"] h4{{color:{d4}}}
  body[data-series="{SK}"][data-series="{SK}"] h2 .n{{background:{d3};color:{d1}}}
  body[data-series="{SK}"][data-series="{SK}"] .sub-title{{
    color:color-mix(in srgb,{dink} 66%,transparent)}}
  body[data-series="{SK}"][data-series="{SK}"] a{{color:{d4}}}
  body[data-series="{SK}"][data-series="{SK}"] a:hover{{color:{d3}}}
  body[data-series="{SK}"][data-series="{SK}"] #toc a{{color:color-mix(in srgb,{dink} 78%,transparent)}}
  body[data-series="{SK}"][data-series="{SK}"] #toc a.on{{
    background:linear-gradient(90deg,
      color-mix(in srgb,{d3} 24%,transparent),
      color-mix(in srgb,{d3} 8%,transparent));
    color:{d4};
  }}
  body[data-series="{SK}"][data-series="{SK}"] table th{{
    background:color-mix(in srgb,{d3} 16%,#1b1e25);color:{dink};
    border-color:var(--s-line);
  }}
  body[data-series="{SK}"][data-series="{SK}"] table tbody tr:nth-child(even){{
    background:color-mix(in srgb,{d3} 6%,transparent)}}
  body[data-series="{SK}"][data-series="{SK}"] .card.key{{
    background:linear-gradient(96deg,#252a33,#2b313b 55%,#1f242c);
    border-left-color:{d3};
  }}
  /* 卡片的底色：原来只改了 --blue-soft 这类变量，但 .card.note 等
     用的是 var(--blue-soft) —— 系列主题里根本没定义这些变量，
     于是暗色下仍是 tutorial.css 里的亮色 → 浅底浅字，看不见。
     这里直接写卡片底色（不靠变量传递）。 */
  body[data-series="{SK}"][data-series="{SK}"] .card.note{{background-color:#16243a}}
  body[data-series="{SK}"][data-series="{SK}"] .card.tip{{background-color:#13291f}}
  body[data-series="{SK}"][data-series="{SK}"] .card.warn{{background-color:#2e1a18}}
  body[data-series="{SK}"][data-series="{SK}"] .card.key{{background-color:#221b36}}
  body[data-series="{SK}"][data-series="{SK}"] .card.teal{{background-color:#122a2a}}
  body[data-series="{SK}"][data-series="{SK}"] .card{{background-color:#1b1e25;
    border-color:var(--s-line,#3a414c)}}
  body[data-series="{SK}"][data-series="{SK}"] .key-mark{{color:{d3}}}
  /* 卡片标题：原来继承卡片自带的品牌色（蓝/绿/红/紫），暗底上太暗 */
  body[data-series="{SK}"][data-series="{SK}"] .card-t{{color:#7cb0ff}}
  body[data-series="{SK}"][data-series="{SK}"] .card.note>.card-t{{color:#7cb0ff}}
  body[data-series="{SK}"][data-series="{SK}"] .card.tip>.card-t{{color:#5fd0a0}}
  body[data-series="{SK}"][data-series="{SK}"] .card.warn>.card-t{{color:#ff9a92}}
  body[data-series="{SK}"][data-series="{SK}"] .card.key>.card-t{{color:{d4}}}
  body[data-series="{SK}"][data-series="{SK}"] .card.teal>.card-t{{color:#5fd0d0}}
  body[data-series="{SK}"][data-series="{SK}"] .tag{{
    background:color-mix(in srgb,{d3} 16%,#1b1e25);
    border-color:var(--s-line);color:{dink};
  }}
  body[data-series="{SK}"][data-series="{SK}"] .home-fab{{
    background:linear-gradient(140deg,{d3},{d4});color:{d1};
    border-color:var(--s-line);
  }}
  body[data-series="{SK}"][data-series="{SK}"] .home-fab:hover{{
    background:linear-gradient(140deg,{d4},{d3});color:{d1};
  }}
  body[data-series="{SK}"][data-series="{SK}"] .s-nav{{
    background:linear-gradient(135deg,#22262e,#1b1e25)}}
  body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a{{
    background:color-mix(in srgb,{d3} 10%,#1b1e25);
    border-color:var(--s-line);color:{dink};
  }}
  body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a:hover{{
    background:color-mix(in srgb,{d3} 20%,#1b1e25);border-color:{d3};
  }}
  body[data-series="{SK}"][data-series="{SK}"] .s-nav-grid a[aria-current="page"]{{
    background:linear-gradient(96deg,color-mix(in srgb,{d3} 20%,#1b1e25),
      color-mix(in srgb,{d3} 10%,#1b1e25));
  }}
  body[data-series="{SK}"][data-series="{SK}"] .s-nav-toc a{{color:{d4}}}
  body[data-series="{SK}"][data-series="{SK}"] .series-nav{{
    background:var(--s-card);border-color:var(--s-line);}}
  body[data-series="{SK}"][data-series="{SK}"] .series-nav b{{color:{dink}}}
  body[data-series="{SK}"][data-series="{SK}"] .series-nav a{{
    background:color-mix(in srgb,{d3} 10%,#1b1e25);
    border-color:var(--s-line);color:{dink};}}
  body[data-series="{SK}"][data-series="{SK}"] .series-nav a.cur{{
    background:linear-gradient(140deg,{d3},{d4});color:{d1};}}
}}

/* 高对比度：渐变文字会被系统改成纯色，反而看不清，直接退回实色 */
@media (forced-colors: active){{
  body[data-series="{SK}"][data-series="{SK}"] h1{{
    -webkit-text-fill-color:currentColor;color:CanvasText;background:none}}
  body[data-series="{SK}"][data-series="{SK}"]::before{{color:CanvasText;background:Canvas}}
}}
"""

HEAD = """/* =====================================================================
   series-theme.css —— 并列系列（M / Q / E / R）的统一主题
   ---------------------------------------------------------------------
   **本文件由 tools/build_series_css.py 生成，请勿手改。**
   要改配色或顶部条文案，改 tools/series_data.py 里的 SERIES，然后重跑：

       python tools/build_series_css.py

   说明：
     · T 的完整规则在 assets/t-theme.css（手写，含两轮对比度修正），
       本文件不为 T 重复生成，只在末尾补一条覆盖，免得两处打架。
     · F 保留原来的蓝色皮肤（用户要求），本文件只把顶部常驻条的文字统一。
     · 顶部常驻条用 body[data-series]::before 实现，position:fixed，
       即「一直吸在视口顶部」——这是原 F / T 就有的行为，按要求保留。
     · 颜色用 color-mix() 从主色派生，所以每个系列只填 4 个色值即可，
       明暗两套完整配色自动出来。
   ===================================================================== */

/* 顶部常驻条的文字由 series_data.py 的 banner 决定，见下方各系列段落 */

/* ---------- 两条必须保留的「坑规避」 ----------
   ① 抽屉打开时藏起「返回 home」按钮
      窄屏抽屉宽 min(86vw,300px)，按钮固定在左下角、z-index 又高于抽屉，
      会把抽屉底部的目录项压住，点不动。
   ② 遮罩层不接收指针事件
      body.toc-open::after 是抽屉打开时的变暗遮罩，它曾经把抽屉里的点击
      全吃掉：实测 elementFromPoint 返回 body.toc-open，连目录项都点不动
      （而 JS 直接 .click() 却正常 —— 说明纯粹是指针层被挡）。
      遮罩只负责变暗，关闭逻辑由脚本按坐标判断。
   这两条以前是以「注入到每篇 head 的 <style>」形式存在的，
   现在统一在这里，各篇不再内嵌。 */
body.toc-open .home-fab{display:none}
body.toc-open::after{pointer-events:none}
@media (min-width:561px) and (max-width:980px){
  .home-fab{left:auto;right:12px}
}

/* 公共部分：不带具体系列，T 篇也要用（T 的主题是手写的 t-theme.css，
   但它同样需要下面这些与系列无关的规则）。 */
/* ---------- 返回 home 按钮：公共样式 ----------
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
.home-fab::before{content:"⌂";font-size:15px;line-height:1}
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

body[data-series]{box-sizing:border-box}
body[data-series] .s-nav{margin:26px 0 8px;padding:14px 16px;
  border:1px solid var(--s-line,#ccd5e3);border-radius:14px}
body[data-series] .s-nav>.s-nav-h{display:flex;align-items:center;gap:8px;
  flex-wrap:wrap;font:700 12.5px/1.4 var(--sans,system-ui,sans-serif);
  letter-spacing:.06em;margin:0 0 10px}
body[data-series] .s-nav>.s-nav-h::before{content:"\\25C6";font-size:10px}
body[data-series] .s-nav-grid{display:flex;flex-wrap:wrap;gap:9px}
body[data-series] .s-nav-grid a{flex:1 1 190px;min-width:0;
  display:flex;align-items:center;gap:9px;padding:9px 12px;border-radius:10px;
  text-decoration:none;border:1px solid var(--s-line,#ccd5e3);
  font:600 13px/1.45 var(--sans,system-ui,sans-serif);
  transition:transform .14s ease,background .14s ease,border-color .14s ease}
body[data-series] .s-nav-grid a:hover{transform:translateY(-1px)}
body[data-series] .s-nav-grid a .s-no{flex:0 0 auto;padding:2px 8px;
  border-radius:6px;font:700 11px/1.6 var(--mono,Consolas,monospace)}
body[data-series] .s-nav-grid a .s-tt{flex:1 1 auto;min-width:0;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
body[data-series] .s-nav-grid a[aria-current="page"]{cursor:default}
body[data-series] .s-nav-grid a[aria-current="page"] .s-tt{font-weight:750}
body[data-series] .s-nav-cur{margin-left:6px;padding:1px 7px;border-radius:5px;
  font:600 10.5px/1.7 var(--sans,system-ui,sans-serif)}
body[data-series] .s-nav-toc{margin:12px 0 0;padding:10px 12px;
  border-top:1px dashed var(--s-line,#ccd5e3)}
body[data-series] .s-nav-toc .s-nav-h{margin-bottom:7px}
body[data-series] .s-nav-toc ol{margin:0;padding-left:22px;columns:2;column-gap:22px}
body[data-series] .s-nav-toc li{margin:0 0 3px;
  font:500 12.5px/1.6 var(--sans,system-ui,sans-serif)}
body[data-series] .s-nav-toc a{text-decoration:none}
body[data-series] .s-nav-toc a:hover{text-decoration:underline}
body[data-series] .s-nav-toc a:hover{text-decoration:underline}
@media (max-width:620px){body[data-series] .s-nav-toc ol{columns:1}}

/* ---------- 页尾「其它系列」跳转 ----------
   这一行的样式原来内联写在 series-common.js 里，零散且与旁边的
   胶囊按钮不一致，看起来像「样式丢了」。现在统一在这里定义。 */
body[data-series] .s-nav-switch{
  margin-top:14px;padding-top:12px;
  border-top:1px dashed var(--s-line,#ccd5e3);
  font:500 12.5px/2 var(--sans,system-ui,sans-serif);
}
body[data-series] .s-nav-switch>b{
  color:var(--s-fg2,#4b5563);font-weight:700;margin-right:2px;
}
body[data-series] .s-nav-switch a{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;background:#fff;
  border:1px solid var(--s-line,#ccd5e3);
  color:var(--s-fg2,#4b5563);text-decoration:none;
  transition:border-color .14s,color .14s,background .14s;
}
body[data-series] .s-nav-switch a:hover{
  border-color:var(--s-main,#1f6feb);color:var(--s-main,#1f6feb);
  background:var(--s-soft,rgba(31,111,235,.10));
}
body[data-series] .s-nav-switch .ss-empty{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;opacity:.62;
  border:1px dashed var(--s-line,#ccd5e3);
}
/* 当前所在的系列：实心标出，一眼看出「我在哪儿」 */
body[data-series] .s-nav-switch .ss-cur{
  display:inline-block;margin:3px 7px 3px 0;padding:2px 11px;
  border-radius:999px;font-weight:700;
  background:var(--s-main,#1f6feb);border:1px solid var(--s-main,#1f6feb);
  color:#fff;
}
@media (max-width:560px){
  body[data-series] .s-nav-switch{font-size:12px}
  body[data-series] .s-nav-switch a,
  body[data-series] .s-nav-switch .ss-empty{
    margin:2px 5px 2px 0;padding:1px 9px}
}
@media (prefers-color-scheme: dark){
  body[data-series] .s-nav-switch>b{color:#cdbf9a}
  body[data-series] .s-nav-switch a{
    background:#22262e;border-color:var(--s-line,#3a414c);color:#d6dde8;
  }
  body[data-series] .s-nav-switch a:hover{
    background:#2b313b;border-color:var(--s-main,#5aa2f0);color:#eef2f8;
  }
  body[data-series] .s-nav-switch .ss-empty{border-color:#3a414c;color:#95a0b0}
  /* 「当前系列」标记：暗色下必须是**亮字压深底**。
     原来沿用亮色的做法（深字 #0d1420 压主题色底），
     而暗色的主题色是中深色（M=#2c4a7c、E=#8b3fbe），
     深字压上去实测只有 2.2~2.4:1 —— 读不出来。
     兜底色也一并加深（FE 页没有 data-series 实色，走兜底）。 */
  body[data-series] .s-nav-switch .ss-cur{
    background:color-mix(in srgb,var(--s-main,#5aa2f0) 78%,#000);
    border-color:color-mix(in srgb,var(--s-main,#5aa2f0) 78%,#000);
    color:#f2f6ff;
  }
}
"""



# =====================================================================
#  实色覆盖表
#  每个系列一组：亮色(链接/副标题/当前项底/当前项字/表头底/表头字)
#                暗色(同上)
#  根据：color-mix 派生的半透明文字在深底上对比度只有 1.09:1。
# =====================================================================
FIXED = {
    "M": ("#14539f", "#4a5b70", "#1f6feb", "#ffffff", "#dbe8f8", "#12447f",
          "#8cc0ff", "#9fb0c6", "#5aa2f0", "#0d1420", "#22304a", "#cfe0f5"),
    "Q": ("#0a7157", "#40584f", "#0f9d76", "#ffffff", "#d6efe6", "#075c46",
          "#7adfc4", "#9db8ae", "#3fc4a0", "#0a1614", "#1c3b33", "#c9ece1"),
    "E": ("#67289a", "#554067", "#8b3fbe", "#ffffff", "#eddcf6", "#541f80",
          "#d6a6f2", "#b9a6c8", "#b877e0", "#150d1c", "#33203f", "#ead9f5"),
    "F": ("#0f6b3a", "#46584f", "#17864a", "#ffffff", "#d9efe2", "#0b5730",
          "#7fd8a8", "#a2bbaa", "#4fc98d", "#0f1a14", "#24402f", "#d6f0e2"),
    "R": ("#a02b40", "#6b4550", "#d1435b", "#ffffff", "#f7dde0", "#8a2338",
          "#f7a8b6", "#c9a6ad", "#ef7288", "#1a0e11", "#3d2229", "#f5dae0"),
}


def _solid_block():
    """逐系列生成实色覆盖。返回一段 CSS 文本。"""
    chunks = []
    for sk in ORDER:
        s = SERIES[sk]
        if sk == "T" or sk not in FIXED:
            continue                      # T 用手写的 t-theme.css
        if s.get("keep_legacy"):
            # F 保留原有样式：它自己那套（f03_compile_and_link.css）已经把
            # 链接、表头、卡片标题都配好了。这里再盖一层实色反而会打架
            # ——试过，暗色对比度从 9 个失败涨到 16 个。跳过。
            continue
        (link, sub, curbg, curfg, thbg, thfg,
         dlink, dsub, dcurbg, dcurfg, dthbg, dthfg) = FIXED[sk]
        q = 'body[data-series="%s"][data-series="%s"]' % (sk, sk)
        chunks.append(f"""
/* ---------------- {sk} 系列：实色覆盖（替掉 color-mix 派生色） ---------------- */
{q} a{{color:{link}}}
{q} a:hover{{color:{s['c3']}}}
{q} .sub-title{{color:{sub}}}
{q} #toc a{{color:{sub}}}
{q} table th{{background:{thbg};color:{thfg};border-color:{s['c3']}}}
{q} .series-nav a.cur{{background:{curbg} !important;color:{curfg} !important;
  border-color:{curbg} !important}}
{q} .series-nav b{{color:{sub}}}
{q} .series-nav a{{color:{link}}}
{q} .s-nav-h{{color:{link}}}
{q} .s-nav-grid a{{color:{link}}}
{q} .s-nav-toc a{{color:{link}}}
{q} .home-fab{{background-color:{s['c2']};
  background-image:linear-gradient(140deg,#fff,{s['c2']}) !important;
  color:{link} !important}}
{q}::before{{background-color:{s['c3']} !important;background-image:none;
  color:#fff !important}}

@media (prefers-color-scheme: dark){{
  {q} a{{color:{dlink}}}
  {q} a:hover{{color:{s['d3']}}}
  {q} .sub-title{{color:{dsub}}}
  {q} #toc a{{color:{dsub}}}
  {q} table th{{background:{dthbg};color:{dthfg};border-color:{s['d3']}}}
  {q} .series-nav a.cur{{background:{dcurbg} !important;color:{dcurfg} !important;
    border-color:{dcurbg} !important}}
  {q} .series-nav b{{color:{dsub}}}
  {q} .series-nav a{{color:{dsub}}}
  {q} .s-nav-h{{color:{dlink}}}
  /* 特异度补齐：亮色写的是 `body[data-series] .s-nav>.s-nav-h`（0,3,0），
     上面这条只有 (0,2,0)，会被亮色压住 —— 实测暗色下标题对比度仅 1.33。
     这里补一条带 `.s-nav>` 的（0,4,0），稳赢。 */
  {q} .s-nav>.s-nav-h{{color:{dlink}}}
  {q} .s-nav-cur{{background:color-mix(in srgb,{s['d3']} 30%,transparent);
    color:{dlink}}}
  {q} .s-nav-grid a{{color:{dsub}}}
  {q} .s-nav-toc a{{color:{dlink}}}
  {q} .home-fab{{background-color:{s['d3']};
    background-image:linear-gradient(140deg,{s['d4']},{s['d3']}) !important;
    color:{s['d1']} !important}}
  {q} .home-fab:hover{{background-color:{s['d4']} !important;
    color:{s['d1']} !important}}
  {q}::before{{background-color:{s['d3']} !important;color:{s['d1']} !important}}
}}
""")
    return "".join(chunks)


SOLID = _solid_block()



# =====================================================================
#  .key-h（重点小节标题）的暗色 + .plain-pre
#  这两个都不随系列变色，属于「公共部分」，所以直接拼在 HEAD 之后。
#  .key-h 原来只有亮色定义（浅金渐变），暗色下跟暗底打架 ——
#  series-theme.css 里根本没有这条规则（用户反馈「不支持暗色模式」）。
# =====================================================================
EXTRA_COMMON = """
/* ---------- 重点小节标题（.key-h） ----------
   亮色：浅金渐变 + 左侧金条（沿用既有观感）
   暗色：换成深金渐变，字色提亮 —— 原来没有暗色定义，
         于是浅金块直接压在暗底上，又刺眼又读不清。 */
h2.key-h,h3.key-h,h4.key-h{
  background:linear-gradient(96deg,#fffdf5 0%,#fdf3dc 58%,#fbe9c4 100%);
  border:1px solid #e8c877;border-left:6px solid #c8901a;
}
.key-hint{
  background:#eef2f8;border:1px solid #ccd5e3;color:#6b7684;
}
@media (prefers-color-scheme: dark){
  h2.key-h,h3.key-h,h4.key-h{
    background:linear-gradient(96deg,#2b2210 0%,#332813 58%,#241d0c 100%);
    border-color:#6b5518;border-left-color:#e0b23f;
    color:#f4e3b4;
  }
  h2.key-h .n,h3.key-h .n,h4.key-h .n{color:#241a03}
  .key-hint{
    background:#2b313b;border-color:#3a414c;color:#b9c4d2;
  }
}

/* ---------- 纯文本 <pre>（.plain-pre） ----------
   F03 第 8 节原本给 <pre> 写了内联样式 background:#f2f4f8，
   内联优先级最高，暗色下就是一块白。改成类名后由这里统一控制。 */
.plain-pre{
  background:#f2f4f8;border:1px solid var(--line,#e3e8f0);border-radius:8px;
  padding:11px 14px;font-family:var(--mono,Consolas,monospace);
  font-size:12.5px;line-height:1.7;color:var(--fg,#1a1f28);overflow:auto;
}
@media (prefers-color-scheme: dark){
  .plain-pre{
    background:#161d26;border-color:#374556;color:#e6ecf4;
  }
}
"""

def main():
    out = [HEAD]

    for sk in ORDER:
        s = SERIES[sk]
        if sk == "T":
            # T 的主题由手写的 assets/t-theme.css 提供（含两轮对比度修正），
            # 这里不重复生成，免得同一批选择器在两个文件里打架。
            out.append('\n/* T 系列见 assets/t-theme.css（手写） */\n')
            continue
        if s.get("keep_legacy"):
            # F：保留原样式，只统一顶部条文字与吸顶行为
            out.append("""
/* ============================ F · File（保留原样式） ====================
   用户要求「为 F 保留之前的样式」——所以底色、卡片、代码块一律沿用
   f03_compile_and_link.css 里的蓝色皮肤，这里**只**改顶部常驻条的
   文字，并确认它仍然是 position:fixed（吸在视口顶部）。
   ==================================================================== */
body[data-series="F"]::before{
  content:"%s";
  position:fixed;top:0;left:0;right:0;z-index:80;
  padding:5px 14px;font:600 12px/1.5 var(--sans,system-ui,sans-serif);
  color:#fff;background:#1f6feb;letter-spacing:.02em;
  box-shadow:0 1px 6px rgba(31,111,235,.28);
}
body[data-series="F"] main{padding-top:52px}
""" % s["banner"])
            continue
        out.append(TPL.format(SK=sk, NAME=s["name"], BANNER=s["banner"],
                              **{k: v for k, v in s.items()
                                 if k in ("c1", "c2", "c3", "c4", "ink",
                                          "d1", "d2", "d3", "d4", "dink")}))

    # ---------- 收尾：用不透明实色盖掉 color-mix 派生色 ----------
    # 原来凡是用 color-mix(…, transparent) 派生出来的文字色都是**半透明**的
    # （实际算成 rgba(...,0.66) 之类），叠在深底上对比度只有 1.09:1，读不出来。
    # 而且透明底 + 渐变底让自动检查与肉眼都难判断。所以这里逐系列换成实色。
    out.append(EXTRA_COMMON)
    out.append(SOLID)
    txt = "".join(out)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(txt)
    print("  ✓ 已生成 %s（%d 字符，含实色覆盖）"
          % (os.path.basename(OUT), len(txt)))
    for sk in ORDER:
        s = SERIES[sk]
        print("      %-2s %-42s %s" % (sk, s["banner"],
                                       "保留原样式" if s.get("keep_legacy")
                                       else "生成主题"))


if __name__ == "__main__":
    main()
