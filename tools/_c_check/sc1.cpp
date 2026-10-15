// 校验 doc 07（新）：作用域、全局与局部变量
#include <iostream>
using namespace std;

// ============ ① 块作用域 ============
void demo1() {
    cout << "=== ① 块作用域：一对花括号就是一层 ===" << endl;
    int a = 1;
    cout << "外层 a = " << a << endl;
    {
        int b = 2;                 // 只在这个 {} 里活着
        cout << "内层 看得到 a = " << a << "，b = " << b << endl;
        a = 99;                    // 可以改外层
        cout << "内层改了 a，a = " << a << endl;
    }
    cout << "出了内层，a = " << a << "（改动保留）" << endl;
    // cout << b;                  // ← 编译错误：b 已经不在了
    cout << "b 出了内层就不能用了" << endl;
}

// ============ ② for / if 里的变量 ============
void demo2() {
    cout << "\n=== ② for / if 里的变量也只活在块里 ===" << endl;
    for (int i = 0; i < 3; i++) {
        int t = i * 10;
        cout << "i=" << i << " t=" << t << endl;
    }
    // cout << i;                  // ← 编译错误
    cout << "循环结束后 i 和 t 都不存在了" << endl;

    if (true) {
        int only = 5;
        cout << "if 块里的 only = " << only << endl;
    }
    cout << "if 块结束后 only 也不存在了" << endl;

    // 同名不冲突：两个 for 各用各的 i
    for (int i = 100; i < 102; i++) cout << "第二个循环 i = " << i << endl;
}

// ============ ③ 函数参数是局部的 ============
void f(int n) {                 // n 只属于 f
    cout << "  f 里的 n = " << n << endl;
    n = 999;                    // 改的是 f 自己的 n
    cout << "  f 里改过之后 n = " << n << endl;
}

void demo3() {
    cout << "\n=== ③ 函数参数是局部的 ===" << endl;
    int n = 5;
    cout << "main 里的 n = " << n << endl;
    f(n);
    cout << "调用 f 之后 main 里的 n = " << n << "（没变）" << endl;
}

// ============ ④ 全局变量 ============
int gCount = 0;                 // 全局：所有函数都能用
int gName = 7;

void bump() { gCount++; }
void reset() { gCount = 0; }

void demo4() {
    cout << "\n=== ④ 全局变量 ===" << endl;
    cout << "开始 gCount = " << gCount << endl;
    bump(); bump(); bump();
    cout << "调用 bump 三次后 gCount = " << gCount << endl;
    reset();
    cout << "reset 之后 gCount = " << gCount << endl;
    cout << "任何函数都能改它 —— 这正是它危险的地方" << endl;
}

// ============ ⑤ static 局部变量 ============
void normalCounter() {
    int n = 0;                  // 每次进来都重新变成 0
    n++;
    cout << "  普通局部   n = " << n << endl;
}
void staticCounter() {
    static int n = 0;           // 只初始化一次，之后一直留着
    n++;
    cout << "  static局部 n = " << n << endl;
}

void demo5() {
    cout << "\n=== ⑤ static 局部变量 ===" << endl;
    for (int i = 0; i < 3; i++) {
        normalCounter();
        staticCounter();
    }
}

// ============ ⑥ 同名遮蔽 + :: 访问全局 ============
int value = 100;                // 全局

void demo6() {
    cout << "\n=== ⑥ 同名遮蔽 ===" << endl;
    cout << "全局 value = " << value << endl;

    int value = 20;             // 局部把全局「遮住」了
    cout << "局部 value = " << value << endl;

    {
        int value = 3;          // 又遮一层
        cout << "最内层 value = " << value << endl;
    }

    cout << "出了内层 value = " << value << endl;
    cout << "用 :: 访问被遮住的全局：::value = " << ::value << endl;

    ::value = 555;              // 改的是全局那个
    cout << "::value = 555 之后，全局 value = " << ::value << endl;
    cout << "局部 value 还是 " << value << endl;
}

// ============ ⑦ 生存期 ≠ 作用域 ============
int &makeStatic() {
    static int keep = 42;       // 作用域只在函数内，但活到程序结束
    return keep;
}

void demo7() {
    cout << "\n=== ⑦ 作用域 ≠ 生存期 ===" << endl;
    cout << "第一次读: " << makeStatic() << endl;
    makeStatic() = 77;          // 还能改它
    cout << "改成 77 后再读: " << makeStatic() << endl;
    cout << "（名字只在函数里可见，但那个变量一直活着）" << endl;
}

int main() {
    demo1(); demo2(); demo3(); demo4(); demo5(); demo6(); demo7();
    return 0;
}
