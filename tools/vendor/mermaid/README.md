# mermaid（本地随项目携带）

这是 [mermaid](https://github.com/mermaid-js/mermaid) 的**离线渲染用**副本。

## 版本与来源

| 项 | 值 |
|---|---|
| 版本 | 11.17.2 |
| 文件 | `dist/mermaid.min.js`（UMD 自包含，含全部依赖） |
| 许可证 | MIT，见同目录 `LICENSE` |
| 取自 | npm 包 `mermaid@11.17.2` 的 `dist/` 与 `LICENSE` |
| SHA-256 | `581ED7D74BD9048D0E3A91363927D72EF22942D7722546B27F7CC29E35390EB8` |

## 为什么放在项目里

`tools/render_gantt.js` 与 `tools/render_mermaid.js` 要用 mermaid 把
`.mmd` 源码渲染成静态 SVG。原先它们指向一个**本机全局安装**的路径
（`~/.dsh/profiles/desktop/node_modules/mermaid`），换一台机器就跑不动，
也没法在仓库里复现。现在随项目携带一份，渲染脚本只认这个相对路径。

## 它不参与页面

**页面运行时不加载它。** 教程页只引用渲染好的 SVG（见
`SharingGroup/tutorials/assets/*.svg`），所以：

* 打开页面不需要 JS，也不需要这 3.4 MB
* 断网、双击本机 HTML 都能正常显示

## 怎么更新

```powershell
npm pack mermaid@<新版本>          # 或直接从 npm 包目录取
# 把 dist/mermaid.min.js 与 LICENSE 覆盖到本目录
node tools/render_gantt.js         # 重新出图
node tools/render_mermaid.js       # M10 的类图
```

更新后请同步改本文件里的版本号与 SHA-256。