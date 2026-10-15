# -*- coding: utf-8 -*-
"""重构 build_fe.py 的样式：
    * BASE_CSS  → 从 tools/fe_theme.css 读取（前端专属花样主题）
    * PREVIEW_CSS → 只留「示例展示 / 颜色拾取器 / 插图」这些组件样式

原先两者混在一个 BASE_CSS 字符串里，主题一改就要动那一大坨 ——
拆开之后调主题只改 fe_theme.css 一个文件。
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\build_fe.py"
TH = r"E:\QKMansion\CSX10\w\UME\tools\fe_theme.css"

t = io.open(P, encoding="utf-8").read()

# ---- 定位 BASE_CSS 与 PREVIEW_CSS 两个赋值块 ----
i_base = t.find('BASE_CSS = r"""')
assert i_base > 0, "找不到 BASE_CSS"
i_base_end = t.find('"""', i_base + len('BASE_CSS = r"""')) + 3

i_pv = t.find('PREVIEW_CSS = r"""')
assert i_pv > i_base_end, "找不到 PREVIEW_CSS"
i_pv_end = t.find('"""', i_pv + len('PREVIEW_CSS = r"""')) + 3

# ---- 新的 BASE_CSS：改为运行时读文件 ----
NEW_BASE = '''# 前端专属主题（暖色渐变 + 玻璃拟态），单独放一个文件方便调
_THEME_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fe_theme.css")
BASE_CSS = io.open(_THEME_PATH, encoding="utf-8").read()'''

