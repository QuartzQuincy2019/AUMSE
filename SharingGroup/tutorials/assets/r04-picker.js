/* =====================================================================
   r04-picker.js —— R04《十六进制颜色模型、HSV 与 Alpha》的「颜色拾取器」
   ---------------------------------------------------------------------
   这一段逻辑原来住在 assets/fe-data.js 里（FE 系列页面的运行时）。
   R04 原本是 FE 的 fe-03-F01，改成 R 系列的文档页后就不再加载
   fe-data.js，滑块因此拖不动 —— 所以把它抽成独立文件单独加载。

   依赖（全在本文件内，不引用 FE 的任何其它代码）：
       h2()         两位十六进制
       hue()        算色相
       copyText()   复制到剪贴板（带 execCommand 兜底）
       initPicker() 全部交互

   页面侧约定：body 里要有 id="picker"，以及 pkR / pkG / pkB / pkA、
   pkSwatch / pkHex / pkRgb / pkHsl / pkRgba / pkPresets 这些元素。
   样式在 assets/r04.css 的「颜色拾取器」一节。
   ===================================================================== */
(function () {
  'use strict';

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

  /* 等 DOM 就绪再挂 —— 本文件用 defer 加载，但保险起见再包一层 */
  function boot() { initPicker(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
