// 故意写错 ②：两个命名空间都有同名函数，却都 using namespace
#include <iostream>
namespace A { void hello() { std::cout << "A\n"; } }
namespace B { void hello() { std::cout << "B\n"; } }

using namespace A;
using namespace B;

int main() {
    hello();          // 不知道要哪个 → 二义性
    return 0;
}
