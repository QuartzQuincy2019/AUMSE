# -*- coding: utf-8 -*-
"""教程系列的**唯一数据源**。

改编号、加篇目、调系列说明，都只改这一个文件，其余靠脚本生成：

    tools/series_data.py        ← 本文件（编号 / 系列 / 标题 / 配色）
    tools/apply_series.py       按它改文件名与正文里的编号
    tools/build_series_css.py   按它生成 assets/css/series-theme.css
    tools/make_pages.py         按它生成首页卡片（import 本文件）

系列一览
    T  Theory      核心理论和底层逻辑
    M  Main Line   课本内容速成与补充     原 01~09
    Q  Qt/C++      C++ 开发事项和 Qt 基础  原 10
    E  Extra       补充练习              原 08-E01 / 08-E02
    F  File        文件操作基础           原 08-F01 ~ 08-F03
    R  Related     相关信息与理论          原为空，现 R01~R03
    FE Frontend    前端系列（独立的 HTML/CSS 外观，不套用本文件的系列主题）
"""

# ---------------------------------------------------------------- 系列定义
# key: 内部标识（写进 body[data-series]）
# num: 编号前缀        label: 顶部常驻条上的文字
# css: 主题变量命名空间（生成 CSS 时用）
SERIES = {
    "T": {
        "name": "Theory",
        "num": "T",
        "banner": "T 系列 · 核心理论和底层逻辑",
        "label": "理论 · T",
        "desc": "文字、编码与字体文件：做回鹘蒙文必须先弄懂的东西",
        "cls": "tseries",
        # 主色（亮色 / 暗色）
        "c1": "#fbe8bf", "c2": "#fdf3dc", "c3": "#9a6b0a", "c4": "#8a6208",
        "ink": "#3a2f14",
        "d1": "#16120a", "d2": "#2b2210", "d3": "#e0b23f", "d4": "#f0cc72",
        "dink": "#ece3cd",
    },
    "M": {
        "name": "Main",
        "num": "M",
        "banner": "M 系列 · 课本内容速成与补充",
        "label": "课本 · M",
        "desc": "C / C++ 主线：从数组到 vector，贴合课本进度",
        "cls": "mseries",
        "c1": "#dbe3ef", "c2": "#eef2f8", "c3": "#2c4a7c", "c4": "#1b3358",
        "ink": "#141d2b",
        "d1": "#0b1018", "d2": "#131b28", "d3": "#6e93c8", "d4": "#9db8dc",
        "dink": "#d8e0ec",
    },
    "Q": {
        "name": "Qt",
        "num": "Q",
        "banner": "Q 系列 · C++ 开发事项和 Qt 基础",
        "label": "C++&Qt · Q",
        "desc": "",   # 不写死：该系列将来会大量补充
        "cls": "qseries",
        "c1": "#dff2ec", "c2": "#eefaf6", "c3": "#0c8261", "c4": "#0a7157",
        "ink": "#10322a",
        "d1": "#0a1614", "d2": "#12231f", "d3": "#3fc4a0", "d4": "#7adfc4",
        "dink": "#d6f0e8",
    },
    "E": {
        "name": "Extra",
        "num": "E",
        "banner": "E 系列 · 补充练习与进阶",
        "label": "Extra · E",
        "desc": "",   # 不写死：该系列将来会大量补充
        "cls": "eseries",
        "c1": "#f3e4f7", "c2": "#faf1fd", "c3": "#8b3fbe", "c4": "#67289a",
        "ink": "#2e1638",
        "d1": "#150d1c", "d2": "#22152c", "d3": "#b877e0", "d4": "#d6a6f2",
        "dink": "#e8d8f2",
    },
    "F": {
        "name": "File",
        "num": "F",
        "banner": "F 系列 · 文件操作基础",
        "label": "文件 · F",
        "desc": "",   # 不写死：该系列将来会大量补充
        "cls": "fseries",
        # F 保持原先的蓝色皮肤（用户要求「为 F 保留之前的样式」）。
        # keep_legacy 让 build_series_css.py 不生成整套主题，只改顶部条；
        # 但配色键仍然要给 —— 实色覆盖表要用它算「当前篇」这类高亮。
        "keep_legacy": True,
        "c1": "#eef3f9", "c2": "#ffffff", "c3": "#1f6feb", "c4": "#14539f",
        "ink": "#16283c",
        "d1": "#0d1420", "d2": "#162130", "d3": "#5aa2f0", "d4": "#8cc0ff",
        "dink": "#dae6f4",
    },
    "R": {
        "name": "Related",
        "num": "R",
        "banner": "R 系列 · 相关信息与理论",
        "label": "相关 · R",
        "desc": "Highly-Related Information and Theories",
        "cls": "rseries",
        "c1": "#fbdfe0", "c2": "#fdf0f0", "c3": "#d1435b", "c4": "#a02b40",
        "ink": "#3a141b",
        "d1": "#1a0e11", "d2": "#291619", "d3": "#ef7288", "d4": "#f7a8b6",
        "dink": "#f2d8dd",
    },

    # FE：前端系列。外观自成一系（走 fe_base.css / fe-dark.css，
    # 不由 build_series_css.py 从本表生成主题），所以这里**只给
    # 页面与导航要用的字段**，不写 c1~d4 / ink / dink 那套主题色。
    "FE": {
        "name": "FrontEnd",
        "num": "FE",
        "banner": "FE 系列 · 前端基础",
        "label": "前端 · FE",
        "desc": "HTML、CSS 与 JavaScript：页面结构、样式与脚本",
        "cls": "feseries",
    },

    # A：进阶。项目组长自用，同样放进教程站，**排在 FE 之后**。
    # 黑金配色自成一套；主题不在这里的 TPL 里生成，
    # 由 build_series_css.py 末尾单独出（TPL 换色 + A_EXTRA 金饰）。
    "A": {
        "name": "Advanced",
        "num": "A",
        "banner": "A 系列 · 进阶",
        "label": "进阶 · A",
        "desc": "排版引擎、字体内部与工程化",
        "cls": "aseries",
        "c1": "#faf6ea", "c2": "#fffdf6", "c3": "#8a6410", "c4": "#5f450a",
        "ink": "#1a1509",
        "d1": "#0b0906", "d2": "#171106", "d3": "#c8a03a", "d4": "#e8c877",
        "dink": "#f0e4c6",
    },
}
# 首页分组顺序（FE 单独处理）
# 展示顺序由项目组长按组员进度手工排优先度 —— 会变，改这一行即可
ORDER = ["T", "F", "M", "R", "Q", "E"]

