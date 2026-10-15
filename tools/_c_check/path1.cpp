// 校验 08-F02：相对路径与 CWD
// 这个程序把「当前工作目录」和「相对路径解析结果」都打印出来，
// 用来证明：相对路径是相对于【工作目录】，不是相对于 exe 所在目录。
#include <iostream>
#include <string>
#include <vector>

#ifdef _WIN32
#include <direct.h>
#define GETCWD _getcwd
#else
#include <unistd.h>
#define GETCWD getcwd
#endif

using namespace std;

int main(int argc, char *argv[]) {
    (void)argc; (void)argv;

    char buf[4096];
    if (GETCWD(buf, sizeof(buf)) == nullptr) {
        cout << "取当前目录失败" << endl;
        return 1;
    }

    cout << "当前工作目录 (CWD) = " << buf << endl;
    cout << "程序自己的路径     = " << (argc > 0 ? argv[0] : "?") << endl;
    cout << endl;
    cout << "这两个不是一回事：CWD 是「你在哪敲的命令」，" << endl;
    cout << "argv[0] 是「程序文件在哪」。" << endl;

    cout << endl << "=== 宏演示 ===" << endl;
    cout << "程序编译于 " << __DATE__ << " " << __TIME__ << endl;
    cout << "这是第 " << __LINE__ << " 行" << endl;
    cout << "文件名   " << __FILE__ << endl;

    return 0;
}
