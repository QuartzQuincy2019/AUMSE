/* =====================================================================
   UMCompos.js — Uyghur-Mongolian Composing
   回鹘蒙文竖式排版组件 · v1.1.0
   ---------------------------------------------------------------------
   目标：**完全独立**，可以原样拷进任何前端项目，不需要配套样式表、
   不需要宿主提供 CSS 变量、不依赖任何全局变量、路径全部可配。

   独立性保证（对照表）：
     · 不写死任何项目路径 —— 字体 URL 由 configure()/loadFont() 给
     · 不读宿主 CSS 变量 —— 自带 :root 上一套 --umc-* 变量，样式可覆盖
     · 不用任何全局名 —— 导出用 UMD，浏览器下只挂一个 UMCompos
     · 自带 @font-face 注入 —— 不要求宿主先声明字体
     · 类名统一前缀 umc- —— 不会与宿主样式撞车
     · 不依赖 DOM 结构 —— 只要求给一个容器元素
     · Node 下可 require（无 DOM 时延迟报错，不影响做纯计算）

   蒙文排版的四道坎（对应下面的实现）：
     1) 列向：writing-mode:vertical-lr + **必须显式 direction:ltr**
              （继承 rtl 会让列序反转）；text-orientation 必须是 mixed，
              蒙文整块 vo=R，设 upright 会把字形摆正、失去连写形态。
     2) 字素簇：元音与自由变体选择符 FVS1-4 是独立码位，但对排版不可分。
              按 UAX #29 GB9 切（Extend / ZWJ / ZWNJ 黏附**前**一字素）——
              注意 ZWJ 黏左边不黏右边，蒙文里它正是用来让前面的字母
              取特定字形变体。
     3) 推进量：**不能估算**。连字（ligature）会让若干簇共享一个字形，
              簇宽 ≠ 字形宽。本组件用一个 1000px 隐藏量尺，逐簇取
              Range.getBoundingClientRect().height（竖排下「行长」就是 height），
              相邻相减得到真实 advance —— 连字自动被算进所在簇。
     4) 缺字：高度会返回 0，用 Math.max(1, …) 兜底，避免除零与死循环。

   许可证：本文件为原创代码，可自由用于任何项目。
          随附的 Noto Sans Mongolian 为 SIL Open Font License 1.1。
   ===================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else if (typeof define === 'function' && define.amd) define([], factory);
  else root.UMCompos = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var VERSION = '1.1.0';
  var UPEM = 1000;            /* Noto Sans Mongolian 的 unitsPerEm */

  /* ==================================================================
     0. 配置：所有外部依赖集中在这里，默认值不指向任何项目
     ================================================================== */
  var CFG = {
    /* 字体文件路径。**故意留空** —— 由调用方 configure() 指定，
       这样插件本身不含任何项目路径。空值时跳过装载，回退到系统字体。 */
    fontURL: null,
    /* 声明 @font-face 时用的族名。可留空 —— 留空就不注入 @font-face，
       直接用 fontFamily 里列出的系统字体。 */
    fontFamily: null,
    /* 渲染字体栈。默认只列跨平台的蒙文字体，不含任何项目自造名。 */
    fontStack: "'Noto Sans Mongolian','Mongolian Baiti','Menk Hawang Tig',serif",
    /* 导出 SVG 时内嵌字体的来源：
         {woff2: "<base64>"}  内嵌 WOFF2（推荐，SVG 当 <img> 也能显示）
         {url: "xxx.ttf"}     引用外部文件
         null                 不内嵌（依赖查看器有字体）
       —— 也可以用 setEmbedProvider(fn) 动态给。 */
    embed: null,
    /* 注入样式的自定义属性。宿主可以覆盖这些 --umc-* 变量换皮，
       也可以整块关掉注入（injectCSS:false）自己写样式。 */
    injectCSS: true,
    /* 类名前缀。统一前缀避免与宿主样式撞车。 */
    prefix: 'umc'
  };

  var embedProvider = null;

  function configure(opt) {
    if (!opt) return CFG;
    for (var k in opt) if (Object.prototype.hasOwnProperty.call(opt, k)) CFG[k] = opt[k];
    return CFG;
  }
  function setEmbedProvider(fn) { embedProvider = fn; return CFG; }

  /* ==================================================================
     1. 字符属性（UCD 18.0.0 实测，只覆盖蒙文区与排版需要的控制字符）
     ================================================================== */
  var PROPS = {
    0x1800:{gc:"Po",lb:"AL"}, 0x1801:{gc:"Po",lb:"AL"},
    0x1802:{gc:"Po",lb:"EX"}, 0x1803:{gc:"Po",lb:"EX"},
    0x1804:{gc:"Po",lb:"BA"}, 0x1805:{gc:"Po",lb:"BA"},
    0x1806:{gc:"Pd",lb:"BB"}, 0x1807:{gc:"Po",lb:"AL"},
    0x1808:{gc:"Po",lb:"EX"}, 0x1809:{gc:"Po",lb:"EX"},
    0x180A:{gc:"Po",lb:"AL"},
    0x180B:{gc:"Mn",lb:"CM",ext:1,ign:1},   /* FVS1 */
    0x180C:{gc:"Mn",lb:"CM",ext:1,ign:1},   /* FVS2 */
    0x180D:{gc:"Mn",lb:"CM",ext:1,ign:1},   /* FVS3 */
    0x180F:{gc:"Mn",lb:"CM",ext:1,ign:1},   /* FVS4 */
    0x180E:{gc:"Cf",lb:"GL",ign:1},         /* MVS：分隔符，不黏附 */
    0x1885:{gc:"Mn",lb:"CM",ext:1},
    0x1886:{gc:"Mn",lb:"CM",ext:1},
    0x18A9:{gc:"Mn",lb:"CM",ext:1},
    0x200C:{gc:"Cf",lb:"CM",ext:1,ign:1},   /* ZWNJ */
    0x200D:{gc:"Cf",lb:"ZWJ",zwj:1}         /* ZWJ */
  };

  function prop(c) {
    if (PROPS[c]) return PROPS[c];
    if (c >= 0x1810 && c <= 0x1819) return { gc:"Nd", lb:"NU" };
    if (c === 0x20 || c === 0x09) return { gc:"Zs", lb:"SP" };
    if (c === 0x0A || c === 0x0D) return { gc:"Cc", lb:"LF" };
    if (c >= 0x1820 && c <= 0x18AA) return { gc:"Lo", lb:"AL" };
    if (c >= 0x11660 && c <= 0x1167F) return { gc:"Po", lb:"AL" };
    return { gc:"?", lb:"XX" };
  }

  function isMongolian(c) {
    return (c >= 0x1800 && c <= 0x18AF) || (c >= 0x11660 && c <= 0x1167F);
  }

  function cpHex(c) {
    return "U+" + c.toString(16).toUpperCase().padStart(4, "0");
  }

  /* ==================================================================
     2. 字素簇（UAX #29 GB9）
     ================================================================== */
  function graphemes(cps) {
    var out = [], cur = [];
    for (var i = 0; i < cps.length; i++) {
      var c = cps[i], p = prop(c);
      var glue = p.ext || p.zwj || c === 0x200C;
      if (cur.length && glue) { cur.push(c); continue; }
      if (cur.length) out.push(cur);
      cur = [c];
    }
    if (cur.length) out.push(cur);
    return out;
  }

  /* ==================================================================
     3. 断行机会（UAX #14 精简版 + LB9 归并）
        语义：返回值里的 i 表示「可在第 i 个码位**之前**断」
     ================================================================== */
  function breakOpps(cps) {
    var opps = new Set();
    if (!cps.length) return opps;
    var cls = cps.map(function (c) { return c === 0x200C ? "CM" : prop(c).lb; });
    for (var i = 1; i < cps.length; i++) {
      if (cls[i] === "CM" || cls[i] === "ZWJ")
        cls[i] = (cls[i - 1] === "SP" || cls[i - 1] === "BK") ? "AL" : cls[i - 1];
    }
    var afterBB = (cls[0] === "BB");
    for (var j = 1; j < cps.length; j++) {
      var a = cls[j - 1], b = cls[j], allow;
      if (afterBB) allow = false;
      else if (a === "LF") allow = true;
      else if (b === "LF") allow = false;
      else if (b === "SP") allow = false;
      else if (b === "BB") allow = true;
      else if (a === "WJ" || b === "WJ") allow = false;
      else if (a === "GL" || b === "GL") allow = false;
      else if (b === "CL" || b === "CP" || b === "EX" || b === "IS" || b === "SY") allow = false;
      else if (a === "OP") allow = false;
      else if (a === "SP") allow = true;
      else if (a === "BA" || a === "HY" || a === "NS") allow = false;
      else if (b === "OP" && (a === "AL" || a === "NU")) allow = false;
      else if (a === "CP" && (b === "AL" || b === "NU")) allow = false;
      else if (a === "CM" || b === "CM" || a === "ZWJ" || b === "ZWJ") allow = false;
      else if (a === "NU" && b === "AL" || a === "AL" && b === "NU") allow = false;
      else if (a === "IS" && b === "NU") allow = false;
      else if (a === "NU" && (b === "NU" || b === "IS" || b === "SY")) allow = false;
      else if (a === "AL" && b === "AL") allow = false;
      else allow = true;
      if (allow) opps.add(j);
      if (b === "BB") afterBB = true;
    }
    return opps;
  }

  /* ==================================================================
     4. 测量宿主（量尺）
     ================================================================== */
  var host = null, hostFont = null;

  function requireDOM() {
    if (typeof document === 'undefined')
      throw new Error('UMCompos: 这一功能需要 DOM（浏览器环境）');
  }

  function ensureHost(fontFamily) {
    requireDOM();
    var fam = fontFamily || CFG.fontStack;
    if (host && hostFont === fam) return host;
    if (host && host.parentNode) host.parentNode.removeChild(host);
    host = document.createElement('div');
    host.setAttribute('aria-hidden', 'true');
    host.setAttribute('lang', 'mn-Mong');
    host.style.cssText =
      'position:absolute;left:-99999px;top:0;visibility:hidden;' +
      'writing-mode:vertical-lr;direction:ltr;text-orientation:mixed;' +
      'font-family:' + fam + ';' +
      'font-size:1000px;line-height:1;white-space:nowrap';
    document.body.appendChild(host);
    hostFont = fam;
    return host;
  }

  /* 量一行：整行放同一个文本节点，保证整形（shaping）上下文正确 */
  function measureLine(lineText, fontFamily) {
    var h = ensureHost(fontFamily);
    h.textContent = '';
    var items = [];
    if (!lineText.length) return { items: items, total: 0 };

    var node = document.createTextNode(lineText);
    h.appendChild(node);

    var cps = Array.from(lineText).map(function (c) { return c.codePointAt(0); });
    var clusters = graphemes(cps);
    var ends = [], off = 0;
    clusters.forEach(function (g) { off += g.length; ends.push(off); });

    var rAll = document.createRange();
    rAll.selectNodeContents(h);
    var total = rAll.getBoundingClientRect().height;   /* 竖排：行长 = height */

    var prev = 0;
    for (var i = 0; i < clusters.length; i++) {
      var r = document.createRange();
      r.setStart(node, 0);
      r.setEnd(node, ends[i]);
      var p = r.getBoundingClientRect().height;
      var adv = Math.max(1, p - prev);   /* 缺字时高度为 0，兜底防死循环 */
      prev = p;
      items.push({
        text: clusters[i].map(function (c) { return String.fromCodePoint(c); }).join(''),
        cps: clusters[i],
        adv: adv,
        penStart: 0
      });
    }
    h.textContent = '';
    return { items: items, total: total };
  }

  function measureText(text, fontFamily) {
    var h = ensureHost(fontFamily);
    h.textContent = '';
    var sp = document.createElement('span');
    sp.textContent = text;
    h.appendChild(sp);
    var r = document.createRange();
    r.selectNodeContents(sp);
    var v = r.getBoundingClientRect().height / 1000 * UPEM;
    h.textContent = '';
    return v;
  }

  /* ==================================================================
     5. 排版计划
     ================================================================== */
  function layout(text, fontFamily) {
    return String(text).split('\n').map(function (ln, li) {
      var m = measureLine(ln, fontFamily);
      var pen = 0;
      m.items.forEach(function (it) { it.penStart = pen; pen += it.adv; });
      return { line: li, items: m.items, length: m.total || pen };
    });
  }

  /* ==================================================================
     6. 导出 SVG
        几何：先在「横排 local 空间」按 advance 摆 x，再
        transform="translate(tx,ty) rotate(90)" 转到竖排。
        SVG 没有 writing-mode，只能这么干；好处是任何查看器都能显示。
     ================================================================== */
  function escXml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;' }[c];
    });
  }

  function embedSrc() {
    if (embedProvider) {
      var r = embedProvider();
      if (r) return r;
    }
    var e = CFG.embed;
    if (!e) return null;
    if (e.woff2) return "url(data:font/woff2;base64," + e.woff2 + ") format('woff2')";
    if (e.url) return "url('" + e.url + "') format('truetype')";
    return null;
  }

  function buildSVG(text, opt) {
    requireDOM();
    opt = opt || {};
    var fs     = opt.fontSize || 100;
    var pad    = (opt.padding == null ? 16 : opt.padding);
    var fg     = opt.color || '#1a1f28';
    var bg     = opt.background || null;
    var lineH  = (opt.lineHeight || 1.42) * fs;
    var ASC    = (opt.ascentRatio == null ? 0.75 : opt.ascentRatio) * fs;
    var family = opt.fontFamily || CFG.fontStack;
    var expFam = 'UMComposExport';

    var plan = layout(text, family);
    if (!plan.length) return { error: '没有内容可导出' };

    var k = fs / UPEM;
    var maxLen = Math.max.apply(null, plan.map(function (l) { return l.length; }).concat([1])) * k;
    var W = plan.length * lineH + pad * 2;
    var H = maxLen + pad * 2;

    var p = [];
    p.push('<svg xmlns="http://www.w3.org/2000/svg" width="' + W.toFixed(1) +
           '" height="' + H.toFixed(1) + '" viewBox="0 0 ' + W.toFixed(1) + ' ' + H.toFixed(1) + '">');
    p.push('<title>' + escXml(String(text).replace(/\n/g, ' ')) + '</title>');
    p.push('<desc>Generated by UMCompos ' + VERSION + '</desc>');

    /* 字体内嵌：SVG 被当 <img> 加载时无法引用外部字体，不内嵌会退化成方块 */
    var src = (opt.embedFont === false) ? null : embedSrc();
    if (src) {
      p.push('<defs><style type="text/css"><![CDATA[');
      p.push("@font-face{font-family:'" + expFam + "';font-style:normal;font-weight:400;src:" + src + ";}");
      p.push(']]></style></defs>');
    }

    if (bg) p.push('<rect width="100%" height="100%" fill="' + bg + '"/>');
    p.push('<g fill="' + fg + '" font-family="' + (src ? expFam + ', ' : '') + family +
           '" font-size="' + fs.toFixed(2) + '" xml:lang="mn-Mong">');

    plan.forEach(function (ln) {
      var lineX = pad + ln.line * lineH, pen = 0;
      ln.items.forEach(function (it) {
        var ch = it.text;
        if (ch === ' ' || !ch.trim()) { pen += it.adv; return; }
        var tf = 'translate(' + (lineX + ASC).toFixed(2) + ',' +
                 (pad + pen * k).toFixed(2) + ') rotate(90)';
        p.push('<text transform="' + tf + '" x="0" y="0">' + escXml(ch) + '</text>');
        pen += it.adv;
      });
    });
    p.push('</g></svg>');

    return { svg: p.join('\n'), W: W, H: H, lines: plan.length, plan: plan };
  }

  /* ==================================================================
     7. 字体装载（自带 @font-face 注入，不要求宿主先声明）
     ================================================================== */
  var injected = {};

  function loadFont(url, family) {
    requireDOM();
    url = url || CFG.fontURL;
    family = family || CFG.fontFamily;
    if (!url || !family) return Promise.resolve(false);
    var key = family + '|' + url;
    if (!injected[key]) {
      injected[key] = true;
      var st = document.createElement('style');
      st.textContent = "@font-face{font-family:'" + family + "';src:url('" + url +
        "') format('truetype');font-weight:400;font-style:normal;font-display:block;}";
      document.head.appendChild(st);
    }
    if (document.fonts && document.fonts.load) {
      return document.fonts.load('400 100px "' + family + '"')
        .then(function () { return document.fonts.ready; })
        .then(function () { return true; })
        .catch(function () { return false; });
    }
    return Promise.resolve(true);
  }

  /* ==================================================================
     8. 自带样式（全部用 --umc-* 变量；宿主可覆盖，也可整块关掉）
     ================================================================== */
  var STYLE_ID = 'umcompos-style-v1';

  function injectCSS() {
    requireDOM();
    if (document.getElementById(STYLE_ID)) return;
    var P = CFG.prefix;
    var st = document.createElement('style');
    st.id = STYLE_ID;
    st.textContent =
      ':root{' +
      '--umc-fg:#1a1f28;--umc-fg-dim:#8b95a5;--umc-line:#ccd5e3;' +
      '--umc-surface:#ffffff;--umc-radius:12px;}\n' +
      '.' + P + '{writing-mode:vertical-lr;direction:ltr;text-orientation:mixed;' +
      'text-align:start;word-break:normal;overflow-wrap:normal;' +
      'font-kerning:none;font-variant-ligatures:normal;}\n' +
      '.' + P + '-frame{display:inline-block;max-width:100%;overflow:auto;' +
      'border:1px solid var(--umc-line);border-radius:var(--umc-radius);' +
      'background:var(--umc-surface);padding:10px}\n' +
      '.' + P + '-label{writing-mode:horizontal-tb;font:600 11.5px/1.6 system-ui,sans-serif;' +
      'color:var(--umc-fg-dim);letter-spacing:.04em;margin:0 0 6px}';
    document.head.appendChild(st);
  }

  /* ==================================================================
     9. mount(el, opt)
     ================================================================== */
  function mount(el, opt) {
    /* 先校验参数再检查环境 —— 否则在 Node 下调 mount(null) 会报
       「需要 DOM」，把「你没给容器」这个更重要的信息盖掉。 */
    if (!el) throw new Error('UMCompos.mount: 缺少容器元素');
    requireDOM();
    opt = opt || {};
    if (CFG.injectCSS) injectCSS();
    var P = CFG.prefix;

    var fontFamily = opt.fontFamily || CFG.fontStack;
    var node = document.createElement('div');
    node.className = P + (opt.className ? ' ' + opt.className : '');
    node.setAttribute('lang', 'mn-Mong');
    node.style.cssText =
      'font-family:' + fontFamily + ';' +
      'font-size:' + (opt.fontSize || 28) + 'px;' +
      'line-height:' + (opt.lineHeight || 1.42) + ';' +
      (opt.height ? 'height:' + opt.height + ';' : '') +
      (opt.width ? 'width:' + opt.width + ';' : '') +
      (opt.color ? 'color:' + opt.color + ';' : '');
    node.textContent = opt.text == null ? '' : String(opt.text);
    el.appendChild(node);

    var api = {
      el: node,
      setText: function (t) { node.textContent = t == null ? '' : String(t); return api; },
      getText: function () { return node.textContent; },
      setFontSize: function (px) { node.style.fontSize = px + 'px'; return api; },
      setHeight: function (h) { node.style.height = h || ''; return api; },
      setFontFamily: function (f) { fontFamily = f; node.style.fontFamily = f; return api; },
      layout: function () { return layout(node.textContent, fontFamily); },
      stats: function () {
        var cps = Array.from(node.textContent).map(function (c) { return c.codePointAt(0); });
        return {
          codePoints: cps.length,
          clusters: graphemes(cps).length,
          mongolian: cps.filter(isMongolian).length,
          lines: node.textContent.split('\n').length
        };
      },
      toSVG: function (o) {
        return buildSVG(node.textContent,
          Object.assign({ fontFamily: fontFamily, fontSize: opt.fontSize || 100 }, o || {}));
      },
      download: function (o, filename) {
        var r = api.toSVG(o);
        if (r.error) return r;
        var blob = new Blob([r.svg], { type: 'image/svg+xml;charset=utf-8' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename || 'umcompos.svg';
        document.body.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
        return r;
      },
      destroy: function () { if (node.parentNode) node.parentNode.removeChild(node); }
    };
    return api;
  }

  /* ==================================================================
     10. 导出
     ================================================================== */
  return {
    version: VERSION,
    UPEM: UPEM,
    configure: configure,
    setEmbedProvider: setEmbedProvider,
    config: function () { return CFG; },

    mount: mount,
    loadFont: loadFont,

    /* 纯计算 / 底层工具（Node 下也能用，除测量类需要 DOM） */
    properties: prop,
    graphemes: graphemes,
    breakOpportunities: breakOpps,
    isMongolian: isMongolian,
    codePointHex: cpHex,

    mountMeasure: function (f) { ensureHost(f); },
    measureLine: measureLine,
    measureText: measureText,
    plan: layout,

    buildSVG: buildSVG,
    escapeXml: escXml
  };
}));