# 遍历**全部**系列（含 FE）时用这个。
# ORDER 不含 FE 是有意的 —— 主题生成那套脚本依赖它跳过 FE；
# 但首页分组与篇目表生成需要 FE，所以单列一个。
PAGE_ORDER = ORDER + ["FE", "A"]

# ---------------------------------------------------------------- 篇目表
# (当前文件名, 新文件名, 系列, 新编号, 标题, 一句话说明, 星标)
PAGES = [
    # 第一个字段是磁盘上的当前文件名，第二个是目标文件名 —— 两者现已相等，
    # 因为短名重构已经落盘。短名规则：<编号小写>.html（M01 → m01.html，
    # 与 FE 的 fe-NN 一致）。加篇目时直接按这个规则起名。

    # ---- M：课本主线（原 01~09）----
    ("m01.html", "m01.html",
     "M", "M01", "数组初步", "一排数据怎么存、怎么遍历", False),
    ("m02.html", "m02.html",
     "M", "M02", "函数初步", "重复的代码怎么打包复用", False),
    ("m03.html", "m03.html",
     "M", "M03", "类型概论", "数据在内存里占多宽、怎么解释", False),
    ("m04.html", "m04.html",
     "M", "M04", "指针初步", "地址是什么、怎么顺着地址改数据", False),
    ("m05.html", "m05.html",
     "M", "M05", "静态、动态内存与内存安全初步", "内存从哪来、怎么还、怎么不崩", False),
    ("m06.html", "m06.html",
     "M", "M06", "类、结构体", "数据和行为怎么打包、怎么保护", False),
    ("m07.html", "m07.html",
     "M", "M07", "作用域、全局与局部变量", "一个名字能被谁看见、活多久", False),
    ("m08.html", "m08.html",
     "M", "M08", "C 风格字符串", "一串文字怎么存、\\0 为什么重要", False),
    ("m09.html", "m09.html",
     "M", "M09", "vector 和 array", "重点：vector", False),
    ("m10.html", "m10.html",
     "M", "M10", "抽象基类和纯虚函数",
     "先学完「多态与虚函数」再读；设计初衷 + 本项目类型树", False),

    # ---- Q：C++ 与 Qt ----
    # 标题约定（从 Q09 起）：小节标题用**正式表述** ——
    #   名词短语，或「对象：属性」结构；
    #   不用「……是什么」「怎么……」「为什么……」这类口语问句，
    #   也不用「它到底」「干的事」这类说法。
    #   「常见错误」「一页速查」是站内固定栏目名，所有篇目统一，保留。
    ("q01.html", "q01.html",
     "Q", "Q01", "std 与命名空间初步", "从这里进入 C++：std:: 是什么、using 该不该用", False),
    ("q02.html", "q02.html",
     "Q", "Q02", "C++ 的引用", "重点：引用是什么、与指针的关系", True),
    ("q03.html", "q03.html",
     "Q", "Q03", "指针进阶：指向对象的指针与引用", "按引用传递的必要性；传递指针与传递引用的分工", True),
    ("q04.html", "q04.html",
     "Q", "Q04", "接口", "接口的定义与常见用途；Actor 的 public 区", True),
    ("q05.html", "q05.html",
     "Q", "Q05", "单一职责原则和开闭原则",
     "一个类该有多大、该多难被改；SRP 与 OCP 的联系", True),
    ("q06.html", "q06.html",
     "Q", "Q06", "组件化编程与解耦合", "什么叫耦合、高耦合的代价、组件化的三条准则", True),
    ("q07.html", "q07.html",
     "Q", "Q07", "代码复用性和扩展性", "从一道作业题看：数据与逻辑分开、给反复出现的东西一个类型", True),
    ("q08.html", "q08.html",
     "Q", "Q08", "接口隔离原则", "调用方不该被迫依赖用不到的方法；接口按谁来用切", True),
    ("q09.html", "q09.html",
     "Q", "Q09", "指针进阶：函数指针",
     "函数指针与成员函数指针；Qt connect 那一句的四个参数", True),
    ("q10.html", "q10.html",
     "Q", "Q10", "智能指针",
     "重点：泄漏、重复释放、悬空指针怎么被挡掉；unique / shared / weak", True),
    ("q11.html", "q11.html",
     "Q", "Q11", "线程与互斥锁",
     "从线程讲到锁：进程与线程、为什么要多线程、竞态与临界区", False),

    # ---- E：补充练习 ----
    ("e01.html", "e01.html",
     "E", "E01", "递归", "函数自己调用自己", False),
    ("e02.html", "e02.html",
     "E", "E02", "批处理与命令提示符进阶", "把命令写成 .bat 一键重跑，接上 node / npm / python", False),
    ("e03.html", "e03.html",
     "E", "E03", "语法糖", "arr[i] 与 arr[i][j] 背后的东西；跨语言的概念", False),
    # E04 原为 R02（冒泡排序），2026-10 起归入 E 系列
    ("e04.html", "e04.html",
     "E", "E04", "冒泡排序与算法复杂度",
     "从「把一排数字排好」引入：冒泡及其两次优化 / O(n²) 与 O(n log n)", False),

    # ---- F：文件操作基础 ----
    ("f01.html", "f01.html",
     "F", "F01", "命令提示符（cmd）初步", "重点：常用命令（含 npm install）", True),
    ("f02.html", "f02.html",
     "F", "F02", "相对文件路径与宏", "重点：相对路径、宏的广义定义", True),
    ("f03.html", "f03.html",
     "F", "F03", "编译与链接、头文件与库", "重点：cpp→exe / 编译期与运行时 / 头文件与文件依赖", True),
    ("f04.html", "f04.html",
     "F", "F04", "构建系统生成器与构建工具",
     "重点：CMake / qmake、Makefile / build.ninja / .sln、Ninja / Make / MSBuild 四层等价关系", True),

    # ---- T：核心理论 ----
    ("t01.html", "t01.html",
     "T", "T01", "初识回鹘蒙文", "拉丁转写 / 字形·连字·连写 / 连写文字系统 / 联合蒙文转写", True),
    ("t02.html", "t02.html",
     "T", "T02", "Unicode 和编码", "重点：Unicode 的定义、编码与变长编码规则", True),
    ("t03.html", "t03.html",
     "T", "T03", "字体文件结构大揭秘", "基于 Noto Sans Mongolian：表结构 / GSUB / 字形名里的音节", True),

    # ---- R：相关信息与理论 ----
    # R01 定位是「背景知识，了解即可」，所以不标重点；
    # R02（原 R03）是 R 系列里最实用的一篇（字典序 / 自然序 / 中文排序），标重点；
    # R03（原 R04，再往前是 FE-03-F01）讲十六进制颜色模型，标重点。
    # 原 R02（冒泡排序）已移入 E 系列，成为 E04。
    ("r01.html", "r01.html",
     "R", "R01", "字体设计里的几个基本概念",
     "EM Square / 基线 / 上下悬线 / 大写字高与 x 字高；了解即可", False),
    ("r02.html", "r02.html",
     "R", "R02", "字典序、自然序与 QCollator",
     "重点：字符串怎么比大小 / 中文为什么排不对 / QCollator 拼音序与自然序", True),
    ("r03.html", "r03.html",
     "R", "R03", "十六进制颜色模型、HSV 与 Alpha",
     "重点：十六进制颜色模型、Alpha 通道", True),
    ("r04.html", "r04.html",
     "R", "R04", "国际音标（IPA）",
     "重点：IPA 与「英语音标」的区别、/e/ 与 /ɛ/、宽式与严式标音", True),

    # ---- A：进阶（项目组长自用，排在 FE 之后）----
    ("a01.html", "a01.html",
     "A", "A01", "HarfBuzz 及其基础用法",
     "从字符到字形：缓冲区、整形、簇、特性，以及落到 Qt 的那一步", False),
    ("a02.html", "a02.html",
     "A", "A02", "如何利用 HarfBuzz 在 Qt 上绘制字形",
     "字形号、advance 与 offset 怎么变成屏幕像素：QTextLayout、QGlyphRun、轮廓与竖排", True),
]

