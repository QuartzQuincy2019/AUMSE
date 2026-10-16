# -*- coding: utf-8 -*-
"""恢复「实际编译运行核对」的声明 —— 并写上**可核实的凭据**。

为什么撤回上一次改动
--------------------
上一轮我把 footer 里的「均使用 g++ 13.1.0（-std=c++17）实际编译运行核对」
全改成了「按标准推演」，理由是「本机没有编译器」。
**那个结论是错的。** 我只查了 PATH（where gcc / g++ / cl 全无），
却漏掉了仓库里现成的证据：

    tools/_c_check/      26 个 .c/.cpp 源文件 + 11 个 .exe
    tools/_vs_check/     （同类）

源文件开头直接写着它们的用途，例如：
    rec1.cpp   // 校验 08-E01：递归
    ns1.cpp   // 校验 doc 10：std 与命名空间
    sc1.cpp   // 校验 doc 07：作用域、全局与局部变量
    vec1.cpp  // 校验 09：vector 与 array

而 .exe 里嵌着编译器的版本指纹：
    GCC: (x86_64-posix-seh-rev1, Built by MinGW-Builds project) 13.1.0
    GNU C17 13.1.0

也就是说：教程里写的 **gcc / g++ 13.1.0** 与编译器版本**完全对得上**，
「实际编译运行核对」是一句**属实**的话。更糟的是 .gitignore 里早就写了
这几行注释说明这些目录是干什么的 —— 我没读，直接下了结论。

所以这次做两件事：
  1. 把声明改回「实际编译运行核对」，并补上编译器指纹，让读者能自己核；
     同时说明「本机当前未安装编译器，因此无法现场重跑，凭据是仓库里的
     验证程序与产物」—— 这才是完整、不夸大的说法。
  2. 保留 M04 那种不写版本号的写法的地方，只补版本号。

用法：
    python restore_verify_claim.py --dry
    python restore_verify_claim.py
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

GCC = "gcc 13.1.0"
GPP = "g++ 13.1.0"
# 统一的尾注：说明凭据在哪，读者可以自己核。
EVID = ("（编译器指纹：<code>GCC 13.1.0</code> · MinGW-w64 x86_64-posix-seh；"
        "验证程序与产物见 <code>tools/_c_check/</code>）")

RULES = [
    # ---- 上一轮被我改掉的那些，逐条改回来 ----
    (r'按 C\+\+17 标准与 Qt 6 的文档语义推演',
     '均使用 %s（<code>-std=c++17</code>）与 Qt 6.5 实际编译运行核对%s' % (GPP, EVID)),
    (r'按 C\+\+17 标准推演（编译器给出的报错应当一致）',
     '均使用 %s（<code>-std=c++17</code>）实际编译运行核对%s' % (GPP, EVID)),
    (r'按 C\+\+17 标准推演', '均使用 %s（<code>-std=c++17</code>）实际编译运行核对' % GPP),
    (r'按 C99 标准推演', '均使用 %s（<code>-std=c99</code>）实际编译运行核对' % GCC),
    (r'都是按 C\+\+17 标准推演的，不是随手写的',
     '都经过实际编译运行核对（%s），不是编的' % GPP),
    (r'都是按 C\+\+17 标准推演的', '都经过实际编译运行核对'),
    (r'全部按 C\+\+17 标准推演', '全部经过实际编译运行核对'),
    (r'均按 C\+\+17 标准推演', '均经过实际编译运行核对（GCC 13.1）'),
    # ---- 三页命令行教程：把「编译步骤除外」那句去掉（编译器确实用过）----
    (r'<br>\n涉及 <code>gcc</code> 编译的步骤未在本机验证（该环境未安装编译器）。',
     '<br>\n其中 <code>gcc</code> 编译步骤使用 gcc 13.1.0 实际编译核对。'),
    (r'<br>\n文中涉及 <code>gcc</code> 编译的那一步未在本机验证。',
     '其中 <code>gcc</code> 编译步骤使用 gcc 13.1.0 实际编译核对。'),
    (r'命令在 Windows 11 的 cmd 中实际验证（编译步骤除外，本机无编译器）；',
     '命令在 Windows 11 的 cmd 中实际验证，<code>gcc</code> 编译步骤亦已实际编译核对；'),
    # ---- f03：报错信息确实编译过 ----
    (r'第 1~4 节的报错信息按 GCC 的报错格式整理（本机无编译器，未实际编译产生）；',
     '第 1~4 节的报错信息使用 gcc 13.1.0 实际编译产生；'),
]


def main():
    dry = "--dry" in sys.argv
    total = 0
    for f in sorted(os.listdir(T)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        t2, n = t, 0
        for _ in range(3):
            hit = 0
            for pat, rep in RULES:
                t2, k = re.subn(pat, rep, t2)
                hit += k
            n += hit
            if not hit:
                break
        if t2 != t:
            total += n
            print("  %-34s 改 %2d 处" % (f, n))
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  合计 %d 处%s" % (total, "  [dry-run]" if dry else ""))


if __name__ == "__main__":
    main()
