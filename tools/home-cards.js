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
    var a = el('a', 'card' + (c.star ? ' star' : ''));
    a.href = 'SharingGroup/tutorials/' + c.file;
    a.target = '_blank';
    a.rel = 'noopener';

    /* 可选：给某张卡片垫一张题干图（c.bg 是相对首页的图片路径）。

       叠加关系：**图在下，卡片底色在上**。
         第一层 linear-gradient —— 卡片**本来的重点底色**
           （亮色 #fffdf5→#fdf3dc / 暗色 #241d0c→#2b2210），
           **两端不透明、中间半透明**；
         第二层 url(…) —— 题干图，按高度居中铺。

       为什么渐变是「两端实、中间透」
         图用 cover 铺满（见下），四边都不留缝，所以渐变不必再去盖缝；
         两端保持不透明，是为了让**标题与说明文字所在的左侧**压在实底上、
         看得清；中间半透明，图才透出来当背景。
         渐变的颜色与卡片底色**完全一致**，所以不透明处与普通重点卡片
         毫无差别，看不出这里藏了一层遮罩。

       两层都用 background-image 而不是 background 简写，这样 CSS 里
       a.card 的 background-color 仍然生效。
       hover 由 make_pages.py 的 .has-bg 规则接管：它只改 --card-veil，
       不动 background-image —— 否则图那一层会被一起丢掉。 */
    if (c.bg) {
      var gm = window.matchMedia
        && window.matchMedia('(prefers-color-scheme: dark)').matches;
      var veil = gm
        ? 'linear-gradient(100deg,'
          + ' rgba(36,29,12,1) 0%, rgba(36,29,12,1) 16%,'
          + ' rgba(36,29,12,.62) 46%, rgba(43,34,16,.62) 54%,'
          + ' rgba(43,34,16,1) 84%, rgba(43,34,16,1) 100%)'
        : 'linear-gradient(100deg,'
          + ' rgba(255,253,245,1) 0%, rgba(255,253,245,1) 16%,'
          + ' rgba(255,253,245,.58) 46%, rgba(253,243,220,.58) 54%,'
          + ' rgba(253,243,220,1) 84%, rgba(253,243,220,1) 100%)';
      /* 把「底色遮罩」的那层渐变放进自定义属性 --card-veil。
         这样 hover 时只换这一个变量即可，**不用重写整个 background-image**
         —— 重写 background-image 会把第二层的图一起丢掉
         （第一版就是这么错的：hover 一上，图整个消失）。 */
      a.style.setProperty('--card-veil', veil);
      a.style.backgroundImage = 'var(--card-veil)' + ", url('" + c.bg + "')";
      a.style.backgroundRepeat = 'no-repeat, no-repeat';
      a.style.backgroundPosition = 'center, center';
      // 保持宽高比，按**高度**铺满（auto 100%）。
      // 图 797x666 接近正方，卡片 348x202 很扁，所以定标后图宽约 239px，
      // 左右各留约 54px。留白能接受，是因为 —— 
      //   **这张图的底色是纯白**（实测 84% 的像素是 #ffffff），
      //   而下面把卡片的 background-color 也设成 #fff，
      //   于是那条「缝」与图自身的底色同色，肉眼看不出来。
      // 这样既不改比例、也不裁切，四个塔都在画面里。
      // cover = 保持比例放大，直到**有一方铺满**，另一方超出并被裁掉。
      // 这正是「铺满高和宽」的本意 —— 不是同时铺满，而是
      // 「一方满、另一方超出也没关系」。超出的部分正好把接缝顶出去，
      // 所以四个方向都不会留边，也不需要靠底色去盖缝。
      a.style.backgroundSize = 'cover, cover';
      // 不需要再设 backgroundColor —— cover 已经把四边盖满，
      // 没有缝要补。

      a.className += ' has-bg';
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
