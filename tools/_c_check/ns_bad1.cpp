// 故意写错 ①：忘了写命名空间
#include <iostream>
namespace ume {
    int version = 10;
}
int main() {
    std::cout << version << "\n";   // 少了 ume::
    return 0;
}
