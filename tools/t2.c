/* 校验：地址、指针、相邻元素、指针运算 */
#include <stdio.h>

int main(void) {
    printf("=== 变量的地址 ===\n");
    int a = 10;
    printf("a 的值   = %d\n", a);
    printf("a 的地址 = %p\n", (void *)&a);

    printf("\n=== 数组元素是连续的 ===\n");
    int arr[4] = {10, 20, 30, 40};
    for (int i = 0; i < 4; i++) {
        printf("arr[%d] 值=%d  地址=%p\n", i, arr[i], (void *)&arr[i]);
    }
    printf("相邻元素地址差 = %d 字节\n",
           (int)((char *)&arr[1] - (char *)&arr[0]));
    printf("整个数组占 %d 字节\n", (int)sizeof(arr));
    printf("数组首地址 = %p\n", (void *)arr);
    printf("arr[0]地址 = %p\n", (void *)&arr[0]);

    printf("\n=== 指针基本操作 ===\n");
    int x = 42;
    int *p = &x;
    printf("x   = %d\n", x);
    printf("&x  = %p\n", (void *)&x);
    printf("p   = %p   (p 里装的就是 &x)\n", (void *)p);
    printf("*p  = %d   (顺着 p 找到 x)\n", *p);

    *p = 99;
    printf("执行 *p = 99 之后：x = %d\n", x);

    x = 7;
    printf("执行 x = 7 之后：*p = %d\n", *p);

    printf("\n=== 指针的算术 ===\n");
    int b[5] = {100, 200, 300, 400, 500};
    int *q = b;
    printf("q     -> %d\n", *q);
    printf("q + 1 -> %d\n", *(q + 1));
    printf("q + 4 -> %d\n", *(q + 4));
    printf("q 与 q+1 的地址差 = %d 字节\n",
           (int)((char *)(q + 1) - (char *)q));

    printf("\n=== 用指针遍历数组 ===\n");
    for (int *r = b; r < b + 5; r++) {
        printf("%d ", *r);
    }
    printf("\n");

    printf("\n=== 指针类型决定步长 ===\n");
    int    ia[2] = {0, 0};
    char   ca[2] = {0, 0};
    double da[2] = {0, 0};
    printf("int*    加 1 前进 %d 字节\n", (int)((char *)(&ia[0] + 1) - (char *)&ia[0]));
    printf("char*   加 1 前进 %d 字节\n", (int)((char *)(&ca[0] + 1) - (char *)&ca[0]));
    printf("double* 加 1 前进 %d 字节\n", (int)((char *)(&da[0] + 1) - (char *)&da[0]));

    printf("\n=== sizeof 的差别 ===\n");
    int arr2[10];
    int *pp = arr2;
    printf("sizeof(arr2) = %d   (整个数组)\n", (int)sizeof(arr2));
    printf("sizeof(pp)   = %d   (指针本身的大小)\n", (int)sizeof(pp));

    printf("\n=== 指针可以为「空」 ===\n");
    int *np = NULL;
    printf("np == NULL 吗？ %d\n", np == NULL);
    if (np == NULL) {
        printf("判断语句里可以安全检查\n");
    }

    printf("\n=== 用指针交换两个变量 ===\n");
    int m = 1, n = 2;
    int *pm = &m, *pn = &n;
    int t = *pm;
    *pm = *pn;
    *pn = t;
    printf("交换后 m=%d n=%d\n", m, n);

    printf("\n=== 函数通过指针修改外部变量 ===\n");
    return 0;
}
