# -*- coding: utf-8 -*-
"""通用页面生成器：正文片段 → 完整教程页。

为什么要有它
------------
Q02 那一篇我写了个专用脚本，E03 又要一份几乎一样的 —— 与其复制，
不如把「外壳」抽出来：骨架、<link> 顺序、三段脚本、NAV-AUTO 锚点
全部与既有 29 篇一致，正文只写一次放在 tools/_<slug>_body.html。

三处必须守住的约定（以前踩过的坑）
  ① <link> 顺序（分层之后的统一顺序）：
       genelayout.css → <该页样式表> → series-theme.css → tg_L.css → tg_D.css
  ② 目录**从正文 h2 自动推导**，并校验 id(s1..sN) 与编号连续 ——
     Q01 当时手写目录，结果目录写「标准库地图」、正文写「::」，锚点全指错。
  ③ 开头的 <h1> 由外壳生成，正文片段**不要**自己再写一个（会重复）。

用法：
    python build_page.py --slug e03 --series E --num E03 \
        --title "语法糖" --css e03_syntactic_sugar.css \
        --subtitle "语法糖：arr[i] 与 arr[i][j] 背后的东西" \
        --tags "要求 C++|从数组下标说起" \
        --file e03-syntactic-sugar.html [--star]
"""
import argparse
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
TOOLS = os.path.dirname(os.path.abspath(__file__))

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{num} · {title}</title>
<link rel="stylesheet" href="assets/genelayout.css">
<link rel="stylesheet" href="assets/{css}">
<link rel="stylesheet" href="assets/series-theme.css">
<link rel="stylesheet" href="assets/tg_L.css">
<link rel="stylesheet" href="assets/tg_D.css">

</head>
<body class="{cls}" data-series="{series}">
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
{toc}
</nav>

<main>
<h1>{title}{star}</h1>
<p class="sub-title">UME 项目组内部教程 · {num}（{series}） · {subtitle}</p>
{tags}
"""

TAIL = """<!-- NAV-AUTO -->
<a class="home-fab" href="../../index.html" title="返回教程总目录">返回 home</a>

</div>

</div>
<!-- /NAV-AUTO -->
<footer>
UME 项目组内部教程 · @@NUM@@《@@TITLE@@》<br>
文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>
</main>
</div>

<script>
/* 目录滚动高亮 */
(function(){
  const links = [...document.querySelectorAll('#toc a')];
  const targets = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const setOn = id => links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#'+id));
  const io = new IntersectionObserver(es => {
    const vis = es.filter(e => e.isIntersecting)
                  .sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (vis[0]) setOn(vis[0].target.id);
  }, { rootMargin:'-8% 0px -72% 0px', threshold:0 });
  targets.forEach(t => io.observe(t));
})();

