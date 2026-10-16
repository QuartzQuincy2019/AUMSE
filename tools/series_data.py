# -*- coding: utf-8 -*-
"""教程系列的**唯一数据源**。

改编号、加篇目、调系列说明，都只改这一个文件，其余靠脚本生成：

    tools/series_data.py        ← 本文件（编号 / 系列 / 标题 / 配色）
    tools/apply_series.py       按它改文件名与正文里的编号
    tools/build_series_css.py   按它生成 assets/series-theme.css
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
        "label": "Qt · Q",
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
        "label": "File · F",
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
}

# 首页分组顺序（FE 单独处理）
# 展示顺序由项目组长按组员进度手工排优先度 —— 会变，改这一行即可
ORDER = ["T", "F", "M", "R", "Q", "E"]

# ---------------------------------------------------------------- 篇目表
# (当前文件名, 新文件名, 系列, 新编号, 标题, 一句话说明, 星标)
PAGES = [
    # ---- M：课本主线（原 01~09）----
    ("01-c-arrays.html",              "m01-c-arrays.html",
     "M", "M01", "数组初步", "一排数据怎么存、怎么遍历", False),
    ("02-c-functions.html",           "m02-c-functions.html",
     "M", "M02", "函数初步", "重复的代码怎么打包复用", False),
    ("03-c-types.html",               "m03-c-types.html",
     "M", "M03", "类型概论", "数据在内存里占多宽、怎么解释", False),
    ("04-c-pointers.html",            "m04-c-pointers.html",
     "M", "M04", "指针初步", "地址是什么、怎么顺着地址改数据", False),
    ("05-memory.html",                "m05-memory.html",
     "M", "M05", "静态、动态内存与内存安全初步", "内存从哪来、怎么还、怎么不崩", False),
    ("06-class-struct.html",          "m06-class-struct.html",
     "M", "M06", "类、结构体", "数据和行为怎么打包、怎么保护", False),
    ("07-scope.html",                 "m07-scope.html",
     "M", "M07", "作用域、全局与局部变量", "一个名字能被谁看见、活多久", False),
    ("08-c-strings.html",             "m08-c-strings.html",
     "M", "M08", "C 风格字符串", "一串文字怎么存、\\0 为什么重要", False),
    ("09-vector-and-array.html",      "m09-vector-and-array.html",
     "M", "M09", "C++ 标准库里的「数组」", "重点：vector", False),

    # ---- Q：C++ 与 Qt ----
    ("10-std-and-namespace.html",     "q01-std-and-namespace.html",
     "Q", "Q01", "std 与命名空间初步", "从这里进入 C++：std:: 是什么、using 该不该用", False),
    ("q02-references.html",             "q02-references.html",
     "Q", "Q02", "C++ 的引用", "重点：引用是什么、与指针的关系、const 引用", True),

    # ---- E：补充练习 ----
    ("08-e01-recursion.html",         "e01-recursion.html",
     "E", "E01", "递归", "函数自己调用自己", False),
    ("08-e02-batch-and-cmd.html",     "e02-batch-and-cmd.html",
     "E", "E02", "批处理与命令提示符进阶", "把命令写成 .bat 一键重跑，接上 node / npm / python", False),
    ("e03-syntactic-sugar.html",      "e03-syntactic-sugar.html",
     "E", "E03", "语法糖", "arr[i] 与 arr[i][j] 背后的东西；跨语言的概念", False),

    # ---- F：文件操作基础 ----
    ("08-f01-command-prompt.html",    "f01-command-prompt.html",
     "F", "F01", "命令提示符（cmd）初步", "重点：常用命令（含 npm install）", True),
    ("08-f02-paths-and-env.html",     "f02-paths-and-env.html",
     "F", "F02", "相对文件路径与宏", "重点：相对路径、宏的广义定义", True),
    ("08-f03-compile-and-link.html",  "f03-compile-and-link.html",
     "F", "F03", "编译与链接、头文件与库", "重点：cpp→exe / 编译期与运行时 / 头文件与库；静态库为选修", True),

    # ---- T：核心理论 ----
    ("t01-mongolian-script-intro.html", "t01-mongolian-script-intro.html",
     "T", "T01", "初识回鹘蒙文", "拉丁转写 / 字形·连字·连写 / 连写文字系统 / 联合蒙文转写", True),
    ("t02-unicode-and-encoding.html",   "t02-unicode-and-encoding.html",
     "T", "T02", "Unicode 和编码", "重点：Unicode 的定义、编码与变长编码规则", True),
    ("t03-font-file-anatomy.html",      "t03-font-file-anatomy.html",
     "T", "T03", "字体文件结构大揭秘", "基于 Noto Sans Mongolian：表结构 / GSUB / 字形名里的音节", True),

    # ---- R：相关信息与理论 ----
    # R01 定位是「背景知识，了解即可」，所以不标重点；
    # R03 是 R 系列里最实用的一篇（字典序 / 自然序 / 中文排序），标重点。
    ("r01-font-design-metrics.html",    "r01-font-design-metrics.html",
     "R", "R01", "字体设计里的几个基本概念",
     "EM Square / 基线 / 上下悬线 / 大写字高与 x 字高；了解即可", False),
    ("r02-bubble-sort.html",            "r02-bubble-sort.html",
     "R", "R02", "冒泡排序与算法复杂度",
     "从「把一排数字排好」引入：冒泡及其两次优化 / O(n²) 与 O(n log n)", False),
    ("r03-collation.html",              "r03-collation.html",
     "R", "R03", "字典序、自然序与 QCollator",
     "重点：字符串怎么比大小 / 中文为什么排不对 / QCollator 拼音序与自然序", True),
]

# ---------------------------------------------------------------- 前端系列
FE_PAGES = [
    ("fe-01.html",     "FE-01",     "HTML 入门与标签语法",            "所写即所得、注释、空格无效性",              "HTML", False),
    ("fe-02.html",     "FE-02",     "HTML 常用标签",                 "p / i / strong / span / ul / div / form / table / a", "HTML", False),
    ("fe-03-F01.html", "FE-03-F01", "十六进制颜色模型、HSV 与 Alpha", "重点：十六进制颜色模型、Alpha 通道",         "CSS",  True),
    ("fe-03.html",     "FE-03",     "CSS 入门",                      "字体、背景色、字体色、装饰、阴影、cursor",   "CSS",  False),
    ("fe-04.html",     "FE-04",     "CSS 选择器语法",                 "标签/类/id、后代、属性限定、伪类、伪元素", "CSS", False),
    ("fe-05.html",     "FE-05",     "Display 与盒模型尺寸",           "block / inline-block / inline、边框、阴影、宽高", "CSS", False),
    ("fe-06.html",     "FE-06",     "Writing Mode 与溢出滚动",        "重点：writing-mode、word-break",             "CSS",  True),
    ("fe-07.html",     "FE-07",     "鼠标悬停与 transition",          "hover、过渡、缓动、常用动效",                "CSS",  False),
    ("fe-08.html",     "FE-08",     "JavaScript 语法初步",           "与 C/C++ 的相似性、console.log / var / alert / prompt", "JS", False),
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
