# assets —— 教程页的静态资源

```
assets/
├── css/     52 个样式表：genelayout（公共骨架）、tg_L/tg_D（深浅主题）、
│            series-theme（并列系列主题）、每页一份 <slug>.css
├── img/     图片与图版：webp / awebp / png / jpg / gif / bmp / svg / pdf
├── js/      页面运行时：series-common.js（页尾系列跳转）、
│            fe-data.js（FE 页运行时）、r03-picker.js（颜色拾取器）
├── fonts/   随项目分发的字体，见下
├── egypt/   圣书体渲染引擎整包：MdCRndr.js + NewGardiner.ttf + OFL.txt
└── ref/     项目组长自己的参考图（未嵌入任何页面）
```

## 引用约定

- 教程页里一律写 **`assets/css/xxx.css`**、**`assets/img/xxx.png`**、**`assets/js/xxx.js`**。
- **样式表内部的 `url()` 是相对样式表自己算的**，所以要从 `css/` 往上一层写
  **`../fonts/xxx.ttf`**。这一处最容易漏：写错不会报错，只是字体悄悄不加载、
  退回系统字体，页面看起来「有点像但不对」。
- 生成器同样遵守上面两条：`tools/build_page.py` 输出 `<link href="assets/css/{css}">`，
  `tools/make_pages.py` 的 `CARD_BG` 指向 `SharingGroup/tutorials/assets/img/…`。
  改目录时这两处与 `tools/build_series_css.py` 的 `OUT`、`tools/gen_series_tables.py`
  的两个路径一起改，否则下次重跑就退回旧结构。

## fonts/ 里都是什么

| 文件 | 字体 | 许可 | 用在哪 |
|---|---|---|---|
| `DejaVuSerif.ttf` | DejaVu Serif 2.37 | Bitstream Vera 系（见 `LICENSE-DejaVu.txt`） | R04 与 A01 的音标（IPA） |
| `Amiri-Regular.ttf` | Amiri 1.002（Khaled Hosny） | OFL 1.1（见 `OFL.txt`） | A01 的阿拉伯字母示例 |
| `Shobhika-Regular.otf` / `-Bold.otf` | Shobhika 1.050（IIT Bombay） | OFL 1.1 | A01 的天城文示例 |
| `../egypt/NewGardiner.ttf` | New Gardiner 3.06（Mark-Jan Nederhof） | OFL 1.1 | A01 第 15 节的圣书体演示 |

三支 OFL 字体共用 `fonts/OFL.txt`；DejaVu 是另一份许可，单独放在
`LICENSE-DejaVu.txt`。**新增字体时请把许可证一并放进来** —— OFL 要求随字体附带。

## 哪些字体**没有**进来

`Mongolian Baiti`（Windows 系统字体，© Microsoft / 北京方正）只允许在 CSS
字体栈里点名，不允许打包或做 `@font-face`。相关说明写在
`web/UME.html` 与 `web/globpreview.html` 的注释里。
蒙文渲染用的是项目自带的 `font/NotoSansMongolian-Regular.ttf`（OFL）。

## 整理历史

原先 103 个文件全部平铺在 `assets/` 顶层。整理由
`tools/organize_assets.py` 完成（可重复执行，幂等），
它同时改写了 91 个文件里的引用路径。
