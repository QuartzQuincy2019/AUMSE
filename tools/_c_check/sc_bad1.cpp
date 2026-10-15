// 故意写错 1：在块外面使用块内的变量
#include <iostream>
int main() {
    {
        int b = 2;
    }
    std::cout << b << std::endl;   // ← b 已经不在了
    return 0;
}
