// 场景 3：重复定义（同一个变量在两个 .cpp 里都定义了）
// 这里用两个函数模拟：把定义写在头文件里被包含两次的效果
#include <iostream>
using namespace std;

int gCount = 0;      // 定义（会分配内存）

int main() {
    gCount++;
    cout << gCount << endl;
    return 0;
}
