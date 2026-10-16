/* =====================================================================
   home-cards.js —— 首页卡片渲染（由 make_pages.py 内联进 index.html）
   ---------------------------------------------------------------------
   数据来自 window.__HOME__，结构：

     { total, star,
       groups: [ { key, label, banner, desc,
                   cards: [ {file,num,title,desc,kind,star} ] } ] }

   分组是**并列系列**（T / M / Q / E / F / R / FE）。加系列或加篇目
   都不用改这个文件 —— 它只按数据画。
   数据内联在页面里（不 fetch），所以本地双击也能看。
   ===================================================================== */
(function () {
  'use strict';

  var D = window.__HOME__;
  if (!D) return;

  /* 语言标注的配色类 —— 与教程页的 .lang 同一套（见 tools/build_tg.py）。
     数据里的 c.kind 现在一律是**语言**（HTML / CSS / JS / C / C++ / Shell），
     不再是系列 key。
     这里同时保留旧的系列 key 映射：万一有人还往数据里塞系列名，
     也不至于把「M」当成语言显示出来。 */
  var LCLS = {
    HTML: 'lang html', CSS: 'lang css', JS: 'lang js',
    C: 'lang c', 'C++': 'lang cpp', Shell: 'lang sh', Python: 'lang py'
  };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function makeCard(c) {
    var a = el('a', 'card' + (c.star ? ' star' : ''));
    a.href = 'SharingGroup/tutorials/' + c.file;
    a.target = '_blank';
    a.rel = 'noopener';

    /* 可选：给某张卡片叠一层题干图（c.bg 是相对首页的图片路径）。
       做法是**两层背景叠着画**：
         第一层 linear-gradient —— 从半透明白渐变到完全透明，
           压在图上，保证图不会盖住文字、也不会太抢眼；
         第二层 url(…) —— 题目本身的图，靠右居中。
       两者都用 background-image（不是 background 简写），
       这样 CSS 里 a.card 的 background-color / a.card.star 的浅金底
       仍然生效，渐变只是叠加在它们之上。
       图片再加一点透明度，让它在亮色与暗色模式下都能融进卡片。 */
    if (c.bg) {
      // 渐变要**覆盖到正文文字所在的整个左侧 3/4**（到 76% 才透明），
      // 否则说明文字会压在图上、两层内容互相干扰。
      // 图只当右下角的水印：缩到 42% 卡片高、贴右下，落进渐变已经很淡的
      // 那一角 —— 看得见题目，但抢不走文字的注意力。
      a.style.backgroundImage =
        'linear-gradient(100deg, rgba(255,255,255,.97) 0%,'
        + ' rgba(255,255,255,.80) 46%, rgba(255,255,255,.30) 68%,'
        + ' rgba(255,255,255,0) 84%),'
        + " url('" + c.bg + "')";
      a.style.backgroundRepeat = 'no-repeat, no-repeat';
      a.style.backgroundPosition = 'center, right 8px bottom 4px';
      a.style.backgroundSize = 'auto, auto 42%';
      a.className += ' has-bg';
    }

    a.appendChild(el('span', 'no', c.num));
    if (LCLS[c.kind]) {
      a.appendChild(el('span', LCLS[c.kind], c.kind));
    }
    a.appendChild(el('span', 'tt', c.title));
    a.appendChild(el('span', 'ds', c.desc));

    if (c.star) {
      a.appendChild(document.createElement('br'));
      a.appendChild(el('span', 'sb', '\u2605 与本项目施行密切相关'));
    }
    return a;
  }

  /* 收集插入点：插在页面底部的「编号怎么看」说明之前 */
  var notes = document.querySelectorAll('.note');
  var anchor = notes.length ? notes[notes.length - 1] : null;
  var parent = anchor ? anchor.parentNode : document.body;

  D.groups.forEach(function (g) {
    var h = el('h2');
    h.appendChild(document.createTextNode(g.banner));
    h.appendChild(el('span', 'h2note',
                     g.count ? '共 ' + g.count + ' 篇' : '暂空'));

    var sub = el('p', null, g.desc);
    sub.style.cssText = 'margin:-6px 0 14px;color:var(--fg-3);font-size:13.5px';

    var grid = el('div', 'grid');
    grid.id = 'grid-' + String(g.key).toLowerCase();

    if (!g.cards.length) {
      grid.appendChild(el('div', 'empty-slot',
        '本系列暂时没有篇目 —— 加篇目只需在 tools/series_data.py 里补一行，'
        + '重跑脚本即可。'));
    } else {
      g.cards.forEach(function (c) { grid.appendChild(makeCard(c)); });
    }

    if (anchor) {
      parent.insertBefore(h, anchor);
      parent.insertBefore(sub, anchor);
      parent.insertBefore(grid, anchor);
    } else {
      parent.appendChild(h);
      parent.appendChild(sub);
      parent.appendChild(grid);
    }
  });

  /* 顶部统计以实际数据为准 */
  var meta = document.querySelector('header .meta');
  if (meta) {
    meta.textContent = '共 ' + D.total + ' 篇 · 其中 ' + D.star
                     + ' 篇为重点 · 卡片列表由脚本按数据生成';
  }
})();