# ---------------------------------------------------------------- 前端系列
FE_PAGES = [
    ("fe-01.html",     "FE-01",     "HTML 入门与标签语法",            "所写即所得、注释、空格无效性",              ["HTML"], False),
    ("fe-02.html",     "FE-02",     "HTML 常用标签",                 "p / i / strong / span / ul / div / form / table / a", ["HTML"], False),
    ("fe-03.html",     "FE-03",     "CSS 入门",                      "字体、背景色、字体色、装饰、阴影、cursor",   ["CSS"],  False),
    ("fe-04.html",     "FE-04",     "CSS 选择器语法",                 "标签/类/id、后代、属性限定、伪类、伪元素", ["CSS"], False),
    ("fe-05.html",     "FE-05",     "Display 与盒模型尺寸",           "block / inline-block / inline、边框、阴影、宽高", ["CSS"], False),
    ("fe-06.html",     "FE-06",     "Writing Mode 与溢出滚动",        "重点：writing-mode、word-break",             ["CSS"],  True),
    ("fe-07.html",     "FE-07",     "鼠标悬停与 transition",          "hover、过渡、缓动、常用动效",                ["CSS"],  False),
    ("fe-08.html",     "FE-08",     "JavaScript 语法初步",           "与 C/C++ 的相似性、console.log / var / alert / prompt", ["JS"], False),
    ("fe-09.html",     "FE-09",     "DOM 操作基础",
     "getElementById / createElement / append；DOM 树与 Qt addWidget 的对照", ["Qt", "JS"], True),
]

