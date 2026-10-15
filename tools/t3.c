/* 校验：指针作参数、字符串、数组退化的证据 */
#include <stdio.h>

/* ① 通过指针修改外部变量 —— 经典 swap */
void swap(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

/* ② 求最大最小并「带出来」 */
void minMax(int arr[], int n, int *pMin, int *pMax) {
    *pMin = arr[0];
    *pMax = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < *pMin) *pMin = arr[i];
        if (arr[i] > *pMax) *pMax = arr[i];
    }
}

/* ③ 累加器 */
void addTo(int *total, int v) {
    *total += v;
}

/* ④ 指针版 strlen */
int myStrLen(char *s) {
    int n = 0;
    while (*s != '\0') {
        n++;
        s++;
    }
    return n;
}

/* ⑤ 数组退化：函数里 sizeof 拿不到真实长度 */
int sizeInFunc(int arr[]) {
    return (int)sizeof(arr);
}
int sizeInFunc2(int *arr) {
    return (int)sizeof(arr);
}

int main(void) {
    printf("=== swap ===\n");
    int x = 3, y = 8;
    printf("交换前 x=%d y=%d\n", x, y);
    swap(&x, &y);
    printf("交换后 x=%d y=%d\n", x, y);

    printf("\n=== 同时带回两个结果 ===\n");
    int a[6] = {88, 52, 79, 95, 61, 84};
    int mn, mx;
    minMax(a, 6, &mn, &mx);
    printf("最小 = %d, 最大 = %d\n", mn, mx);

    printf("\n=== 累加器 ===\n");
    int total = 0;
    for (int i = 0; i < 6; i++) {
        addTo(&total, a[i]);
    }
    printf("total = %d\n", total);

    printf("\n=== 字符串与 char* ===\n");
    char s[] = "Mongol";
    char *p = s;
    printf("s      = %s\n", s);
    printf("逐字符: ");
    while (*p != '\0') {
        printf("%c ", *p);
        p++;
    }
    printf("\n");
    printf("myStrLen(s) = %d\n", myStrLen(s));
    printf("s[0]=%c  *(s+1)=%c  *(s+5)=%c\n", s[0], *(s + 1), *(s + 5));
    printf("sizeof(s) = %d  (含结尾的 '\0')\n", (int)sizeof(s));

    printf("\n=== 数组退化的证据 ===\n");
    int arr[10];
    printf("main 里 sizeof(arr)  = %d\n", (int)sizeof(arr));
    printf("函数里 sizeof(arr)   = %d\n", sizeInFunc(arr));
    printf("指针参数 sizeof(arr) = %d\n", sizeInFunc2(arr));
    printf("sizeof(int*)         = %d\n", (int)sizeof(int *));

    printf("\n=== 指针可以改指向 ===\n");
    int u = 1, v = 2;
    int *q = &u;
    printf("*q = %d\n", *q);
    q = &v;
    printf("改指后 *q = %d\n", *q);

    printf("\n=== 二级指针：指针的地址 ===\n");
    int w = 5;
    int *pw = &w;
    int **ppw = &pw;
    printf("w=%d  *pw=%d  **ppw=%d\n", w, *pw, **ppw);
    **ppw = 50;
    printf("执行 **ppw = 50 后 w = %d\n", w);

    return 0;
}
