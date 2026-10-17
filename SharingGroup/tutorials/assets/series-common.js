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
    Q: { label: 'C++&Qt · Q',   banner: 'Q 系列 · C++ 开发事项和 Qt 基础' },
    E: { label: 'Extra · E', banner: 'E 系列 · 补充练习与进阶' },
    F: { label: '文件 · F', banner: 'F 系列 · 文件操作基础' },
    R: { label: '相关 · R', banner: 'R 系列 · 相关信息与理论' },
    FE: { label: '前端 · FE', banner: 'FE 系列 · 前端基础' }
  };

  /* 展示顺序由项目组长按组员进度手工排优先度 —— 会变，
     必须与 tools/series_data.py 的 ORDER 保持一致 */
  /* 末尾的 FE 也要列进来 —— 它的外观自成一系，
     但同样是「一个系列」，『全部系列』里必须有它 */
  var ORDER = ['T', 'F', 'M', 'R', 'Q', 'E', 'FE'];

  /* ---------- 篇目表 ---------- */
  var PAGES = [
    /* ---- T：T 系列 · 核心理论和底层逻辑 ---- */
    { f: 't01.html',                        n: 'T01',       t: '初识回鹘蒙文', s: 'T' },
    { f: 't02.html',                        n: 'T02',       t: 'Unicode 和编码', s: 'T' },
    { f: 't03.html',                        n: 'T03',       t: '字体文件结构大揭秘', s: 'T' },

    /* ---- F：F 系列 · 文件操作基础 ---- */
    { f: 'f01.html',                        n: 'F01',       t: '命令提示符（cmd）初步', s: 'F' },
    { f: 'f02.html',                        n: 'F02',       t: '相对文件路径与宏', s: 'F' },
    { f: 'f03.html',                        n: 'F03',       t: '编译与链接、头文件与库', s: 'F' },
    { f: 'f04.html',                        n: 'F04',       t: '构建系统生成器与构建工具', s: 'F' },

    /* ---- M：M 系列 · 课本内容速成与补充 ---- */
    { f: 'm01.html',                        n: 'M01',       t: '数组初步', s: 'M' },
    { f: 'm02.html',                        n: 'M02',       t: '函数初步', s: 'M' },
    { f: 'm03.html',                        n: 'M03',       t: '类型概论', s: 'M' },
    { f: 'm04.html',                        n: 'M04',       t: '指针初步', s: 'M' },
    { f: 'm05.html',                        n: 'M05',       t: '静态、动态内存与内存安全初步', s: 'M' },
    { f: 'm06.html',                        n: 'M06',       t: '类、结构体', s: 'M' },
    { f: 'm07.html',                        n: 'M07',       t: '作用域、全局与局部变量', s: 'M' },
    { f: 'm08.html',                        n: 'M08',       t: 'C 风格字符串', s: 'M' },
    { f: 'm09.html',                        n: 'M09',       t: 'vector 和 array', s: 'M' },
    { f: 'm10.html',                        n: 'M10',       t: '抽象基类和纯虚函数', s: 'M' },

    /* ---- R：R 系列 · 相关信息与理论 ---- */
    { f: 'r01.html',                        n: 'R01',       t: '字体设计里的几个基本概念', s: 'R' },
    { f: 'r02.html',                        n: 'R02',       t: '字典序、自然序与 QCollator', s: 'R' },
    { f: 'r03.html',                        n: 'R03',       t: '十六进制颜色模型、HSV 与 Alpha', s: 'R' },
    { f: 'r04.html',                        n: 'R04',       t: '国际音标（IPA）', s: 'R' },

    /* ---- Q：Q 系列 · C++ 开发事项和 Qt 基础 ---- */
    { f: 'q01.html',                        n: 'Q01',       t: 'std 与命名空间初步', s: 'Q' },
    { f: 'q02.html',                        n: 'Q02',       t: 'C++ 的引用', s: 'Q' },
    { f: 'q03.html',                        n: 'Q03',       t: '指针进阶：指向对象的指针与引用', s: 'Q' },
    { f: 'q04.html',                        n: 'Q04',       t: '接口', s: 'Q' },
    { f: 'q05.html',                        n: 'Q05',       t: '单一职责原则和开闭原则', s: 'Q' },
    { f: 'q06.html',                        n: 'Q06',       t: '组件化编程与解耦合', s: 'Q' },
    { f: 'q07.html',                        n: 'Q07',       t: '代码复用性和扩展性', s: 'Q' },
    { f: 'q08.html',                        n: 'Q08',       t: '接口隔离原则', s: 'Q' },
    { f: 'q09.html',                        n: 'Q09',       t: '指针进阶：函数指针', s: 'Q' },
    { f: 'q10.html',                        n: 'Q10',       t: '智能指针', s: 'Q' },
    { f: 'q11.html',                        n: 'Q11',       t: '线程与互斥锁', s: 'Q' },

    /* ---- E：E 系列 · 补充练习与进阶 ---- */
    { f: 'e01.html',                        n: 'E01',       t: '递归', s: 'E' },
    { f: 'e02.html',                        n: 'E02',       t: '批处理与命令提示符进阶', s: 'E' },
    { f: 'e03.html',                        n: 'E03',       t: '语法糖', s: 'E' },
    { f: 'e04.html',                        n: 'E04',       t: '冒泡排序与算法复杂度', s: 'E' },

    /* ---- FE：FE 系列 · 前端基础 ---- */
    { f: 'fe-01.html',                      n: 'FE-01',     t: 'HTML 入门与标签语法', s: 'FE' },
    { f: 'fe-02.html',                      n: 'FE-02',     t: 'HTML 常用标签', s: 'FE' },
    { f: 'fe-03.html',                      n: 'FE-03',     t: 'CSS 入门', s: 'FE' },
    { f: 'fe-04.html',                      n: 'FE-04',     t: 'CSS 选择器语法', s: 'FE' },
    { f: 'fe-05.html',                      n: 'FE-05',     t: 'Display 与盒模型尺寸', s: 'FE' },
    { f: 'fe-06.html',                      n: 'FE-06',     t: 'Writing Mode 与溢出滚动', s: 'FE' },
    { f: 'fe-07.html',                      n: 'FE-07',     t: '鼠标悬停与 transition', s: 'FE' },
    { f: 'fe-08.html',                      n: 'FE-08',     t: 'JavaScript 语法初步', s: 'FE' },
    { f: 'fe-09.html',                      n: 'FE-09',     t: 'DOM 操作基础', s: 'FE' },
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

    /* 「全部系列」：列出**所有**系列（含本系列与前端 FE），当前项就地标出。
       原来排除了自己、也不含 FE —— 用户要求「全部系列」就得是全部。 */
    var sw = el('div', 's-nav-switch');
    sw.appendChild(el('b', null, '全部系列'));
    sw.appendChild(el('span', null, '　'));
    ORDER.forEach(function (k) {
      var list = PAGES.filter(function (p) { return p.s === k; });
      var lab = (SERIES[k] ? SERIES[k].label : k) +
                '（' + list.length + ' 篇' + (list.length ? '' : '，暂空') + '）';
      if (k === sk) {
        sw.appendChild(el('span', 'ss-cur', lab + '　当前'));
        return;
      }
      if (!list.length) {
        sw.appendChild(el('span', 'ss-empty', lab));
        return;
      }
      var a = el('a', 'ss-link', lab);
      a.href = list[0].f;
      sw.appendChild(a);
    });
    box.appendChild(sw);

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

    /* 插到正文末尾。
       注意：footer 与 h2[id] 都不是每篇都有 —— e01 与 m04 两个都没有，
       原来只判断 footer，结果这两篇的跳转整块**没挂上**。
       所以最后一个分支必须是无条件 appendChild。 */
    var foot = main.querySelector('footer');
    if (foot) main.insertBefore(box, foot);
    else main.appendChild(box);

    /* 如果连 main 都没有，退回挂到 body 末尾 —— 有总比没有好 */
    if (!box.parentNode) document.body.appendChild(box);
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