# ---------------------------------------------------------------- 派生量
# 旧编号 → 新编号（只替换「按编号引用」的写法，见 apply_series.py 的白名单）
OLD_NUM = {
    "01": "M01", "02": "M02", "03": "M03", "04": "M04", "05": "M05",
    "06": "M06", "07": "M07", "08": "M08", "09": "M09", "10": "Q01",
    "08-E01": "E01", "08-E02": "E02",
    "08-F01": "F01", "08-F02": "F02", "08-F03": "F03",
}

# 旧文件名 → 新文件名
RENAME = {old: new for old, new, *_ in PAGES if old != new}

# 新文件名 → 篇目元组
BY_FILE = {new: p for p in PAGES for new in [p[1]]}


def pages_of(sk):
    """某个系列的全部篇目，按编号排序。"""
    return [p for p in PAGES if p[2] == sk]


def summary():
    lines = []
    for sk in ORDER:
        s = SERIES[sk]
        ps = pages_of(sk)
        lines.append("  %-2s %-9s %-26s %d 篇  %s"
                     % (sk, s["name"], s["banner"], len(ps),
                        "、".join(p[3] for p in ps) if ps else "（空）"))
    lines.append("  FE Frontend  前端系列（独立外观）                    %d 篇"
                 % len(FE_PAGES))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("=== 系列 ===")
    print(summary())
    print()
    print("=== 改名（%d 个）===" % len(RENAME))
    for a, b in RENAME.items():
        print("  %-36s → %s" % (a, b))


