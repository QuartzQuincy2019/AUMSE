# -*- coding: utf-8 -*-
"""生成 Q02《C++ 的引用》。

与既有页面保持一致的三处约定
  ① <link> 顺序（分层之后的统一顺序）：
       genelayout.css → q02_references.css → series-theme.css
       → tg_L.css → tg_D.css
  ② 骨架与 26 篇一致：head / #toc / <main> / NAV-AUTO 锚点 / footer / 三段脚本
     （少了 footer 或脚本，series-common.js 就找不到插入点、窄屏目录也打不开）
  ③ 目录**从正文 h2 自动推导**，并校验 id 与编号连续 ——
     避免 Q01 那次「目录与正文错位」的坑（当时目录写 s8 标准库地图、
     正文写 s8 ::，锚点全指错）。

正文只写一次，放在本文件的 BODY 里。
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

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Q02 · C++ 的引用</title>
<link rel="stylesheet" href="assets/genelayout.css">
<link rel="stylesheet" href="assets/q02_references.css">
<link rel="stylesheet" href="assets/series-theme.css">
<link rel="stylesheet" href="assets/tg_L.css">
<link rel="stylesheet" href="assets/tg_D.css">

</head>
<body class="qseries" data-series="Q">
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
{toc}
</nav>

<main>
<h1>C++ 的引用<span class="star" title="与本项目施行密切相关">*</span></h1>
<p class="sub-title">UME 项目组内部教程 · Q02（Qt） · 引用与指针的关系</p>
<p><span class="tag">要求 C++</span> <span class="tag b">本讲：给同一份数据起第二个名字</span></p>
"""

TAIL = """<!-- NAV-AUTO -->
<a class="home-fab" href="../../index.html" title="返回教程总目录">返回 home</a>

</div>

</div>
<!-- /NAV-AUTO -->
<footer>
UME 项目组内部教程 · Q02《C++ 的引用》<br>
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

BODY = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "_q02_body.html"), encoding="utf-8").read()


def main():
    heads = re.findall(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                       BODY, re.S)
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

    # 目录文字直接取 h2 里 <span class="n"> 之后的那段标题。
    # 踩过的坑：这里原先写成
    #     for k, (i, n, h) in enumerate([(h[0], h[1], h[2]) for h in heads])
    # 内层把三元组原样重排了一遍，结果 (i,n,h) 拿到的其实是
    # (id, 编号, 标题)，但外层又用 h[2] 去取标题 —— h 已经是字符串「标题」，
    # h[2] 取的是它的**第三个字符**，于是目录全变成「1 · 是」「2 · 铁」。
    # 直接遍历三元组即可，不要再套一层。
    toc = "\n".join('  <a href="#%s">%s · %s</a>' % (hid, num, title.strip())
                    for hid, num, title in heads)
    html = (HEAD.format(toc=toc) + BODY.rstrip() + "\n\n" + TAIL)
    p = os.path.join(T, "q02-references.html")
    io.open(p, "w", encoding="utf-8", newline="").write(html)
    print("  ✓ q02-references.html  %d 节  目录 %d 条  %d B"
          % (len(ids), len(heads), len(html)))
    print()
    for hid, num, title in heads:
        print("     %-5s %-3s %s" % (hid, num,
                                     re.sub(r'<[^>]+>', '', title).strip()[:46]))


if __name__ == "__main__":
    main()
