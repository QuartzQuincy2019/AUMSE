# -*- coding: utf-8 -*-
"""把两篇提升进理论系列：
     09-e03-unicode-and-encoding.html   → t02-unicode-and-encoding.html   （09-E03 → T02）
     08-f04-font-file-anatomy.html      → t03-font-file-anatomy.html      （08-F04 → T03）

同时改掉：
  · 两个 html 文件自己的 <link> 与内部标题
  · 15 篇后端教程页尾「本系列」小目录里的链接与编号
  · assets/<旧名>.css → assets/<新名>.css
  · 两篇互指的地方（T02 ↔ T03）
  · tools/ 里生成它们的脚本
  · make_pages.py / mark_key_points.py 的数据表

顺序很重要：先把映射表定下来，再对**所有**文件做一次性替换，
避免「A 改成 B、B 又被改成 C」的连锁错。


# 说明：本文件里的旧编号（09-e03 / 08-f04 等）是【被映射的源】，
#       属于历史记录，不要因为「看起来像残留」而改掉。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")

# 文件名映射（长的先替换，避免前缀冲突）
FILE_MAP = [
    ("09-e03-unicode-and-encoding.html", "t02-unicode-and-encoding.html"),
    ("08-f04-font-file-anatomy.html",    "t03-font-file-anatomy.html"),
]
CSS_MAP = [
    ("09_e03_unicode_and_encoding.css", "t02_unicode_and_encoding.css"),
    ("08_f04_font_file_anatomy.css",    "t03_font_file_anatomy.css"),
]
# 显示编号映射
NUM_MAP = [
    ("09-E03", "T02"),
    ("08-F04", "T03"),
]
# 正文里「裸编号」的提法
TEXT_MAP = [
    ("09-E03 Unicode 和编码", "T02 Unicode 和编码"),
    ("08-F04 字体文件结构大揭秘", "T03 字体文件结构大揭秘"),
    ("<b>F04 字体文件结构大揭秘</b>", "<b>T03 字体文件结构大揭秘</b>"),
    ("详见 F04", "详见 T03"),
    ("见 F04", "见 T03"),
    ("F04 里「字形名里的音节」", "T03 里「字形名里的音节」"),
    ("<b>09-E03 Unicode 和编码</b>", "<b>T02 Unicode 和编码</b>"),
    ("09-E03</b>", "T02</b>"),
    ("F04 字体文件结构大揭秘", "T03 字体文件结构大揭秘"),
]

ALL_SUB = FILE_MAP + CSS_MAP + NUM_MAP + TEXT_MAP


def apply_subs(text):
    for a, b in ALL_SUB:
        text = text.replace(a, b)
    return text


def main():
    # ---- 1. 先重命名文件（用 git mv 保留历史更好，但直接 rename 也可以） ----
    for old, new in FILE_MAP + CSS_MAP:
        d = T if old.endswith(".html") else A
        s, t2 = os.path.join(d, old), os.path.join(d, new)
        if os.path.exists(t2):
            print("  · %s 已存在" % new)
        elif os.path.exists(s):
            os.rename(s, t2)
            print("  ✔ 改名 %s → %s" % (old, new))
        else:
            print("  ! 找不到 %s" % old)

    # ---- 2. 全仓替换引用 ----
    changed = []
    for root, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs
                   if d not in (".git", "node_modules", "__pycache__", ".vs")]
        for f in files:
            if not re.search(r'\.(html|css|js|py|md|json)$', f):
                continue
            p = os.path.join(root, f)
            # 跳过本次的映射脚本自己（避免自我改写）
            if p.endswith("reindex_t.py") or p.endswith("_cnmn_wikitext.txt"):
                continue
            try:
                t = io.open(p, encoding="utf-8").read()
            except Exception:
                continue
            nt = apply_subs(t)
            if nt != t:
                io.open(p, "w", encoding="utf-8", newline="").write(nt)
                changed.append(p.replace(R, ""))
    print("  ✔ 改了 %d 个文件的引用" % len(changed))
    for c in sorted(changed):
        print("      " + c)


if __name__ == "__main__":
    main()
