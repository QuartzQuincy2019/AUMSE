# 教程输出的编译核对凭据

本目录（以及同类的 `tools/_vs_check/`）是为了**验证教程里写的输出是真的**
而建立的：每个 `.c` / `.cpp` 是一个最小验证程序，编译运行后
把结果抄进对应教程。

编译产物（`.exe` / `.obj` / `.pdb` / `.tlog` 等）在 `.gitignore` 里被排除，
**源码与工程文件保留入库** —— 所以即使产物被清掉，仍然可以重新编译核对。

> **不要删这两个目录。** 网站里每一句「实际编译运行核对」都指回这里。
> 改动教程里任何「运行结果」时，请同时更新对应的验证程序并重新编译核对，
> 否则那份声明就不再成立。

---

## 一、`tools/_c_check/` —— GCC（MinGW-w64）

从产物里可以读出编译器指纹：

```
GCC: (x86_64-posix-seh-rev1, Built by MinGW-Builds project) 13.1.0
GNU C17 13.1.0
```

即 **MinGW-w64 GCC 13.1.0**（x86_64-posix-seh-rev1）。
教程 footer 里写的 `gcc 13.1.0` / `g++ 13.1.0` 与此一致。

| 程序 | 校验的教程 |
|---|---|
| `rec1.cpp` | E01 递归 |
| `ns1.cpp`、`ns_bad1.cpp`、`ns_bad2.cpp` | Q01 std 与命名空间 |
| `sc1.cpp`、`sc2.c`、`sc_bad1.cpp`、`sc_bad2.cpp` | M07 作用域 |
| `st1.c` | M08 C 风格字符串 |
| `vec1.cpp` | M09 vector 与 array |
| `cmp1.cpp` | M03 类型概论（比较与尺寸） |
| `uni1.cpp`、`uni2.c` | T02 Unicode 与编码 |
| `path1.cpp`、`pathread.cpp` | F02 相对路径与 CWD |
| `f02a.c`、`f02b.c` | F02 路径演示 |
| `lk1.c`、`lk1.cpp`、`lk3.cpp`、`lk4.cpp` | F03 链接相关的错误复现 |
| `nohdr.c`、`nohdr.cpp` | F03 缺头文件 |
| `undecl.c` | 未声明标识符的报错形状 |
| `syn.c`、`syn.cpp` | 语法检查用的小片段 |

`build/`、`f02/`、`mf/` 是运行时需要的工作目录（含固定输入 `data.txt`）。

---

## 二、`tools/_vs_check/` —— MSVC / Visual Studio

`LibDemo/` 与 `Demo/` 是完整的 VS 工程（`.sln` + `.vcxproj`），
用来核对 F03 里那段**静态库流程**：建库、链接、`LNK` 系列报错。

从 `.pdb` / `.obj` 里读出的工具链版本：

```
MSVC\14.51.36231        （cl 编译器版本）
vc145.pdb / vc145.idb   （平台工具集 v145）
```

与 F03 footer 里写的
「Visual Studio Community 2026（18.10.3 · MSVC 14.51.36231 · MSBuild v145）」
一致。

| 内容 | 校验的教程 |
|---|---|
| `Demo/` | 单工程编译（含 `include/my.h`） |
| `LibDemo/UmeMath/` | 静态库工程（`ume_math`、`extras`） |
| `LibDemo/App/` | 调用静态库的应用（产生 `LNK` 报错的地方） |

---

## 三、当前环境没有编译器 —— 这不构成「输出是编造的」

写这份说明时的开发环境（Windows 11 Build 26200）PATH 上
**没有** gcc / g++ / cl（`where` 查过全无）。这**不能**推出
「教程里的输出是编的」—— 本目录就是当年核对留下的凭据。

若要现场重跑：

* C/C++ 部分 → 安装 **MinGW-w64 GCC 13.x**（x86_64-posix-seh）
* F03 的静态库部分 → 安装 **Visual Studio 2026**（MSVC 14.51 / v145）
