// 校验 08-F02：相对路径读文件的成败
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
    const char *name = "data.txt";

    ifstream in(name);
    if (in.is_open()) {
        string line;
        cout << "打开 " << name << " 成功，内容:" << endl;
        while (getline(in, line)) cout << "  " << line << endl;
        in.close();
    } else {
        cout << "打开 " << name << " 失败（当前目录里没有它）" << endl;
    }
    return 0;
}
