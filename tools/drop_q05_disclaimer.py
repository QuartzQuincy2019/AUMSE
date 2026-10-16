# -*- coding: utf-8 -*-
"""删掉 Q05 简介里的「只给方向，不给代码」。

出现三处（外加一个会把它写回去的生成器）：
    1. tools/_q05_body.html            §7 末尾卡片的标题
    2. tools/series_data.py            首页卡片的说明文字
    3. tools/register_q05.py           登记脚本里的字面量（重跑会写回 #2）
    （页面副标题走 --subtitle 参数，重建时给新的即可，不在这里改。）

顺带把 §7 末尾那张卡片也调整一下：标题去掉之后，
卡片里说「这一篇只需要记住一件事」，与「不给代码」已经无关，
保留即可；只把标题改成正文本来就在讲的意思。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"

EDITS = [
    # (文件, 旧串, 新串)
    (r"tools\_q05_body.html",
     "<div class=\"card-t\">本篇只给方向，不给代码</div>",
     "<div class=\"card-t\">这一篇的落点</div>"),
    (r"tools\series_data.py",
     "\"为什么不能什么都塞进一个类；只给方向不给代码\"",
     "\"为什么不能什么都塞进一个类；耦合的代价与拆分方向\""),
    (r"tools\register_q05.py",
     "为什么不能什么都塞进一个类；只给方向不给代码",
     "为什么不能什么都塞进一个类；耦合的代价与拆分方向"),
    # 正文里还有一处类似的措辞（§5 标题），一并看情况
    (r"tools\_q05_body.html",
     "<h2 id=\"s5\"><span class=\"n\">5</span>大致的方向（这一篇只提思路）</h2>",
     "<h2 id=\"s5\"><span class=\"n\">5</span>大致的方向</h2>"),
]


def main():
    dry = "--dry" in sys.argv
    for rel, old, new in EDITS:
        p = os.path.join(R, rel)
        if not os.path.exists(p):
            print("  !! 找不到 %s" % rel)
            continue
        t = io.open(p, encoding="utf-8").read()
        if new in t and old not in t:
            print("  %-28s 已是新内容" % rel)
            continue
        if old not in t:
            print("  %-28s !! 未匹配：%s" % (rel, old[:46]))
            continue
        t2 = t.replace(old, new)
        print("  %-28s 改 %d 处" % (rel, t.count(old)))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
