/* 场景 A：只有声明没有定义 → 链接错误（C 版） */
#include <stdio.h>

int add(int a, int b);      /* 声明了，但没人实现它 */

int main(void) {
    printf("%d\n", add(1, 2));
    return 0;
}
