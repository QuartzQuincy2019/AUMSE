/* 校验：补码、回绕、按位运算、类型转换 */
#include <stdio.h>

int main(void) {
    printf("=== 按位运算 ===\n");
    int a = 12, b = 10;
    printf("12 & 10  = %d\n", a & b);
    printf("12 | 10  = %d\n", a | b);
    printf("12 ^ 10  = %d\n", a ^ b);
    printf("12 << 1  = %d\n", a << 1);
    printf("12 >> 1  = %d\n", a >> 1);

    printf("\n=== %d 的十六进制 ===\n", a);
    printf("12 = 0x%X\n", a);
    printf("255 = 0x%X\n", 255);
    printf("0xFF = %d\n", 0xFF);
    printf("0x10 = %d\n", 0x10);

    printf("\n=== 回绕：0 减 1 的两种命运 ===\n");
    int  i = 0;
    unsigned int u = 0;
    printf("int      0 - 1 = %d\n", i - 1);
    printf("unsigned 0 - 1 = %u\n", u - 1);
    printf("short    0 - 1 = %d\n", (short)((short)0 - 1));
    unsigned char uc = 0;
    printf("uchar    0 - 1 = %d\n", (int)(unsigned char)(uc - 1));

    printf("\n=== 有符号 / 无符号比较陷阱 ===\n");
    unsigned int big = 1;
    if (big > -1) {
        printf("1 > -1 成立（无符号视角下 -1 变成很大的数）\n");
    } else {
        printf("1 > -1 不成立\n");
    }
    printf("(unsigned)-1 = %u\n", (unsigned)-1);

    printf("\n=== 类型转换：数值变了 ===\n");
    int v = 300;
    printf("(char)300 = %d\n", (char)v);
    printf("(short)70000 = %d\n", (short)70000);
    printf("(unsigned char)300 = %d\n", (unsigned char)v);

    printf("\n=== 类型转换：小数变整数是截断 ===\n");
    printf("(int)3.9   = %d\n", (int)3.9);
    printf("(int)-3.9  = %d\n", (int)-3.9);
    printf("(int)3.5+ (int)3.5 = %d\n", (int)3.5 + (int)3.5);
    printf("(int)(3.5+3.5)     = %d\n", (int)(3.5 + 3.5));

    printf("\n=== 整数除法 ===\n");
    printf("7/2   = %d\n", 7 / 2);
    printf("7/2.0 = %.1f\n", 7 / 2.0);
    printf("(double)7/2 = %.1f\n", (double)7 / 2);

    printf("\n=== 一个 struct 占多少字节 ===\n");
    struct P { int x; int y; };
    struct Q { char c; int n; };
    struct R { char a; char b; char c; char d; };
    printf("struct P { int x; int y; }        = %d 字节\n", (int)sizeof(struct P));
    printf("struct Q { char c; int n; }       = %d 字节\n", (int)sizeof(struct Q));
    printf("struct R { char a,b,c,d; }        = %d 字节\n", (int)sizeof(struct R));

    return 0;
}
