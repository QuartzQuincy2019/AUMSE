# -*- coding: utf-8 -*-
"""首页内联 CSS 里的语言徽章规则，改为从 tools/build_tg.py 生成。

问题
    语言徽章的颜色定义在**两处**：
      · tools/build_tg.py 的 LANG_CSS / LANG_DARK_CSS
        → 写进 assets/tg_L.css 与 tg_D.css，供 38 篇教程页使用
      · tools/make_pages.py 里的 HEAD 模板
        → 写进 index.html 的内联 <style>，供首页卡片使用
    首页是**全内联样式**（没有外链样式表，双击也能看），所以它加载不到
    tg_L/tg_D.css，只能自己再写一份。两边一旦不同步，
    同一个语言在首页与教程页就是两个颜色。

    这是本会话第 4 次处理「同一份数据散在多处」——
    前三次（篇目表、FE 系列定义、语言映射）都是改成派生，这次也一样。

做法
    从 build_tg.py 里**读出**颜色值（用正则解析那两段 CSS 字面量：
    `.lang.xx{background:#RRGGBB...}`），再由本脚本按首页自己的尺寸
    （字号 11px、行高 1.7、圆角 999px）拼出首页那套规则。

    为什么不直接整段照搬 LANG_CSS
      教程页那份是 11.5px / vertical-align:2px，首页卡片更紧凑，
      用的是 11px / vertical-align:1px。颜色要统一，尺寸各按各的场合。
      所以只取色值，版式仍由首页自己决定。

    暗色那套由 make_pages.py 放进它自己的 @media 块里（首页的暗色规则
    都集中在那一块），所以本模块只返回「不带 @media 包装」的内层规则。

用法
    由 make_pages.py 导入：build_light() / build_dark()
    也可单独运行做自检：python gen_home_lang_css.py
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)

# 顺序固定，输出才稳定（html / css / cpp / c 是用户指定的四门，
# qt 本轮新增，sh / py 是我补的，js 单独一套色）
ORDER = ["html", "css", "cpp", "c", "qt", "sh", "py", "js"]

# 首页这套的版式（与教程页不同，见文件头说明）
GEOM = ("display:inline-block;font:700 11px/1.7 var(--mono);\n"
        "  border-radius:999px;padding:0 9px;vertical-align:1px;\n"
        "  letter-spacing:.02em")
# 教程页的版式，用来从 LANG_CSS 里抠出「哪些属性是颜色、哪些是版式」——
# 实际上不需要：只要有 .lang.xx{…} 的整块，再挑出颜色属性即可。
# 这些是「视觉」属性，其余（字号、圆角、padding）属于版式，由首页自己定。
# background-image 是给渐变用的（Qt 没有单一 background 色）。
COLOR_PROPS = ("background", "background-image", "color",
               "border", "border-color")


def _load_tg():
    """取 build_tg.py 里的两段 CSS 字面量。"""
    p = os.path.join(TOOLS, "build_tg.py")
    t = io.open(p, encoding="utf-8").read()

    def grab(name):
        m = re.search(r'(?ms)^%s = """(.*?)"""' % name, t)
        if not m:
            raise SystemExit("  !! build_tg.py 里找不到 %s" % name)
        return m.group(1)

    return grab("LANG_CSS"), grab("LANG_DARK_CSS")


def _props(css, lang):
    """从 CSS 里取出 .lang.<lang>{…} 的属性串。"""
    m = re.search(r"\.lang\.%s\s*\{([^}]*)\}" % re.escape(lang), css)
    return m.group(1).strip() if m else ""


def _colors(prop_str):
    """只保留颜色相关属性，按固定顺序输出。"""
    out = []
    for part in prop_str.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        k = k.strip()
        if k in COLOR_PROPS:
            out.append("%s:%s" % (k, v.strip()))
    return ";".join(out)


def build_light():
    light, _ = _load_tg()
    lines = ["/* ---------- 语言标注（.lang）----------",
             "   颜色由 tools/gen_home_lang_css.py 从 build_tg.py 的",
             "   LANG_CSS 生成 —— 与教程页共用同一份色值，别手工改这里。 */",
             ".lang{%s;\n  color:#fff;border:1px solid transparent}" % GEOM]
    for lang in ORDER:
        c = _colors(_props(light, lang))
        if not c:
            continue
        note = ""
        if lang == "sh":
            note = "   /* Shell：用户未指定 */"
        elif lang == "py":
            note = "   /* Python：用户未指定 */"
        elif lang == "js":
            note = "   /* JS：正黄 + 深字 */"
        lines.append(".lang.%s{%s}%s" % (lang, c, note))
    return "\n".join(lines)


def build_dark():
    _, dark = _load_tg()
    lines = ["/* 语言标注（暗色）—— 与教程页同一套色值（tg_D.css） */",
             "  .lang{color:#12161d;border-color:transparent}"]
    for lang in ORDER:
        c = _colors(_props(dark, lang))
        if not c:
            continue
        if lang == "js":
            lines.append("  /* JS 在暗色下沿用同一个正黄底 + 深字 */")
        lines.append("  .lang.%s{%s}" % (lang, c))
    return "\n".join(lines)


def chip_colors():
    """给 noscript 兜底列表用的两张小表。

    返回 (INLINE, DARK_INK)：
        INLINE    语言显示名 → 亮色模式的底色
        DARK_INK  需要深字（而不是白字）的语言 → 深字色

    「哪些语言用深字」也从 LANG_CSS 里读 —— JS 那一条同时写了
    background 和 color，所以能自动判断，不必再写死 `if e == "JS"`。
    """
    light, _ = _load_tg()
    inline, dark_ink = {}, {}
    DISP = {"html": "HTML", "css": "CSS", "js": "JS", "cpp": "C++",
            "c": "C", "qt": "Qt", "sh": "Shell", "py": "Python"}
    for lang in ORDER:
        props = _props(light, lang)
        disp = DISP[lang]
        # ① 实色底（绝大部分）—— 返回 #rrggbb，供内联 style 用
        mb = re.search(r"background\s*:\s*(#[0-9a-fA-F]{6})", props)
        if mb:
            inline[disp] = mb.group(1)
        else:
            # ② 渐变底（Qt）—— 内联 style 里写 background-image 更简单，
            #    直接给字符串，让调用方自己决定是用 background 还是
            #    background-image。这里包一层 dict 区分两种来源。
            mg = re.search(r"background-image\s*:\s*(linear-gradient\([^}]*?\))", props)
            if mg:
                inline[disp] = {"image": mg.group(1)}
        mc = re.search(r"(?<!border-)color\s*:\s*(#[0-9a-fA-F]{6})", props)
        if mc:
            dark_ink[disp] = mc.group(1)
    return inline, dark_ink


def main():
    print("  浅色（首页内联）：")
    print(build_light())
    print()
    print("  暗色（放进首页的 @media 块）：")
    print(build_dark())
    print()
    inline, dark_ink = chip_colors()
    print("  noscript 用的内联表：")
    print("      INLINE   = %s" % inline)
    print("      DARK_INK = %s" % dark_ink)


if __name__ == "__main__":
    main()