# ------------------------------------------------------------ 语言标注
# 每篇教程「用的是什么语言」，供语言徽章（.lang）与首页卡片使用。
#
#   SERIES_LANG  按系列给默认语言（这几组的主线语言各自统一）
#   PAGE_LANG    单篇覆盖（系列默认不合适时）
#   LANG_CLS     语言 → CSS 类名
#   LANG_OF      导出的**权威表**：文件名 → (显示名, class)
#
# FE 各篇的语言不在上表里 —— 它本来就写在 FE_PAGES 的第 5 项，
# 直接从那里取，避免又造一份副本。
SERIES_LANG = {
    # T 系列不加语言徽章 —— 正文讲的是文字与编码，没有「用什么语言写」这回事
    "T": [],
    "F": ["Shell"],   # F01/F02 命令提示符、F03 编译与链接的工具链
    "M": ["C"],       # 课本前半部分是 C（M09 例外，见下）
    "Q": ["C++"],
    "R": ["C++"],
    "E": ["C++"],     # E01/E03 是 C++，E02 见下面的单篇覆盖
    # A01 讲 HarfBuzz 的 C++ 接口；A 系列以后可能混入别的语言，
    # 到时候用 PAGE_LANG 单篇覆盖
    "A": ["C++"],
}

# 单篇的语言与系列默认不同时，用这里**整篇替换**（不是追加）——
# 若做成追加，想「拿掉系列默认语言」就没法表达了。
PAGE_LANG = {
    # M09 讲 vector / array —— 那是 C++ 标准库，不是 C
    "m09.html": ["C++"],
    # M10 讲抽象基类 / 纯虚函数 —— C++ 的类机制，M 系列默认的 C 表达不了
    "m10.html": ["C++"],
    # E02 是批处理（.bat），与 E 系列默认的 C++ 不同
    "e02.html": ["Shell"],
    # R01 只讲字体度量（EM Square / x 字高 / 行高），一个编程语言例子都没有；
    # 它讲的东西正是 CSS 关心的，所以归 CSS（与首页卡片一致）。
    "r01.html": ["CSS"],
    # R03 讲蒙古文排序，正文用的是 Qt 的 QString 相关接口
    "r02.html": ["Qt"],
    # R04 讲国际音标，一个编程语言例子都没有 —— 与 T 系列同理，整篇不要徽章
    "r04.html": [],
    # FE-09 同时是 Qt 与 JS：DOM 那半是 JS，与 Qt 对照那半是 Qt
    "fe-09.html": ["Qt", "JS"],
    # R03（原 R04，再往前是 FE-03-F01）：讲颜色模型，语言标识是 CSS
    "r03.html": ["CSS"],
}
LANG_CLS = {"HTML": "html", "CSS": "css", "JS": "js",
            "C++": "cpp", "C": "c", "Shell": "sh", "Python": "py",
            "Qt": "qt"}


def _lang_of_pages():
    """文件名 → 语言列表。"""
    out = {}
    for key in PAGE_ORDER:
        if key == "FE":
            continue
        for p in pages_of(key):
            fn = p[1]
            out[fn] = list(PAGE_LANG.get(fn, SERIES_LANG[key]))
    for p in FE_PAGES:
        out[p[0]] = list(p[4]) if p[4] else []   # FE_PAGES 第 5 项，现在是列表
    return out


# 文件名 → [(显示名, class), …]。**空列表**表示这篇不显示语言徽章。
LANG_OF = {fn: [(lang, LANG_CLS[lang]) for lang in langs]
           for fn, langs in _lang_of_pages().items()}