# ---- 新的 PREVIEW_CSS：只留组件 ----
NEW_PV = '''PREVIEW_CSS = r"""
/* ================= 示例展示：把示例真的渲染出来 ================= */
.pv-wrap{margin:18px 0}
.pv-wrap .code-wrap{margin:0;border-radius:12px 12px 0 0;border-bottom:none}
.pv-frame{border:1px solid var(--line-2);border-top:none;
  border-radius:0 0 12px 12px;background:var(--surface-solid);
  overflow:hidden;transition:box-shadow .18s}
.pv-wrap:hover .pv-frame{box-shadow:0 8px 22px rgba(76,29,149,.13)}
.pv-cap{padding:6px 14px;background:linear-gradient(90deg,
  rgba(124,58,237,.10),rgba(219,39,119,.07));
  border-bottom:1px solid var(--line);font:600 11.5px/1.6 var(--sans);
  color:#6d28d9;letter-spacing:.04em}
.pv-cap::before{content:"示例展示 · ";opacity:.7}
.pv-body{padding:18px 16px;overflow:auto;font:16px/1.8 var(--sans);color:var(--fg)}
.pv-body>*:first-child{margin-top:0}
.pv-body>*:last-child{margin-bottom:0}
.pv-body table{margin:0}
.pv-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}

/* 示例框里 .box / .nl / .zt … 的基础样式 —— 放在这里，
   示例代码就只留要讲的那条规则 */
.pv-body .box{border:1px dashed var(--line-2);border-radius:10px;padding:10px 14px;
  background:rgba(255,255,255,.66)}
.pv-body .box p{margin:4px 0;padding:3px 8px;border-radius:6px}
.pv-body .box a{display:inline-block;margin:3px 0;padding:2px 9px;border-radius:6px;
  text-decoration:none;color:var(--fg);background:rgba(124,58,237,.07);
  border:1px solid transparent}
.pv-body .nl{margin:0;padding-left:22px}
.pv-body .nl li{padding:3px 8px;border-radius:6px}
.pv-body .zt{border-collapse:collapse;width:100%;font-size:14px;background:none;
  box-shadow:none;border-radius:0}
.pv-body .zt th,.pv-body .zt td{border:1px solid var(--line-2);padding:6px 12px;
  background:none}
.pv-body .zt th{background:rgba(124,58,237,.09)}
.pv-body .s8 p{margin:3px 0;padding:3px 8px;border-radius:6px;font-size:15px}
.pv-body .fx{margin:0;padding:12px 14px;background:rgba(255,255,255,.66);
  border-left:4px solid var(--blue);border-radius:0 10px 10px 0}
.pv-body .btn{display:inline-block;margin:4px 6px 4px 0;padding:8px 18px;
  border-radius:10px;color:#fff;cursor:pointer;
  background:linear-gradient(135deg,#7c3aed,#db2777);
  box-shadow:0 3px 12px rgba(124,58,237,.3);
  transition:filter .15s,transform .15s}
.pv-body .inp{margin-top:8px;padding:8px 12px;border:1px solid var(--line-2);
  border-radius:10px;outline:none;transition:box-shadow .15s;font:inherit;
  width:min(100%,260px);background:rgba(255,255,255,.9)}
.pv-body .tagp{display:inline-block;padding:4px 10px;border-radius:999px;
  background:var(--blue-soft);color:var(--blue);font-size:13px}
.pv-body .li2{margin:6px 0}

/* ================= 插图 ================= */
.fig{margin:20px 0;padding:0}
.fig img{display:block;width:100%;height:auto;max-width:620px;margin:0 auto;
  border:1px solid var(--line-2);border-radius:16px;background:#fff;padding:7px;
  box-shadow:0 4px 18px rgba(76,29,149,.10);
  transition:box-shadow .2s,transform .2s}
.fig:hover img{box-shadow:0 16px 40px rgba(76,29,149,.20);transform:translateY(-3px)}
.fig figcaption{margin:12px auto 0;max-width:620px;font-size:12.5px;
  color:var(--fg-3);line-height:1.75;text-align:center}
.fig figcaption b{color:var(--fg-2)}

/* ================= 颜色拾取器 ================= */
.picker{border:1px solid var(--line-2);border-radius:16px;overflow:hidden;
  background:var(--surface);margin:18px 0;
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
  box-shadow:0 4px 20px rgba(76,29,149,.10)}
.picker .pk-top{display:flex;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.picker .pk-swatch{flex:1 1 200px;min-height:156px;display:flex;align-items:flex-end;
  padding:14px 16px;background:#7c3aed;transition:background .12s}
.picker .pk-swatch span{font:700 15px/1.4 var(--mono);color:#fff;
  text-shadow:0 1px 4px rgba(0,0,0,.55)}
.picker .pk-out{flex:1 1 320px;padding:14px 16px;display:grid;gap:9px;
  align-content:center;background:rgba(255,255,255,.5)}
.picker .pk-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.picker .pk-row b{min-width:78px;color:var(--fg-3);font-weight:600;
  font-family:var(--mono);font-size:12px}
.picker .pk-row code{font-size:12.5px;background:rgba(255,255,255,.85)}
/* 十六进制那一行：放大强调 —— 它是最常被抄走的值 */
.picker .pk-row.pk-hex{align-items:baseline}
.picker .pk-row.pk-hex code{font-size:27px;font-weight:700;letter-spacing:.02em;
  padding:4px 12px;border-radius:10px;line-height:1.25;color:#4c1d95;
  background:linear-gradient(135deg,#ede9fe,#fce7f3);
  border:1px solid rgba(124,58,237,.35);
  text-shadow:0 1px 0 rgba(255,255,255,.7)}
.picker .pk-row .cp2{margin-left:auto;font-size:11.5px;color:var(--blue);cursor:pointer;
  border:1px solid rgba(124,58,237,.32);border-radius:7px;padding:1px 9px;
  background:rgba(255,255,255,.8)}
.picker .pk-row .cp2:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
.picker .pk-ctl{padding:14px 16px;display:grid;gap:12px}
.picker .pk-sl{display:grid;grid-template-columns:104px 1fr 70px;align-items:center;gap:12px;
  font-size:13px}
.picker .pk-sl label{font-family:var(--mono);font-size:12.5px;color:var(--fg-2)}
.picker .pk-sl input[type=range]{width:100%;height:22px;cursor:pointer;
  -webkit-appearance:none;appearance:none;background:transparent}
.picker .pk-sl input[type=range]::-webkit-slider-runnable-track{height:11px;
  border-radius:6px;border:1px solid var(--line-2);background:var(--tk,#e3e8f0)}
.picker .pk-sl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;
  width:19px;height:19px;margin-top:-5px;border-radius:50%;background:#fff;
  border:2px solid #7c3aed;box-shadow:0 1px 4px rgba(76,29,149,.4)}
.picker .pk-sl .val{font-family:var(--mono);font-size:12.5px;color:var(--fg-2);
  text-align:right}
.picker .pk-sw{display:flex;flex-wrap:wrap;gap:7px;padding:0 16px 14px}
.picker .pk-sw i{width:30px;height:30px;border-radius:9px;cursor:pointer;
  border:1px solid rgba(0,0,0,.14);transition:transform .12s}
.picker .pk-sw i:hover{transform:scale(1.16)}
.picker .pk-native{margin:0 16px 12px}
.picker .pk-note{padding:0 16px 15px;font-size:12px;color:var(--fg-3);line-height:1.7}
@media (max-width:560px){
  .picker .pk-row.pk-hex code{font-size:21px}
  .picker .pk-sl{grid-template-columns:78px 1fr 58px;gap:8px}
  .pv-body{padding:14px 12px;font-size:15px}
}
"""'''

t = t[:i_base] + NEW_BASE + "\n\n" + t[i_base_end:i_pv].lstrip("\n") + NEW_PV + t[i_pv_end:]
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  ✓ build_fe.py：BASE_CSS 改为读 fe_theme.css；PREVIEW_CSS 精简为组件样式")
