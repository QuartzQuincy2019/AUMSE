# -*- coding: utf-8 -*-
"""整理 SharingGroup/tutorials/assets：把散在顶层的文件按类型收进子目录。

目标结构
    assets/
      css/     52 个样式表
      img/     图片（webp / awebp / png / jpg / jpeg / gif / bmp / svg / pdf）
      js/      三个脚本（series-common / fe-data / r03-picker）
      fonts/   字体 + 许可证（已有，本脚本只补两条路径改写）
      egypt/   第三方整包（MdCRndr + New Gardiner + OFL），**保持原样**
      ref/     项目组长自己的参考图，**保持原样**

为什么要脚本而不是手拖
    被引用的路径有四种写法，任何一处漏改都会变成「页面不报错、样式/图片悄悄没了」：
        1. 教程页  assets/xxx.css           → assets/css/xxx.css
        2. 教程页  assets/xxx.png           → assets/img/xxx.png
        3. 首页    SharingGroup/tutorials/assets/xxx.png
        4. CSS 内部 url("fonts/xxx.ttf")    → url("../fonts/xxx.ttf")
    另外 tools/*.py 里也有硬编码（make_pages.py 的 CARD_BG）。

用法
    python tools/organize_assets.py --dry
    python tools/organize_assets.py
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(ROOT, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")

IMG_EXT = {".webp", ".awebp", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
           ".svg", ".pdf"}
KEEP_DIRS = {"fonts", "egypt", "ref", "css", "img", "js"}
TEXT_EXT = {".html", ".css", ".js", ".py", ".md", ".json"}


def plan():
    """返回 [(源文件名, 目标子目录)]。"""
    out = []
    for name in sorted(os.listdir(A)):
        p = os.path.join(A, name)
        if not os.path.isfile(p):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext == ".css":
            out.append((name, "css"))
        elif ext in IMG_EXT:
            out.append((name, "img"))
        elif ext == ".js":
            out.append((name, "js"))
    return out


def all_text_files():
    """仓库里需要改引用的文本文件。跳过 .git / .shots / _proj 等。"""
    skip = {".git", ".shots", ".dsh-vision-router", "__pycache__",
            "refs", "_proj", "backup"}
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if os.path.splitext(f)[1].lower() in TEXT_EXT:
                yield os.path.join(base, f)


def main():
    dry = "--dry" in sys.argv
    moves = plan()
    by_ext = {}
    for name, sub in moves:
        by_ext.setdefault(sub, []).append(name)

    print("  计划：%d 个文件移入子目录" % len(moves))
    for sub in ("css", "img", "js"):
        print("      → assets/%-5s %d 个" % (sub, len(by_ext.get(sub, []))))
    print()

    if not moves:
        print("  已经整理过了，什么都不做。")
        return

    # ---------- 1. 搬文件 ----------
    for sub in ("css", "img", "js"):
        os.makedirs(os.path.join(A, sub), exist_ok=True)
    for name, sub in moves:
        src = os.path.join(A, name)
        dst = os.path.join(A, sub, name)
        if dry:
            continue
        os.replace(src, dst)
    if not dry:
        print("  ① 已搬移 %d 个文件" % len(moves))

    # ---------- 2. 构造替换表 ----------
    # 长名字先替换，避免 a.css 把 aa.css 的前缀吃掉
    subs = []
    for name, sub in sorted(moves, key=lambda x: -len(x[0])):
        subs.append(("assets/" + name, "assets/%s/%s" % (sub, name)))
        subs.append(("SharingGroup/tutorials/assets/" + name,
                     "SharingGroup/tutorials/assets/%s/%s" % (sub, name)))

    # ---------- 3. 改写所有文本文件 ----------
    touched = {}
    for path in all_text_files():
        try:
            t = io.open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        orig = t
        for old, new in subs:
            if old in t:
                t = t.replace(old, new)
        # CSS 内部的字体相对路径（样式表从 assets/ 移到了 assets/css/）
        if path.endswith(".css"):
            t = re.sub(r'url\((["\']?)fonts/', r'url(\1../fonts/', t)
        if t != orig:
            touched[path] = sum(1 for _ in range(1))
            if not dry:
                io.open(path, "w", encoding="utf-8", newline="").write(t)

    rel = [os.path.relpath(p, ROOT) for p in touched]
    print("  ② 改写了 %d 个文件：" % len(rel))
    for r in sorted(rel)[:14]:
        print("      " + r)
    if len(rel) > 14:
        print("      … 另 %d 个" % (len(rel) - 14))

    # ---------- 4. 自检：还有没有指向顶层 css/img/js 的旧写法 ----------
    if not dry:
        left = []
        for path in all_text_files():
            try:
                t = io.open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for m in re.finditer(r"assets/([A-Za-z0-9_\u4e00-\u9fff\.\-]+\.(?:css|js))", t):
                left.append((os.path.relpath(path, ROOT), m.group(0)))
        bad = [x for x in left if "/css/" not in x[1] and "/js/" not in x[1]]
        print()
        if bad:
            print("  !! 仍有 %d 处指向 assets/ 顶层的样式或脚本：" % len(bad))
            for f, s in bad[:10]:
                print("      %-46s %s" % (f, s))
        else:
            print("  ③ 自检通过：没有遗留的顶层 css/js 引用")

    print()
    print("  %s" % ("[dry-run] 未改动磁盘" if dry else "已写入"))


if __name__ == "__main__":
    main()
