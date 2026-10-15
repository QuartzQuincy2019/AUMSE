/* 校验：常见类型的存储大小与取值范围 */
#include <stdio.h>
#include <limits.h>

int main(void) {
    printf("=== 类型大小 (bytes) ===\n");
    printf("char        %d\n", (int)sizeof(char));
    printf("short       %d\n", (int)sizeof(short));
    printf("int         %d\n", (int)sizeof(int));
    printf("long        %d\n", (int)sizeof(long));
    printf("long long   %d\n", (int)sizeof(long long));
    printf("unsigned    %d\n", (int)sizeof(unsigned int));
    printf("float       %d\n", (int)sizeof(float));
    printf("double      %d\n", (int)sizeof(double));
    printf("char*       %d\n", (int)sizeof(char *));

    printf("\n=== 取值范围 ===\n");
    printf("char        %d ~ %d\n", CHAR_MIN, CHAR_MAX);
    printf("short       %d ~ %d\n", SHRT_MIN, SHRT_MAX);
    printf("int         %d ~ %d\n", INT_MIN, INT_MAX);
    printf("long long   %lld ~ %lld\n", LLONG_MIN, LLONG_MAX);
    printf("unsigned    %u ~ %u\n", 0u, UINT_MAX);
    printf("unsigned short %u ~ %u\n", 0u, USHRT_MAX);

    printf("\n=== 位数 ===\n");
    printf("int 有 %d 位\n", (int)(sizeof(int) * 8));
    printf("char 有 %d 位\n", (int)(sizeof(char) * 8));

    printf("\n=== 整数溢出的实际行为 ===\n");
    int big = INT_MAX;
    printf("INT_MAX      = %d\n", big);
    printf("INT_MAX + 1  = %d\n", big + 1);
    printf("INT_MIN      = %d\n", INT_MIN);
    printf("INT_MIN - 1  = %d\n", INT_MIN - 1);

    printf("\n=== 无符号回绕 ===\n");
    unsigned int u = 0;
    printf("0u - 1       = %u\n", u - 1);
    unsigned char uc = 255;
    printf("(unsigned char)255 + 1 = %d\n", (int)(unsigned char)(uc + 1));

    printf("\n=== char 作为整数的两面 ===\n");
    char c1 = 'A';
    char c2 = 65;
    printf("'A' = %d, 65 = %c\n", c1, c2);
    char neg = -1;
    unsigned char pos = (unsigned char)-1;
    printf("(char)-1 = %d\n", (int)neg);
    printf("(unsigned char)-1 = %d\n", (int)pos);

    printf("\n=== 整数除法的方向 ===\n");
    printf("7 / 2   = %d\n", 7 / 2);
    printf("-7 / 2  = %d\n", -7 / 2);
    printf("7 %% 2   = %d\n", 7 % 2);
    printf("-7 %% 2  = %d\n", -7 % 2);

    printf("\n=== 类型转换 ===\n");
    int i = 300;
    char ch = (char)i;
    printf("(char)300 = %d\n", (int)ch);
    printf("(int)3.9   = %d\n", (int)3.9);
    printf("(int)-3.9  = %d\n", (int)-3.9);
    printf("5 / 2      = %d\n", 5 / 2);
    printf("5 / 2.0    = %.1f\n", 5 / 2.0);

    return 0;
}
