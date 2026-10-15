/* 教程示例校验 1：数组基础 */
#include <stdio.h>

int main(void) {
    /* ① 声明与初始化 */
    int a[5] = {3, 1, 4, 1, 5};
    printf("%d %d %d %d %d\n", a[0], a[1], a[2], a[3], a[4]);

    /* 省略长度 */
    int b[] = {10, 20, 30};
    printf("%d %d %d\n", b[0], b[1], b[2]);

    /* 部分初始化 */
    int c[5] = {1, 2};
    printf("%d %d %d %d %d\n", c[0], c[1], c[2], c[3], c[4]);

    /* 全部置 0 */
    int z[4] = {0};
    printf("%d %d %d %d\n", z[0], z[1], z[2], z[3]);

    /* ② 下标读写 */
    int d[5] = {3, 1, 4, 1, 5};
    d[0] = 100;
    d[4] = d[0] + d[1];
    printf("%d %d %d %d %d\n", d[0], d[1], d[2], d[3], d[4]);

    /* ③ 用循环遍历 */
    int e[5] = {3, 1, 4, 1, 5};
    for (int i = 0; i < 5; i++) {
        printf("e[%d] = %d\n", i, e[i]);
    }

    /* ④ 倒着遍历 */
    for (int i = 4; i >= 0; i--) {
        printf("%d ", e[i]);
    }
    printf("\n");

    /* ⑤ 求和与平均 */
    int sum = 0;
    for (int i = 0; i < 5; i++) {
        sum += e[i];
    }
    printf("sum = %d\n", sum);
    printf("avg = %.2f\n", sum / 5.0);

    /* ⑥ 最大值 */
    int mx = e[0];
    for (int i = 1; i < 5; i++) {
        if (e[i] > mx) {
            mx = e[i];
        }
    }
    printf("max = %d\n", mx);

    /* ⑦ 计数 */
    int n1 = 0;
    for (int i = 0; i < 5; i++) {
        if (e[i] == 1) {
            n1++;
        }
    }
    printf("count of 1 = %d\n", n1);

    /* ⑧ 查找 */
    int target = 4;
    int pos = -1;
    for (int i = 0; i < 5; i++) {
        if (e[i] == target) {
            pos = i;
            break;
        }
    }
    if (pos >= 0) {
        printf("found at %d\n", pos);
    } else {
        printf("not found\n");
    }

    /* ⑨ 逆序存放 */
    int src[5] = {1, 2, 3, 4, 5};
    int rev[5];
    for (int i = 0; i < 5; i++) {
        rev[i] = src[4 - i];
    }
    for (int i = 0; i < 5; i++) {
        printf("%d ", rev[i]);
    }
    printf("\n");

    /* ⑩ 元素颠倒（原地交换） */
    int f[5] = {1, 2, 3, 4, 5};
    for (int i = 0; i < 5 / 2; i++) {
        int t = f[i];
        f[i] = f[4 - i];
        f[4 - i] = t;
    }
    for (int i = 0; i < 5; i++) {
        printf("%d ", f[i]);
    }
    printf("\n");

    /* ⑪ 辅助数组打标记：统计每个数字出现次数 */
    int g[8] = {2, 5, 2, 7, 5, 2, 9, 7};
    int cnt[10] = {0};
    for (int i = 0; i < 8; i++) {
        cnt[g[i]]++;
    }
    for (int v = 0; v <= 9; v++) {
        if (cnt[v] > 0) {
            printf("%d 出现 %d 次\n", v, cnt[v]);
        }
    }

    return 0;
}
