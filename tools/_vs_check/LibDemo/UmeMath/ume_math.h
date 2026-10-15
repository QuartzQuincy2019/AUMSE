#pragma once
// ume_math.h —— 静态库对外公开的头文件

// ① 只声明：实现在 ume_math.cpp 里
int  ume_add(int a, int b);
int  ume_mul(int a, int b);
int  ume_clamp(int v, int lo, int hi);

// ② 写在头文件里的函数，必须加 inline
//    否则被多个 .cpp 同时包含时，链接期会报「重复定义」
inline int ume_max(int a, int b) {
    return (a > b) ? a : b;
}

// ③ 头文件里的常量：C++17 起用 inline 变量，可以直接给值
inline const int kUmeVersion = 2026;
