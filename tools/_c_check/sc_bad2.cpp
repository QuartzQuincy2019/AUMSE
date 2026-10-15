// 故意写错 2：在循环外面使用循环变量
#include <iostream>
int main() {
    for (int i = 0; i < 3; i++) { }
    std::cout << i << std::endl;   // ← i 已经不在了
    return 0;
}
