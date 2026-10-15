/* 校验 doc 08：C 风格字符串
   用 g++ 以 C 风格编译（避免 TCC 里 \\0 被再次解析的问题）。 */
#include <stdio.h>
#include <string.h>

int main(void) {
    printf("=== 1. 字符串就是「字符数组 + 结尾的 \\0」 ===\n");
    char a[] = "Mongol";
    printf("内容: %s\n", a);
    printf("sizeof(a) = %d  （占多少字节）\n", (int)sizeof(a));
    printf("strlen(a) = %d  （几个字符）\n", (int)strlen(a));
    printf("差 %d —— 结尾多了一个 '\\0'\n", (int)(sizeof(a) - strlen(a)));

    printf("\n=== 2. 逐字节看真实内容 ===\n");
    for (int i = 0; i < (int)sizeof(a); i++) {
        printf("a[%d] = %d\n", i, a[i]);
    }
    printf("（最后一个的数值是 0，就是 '\\0'，表示字符串到此结束）\n");

    printf("\n=== 3. sizeof 只在「数组名」上有效 ===\n");
    char arr[] = "Mongol";
    char *p = arr;
    printf("sizeof(arr) = %d\n", (int)sizeof(arr));
    printf("sizeof(p)   = %d  （只是指针）\n", (int)sizeof(p));
    printf("strlen(arr) = %d  （这个对两者都有效）\n", (int)strlen(arr));
    printf("strlen(p)   = %d\n", (int)strlen(p));

    printf("\n=== 4. 两种写法：数组 vs 指针 ===\n");
    char s1[] = "Mongol";
    char *s2  = "Mongol";
    s1[0] = 'T';
    printf("改过之后 s1 = %s\n", s1);
    printf("s2 = %s （不要改 s2[0]，那是只读区）\n", s2);

    printf("\n=== 5. == 比地址，strcmp 比内容 ===\n");
    char x[] = "abc";
    char y[] = "abc";
    char *q = x;
    printf("x == y  ? %d   （两个不同的数组，地址不同）\n", x == y);
    printf("x == q  ? %d   （同一个数组）\n", x == q);
    printf("strcmp(x, y) = %d  （0 表示内容相同）\n", strcmp(x, y));
    printf("strcmp(abc,abd) = %d\n", strcmp("abc", "abd"));
    printf("strcmp(abd,abc) = %d\n", strcmp("abd", "abc"));
    printf("strcmp(abc,ab)  = %d\n", strcmp("abc", "ab"));

    printf("\n=== 6. strcpy / strcat ===\n");
    char buf[32];
    strcpy(buf, "Mongol");
    printf("strcpy 后: %s\n", buf);
    strcat(buf, " bichig");
    printf("strcat 后: %s\n", buf);
    printf("长度 %d\n", (int)strlen(buf));

    printf("\n=== 7. strncpy 限定长度 ===\n");
    char small[6];
    strncpy(small, "Mongolian", sizeof(small) - 1);
    small[sizeof(small) - 1] = '\0';
    printf("small = %s （被截断到 5 个字符）\n", small);

    printf("\n=== 8. 查找字符 ===\n");
    char text[] = "Mongol bichig";
    char *found = strchr(text, ' ');
    if (found != NULL) {
        printf("找到空格，位置是下标 %d\n", (int)(found - text));
        printf("空格之后的内容: %s\n", found + 1);
    }
    char *none = strchr(text, 'z');
    printf("找 z：%s\n", none == NULL ? "没找到" : "找到了");

    printf("\n=== 9. 数字与字符的关系 ===\n");
    printf("A = %d, a = %d, 差 %d\n", 'A', 'a', 'a' - 'A');
    char c = 'a';
    printf("a 转大写: %c\n", c - 32);
    printf("a - a = %d\n", 'a' - 'a');

    return 0;
}
