/* ===================================================================
   UME 项目组内部教程 · 前端系列（FE）运行时
   -------------------------------------------------------------------
   这一份脚本负责三件事：
     1. 用 window.__FE_PAGE__ 里的数据**动态生成整个页面 DOM**
        —— 左侧目录是从正文里的 <h2 id> 自动扫出来的，
           所以加小节不用手改目录
     2. 让「示例展示」的 CSS 只在各自示例框内生效（作用域隔离）
     3. 驱动颜色拾取器
   =================================================================== */
(function () {
  'use strict';

  var P = window.__FE_PAGE__;
  if (!P) return;

  /* ================= 1. 动态生成页面 ================= */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  function buildToc(bodyEl) {
    var toc = el('nav');
    toc.id = 'toc';
    toc.appendChild(el('h5', null, '目录'));
    var hs = bodyEl.querySelectorAll('h2[id], h3[id]');
    for (var i = 0; i < hs.length; i++) {
      var h = hs[i];
      var a = document.createElement('a');
      a.href = '#' + h.id;
      if (h.tagName === 'H3') a.className = 'sub';
      /* 标题结构是 <span class="n">3</span>标题文字。
         直接取 textContent 会把编号和文字粘成「3标题文字」，
         所以编号单独取出来加个分隔。 */
      var numEl = h.querySelector('.n');
      var num = numEl ? numEl.textContent.trim() : '';
      var txt;
      if (numEl) {
        var c = h.cloneNode(true);
        c.querySelectorAll('.n, .key-mark, .key-hint').forEach(function (x) {
          x.parentNode.removeChild(x);
        });
        txt = c.textContent.trim();
      } else {
        txt = h.textContent.replace(/★/g, '').trim();
      }
      a.textContent = num ? (num + ' · ' + txt) : txt;
      toc.appendChild(a);
    }
    return toc;
  }

  function buildSeriesNav() {
    var box = el('div', 'series-nav');
    box.appendChild(el('b', null, '本系列'));
    box.appendChild(document.createTextNode('\u3000'));
    P.series.forEach(function (s) {
      var a = document.createElement('a');
      a.href = s.file;
      if (s.file === P.file) a.className = 'cur';
      a.textContent = s.num + ' ' + s.title;
      if (s.star) {
        var sp = document.createElement('span');
        sp.style.color = '#c8901a';
        sp.textContent = ' *';
        a.appendChild(sp);
      }
      box.appendChild(a);
    });
    return box;
  }



  /* ---------- 系列定义（与 assets/series-common.js 逐字一致） ----------
     原来这里手写了一份 ALL_SERIES，和 series-common.js 的
     SERIES + ORDER + PAGES 是两套数据 —— 于是 R 抄的时候留了 f: null，
     FE 页尾的「相关 · R」永远是灰色点不动的 ss-empty，而 R 其实有 3 篇。
     现在改成同构：只留系列定义 + 现有篇目，渲染时现算篇数与跳转目标。 */
  var SERIES = {
    T: { label: '理论 · T' },
    M: { label: '课本 · M' },
    Q: { label: 'C++&Qt · Q' },
    E: { label: 'Extra · E' },
    F: { label: '文件 · F' },
    R: { label: '相关 · R' },
    FE: { label: '前端 · FE' }
  };

  /* 展示顺序，必须与 tools/series_data.py 的 ORDER 一致 */
  var ORDER = ['T', 'F', 'M', 'R', 'Q', 'E', 'FE'];

  /* 现存的篇目（除 FE 自己，FE 那份在页面数据 P.series 里）。
     用来数篇数、并取每个系列的首篇作为跳转目标。 */
  var SERIES_FILES = [
    't01-mongolian-script-intro.html','t02-unicode-and-encoding.html',
    't03-font-file-anatomy.html',
    'f01-command-prompt.html','f02-paths-and-env.html',
    'f03-compile-and-link.html',
    'm01-c-arrays.html','m02-c-functions.html','m03-c-types.html',
    'm04-c-pointers.html','m05-memory.html','m06-class-struct.html',
    'm07-scope.html','m08-c-strings.html','m09-vector-and-array.html',
    'r01-font-design-metrics.html','r02-bubble-sort.html',
    'r03-collation.html',
    'q01-std-and-namespace.html','q02-references.html',
    'q03-pointers-to-objects.html','q04-interfaces.html',
    'e01-recursion.html','e02-batch-and-cmd.html',
    'e03-syntactic-sugar.html',
    'fe-01.html','fe-02.html','fe-03-F01.html','fe-03.html','fe-04.html',
    'fe-05.html','fe-06.html','fe-07.html','fe-08.html'
  ];

  /* fe- 开头的一律算 FE（fe-03-F01.html 也是 FE），其余按首字母。 */
  function seriesKeyOf(file) {
    if (/^fe-/.test(file)) return 'FE';
    return file.charAt(0).toUpperCase();
  }

  function filesOfSeries(key) {
    if (key === 'FE') {
      return (typeof P !== 'undefined' && P.series)
        ? P.series.map(function (s) { return s.file; }) : [];
    }
    return SERIES_FILES.filter(function (f) {
      return seriesKeyOf(f) === key;
    });
  }

  function buildSeriesSwitch() {
    var box = el('div', 's-nav-switch');
    box.appendChild(el('b', null, '全部系列'));
    box.appendChild(document.createTextNode('\u3000'));
    ORDER.forEach(function (k) {
      var list = filesOfSeries(k);
      var lab = (SERIES[k] ? SERIES[k].label : k) +
                '（' + list.length + ' 篇' + (list.length ? '' : '，暂空') + '）';
      if (k === 'FE') {                       /* FE 页自己就是当前项 */
        box.appendChild(el('span', 'ss-cur', lab + '\u3000当前'));
        return;
      }
      if (!list.length) {                     /* 真的没有篇目才灰 */
        box.appendChild(el('span', 'ss-empty', lab));
        return;
      }
      var a = el('a', 'ss-link', lab);        /* 首篇作为跳转目标 */
      a.href = list[0];
      box.appendChild(a);
    });
    return box;
  }

  function build() {
    var btn = el('button', null, '目录');
    btn.id = 'tocToggle';
    document.body.appendChild(btn);

    var shell = el('div');
    shell.id = 'shell';

    var body = el('div');
    body.innerHTML = P.body;

    shell.appendChild(buildToc(body));

    var main = el('main');
    main.id = 'top';
    var h1 = el('h1', null, P.title);
    if (P.star) {
      var st = el('span', 'key-mark', '★');
      st.title = '重要内容';
      st.style.marginLeft = '8px';
      h1.appendChild(st);
    }
    main.appendChild(h1);
    main.appendChild(el('p', 'sub-title',
      'UME 项目组内部教程 · 前端系列（FE）· ' + P.num));
    while (body.firstChild) main.appendChild(body.firstChild);

    main.appendChild(buildSeriesNav());
    main.appendChild(buildSeriesSwitch());
    var f = el('footer');
    f.innerHTML = 'UME 项目组内部教程 · 前端系列 ' + P.num + '《' + P.title + '》<br>'
      + '示例均以 <b>Consolas</b> 等宽字体呈现；'
      + '标着「示例展示」的代码块会把效果真的渲染出来。';
    main.appendChild(f);

    shell.appendChild(main);
    document.body.setAttribute('data-series', 'FE');
    document.body.appendChild(shell);

    var fab = el('a', 'home-fab', '返回 home');
    fab.href = '../../index.html';
    fab.title = '返回教程总目录';
    document.body.appendChild(fab);

    return { main: main, toc: toc_ };
  }

  var toc_;
  function init() {
    var r = build();
    toc_ = document.getElementById('toc');
    wireToc();
    wireCopy();
    scopePreviews();
    initPicker();
  }

  function wireToc() {
    var toc = document.getElementById('toc');
    var btn = document.getElementById('tocToggle');

    function closeDrawer() {
      toc.classList.remove('open');
      document.body.classList.remove('toc-open');
    }
    function openDrawer() {
      toc.classList.add('open');
      document.body.classList.add('toc-open');
    }

    if (btn && toc) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (toc.classList.contains('open')) closeDrawer(); else openDrawer();
      });

      /* 点抽屉里的目录项 → 跳转并收起抽屉。
         注意别在这里 preventDefault —— 否则就跳不动了。 */
      toc.addEventListener('click', function (e) {
        if (e.target.closest('a')) closeDrawer();
      });

      /* 点抽屉外面 → 收起。
         遮罩层已经设了 pointer-events:none（它曾经把抽屉里的点击全吃掉），
         所以这里用坐标判断，而不是靠遮罩拿到点击。 */
      document.addEventListener('click', function (e) {
        if (!toc.classList.contains('open')) return;
        if (toc.contains(e.target) || e.target === btn) return;
        var r = toc.getBoundingClientRect();
        if (e.clientX >= r.left && e.clientX <= r.right
            && e.clientY >= r.top && e.clientY <= r.bottom) return;
        closeDrawer();
      });
    }

    var links = [].slice.call(document.querySelectorAll('#toc a[href^="#"]'));
    var targets = links.map(function (a) {
      return document.querySelector(a.getAttribute('href'));
    }).filter(Boolean);
    if (!targets.length || !window.IntersectionObserver) return;
    var io = new IntersectionObserver(function (es) {
      var vis = es.filter(function (e) { return e.isIntersecting; })
        .sort(function (a, b) {
          return a.boundingClientRect.top - b.boundingClientRect.top;
        });
      if (vis[0]) {
        var id = vis[0].target.id;
        links.forEach(function (a) {
          a.classList.toggle('on', a.getAttribute('href') === '#' + id);
        });
      }
    }, { rootMargin: '-10% 0px -70% 0px' });
    targets.forEach(function (t) { io.observe(t); });
  }

  function wireCopy() {
    document.querySelectorAll('.cp').forEach(function (b) {
      b.addEventListener('click', function () {
        var pre = b.closest('.code-wrap').querySelector('pre');
        copyText(pre.innerText).then(function () {
          var old = b.textContent;
          b.textContent = '已复制';
          setTimeout(function () { b.textContent = old; }, 1200);
        });
      });
    });
  }

  function copyText(s) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(s).catch(function () {});
    }
    var ta = document.createElement('textarea');
    ta.value = s;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    return Promise.resolve();
  }

  /* ================= 2. 示例展示的作用域隔离 =================
     CSS 示例里的 .card / div 之类选择器不能作用到文档本身，
     所以给每条规则加上 [data-pv="N"] 前缀，只在那个示例框内生效。
     前缀不改变偏移量，示例内部的优先级关系与真实页面一致。

     必须**数花括号配平** —— 示例 CSS 是三行式，还可能有 @media 嵌套，
     找第一个 '}' 会截断。字符串里的花括号也要跳过。 */
  function scoped(css, scope) {
    var out = '', i = 0, n = css.length;
    while (i < n) {
      if (css.substr(i, 2) === '/*') {
        var ce = css.indexOf('*/', i + 2);
        i = ce < 0 ? n : ce + 2;
        continue;
      }
      var b = css.indexOf('{', i);
      if (b < 0) break;
      var sel = css.slice(i, b).replace(/\/\*[\s\S]*?\*\//g, '').trim();
      var depth = 1, k = b + 1, q = null;
      while (k < n && depth > 0) {
        var ch = css.charAt(k);
        if (q) { if (ch === q && css.charAt(k - 1) !== '\\') q = null; }
        else if (ch === '"' || ch === "'") q = ch;
        else if (ch === '{') depth++;
        else if (ch === '}') depth--;
        k++;
      }
      var body = css.slice(b + 1, k - 1);
      if (sel && sel.charAt(0) !== '@') {
        sel = sel.split(',').map(function (x) {
          x = x.trim();
          return x ? scope + ' ' + x : x;
        }).join(', ');
      }
      out += sel + '{' + body + '}';
      i = k;
    }
    return out;
  }

  function scopePreviews() {
    document.querySelectorAll('.pv-wrap[data-pv]').forEach(function (w) {
      var scope = '[data-pv="' + w.dataset.pv + '"]';
      var body = w.querySelector('.pv-body');
      var code = w.querySelector('pre');
      if (!body || !code) return;
      var text = code.textContent;
      if ((w.dataset.pvKind || 'html') === 'css') {
        var st = document.createElement('style');
        st.textContent = scoped(text, scope);
        w.appendChild(st);
      } else {
        body.innerHTML = text;
      }
    });
  }

  /* ================= 3. 颜色拾取器 ================= */
  function h2(n) {
    n = Math.round(n);
    return (n < 16 ? '0' : '') + n.toString(16).toUpperCase();
  }
  function hue(r, g, b, mx, mn, d) {
    if (!d) return 0;
    var h;
    if (mx === r) h = ((g - b) / d) % 6;
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60;
    return h < 0 ? h + 360 : h;
  }

  function initPicker() {
    var box = document.getElementById('picker');
    if (!box) return;
    var R = document.getElementById('pkR'), G = document.getElementById('pkG'),
        B = document.getElementById('pkB'), A = document.getElementById('pkA');
    var sw = document.getElementById('pkSwatch');
    var hx = document.getElementById('pkHex'), rg = document.getElementById('pkRgb'),
        hs = document.getElementById('pkHsl'), ra = document.getElementById('pkRgba');
    if (!R || !sw) return;

    function sync() {
      var r = +R.value, g = +G.value, b = +B.value, a = +A.value;
      document.getElementById('pkRv').textContent = r;
      document.getElementById('pkGv').textContent = g;
      document.getElementById('pkBv').textContent = b;
      document.getElementById('pkAv').textContent = a + '%';

      var hexv = '#' + h2(r) + h2(g) + h2(b);
      sw.style.background = a >= 100 ? hexv
        : 'rgba(' + r + ',' + g + ',' + b + ',' + (a / 100) + ')';

      var mx = Math.max(r, g, b) / 255, mn = Math.min(r, g, b) / 255, d = mx - mn;
      var hh = Math.round(hue(r / 255, g / 255, b / 255, mx, mn, d));
      var sv = mx ? Math.round(d / mx * 100) : 0;
      var vv = Math.round(mx * 100);
      var ll = Math.round((mx + mn) / 2 * 100);
      var sl = (mx + mn) === 0 || (mx + mn) === 2 ? 0
        : Math.round(d / (1 - Math.abs(mx + mn - 1)) * 100);

      hx.textContent = hexv;
      rg.textContent = 'rgb(' + r + ', ' + g + ', ' + b + ')';
      hs.textContent = 'hsl(' + hh + ', ' + sl + '%, ' + ll + '%)  /  hsv('
        + hh + ', ' + sv + '%, ' + vv + '%)';
      ra.textContent = (hexv + h2(a * 255 / 100)).toLowerCase()
        + '  rgba(' + r + ', ' + g + ', ' + b + ', ' + (a / 100).toFixed(2) + ')';

      R.style.setProperty('--tk',
        'linear-gradient(90deg, rgb(0,' + g + ',' + b + '), rgb(255,' + g + ',' + b + '))');
      G.style.setProperty('--tk',
        'linear-gradient(90deg, rgb(' + r + ',0,' + b + '), rgb(' + r + ',255,' + b + '))');
      B.style.setProperty('--tk',
        'linear-gradient(90deg, rgb(' + r + ',' + g + ',0), rgb(' + r + ',' + g + ',255))');
      A.style.setProperty('--tk',
        'linear-gradient(90deg, rgba(' + r + ',' + g + ',' + b + ',0), rgb(' + r + ',' + g + ',' + b + '))');
    }
    [R, G, B, A].forEach(function (s) { s.addEventListener('input', sync); });

    var presets = ['#1F6FEB', '#17864A', '#C0392B', '#A4690D', '#6B46C1', '#0D7D7D',
      '#1a1f28', '#4b5563', '#8b95a5', '#ccd5e3', '#e3e8f0', '#f7f9fc',
      '#ffffff', '#000000', '#ff0000', '#ff6f00', '#ffd400'];
    var pbox = document.getElementById('pkPresets');
    presets.forEach(function (c) {
      var i = document.createElement('i');
      i.style.background = c;
      i.title = c;
      i.addEventListener('click', function () {
        R.value = parseInt(c.slice(1, 3), 16);
        G.value = parseInt(c.slice(3, 5), 16);
        B.value = parseInt(c.slice(5, 7), 16);
        A.value = 100;
        sync();
      });
      pbox.appendChild(i);
    });

    box.querySelectorAll('.cp2').forEach(function (b) {
      b.addEventListener('click', function () {
        var full = document.getElementById(b.dataset.cp).textContent;
        copyText(full.split('  ')[0].trim()).then(function () {
          var o = b.textContent;
          b.textContent = '已复制';
          setTimeout(function () { b.textContent = o; }, 1100);
        });
      });
    });

    var inp = document.createElement('input');
    inp.type = 'color';
    inp.value = '#1f6feb';
    inp.className = 'pk-native';
    inp.title = '用系统取色器选色';
    inp.style.cssText = 'width:44px;height:32px;padding:2px;border:1px solid #ccd5e3;'
      + 'border-radius:9px;cursor:pointer;background:#fff';
    inp.addEventListener('input', function () {
      R.value = parseInt(inp.value.slice(1, 3), 16);
      G.value = parseInt(inp.value.slice(3, 5), 16);
      B.value = parseInt(inp.value.slice(5, 7), 16);
      sync();
    });
    var hint = box.querySelector('.pk-note');
    if (hint && hint.parentNode) hint.parentNode.insertBefore(inp, hint);
    else box.appendChild(inp);

    sync();
  }

  /* ================= 启动 ================= */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
