// main.cpp —— 使用静态库里的函数
#include <iostream>
#include "ume_math.h"          // 只用引号：这是「自己写的头文件」

int main() {
    std::cout << "ume_add(2, 3)   = " << ume_add(2, 3)   << "\n";
    std::cout << "ume_mul(4, 5)   = " << ume_mul(4, 5)   << "\n";
    std::cout << "ume_clamp(99,0,10) = " << ume_clamp(99, 0, 10) << "\n";
    std::cout << "ume_max(7, 9)   = " << ume_max(7, 9)   << "\n";   // 这个是 inline 的
    std::cout << "kUmeVersion     = " << kUmeVersion     << "\n";
    return 0;
}
