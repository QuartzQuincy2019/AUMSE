/* =====================================================================
   project-config.js — 把「本项目的具体信息」告诉 UMCompos
   ---------------------------------------------------------------------
   分工：
     UMCompos.js        纯组件，不认识本项目，可原样拷到任何项目
     project-config.js  本项目对组件的配置（字体路径、族名、内嵌字体源）

   为什么单独一个文件：
     路径和字体名是**项目信息**，不该写进组件。这样以后换字体、
     挪目录，只改这里一处，组件一个字都不用动。
   ===================================================================== */
(function () {
  'use strict';
  if (typeof UMCompos === 'undefined') return;

  UMCompos.configure({
    /* 字体文件。相对本文件所在目录（web/）解析成 URL 时用绝对路径更稳，
       所以这里用「相对站点根」的写法，两个页面（web/ 与 tutorials/）都能用。 */
    fontURL: new URL('../font/NotoSansMongolian-Regular.ttf', document.baseURI).href,
    fontFamily: 'UME Mongolian',
    fontStack: "'UME Mongolian','Noto Sans Mongolian','Mongolian Baiti',serif"
  });

  /* 导出 SVG 时内嵌字体：优先用 WOFF2 子集（体积小、SVG 当 <img> 也能显示）。
     子集由 tools/make_font_subset.py 生成，挂在 window.UME_FONT_SUBSET。
     没加载到就回退到外部 TTF 引用。 */
  UMCompos.setEmbedProvider(function () {
    if (window.UME_FONT_SUBSET) {
      return "url(data:font/woff2;base64," + window.UME_FONT_SUBSET + ") format('woff2')";
    }
    return "url('" + UMCompos.config().fontURL + "') format('truetype')";
  });
})();
