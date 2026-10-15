/* 校验：指针的用途与常见疑难 */
#include <stdio.h>

/* 返回数组中第一个等于 target 的元素的指针；找不到返回 NULL */
int *find(int arr[], int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) {
            return &arr[i];
        }
    }
    return NULL;
}

/* 通过指针把两个数按从小到大排好 */
void sortTwo(int *a, int *b) {
    if (*a > *b) {
        int t = *a;
        *a = *b;
        *b = t;
    }
}

/* 用指针求数组和 */
int sumByPointer(int *begin, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        s += *(begin + i);
    }
    return s;
}

int main(void) {
    printf("=== & 与 * 是相反操作 ===\n");
    int x = 42;
    int *p = &x;
    printf("x     = %d\n", x);
    printf("*&x   = %d   （先取地址再解引用，回到原值）\n", *&x);
    printf("*p    = %d\n", *p);
    printf("p == &x ? %d\n", p == &x);

    printf("\n=== 指针指向数组中的一个元素 ===\n");
    int a[6] = {88, 52, 79, 95, 61, 84};
    int *q = find(a, 6, 79);
    if (q != NULL) {
        printf("找到了，*q = %d\n", *q);
        printf("它在第 %d 个（下标 %d）\n", (int)(q - a) + 1, (int)(q - a));
    }

    int *notfound = find(a, 6, 100);
    printf("找 100：%s\n", notfound == NULL ? "没找到" : "找到了");

    printf("\n=== 指针让函数能改外部变量 ===\n");
    int u = 9, v = 2;
    printf("排序前 u=%d v=%d\n", u, v);
    sortTwo(&u, &v);
    printf("排序后 u=%d v=%d\n", u, v);

    printf("\n=== 指针遍历（begin + i）===\n");
    printf("sumByPointer = %d\n", sumByPointer(a, 6));

    printf("\n=== 用指针在数组里「就地」加倍 ===\n");
    int b[4] = {1, 2, 3, 4};
    for (int *r = b; r < b + 4; r++) {
        *r = *r * 2;
    }
    for (int i = 0; i < 4; i++) printf("%d ", b[i]);
    printf("\n");

    printf("\n=== 疑难：指针的指针 ===\n");
    int w = 5;
    int *pw = &w;
    int **ppw = &pw;
    printf("  w    = %d\n", w);
    printf("  *pw  = %d\n", *pw);
    printf("  **ppw= %d\n", **ppw);
    printf("  *ppw == pw ? %d\n", *ppw == pw);

    printf("\n=== 疑难：NULL 指针不能解引用 ===\n");
    int *np = NULL;
    if (np == NULL) {
        printf("先判断再使用，这是安全做法\n");
    }

    printf("\n=== 疑难：指针类型要匹配 ===\n");
    int ival = 7;
    double dval = 1.5;
    int *ip = &ival;
    double *dp = &dval;
    printf("sizeof(int*)    = %d\n", (int)sizeof(ip));
    printf("sizeof(double*) = %d\n", (int)sizeof(dp));
    printf("*ip = %d   *dp = %.1f\n", *ip, *dp);

    return 0;
}
