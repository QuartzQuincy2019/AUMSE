/* 教程示例校验 2：函数基础 */
#include <stdio.h>

/* ① 最简单的函数 */
void sayHello(void) {
    printf("Hello, C!\n");
}

/* ② 有参数 */
void greet(char who[]) {
    printf("Hello, %s!\n", who);
}

/* ③ 有返回值 */
int square(int x) {
    return x * x;
}

/* ④ 多个参数 */
int add(int a, int b) {
    return a + b;
}

/* ⑤ 返回较大者 */
int maxOf(int a, int b) {
    if (a > b) {
        return a;
    }
    return b;
}

/* ⑥ 提前返回 */
int isEven(int n) {
    if (n % 2 == 0) {
        return 1;
    }
    return 0;
}

/* ⑦ 先声明后定义 */
int cube(int x);

int main(void) {
    sayHello();
    greet("Mongol");
    printf("%d\n", square(5));
    printf("%d\n", add(3, 4));
    printf("%d\n", maxOf(7, 12));
    printf("%d\n", isEven(8));
    printf("%d\n", isEven(9));
    printf("%d\n", cube(3));

    /* 形参是副本：改不动实参 */
    int n = 10;
    printf("before: %d\n", n);
    square(n);
    printf("after : %d\n", n);

    /* 变量作用域：i 只活在 for 里 */
    for (int i = 0; i < 3; i++) {
        int t = i * 10;
        printf("%d ", t);
    }
    printf("\n");

    return 0;
}

int cube(int x) {
    return x * x * x;
}
