/* C 版：document 07 作用域示例 */
#include <stdio.h>

/* ① 块作用域 */
void demo1(void) {
    int a = 1;
    printf("外层 a = %d\n", a);
    {
        int b = 2;
        printf("内层 看得到 a = %d，b = %d\n", a, b);
        a = 99;
        printf("内层改了 a，a = %d\n", a);
    }
    printf("出了内层，a = %d（改动保留）\n", a);
    /* printf("%d", b);   ← 编译错误：b 已经不在了 */
}

/* ② for / if 里的变量 */
void demo2(void) {
    for (int i = 0; i < 3; i++) {
        int t = i * 10;
        printf("i=%d t=%d\n", i, t);
    }
    printf("循环结束后 i 和 t 都不存在了\n");

    if (1) {
        int only = 5;
        printf("if 块里的 only = %d\n", only);
    }
    printf("if 块结束后 only 也不存在了\n");

    for (int i = 100; i < 102; i++) {
        printf("第二个循环 i = %d\n", i);
    }
}

/* ③ 函数参数是局部的 */
void f(int n) {
    printf("  f 里的 n = %d\n", n);
    n = 999;
    printf("  f 里改过之后 n = %d\n", n);
}
void demo3(void) {
    int n = 5;
    printf("main 里的 n = %d\n", n);
    f(n);
    printf("调用 f 之后 main 里的 n = %d（没变）\n", n);
}

/* ④ 全局变量 */
int gCount = 0;
void bump(void) { gCount++; }
void reset(void) { gCount = 0; }
void demo4(void) {
    printf("开始 gCount = %d\n", gCount);
    bump(); bump(); bump();
    printf("调用 bump 三次后 gCount = %d\n", gCount);
    reset();
    printf("reset 之后 gCount = %d\n", gCount);
}

/* ⑤ static 局部 */
void normalCounter(void) {
    int n = 0;
    n++;
    printf("  普通局部   n = %d\n", n);
}
void staticCounter(void) {
    static int n = 0;
    n++;
    printf("  static局部 n = %d\n", n);
}
void demo5(void) {
    for (int i = 0; i < 3; i++) { normalCounter(); staticCounter(); }
}

/* ⑥ 同名遮蔽 */
int value = 100;
void demo6(void) {
    printf("全局 value = %d\n", value);
    {
        int value = 20;
        printf("局部 value = %d\n", value);
        {
            int value = 3;
            printf("最内层 value = %d\n", value);
        }
        printf("出了内层 value = %d\n", value);
    }
    printf("回到函数层，全局 value = %d\n", value);
    value = 555;
    printf("直接改 value 之后 = %d\n", value);
}

/* ⑦ 作用域 != 生存期：用指针返回 static 变量的地址 */
int *makeStatic(void) {
    static int keep = 42;
    return &keep;
}
void demo7(void) {
    printf("第一次读: %d\n", *makeStatic());
    *makeStatic() = 77;
    printf("改成 77 后再读: %d\n", *makeStatic());
}

int main(void) {
    printf("=== 1. 块作用域 ===\n"); demo1();
    printf("\n=== 2. for / if ===\n"); demo2();
    printf("\n=== 3. 函数参数 ===\n"); demo3();
    printf("\n=== 4. 全局变量 ===\n"); demo4();
    printf("\n=== 5. static 局部 ===\n"); demo5();
    printf("\n=== 6. 同名遮蔽 ===\n"); demo6();
    printf("\n=== 7. 作用域 != 生存期 ===\n"); demo7();
    return 0;
}
