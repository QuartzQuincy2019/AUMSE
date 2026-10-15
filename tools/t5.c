/* 校验：二进制、位、按位运算 */
#include <stdio.h>

/* 打印一个整数的二进制（32 位） */
void printBinary(int n) {
    for (int i = 31; i >= 0; i--) {
        printf("%d", (n >> i) & 1);
        if (i % 8 == 0 && i > 0) printf(" ");
    }
}

int main(void) {
    printf("=== 几个数的二进制 ===\n");
    int vals[5] = {0, 1, 2, 5, 255};
    for (int i = 0; i < 5; i++) {
        printf("%4d -> ", vals[i]);
        printBinary(vals[i]);
        printf("\n");
    }

    printf("\n=== 2 的幂与位数 ===\n");
    for (int i = 0; i <= 8; i++) {
        int v = 1 << i;
        printf("2^%d = %3d  二进制 ", i, v);
        printBinary(v);
        printf("\n");
    }

    printf("\n=== 一个字节能表示多少 ===\n");
    printf("1 字节 = 8 位\n");
    printf("无符号：2^8 = %d 种，0 ~ 255\n", 256);
    printf("有符号：-128 ~ 127（共 256 种）\n");

    printf("\n=== 取某一位 ===\n");
    int n = 5;   /* 二进制 101 */
    printf("n = %d，二进制 ", n);
    printBinary(n);
    printf("\n");
    printf("第 0 位 = %d\n", (n >> 0) & 1);
    printf("第 1 位 = %d\n", (n >> 1) & 1);
    printf("第 2 位 = %d\n", (n >> 2) & 1);
    printf("第 3 位 = %d\n", (n >> 3) & 1);

    printf("\n=== 奇偶判断的两种写法 ===\n");
    for (int i = 1; i <= 6; i++) {
        printf("%d: %%2=%d   &1=%d\n", i, i % 2, i & 1);
    }

    printf("\n=== 负数在内存里（补码）===\n");
    printf("-1 -> ");
    printBinary(-1);
    printf("\n");
    printf("-2 -> ");
    printBinary(-2);
    printf("\n");
    printf("(unsigned char)-1 = %d\n", (int)(unsigned char)-1);

    printf("\n=== 大小端：一个 int 的 4 个字节 ===\n");
    unsigned int v = 0x01020304u;
    unsigned char *bp = (unsigned char *)&v;
    for (int i = 0; i < 4; i++) {
        printf("第 %d 个字节 = 0x%02X\n", i, bp[i]);
    }

    return 0;
}
