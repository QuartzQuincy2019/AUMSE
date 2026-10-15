// 场景 1：只有声明没有定义 → 链接错误
#include <iostream>
using namespace std;

int add(int a, int b);      // 声明了，但没人实现它

int main() {
    cout << add(1, 2) << endl;
    return 0;
}
