// 场景：头文件里放函数定义，被两个 .cpp 同时包含 → 重复定义
// common.h 的内容（这里内联模拟）
#include <iostream>
using namespace std;

int add(int a, int b) { return a + b; }   // ← 头文件里不该写函数体

int main() {
    cout << add(1, 2) << endl;
    return 0;
}
