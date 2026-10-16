# -*- coding: utf-8 -*-
"""Q07 第 1 步：去掉正文里所有 key-h，并重排小节编号。

用户要求
    · 只在大标题设 "*"，**内部不要乱设 "*"** —— 删掉所有内部 key-h
    · 标题要正式、学术，不要口语化

    页面 <h1> 的那个 * 来自 build_page.py 的 --star，与内部 key-h 无关，
    所以删掉内部三个 key-h 之后，大标题的 * 仍然保留。

各节标题的改写（口语化 → 书面）
    1  先说数学：一切归结为一个距离      → 数学模型：点到塔心的距离判定
    2  选择题里说「合适的数据类型」        → 数据类型的选择
    3  初学者的写法：把数字写死在 main 里  → 直接实现：题面数据内嵌于主函数
    4  老师改题了                        → 需求变更的影响范围
    5  把「点」变成一个类型               → 第一层抽象：将坐标封装为 Point
    6  把「塔」和「查询」也拆开            → 第二层抽象：Tower 与查询接口的分离
    7  数据搬出去，main 就只剩流程         → 数据与逻辑分离
    8  提高扩展性的原则和要点              → 提高可扩展性的原则
    9  两种写法摆在一起                   → 两种实现的对照
    10 一页速查                          → 小结

新增的小节（本轮要补的内容）见第 2 步脚本。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\_q07_body.html"

RENAME = {
    "s1":  "数学模型：点到塔心的距离判定",
    "s2":  "数据类型的选择",
    "s3":  "直接实现：题面数据内嵌于主函数",
    "s4":  "需求变更的影响范围",
    "s5":  "第一层抽象：将坐标封装为 Point",
    "s6":  "第二层抽象：塔与查询的分离",
    "s7":  "数据与逻辑分离",
    "s8":  "提高可扩展性的原则",
    "s9":  "两种实现的对照",
    "s10": "小结",
}


def main():
    dry = "--dry" in sys.argv
    t = io.open(P, encoding="utf-8").read()

    # ---- 1. 去掉所有 key-h 与大标题之外的 ★ ----
    n_before = t.count("key-h")
    # <h2 id="s3" class="key-h"><span class="key-mark" …>★</span>  →  <h2 id="s3">
    t = re.sub(r'<h2 id="(s\d+)" class="key-h">'
               r'<span class="key-mark" title="重点内容">★</span>',
               r'<h2 id="\1">', t)
    t = re.sub(r'<h2 id="(s\d+)" class="key-h">', r'<h2 id="\1">', t)
    print("  删除 key-h：%d 处 → 剩 %d 处" % (n_before, t.count("key-h")))
    print("  剩余 ★：%d 个（应为 0）" % t.count("★"))

    # ---- 2. 改写标题 ----
    for sid, title in RENAME.items():
        pat = re.compile(r'<h2 id="%s"><span class="n">(\d+)</span>.*?</h2>'
                         % sid, re.S)
        m = pat.search(t)
        if not m:
            print("  !! 找不到 %s 的标题" % sid)
            continue
        new = '<h2 id="%s"><span class="n">%s</span>%s</h2>' % (sid, m.group(1), title)
        t = t[:m.start()] + new + t[m.end():]
        print("  %-4s → %s" % (sid, title))
    # 编号与标题之间补空格
    t = re.sub(r'(<h2 id="s\d+"><span class="n">\d+</span>)(?=[^\s<])',
               r'\1 ', t)

    print()
    print("  改后的小节：")
    for m in re.finditer(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                         t, re.S):
        print("      %-4s %-3s %s" % (m.group(1), m.group(2),
                                      re.sub(r"<[^>]+>", "", m.group(3)).strip()))

    if not dry:
        io.open(P, "w", encoding="utf-8", newline="").write(t)
        print()
        print("  已写入")


if __name__ == "__main__":
    main()
