/* C 版：08-F02 读文件示例 */
#include <stdio.h>

int main(void) {
    FILE *fp = fopen("data.txt", "r");      /* 相对路径 */
    if (fp != NULL) {
        char line[256];
        printf("打开成功，内容:\n");
        while (fgets(line, sizeof(line), fp) != NULL) {
            printf("  %s", line);
        }
        fclose(fp);
    } else {
        printf("打开 data.txt 失败（当前目录里没有它）\n");
    }
    return 0;
}
