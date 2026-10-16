# -*- coding: utf-8 -*-
"""按 Q01 的结构生成 R 系列页面的「通用外壳」。

为什么要有这个脚本
------------------
每篇教程的骨架（head / #toc / <main> / NAV-AUTO 锚点 / footer / 三段脚本）
必须和既有 26 篇**完全一致**，否则：
  · series-common.js 找不到 <footer> → 页尾导航插错位置
  · 窄屏「目录」按钮的脚本没挂 → 手机上打不开目录
  · 页尾落款格式不统一

手抄一遍极易漏（我第一次就漏了 <footer> 和整个脚本段）。
所以把外壳抽成函数，三篇共用一份，正文单独给。

用法：
    from build_r_shell import shell
    shell(toc_items, body_html, num="R01", title="…", foot="…")
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# 与既有 26 篇逐字一致的三段脚本 + NAV-AUTO 锚点 + footer
TAIL = """<!-- NAV-AUTO -->
<a class="home-fab" href="../../index.html" title="返回教程总目录">返回 home</a>

</div>

</div>
<!-- /NAV-AUTO -->
<footer>
{foot}
</footer>
</main>
</div>

<script>
/* 目录滚动高亮 */
(function(){{
  const links = [...document.querySelectorAll('#toc a')];
  const targets = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const setOn = id => links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#'+id));
  const io = new IntersectionObserver(es => {{
    const vis = es.filter(e => e.isIntersecting)
                  .sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (vis[0]) setOn(vis[0].target.id);
  }}, {{ rootMargin:'-8% 0px -72% 0px', threshold:0 }});
  targets.forEach(t => io.observe(t));
}})();

/* 复制按钮 */
(function(){{
  document.querySelectorAll('.code-wrap').forEach(box => {{
    const btn = box.querySelector('.cp');
    const pre = box.querySelector('pre');
    if (!btn || !pre) return;
    btn.addEventListener('click', async () => {{
      const text = pre.textContent;
      try {{ await navigator.clipboard.writeText(text); }}
      catch (e) {{
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta);
        ta.select(); document.execCommand('copy'); ta.remove();
      }}
      const old = btn.textContent;
      btn.textContent = '已复制 ✓';
      setTimeout(() => {{ btn.textContent = old; }}, 1200);
    }});
  }});
}})();
</script>
<script>
/* 移动端：生成「目录」按钮，点击呼出/收起侧滑目录 */
(function(){{
  var toc = document.getElementById('toc');
  if (!toc) return;
  var btn = document.createElement('button');
  btn.id = 'tocToggle';
  btn.type = 'button';
  btn.setAttribute('aria-controls','toc');
  btn.textContent = '目录';
  document.body.appendChild(btn);

  function setOpen(on){{
    toc.classList.toggle('open', on);
    document.body.classList.toggle('toc-open', on);
    btn.setAttribute('aria-expanded', on ? 'true' : 'false');
    btn.textContent = on ? '收起' : '目录';
  }}
  btn.addEventListener('click', function(){{
    setOpen(!toc.classList.contains('open'));
  }});
  /* 点目录里的链接后自动收起；点遮罩（#toc 之外的区域）也收起 */
  toc.addEventListener('click', function(e){{
    if (e.target.closest('a')) setOpen(false);
  }});
  document.addEventListener('click', function(e){{
    if (!toc.classList.contains('open')) return;
    if (e.target === toc || toc.contains(e.target) || e.target === btn) return;
    setOpen(false);
  }});
  document.addEventListener('keydown', function(e){{
    if (e.key === 'Escape') setOpen(false);
  }});
  /* 窄屏进入页面时默认收起，宽屏则清掉状态 */
  function sync(){{ if (window.innerWidth > 980) setOpen(false); }}
  window.addEventListener('resize', sync);
  sync();
}})();
</script>
<script src="assets/series-common.js"></script>
</body>
</html>
"""

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{num} · {title}</title>
<link rel="stylesheet" href="assets/{css}">
<link rel="stylesheet" href="assets/series-theme.css">

</head>
<body class="rseries" data-series="R">
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
{toc}
</nav>

<main id="top">
<h1>{title}</h1>
<p class="sub-title">UME 项目组内部教程 · {num}（Related） · {sub}</p>

"""


def shell(num, title, sub, css, toc_items, body, foot, out_file):
    """toc_items: [(id, 标题)]；body: 正文 HTML（含各 h2）。"""
    toc = "\n".join('  <a href="#%s">%d · %s</a>' % (i, k + 1, ti)
                    for k, (i, ti) in enumerate(toc_items))
    html = (HEAD.format(num=num, title=title, css=css, toc=toc, sub=sub)
            + body.rstrip() + "\n\n" + TAIL.format(foot=foot))
    p = os.path.join(T, out_file)
    io.open(p, "w", encoding="utf-8", newline="").write(html)
    return p, len(html)


if __name__ == "__main__":
    print("  （本文件是模块，被 build_r_pages.py 调用）")
