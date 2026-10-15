/* 校验：有符号 / 无符号比较陷阱 */
#include <stdio.h>

int main(void) {
    int i = -1;
    unsigned int u = 1;

    /* 正确写法：显式转向无符号，才能看出陷阱 */
    if (u > (unsigned int)i) {
        printf("u=1 > (unsigned)-1 → 成立（-1 被当成 4294967295）\n");
    } else {
        printf("不成立\n");
    }

    /* 常见陷阱：变量参与比较时，int 会被悄悄转成 unsigned */
    int n = -1;
    unsigned int m = 1;
    printf("m > n 的结果 = %d   （人们常以为该成立）\n", m > n);

    /* 循环变量的陷阱 */
    printf("\n=== 无符号循环变量的陷阱 ===\n");
    printf("for (unsigned i = 5; i >= 0; i--) 会死循环\n");
    printf("  因为 i=0 再减 1 会变成 %u\n", 0u - 1);

    printf("\n=== sizeof 的结果是无符号的 ===\n");
    int arr[3];
    /* sizeof(arr)/sizeof(arr[0]) - 1 若无符号参与减法要小心 */
    printf("(int)(sizeof(arr)/sizeof(arr[0])) = %d\n",
           (int)(sizeof(arr) / sizeof(arr[0])));

    return 0;
}
