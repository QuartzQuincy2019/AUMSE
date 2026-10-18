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
  /* 语言 → class。**优先用页面注入的 D.langs**（由 make_pages.py 从
     series_data.LANG_OF 派生），下面这份只是兜底 —— 万一有人单独拿这个
     js 去用、没有 __HOME__.langs，也还能显示最常用的几种。
     原来这里是唯一来源，加 Qt 时漏改，首页的 Qt 徽章就没有 class、
     样式整个丢掉（实测：首页只有 5 种语言，Qt 缺席）。 */
  var LCLS = (D && D.langs) || {};
  if (!LCLS.Qt) {   // 兜底表（仅在没拿到 D.langs 时生效）
    var FALLBACK = {
      HTML: 'lang html', CSS: 'lang css', JS: 'lang js',
      C: 'lang c', 'C++': 'lang cpp', Shell: 'lang sh',
      Python: 'lang py', Qt: 'lang qt'
    };
    for (var k in FALLBACK) if (!LCLS[k]) LCLS[k] = FALLBACK[k];
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function makeCard(c) {
    /* 系列 key → s-<key> 类。A 系列的黑金卡片靠它在样式表里命中；
       其它系列没有对应的 s-* 规则，加了也无副作用。 */
    var a = el('a', 'card' + (c.star ? ' star' : '')
      + (c.series ? ' s-' + String(c.series).toLowerCase() : ''));
    a.href = 'SharingGroup/tutorials/' + c.file;
    a.target = '_blank';
    a.rel = 'noopener';

    if (c.bg) {
      /* 只把「图」通过 --bg-img 交给 CSS；**遮罩（--card-veil）留在样式表里**。
         早期版本把遮罩也写进行内，结果样式表的 .has-bg:hover 改不动它
         —— 行内声明优先级更高，hover 一直没生效。
         另外基图用 cover 铺满，四边不留缝，遮罩两端不透明是为了
         让左侧标题压实在实底上看得清。 */
      a.style.setProperty('--bg-img', "url('" + c.bg + "')");
      a.className += ' has-bg' + (c.veil === 'mono' ? ' mono' : '')
                   + (c.fit ? ' fit-' + c.fit : '');
    }

    a.appendChild(el('span', 'no', c.num));
    /* 语言徽章：一篇可以有**多个**（FE-09 = Qt + JS 两个），
       所以遍历 c.kinds 逐个画。若某条数据只有单个 c.kind 字符串
       （旧格式），也照样画得出来。 */
    var kinds = (c.kinds && c.kinds.length)
      ? c.kinds
      : (c.kind ? [[c.kind, null]] : []);
    kinds.forEach(function (k) {
      var name = k[0], cls = k[1];
      var label = LCLS[name] || (cls ? 'lang ' + cls : null);
      if (!label) return;          // 没有对应样式就不画，别留个裸文字
      a.appendChild(el('span', label, name));
    });
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
