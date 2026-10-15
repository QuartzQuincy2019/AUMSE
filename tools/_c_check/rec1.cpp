// 校验 08-E01：递归
#include <iostream>
using namespace std;

// 看递归的每一层
void countdown(int n, int depth) {
    for (int i = 0; i < depth; i++) cout << "  ";
    cout << "countdown(" << n << ")" << endl;
    if (n == 0) {
        for (int i = 0; i < depth; i++) cout << "  ";
        cout << "到底了，开始返回" << endl;
        return;
    }
    countdown(n - 1, depth + 1);
}

// 阶乘
long long fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}

// 斐波那契
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

// 递归求和
int sumTo(int n) {
    if (n == 0) return 0;
    return n + sumTo(n - 1);
}

// 十进制转二进制（递归打印）
void toBinary(int n) {
    if (n == 0) return;
    toBinary(n / 2);
    cout << (n % 2);
}

// 递归反转字符串
void printReverse(const char *s) {
    if (*s == '\0') return;
    printReverse(s + 1);
    cout << *s;
}

// 汉诺塔
int hanoiMoves = 0;
void hanoi(int n, char a, char c, char b) {
    if (n == 0) return;
    hanoi(n - 1, a, b, c);
    hanoiMoves++;
    hanoi(n - 1, b, c, a);
}

// 递归求数组最大值
int maxInArray(int a[], int n) {
    if (n == 1) return a[0];
    int rest = maxInArray(a, n - 1);
    return a[n - 1] > rest ? a[n - 1] : rest;
}

int main() {
    cout << "=== ① 递归的展开与返回 ===" << endl;
    countdown(3, 0);

    cout << "\n=== ② 阶乘 ===" << endl;
    for (int i = 1; i <= 6; i++) cout << i << "! = " << fact(i) << endl;

    cout << "\n=== ③ 斐波那契 ===" << endl;
    for (int i = 0; i <= 8; i++) cout << fib(i) << " ";
    cout << endl;

    cout << "\n=== ④ 递归求和 ===" << endl;
    cout << "1+2+...+10 = " << sumTo(10) << endl;

    cout << "\n=== ⑤ 十进制转二进制 ===" << endl;
    cout << "10 -> ";  toBinary(10);  cout << endl;
    cout << "255 -> "; toBinary(255); cout << endl;

    cout << "\n=== ⑥ 递归反转字符串 ===" << endl;
    cout << "Mongol 倒过来: ";
    printReverse("Mongol");
    cout << endl;

    cout << "\n=== ⑦ 汉诺塔步数 ===" << endl;
    for (int n = 1; n <= 5; n++) {
        hanoiMoves = 0;
        hanoi(n, 'A', 'C', 'B');
        cout << n << " 层需要 " << hanoiMoves << " 步" << endl;
    }

    cout << "\n=== ⑧ 递归求最大值 ===" << endl;
    int a[6] = {88, 52, 79, 95, 61, 84};
    cout << "max = " << maxInArray(a, 6) << endl;

    return 0;
}
