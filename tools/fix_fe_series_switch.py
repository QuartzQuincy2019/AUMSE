# -*- coding: utf-8 -*-
"""把 fe-data.js 的「全部系列」改成与 series-common.js **同构**的写法。

问题
----
FE 页尾的「全部系列」里的 R 一直是灰色的 ss-empty，点不动 ——
因为 fe-data.js 手写的那份 ALL_SERIES 里 R 的跳转目标是：

    { lab: '相关 · R', f: null, key: 'R' }

f 是 null，渲染时就走 `if (!s.f) → ss-empty` 分支。
而 R 其实有 3 篇（R01/R02/R03），series-common.js 那边就是好的。

根因：这份列表是**手抄的**，和 series-common.js 的
SERIES + ORDER + PAGES 是两套数据，抄的时候 R 还没写，留了 null。
上一轮我只把篇数改成现算，没动跳转目标，所以按钮还是灰的。

做法
----
不再维护两套数据。fe-data.js 改成和 series-common.js 完全同构：
    SERIES   系列 key → 标签
    ORDER    展示顺序
    SERIES_FILES  现有篇目（用来数篇数、取首篇做跳转目标）
渲染时按 ORDER 遍历，篇数为 0 才出 ss-empty。
这样 R 会自动指到 r01.html，以后任何系列
只要 SERIES_FILES 里有篇目就不会再灰。

用法：
    python fix_fe_series_switch.py --dry
    python fix_fe_series_switch.py
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
FE = os.path.join(A, "fe-data.js")

# 与 series-common.js 的 SERIES / ORDER **逐字一致**
NEW_DATA = """  /* ---------- 系列定义（与 assets/series-common.js 逐字一致） ----------
     原来这里手写了一份 ALL_SERIES，和 series-common.js 的
     SERIES + ORDER + PAGES 是两套数据 —— 于是 R 抄的时候留了 f: null，
     FE 页尾的「相关 · R」永远是灰色点不动的 ss-empty，而 R 其实有 3 篇。
     现在改成同构：只留系列定义 + 现有篇目，渲染时现算篇数与跳转目标。 */
  var SERIES = {
    T: { label: '理论 · T' },
    M: { label: '课本 · M' },
    Q: { label: 'C++&Qt · Q' },
    E: { label: 'Extra · E' },
    F: { label: '文件 · F' },
    R: { label: '相关 · R' },
    FE: { label: '前端 · FE' }
  };

  /* 展示顺序，必须与 tools/series_data.py 的 ORDER 一致 */
  var ORDER = ['T', 'F', 'M', 'R', 'Q', 'E', 'FE'];

  /* 现存的篇目（除 FE 自己，FE 那份在页面数据 P.series 里）。
     用来数篇数、并取每个系列的首篇作为跳转目标。 */
  var SERIES_FILES = [
    't01.html','t02.html',
    't03.html',
    'f01.html','f02.html',
    'f03.html',
    'm01.html','m02.html','m03.html',
    'm04.html','m05.html','m06.html',
    'm07.html','m08.html','m09.html',
    'r01.html','r02.html',
    'r03.html',
    'q01.html','q02.html',
    'q03.html','q04.html',
    'e01.html','e02.html',
    'e03.html',
    'fe-01.html','fe-02.html','r04.html','fe-03.html','fe-04.html',
    'fe-05.html','fe-06.html','fe-07.html','fe-08.html'
  ];

  /* fe- 开头的一律算 FE（r04.html 也是 FE），其余按首字母。 */
  function seriesKeyOf(file) {
    if (/^fe-/.test(file)) return 'FE';
    return file.charAt(0).toUpperCase();
  }

  function filesOfSeries(key) {
    if (key === 'FE') {
      return (typeof P !== 'undefined' && P.series)
        ? P.series.map(function (s) { return s.file; }) : [];
    }
    return SERIES_FILES.filter(function (f) {
      return seriesKeyOf(f) === key;
    });
  }
"""


def main():
    dry = "--dry" in sys.argv
    t = io.open(FE, encoding="utf-8").read()

    # ---- 1. 用新的数据段替换掉旧的 helper + ALL_SERIES ----
    start = t.find("  /* 「全部系列」的篇数**现算**")
    if start < 0:
        start = t.find("  /* ---------- 系列定义")
    end = t.find("  function buildSeriesSwitch()")
    if start < 0 or end < 0 or end <= start:
        print("  !! 定位失败（start=%s end=%s）" % (start, end))
        return
    print("  替换数据段：%d 字符 → %d 字符" % (end - start, len(NEW_DATA)))
    t2 = t[:start] + NEW_DATA + "\n" + t[end:]

    # ---- 2. 重写 buildSeriesSwitch ----
    i = t2.find("  function buildSeriesSwitch()")
    j = t2.find("  function build()")
    if i < 0 or j < 0:
        print("  !! 找不到 buildSeriesSwitch / build")
        return
    NEW_FN = """  function buildSeriesSwitch() {
    var box = el('div', 's-nav-switch');
    box.appendChild(el('b', null, '全部系列'));
    box.appendChild(document.createTextNode('\\u3000'));
    ORDER.forEach(function (k) {
      var list = filesOfSeries(k);
      var lab = (SERIES[k] ? SERIES[k].label : k) +
                '（' + list.length + ' 篇' + (list.length ? '' : '，暂空') + '）';
      if (k === 'FE') {                       /* FE 页自己就是当前项 */
        box.appendChild(el('span', 'ss-cur', lab + '\\u3000当前'));
        return;
      }
      if (!list.length) {                     /* 真的没有篇目才灰 */
        box.appendChild(el('span', 'ss-empty', lab));
        return;
      }
      var a = el('a', 'ss-link', lab);        /* 首篇作为跳转目标 */
      a.href = list[0];
      box.appendChild(a);
    });
    return box;
  }

"""
    print("  重写 buildSeriesSwitch：%d 字符 → %d 字符" % (j - i, len(NEW_FN)))
    t2 = t2[:i] + NEW_FN + t2[j:]

    if not dry:
        io.open(FE, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  %s" % ("[dry-run]" if dry else "已写入 fe-data.js"))


if __name__ == "__main__":
    main()