/* 复制按钮 */
(function(){
  document.querySelectorAll('.code-wrap').forEach(box => {
    const btn = box.querySelector('.cp');
    const pre = box.querySelector('pre');
    if (!btn || !pre) return;
    btn.addEventListener('click', async () => {
      const text = pre.textContent;
      try { await navigator.clipboard.writeText(text); }
      catch (e) {
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta);
        ta.select(); document.execCommand('copy'); ta.remove();
      }
      const old = btn.textContent;
      btn.textContent = '已复制 ✓';
      setTimeout(() => { btn.textContent = old; }, 1200);
    });
  });
})();
</script>
<script>
/* 移动端：生成「目录」按钮，点击呼出/收起侧滑目录 */
(function(){
  var toc = document.getElementById('toc');
  if (!toc) return;
  var btn = document.createElement('button');
  btn.id = 'tocToggle';
  btn.type = 'button';
  btn.setAttribute('aria-controls','toc');
  btn.textContent = '目录';
  document.body.appendChild(btn);

  function setOpen(on){
    toc.classList.toggle('open', on);
    document.body.classList.toggle('toc-open', on);
    btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    btn.textContent = on ? '收起' : '目录';
  }
  btn.addEventListener('click', function(){
    setOpen(!toc.classList.contains('open'));
  });
  toc.addEventListener('click', function(e){
    if (e.target.closest('a')) setOpen(false);
  });
  document.addEventListener('click', function(e){
    if (!toc.classList.contains('open')) return;
    if (e.target === toc || toc.contains(e.target) || e.target === btn) return;
    setOpen(false);
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') setOpen(false);
  });
  function sync(){ if (window.innerWidth > 980) setOpen(false); }
  window.addEventListener('resize', sync);
  sync();
})();
</script>
<script src="assets/series-common.js"></script>
</body>
</html>
"""

CLS = {"T": "tseries", "F": "fseries", "M": "mseries",
       "R": "rseries", "Q": "qseries", "E": "eseries"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--series", required=True)
    ap.add_argument("--num", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--css", required=True)
    ap.add_argument("--subtitle", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--file", required=True)
    ap.add_argument("--star", action="store_true")
    a = ap.parse_args()

    body = io.open(os.path.join(TOOLS, "_%s_body.html" % a.slug),
                   encoding="utf-8").read()

    # ---- 校验：正文片段不得自带 h1（外壳会生成）----
    if re.search(r'<h1[\s>]', body):
        print("  !! 正文片段里有 <h1>，外壳会再加一个 —— 请删掉")
        return
    if "<h2" not in body:
        print("  !! 正文片段里没有 <h2>，目录会空")
        return

    heads = re.findall(r'<h2[^>]*id="(s\d+)"[^>]*>(?:<span class="key-mark"[^>]*>[^<]*</span>)?<span class="n">(\d+)</span>(?:<span class="key-mark"[^>]*>[^<]*</span>)?(.*?)</h2>',
                       body, re.S)
    ids = [h[0] for h in heads]
    nos = [int(h[1]) for h in heads]
    errs = []
    if ids != ["s%d" % i for i in range(1, len(ids) + 1)]:
        errs.append("id 不是 s1..sN 连续：%s" % ids)
    if nos != list(range(1, len(ids) + 1)):
        errs.append("编号与序位不一致：%s" % nos)
    if errs:
        print("  !! 校验失败：")
        for e in errs:
            print("       " + e)
        return

    # 目录文字直接取 h2 里 <span class="n"> 之后那段。
    # 坑：别再对 heads 做一层重组 —— Q02 那次就是因为多套了一层
    # 列表推导，h 变成了字符串，h[2] 取到标题的第三个字，
    # 目录全成了「1 · 是」「2 · 铁」。
    toc = "\n".join('  <a href="#%s">%s · %s</a>'
                    % (hid, num, re.sub(r'<[^>]+>', '', title).strip())
                    for hid, num, title in heads)

    tags = ""
    if a.tags:
        parts = a.tags.split("|")
        tags = ("<p>" + " ".join(
            '<span class="tag%s">%s</span>' % (" b" if i else "", t)
            for i, t in enumerate(parts)) + "</p>\n")

    # 注意：TAIL 里全是 JavaScript 的花括号，**不能用 str.format** ——
    # 那些 { } 会被当成占位符，报 "unexpected '{' in field name"。
    # 用普通字符串替换即可（占位符写成 @@NUM@@ 这种不会与 JS 冲突的形式）。
    tail = (TAIL.replace("@@NUM@@", a.num).replace("@@TITLE@@", a.title))

    html = (HEAD.format(num=a.num, title=a.title, css=a.css,
                        subtitle=a.subtitle,
                        cls=CLS.get(a.series, a.series.lower() + "series"),
                        series=a.series, toc=toc, tags=tags,
                        star='<span class="star" title="与本项目施行密切相关">*</span>'
                             if a.star else "")
            + body.rstrip() + "\n\n" + tail)

    p = os.path.join(T, a.file)
    io.open(p, "w", encoding="utf-8", newline="").write(html)
    print("  ✓ %s  %d 节  目录 %d 条  %d B" % (a.file, len(ids), len(heads), len(html)))
    print()
    for hid, num, title in heads:
        print("     %-5s %-3s %s" % (hid, num,
                                     re.sub(r'<[^>]+>', '', title).strip()[:46]))


if __name__ == "__main__":
    main()
