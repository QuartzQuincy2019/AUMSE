/* =====================================================================
   series-common.js —— 并列系列（T / M / Q / E / F / R）共用脚本
   ---------------------------------------------------------------------
   和 t-common.js 是同一个思路，只是不再只服务 T：

     1. 文末「系列内部跳转」—— 动态生成
        篇目表只有下面 SERIES 这一处，加新篇只改这里；
        页面靠 <body data-series="X"> 告诉脚本「我在哪个系列」。

     2. 当前页小目录 —— 从正文 h2 现读，不写死。

     3. 暗色模式：同步 color-scheme / theme-color，并防白闪。

   用法（放在 </body> 之前）：
     <script src="assets/series-common.js"></script>

   ⚠ 这个文件里的 SERIES 必须与 tools/series_data.py 保持一致。
     两边是同一份数据的两个副本 —— 改完 Python 那边记得同步这里。
   ===================================================================== */
(function () {
  'use strict';

  /* ---------- 系列定义（与 tools/series_data.py 对应） ---------- */
  var SERIES = {
    T: { label: '理论 · T', banner: 'T 系列 · 核心理论和底层逻辑' },
    M: { label: '课本 · M', banner: 'M 系列 · 课本内容速成与补充' },
    Q: { label: 'Qt · Q',   banner: 'Q 系列 · C++ 开发事项和 Qt 基础' },
    E: { label: 'Extra · E', banner: 'E 系列 · 补充练习与进阶' },
    F: { label: 'File · F', banner: 'F 系列 · 文件操作基础' },
    R: { label: '相关 · R', banner: 'R 系列 · 相关资讯与理论' }
  };

  var ORDER = ['T', 'M', 'Q', 'E', 'F', 'R'];

  /* ---------- 篇目表 ---------- */
  var PAGES = [
    { f: 't01-mongolian-script-intro.html', n: 'T01', t: '初识回鹘蒙文',            s: 'T' },
    { f: 't02-unicode-and-encoding.html',   n: 'T02', t: 'Unicode 和编码',          s: 'T' },
    { f: 't03-font-file-anatomy.html',      n: 'T03', t: '字体文件结构大揭秘',       s: 'T' },

    { f: 'm01-c-arrays.html',      n: 'M01', t: '数组初步',                    s: 'M' },
    { f: 'm02-c-functions.html',   n: 'M02', t: '函数初步',                    s: 'M' },
    { f: 'm03-c-types.html',       n: 'M03', t: '类型概论',                    s: 'M' },
    { f: 'm04-c-pointers.html',    n: 'M04', t: '指针初步',                    s: 'M' },
    { f: 'm05-memory.html',        n: 'M05', t: '静态、动态内存与内存安全初步',   s: 'M' },
    { f: 'm06-class-struct.html',  n: 'M06', t: '类、结构体',                   s: 'M' },
    { f: 'm07-scope.html',         n: 'M07', t: '作用域、全局与局部变量',        s: 'M' },
    { f: 'm08-c-strings.html',     n: 'M08', t: 'C 风格字符串',                s: 'M' },
    { f: 'm09-vector-and-array.html', n: 'M09', t: 'vector 和 array',         s: 'M' },

    { f: 'q01-std-and-namespace.html', n: 'Q01', t: 'std 与命名空间初步',       s: 'Q' },

    { f: 'e01-recursion.html',      n: 'E01', t: '递归',                       s: 'E' },
    { f: 'e02-batch-and-cmd.html',  n: 'E02', t: '批处理与命令提示符进阶',       s: 'E' },

    { f: 'f01-command-prompt.html', n: 'F01', t: '命令提示符（cmd）初步',       s: 'F' },
    { f: 'f02-paths-and-env.html',  n: 'F02', t: '相对文件路径与宏',            s: 'F' },
    { f: 'f03-compile-and-link.html', n: 'F03', t: '编译与链接、头文件与库',     s: 'F' }

    /* R 系列暂空 —— 将来加篇目就写在下面，格式同上
       { f: 'r01-xxx.html', n: 'R01', t: '标题', s: 'R' }, */
  ];

  function currentFile() {
    var p = location.pathname.split('/').pop() || '';
    return decodeURIComponent(p);
  }

  function curSeries() {
    return document.body.getAttribute('data-series') || '';
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* ---------- 1. 文末系列内跳转 ---------- */
  function buildNav() {
    var main = document.querySelector('main');
    if (!main || main.querySelector('.s-nav')) return;

    var sk = curSeries();
    var cur = currentFile();
    var box = el('nav', 's-nav');
    box.setAttribute('aria-label', '系列内部跳转');

    var mine = PAGES.filter(function (p) { return p.s === sk; });
    var s = SERIES[sk] || { label: sk };

    box.appendChild(el('p', 's-nav-h',
      (s.label || sk) + '　共 ' + mine.length + ' 篇'));

    if (mine.length) {
      var grid = el('div', 's-nav-grid');
      mine.forEach(function (p) {
        var a = el('a');
        a.href = p.f;
        a.appendChild(el('span', 's-no', p.n));
        a.appendChild(el('span', 's-tt', p.t));
        if (p.f === cur) {
          a.setAttribute('aria-current', 'page');
          a.appendChild(el('span', 's-nav-cur', '当前'));
        }
        grid.appendChild(a);
      });
      box.appendChild(grid);
    } else {
      var empty = el('p', null, '本系列暂无篇目。');
      empty.style.margin = '0';
      box.appendChild(empty);
    }

    /* 其它系列：一行快捷入口 */
    var others = ORDER.filter(function (k) { return k !== sk; });
    if (others.length) {
      var sw = el('div', 's-nav-switch');
      sw.style.marginTop = '12px';
      sw.style.paddingTop = '10px';
      sw.style.borderTop = '1px dashed var(--s-line,#ccd5e3)';
      sw.style.font = '500 12.5px/1.9 var(--sans,system-ui,sans-serif)';
      sw.appendChild(el('span', null, '其它系列：　'));
      others.forEach(function (k) {
        var list = PAGES.filter(function (p) { return p.s === k; });
        var lab = (SERIES[k] ? SERIES[k].label : k) +
                  '（' + list.length + ' 篇' + (list.length ? '' : '，暂空') + '）';
        if (!list.length) {
          var sp = el('span', null, lab + '　');
          sp.style.opacity = '.6';
          sw.appendChild(sp);
          return;
        }
        var a = el('a', null, lab);
        a.href = list[0].f;
        a.style.marginRight = '10px';
        sw.appendChild(a);
      });
      box.appendChild(sw);
    }

    /* 当前页小目录 */
    var heads = main.querySelectorAll('h2[id]');
    if (heads.length) {
      var toc = el('div', 's-nav-toc');
      toc.appendChild(el('p', 's-nav-h', '本篇小节'));
      var ol = el('ol');
      Array.prototype.forEach.call(heads, function (hd) {
        var li = el('li');
        var a = el('a');
        a.href = '#' + hd.id;
        /* 去掉序号徽标与重点星标 —— 直接取 textContent 会拼成「1选择器是什么」 */
        var clone = hd.cloneNode(true);
        Array.prototype.forEach.call(
          clone.querySelectorAll('.n, .key-mark, .key-hint'),
          function (x) { x.parentNode.removeChild(x); });
        a.textContent = clone.textContent.trim();
        li.appendChild(a);
        ol.appendChild(li);
      });
      toc.appendChild(ol);
      box.appendChild(toc);
    }

    var foot = main.querySelector('footer');
    if (foot) main.insertBefore(box, foot);
    else main.appendChild(box);
  }

  /* ---------- 2. 配色方案同步 ---------- */
  function syncColorScheme() {
    var dark = window.matchMedia &&
               window.matchMedia('(prefers-color-scheme: dark)').matches;
    var m = document.querySelector('meta[name="color-scheme"]');
    if (!m) {
      m = document.createElement('meta');
      m.setAttribute('name', 'color-scheme');
      document.head.appendChild(m);
    }
    m.setAttribute('content', dark ? 'dark light' : 'light dark');
    var tm = document.querySelector('meta[name="theme-color"]');
    if (!tm) {
      tm = document.createElement('meta');
      tm.setAttribute('name', 'theme-color');
      document.head.appendChild(tm);
    }
    if (!tm.dataset.auto) return;      /* 只改由脚本管理的那个 */
    tm.setAttribute('content', dark ? '#15171c' : '#eef3f9');
  }

  function boot() {
    buildNav();
    syncColorScheme();
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      var on = function () { syncColorScheme(); };
      if (mq.addEventListener) mq.addEventListener('change', on);
      else if (mq.addListener) mq.addListener(on);
    }
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', boot);
  else
    boot();

  window.__SERIES__ = SERIES;
  window.__SERIES_PAGES__ = PAGES;
})();
