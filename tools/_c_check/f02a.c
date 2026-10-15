/* C 版：08-F02 的两个示例 */
#include <stdio.h>
#include <direct.h>       /* Windows 下的 _getcwd */

int main(int argc, char *argv[]) {
    char buf[4096];
    _getcwd(buf, sizeof(buf));

    printf("当前工作目录 (CWD) = %s\n", buf);
    printf("程序自己的路径     = %s\n", argc > 0 ? argv[0] : "?");
    return 0;
}
