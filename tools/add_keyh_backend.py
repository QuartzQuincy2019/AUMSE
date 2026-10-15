# -*- coding: utf-8 -*-
"""把「重点小节黄底」规则加到**真正被加载的**样式表里。

教训：后端 16 篇用的是**合并后的每篇一个** css
（`f02_paths_and_env.css` 之类），`tutorial.css` 根本不会被加载。
我一开始把规则追加到 tutorial.css，结果 fe-05 之外一篇都没生效，
而且检查「规则数」时才发现整张表在页面上是 0 条 —— 因为
`cssRules` 读取方式的问题掩盖了真相。

所以：规则要写进每个 per-page css，并且插在**第一条 @media 之前**，
否则会被「媒体查询在后」的重排规则挪到媒体查询里，桌面端就不生效了。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

AS = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"

BLOCK = """
/* ================= 重点小节：整块黄底 =================
   与 home.html 的重点卡片同一套配色（淡金渐变底 + 金色左边框 + 金色 ★），
   一眼看出「这一节是本项目的重点」。 */
h2.key-h,
h3.key-h,
h4.key-h{
  position:relative;
  background:linear-gradient(96deg,#fffdf5 0%,#fdf3dc 58%,#fbe9c4 100%);
  border:1px solid #e8c877;
  border-left:6px solid #c8901a;
  border-radius:0 10px 10px 0;
  padding:10px 16px 10px 14px;
  margin-left:-4px;
  box-shadow:0 2px 10px rgba(200,144,26,.14);
}
h2.key-h{border-top:1px solid #e8c877;padding-top:10px}
.key-mark{display:inline-block;margin-right:8px;color:#c8901a;font-size:15px;
  vertical-align:1px;cursor:help}
.key-hint{display:inline-block;margin-left:8px;padding:1px 9px;border-radius:999px;
  font-size:11px;font-weight:600;background:#eef2f8;border:1px solid #ccd5e3;
  color:#8b95a5;vertical-align:2px;font-family:var(--sans)}
@media (max-width:980px){
  h2.key-h,h3.key-h,h4.key-h{margin-left:0;border-radius:0 8px 8px 0}
}
"""


def main():
    n = 0
    for f in sorted(os.listdir(AS)):
        if not f.endswith(".css") or f == "tutorial.css" or f.startswith("fe_"):
            continue
        p = os.path.join(AS, f)
        t = io.open(p, encoding="utf-8").read()
        if "h2.key-h" in t:
            print("  ·  %-34s 已有" % f)
            continue
        # 插在第一条 @media 之前（保证属于「非媒体」区，桌面端生效）
        i = t.find("@media")
        if i < 0:
            t = t.rstrip() + "\n" + BLOCK
        else:
            # 退到该行的行首，避免切在规则中间
            j = t.rfind("\n", 0, i) + 1
            t = t[:j] + BLOCK.strip() + "\n\n" + t[j:]
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        print("  ✔  %-34s 插在 @media 之前" % f)
        n += 1
    print("\n  处理 %d 个文件" % n)


if __name__ == "__main__":
    main()
