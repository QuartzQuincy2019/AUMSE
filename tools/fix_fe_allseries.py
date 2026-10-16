# -*- coding: utf-8 -*-
"""修掉 fe-data.js 里「全部系列」的过期篇数，并改成从篇目表现算。

问题
----
fe-data.js 的 ALL_SERIES 把每个系列的篇数**写死**在 n 字段里：

    { lab: 'C++&Qt · Q', f: '…', n: 1 }        ← Q 早就 4 篇了
    { lab: 'Extra · E',  f: '…', n: 2 }        ← E 实际 3 篇
    { lab: '前端 · FE',  f: '…', n: 8, cur: true }

系列一长，这些数字没人想起来改 —— FE 页尾于是显示
「C++&Qt · Q（1 篇）」「Extra · E（2 篇）」「前端 · FE（8 篇）」，
全是旧的。（R 那项本来就写 n:0，显示「暂空」，属于第三种错。）

做法
----
1. 篇目表在 fe-data.js 里已经有了（每个页面数据里的 P.series），
   但那只覆盖 FE 自己。所以这里补一份**已知篇目的文件名清单**，
   与 series-common.js 的 PAGES 一致，然后按文件名首字母分组现算。
2. 把 ALL_SERIES 的 n 全部删掉，改成渲染前现算覆盖。
   这样以后加篇目，篇数自动跟着走，不会再出现写死的旧数字。

用法：
    python fix_fe_allseries.py --dry
    python fix_fe_allseries.py
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

# 非 FE 各篇的编号前缀 → 系列 key
#   t01… → T ，f01… → F ，m01… → M ，r01… → R ，q01… → Q ，e01… → E
# 注意 fe-03-F01.html 属于 FE，不能按 f 开头算成 F。
HELPER = """
  /* 「全部系列」的篇数**现算**，不写死。
     写死的代价：系列一长就没人想起来改 —— 之前这里一直显示
     Q（1 篇）/ E（2 篇）/ FE（8 篇），全是旧的。
     规则：看文件名前缀；fe- 开头的一律算 FE（fe-03-F01.html 也是 FE），
     其余按第一个字母对应系列。 */
  var SERIES_FILES = [
    't01-mongolian-script-intro.html','t02-unicode-and-encoding.html',
    't03-font-file-anatomy.html',
    'f01-command-prompt.html','f02-paths-and-env.html',
    'f03-compile-and-link.html',
    'm01-c-arrays.html','m02-c-functions.html','m03-c-types.html',
    'm04-c-pointers.html','m05-memory.html','m06-class-struct.html',
    'm07-scope.html','m08-c-strings.html','m09-vector-and-array.html',
    'r01-font-design-metrics.html','r02-bubble-sort.html',
    'r03-collation.html',
    'q01-std-and-namespace.html','q02-references.html',
    'q03-pointers-to-objects.html','q04-interfaces.html',
    'e01-recursion.html','e02-batch-and-cmd.html',
    'e03-syntactic-sugar.html',
    'fe-01.html','fe-02.html','fe-03-F01.html','fe-03.html','fe-04.html',
    'fe-05.html','fe-06.html','fe-07.html','fe-08.html'
  ];

  function seriesKeyOf(file) {
    if (/^fe-/.test(file)) return 'FE';
    return file.charAt(0).toUpperCase();
  }

  function seriesCount(key) {
    if (key === 'FE') {
      /* FE 自己的篇目表就是权威来源 */
      return (typeof P !== 'undefined' && P.series) ? P.series.length : 0;
    }
    var n = 0;
    SERIES_FILES.forEach(function (f) {
      if (seriesKeyOf(f) === key) n++;
    });
    return n;
  }
"""

OLD_BLOCK = re.compile(r"( *)var ALL_SERIES = \[(.*?)\n\s*\];", re.S)


def main():
    dry = "--dry" in sys.argv
    t = io.open(FE, encoding="utf-8").read()

    m = OLD_BLOCK.search(t)
    if not m:
        print("  !! 没找到 ALL_SERIES 数组")
        return

    entries = re.findall(r"\{\s*lab:\s*'([^']*)',\s*f:\s*(null|'[^']*')"
                         r"(?:,\s*n:\s*\d+)?(?:,\s*cur:\s*true)?\s*\}", t)
    if "var ALL_SERIES" in t and "%s" not in t:
        print("  现有 ALL_SERIES 条目：")
        for lab, f in entries:
            print("      %-18s %s" % (lab, f))
    else:
        print("  条目解析异常，退出")
        return

    # key 从 lab 里最后那个字母取（'C++&Qt · Q' → Q，'前端 · FE' → FE）
    def key_of(lab):
        mm = re.search(r'·\s*([A-Za-z]+)\s*$', lab)
        return mm.group(1).upper() if mm else lab

    lines = ["  var ALL_SERIES = ["]
    for i, (lab, f) in enumerate(entries):
        k = key_of(lab)
        cur = ", cur: true" if lab.startswith("前端") else ""
        lines.append("    { lab: '%s',%sf: %s, key: '%s'%s }%s"
                     % (lab, " " * max(1, 16 - len(lab)), f, k, cur,
                        "," if i < len(entries) - 1 else ""))
    lines.append("  ];")
    new_arr = "\n".join(lines)

    # 渲染处：n 改成现算
    t2 = t[:m.start()] + new_arr + t[m.end():]

    old_render = "var lab = s.lab + '（' + s.n + ' 篇' + (s.n ? '' : '，暂空') + '）';"
    new_render = ("var cnt = seriesCount(s.key);\n"
                  "        var lab = s.lab + '（' + cnt + ' 篇'"
                  " + (cnt ? '' : '，暂空') + '）';")
    if old_render in t2:
        t2 = t2.replace(old_render, new_render, 1)
        print("  渲染处：s.n → seriesCount(s.key)（现算）")
    else:
        print("  !! 渲染处未匹配，需手工看")

    # helper 插在 ALL_SERIES 之前
    t2 = t2.replace("  /* 「全部系列」：与其它系列页尾一致。",
                    HELPER + "\n  /* 「全部系列」：与其它系列页尾一致。", 1)

    print()
    print("  新 ALL_SERIES：")
    for l in lines:
        print("  " + l)
    print()
    if not dry:
        io.open(FE, "w", encoding="utf-8", newline="").write(t2)
        print("  已写入 fe-data.js")
    else:
        print("  [dry-run]")


if __name__ == "__main__":
    main()
