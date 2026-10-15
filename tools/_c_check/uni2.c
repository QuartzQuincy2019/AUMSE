/* C 版：09-F04 的字节打印与 sizeof 演示
   用 gcc -std=c99 实跑核对。 */
#include <stdio.h>
#include <string.h>

/* 把一段字节按十六进制打印出来 */
void dump_bytes(const char *s, const char *label) {
    printf("%s (%d 字节): ", label, (int)strlen(s));
    for (int i = 0; i < (int)strlen(s); i++) {
        printf("%02X ", (unsigned char)s[i]);
    }
    printf("\n");
}

int main(void) {
    printf("=== 1. 不同字符在 UTF-8 下的字节 ===\n");
    dump_bytes("A", "ASCII 里的 A");
    dump_bytes("\xC3\xA9", "e 带音标 U+00E9");
    dump_bytes("\xE4\xB8\xAD", "中 U+4E2D");
    dump_bytes("\xE1\xA0\xAE", "蒙文 MA U+182E");
    dump_bytes("\xF0\x9F\x98\x80", "笑脸 U+1F600");

    printf("\n=== 2. 字节数 != 字符数 ===\n");
    printf("「中」strlen = %d 字节，但它只是 1 个字符\n",
           (int)strlen("\xE4\xB8\xAD"));

    /* ᠮᠣᠩᠭᠣᠯ：6 个蒙文字母，每个 3 字节 */
    const char *mongol = "\xE1\xA0\xAE\xE1\xA0\xA3\xE1\xA0\xA9"
                         "\xE1\xA0\xAD\xE1\xA0\xA3\xE1\xA0\xAF";
    printf("蒙文串 strlen = %d 字节（6 个蒙文字母）\n", (int)strlen(mongol));

    printf("\n=== 3. char 与 wchar_t ===\n");
    printf("sizeof(char)    = %d\n", (int)sizeof(char));
    printf("sizeof(wchar_t) = %d\n", (int)sizeof(wchar_t));
    printf("wchar_t 能装下 U+182E 吗？ %s\n",
           0x182E <= 0xFFFF ? "能" : "不能");

    return 0;
}
