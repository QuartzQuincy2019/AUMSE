// 校验 doc 10：std 与命名空间
#include <iostream>
#include <string>
#include <vector>
using namespace std;

// ---------- 1. 为什么需要命名空间 ----------
namespace ume {
    int version = 10;
    void hello() { cout << "  ume::hello() 被调用\n"; }
}
namespace other {
    int version = 99;
    void hello() { cout << "  other::hello() 被调用\n"; }
}

// ---------- 2. 嵌套命名空间 ----------
namespace ume {
    namespace font {
        int count = 42;
        void info() { cout << "  ume::font::info()，字体数 = " << count << "\n"; }
    }
}

// C++17 嵌套写法
namespace a::b::c {
    int deep = 7;
}

// ---------- 3. using 声明 vs using 指令 ----------
namespace lib {
    int x = 1;
    int y = 2;
}

// ---------- 4. 匿名命名空间（内部链接，相当于 static） ----------
namespace {
    int hidden = 123;
    void onlyHere() { cout << "  匿名命名空间里的函数\n"; }
}

// ---------- 5. 同名冲突演示：在函数内 using ----------
void conflictDemo() {
    using lib::x;              // 只引入 x
    cout << "  conflictDemo: x = " << x << "\n";
    cout << "  conflictDemo: lib::y = " << lib::y << "（y 没引入，要写全名）\n";
}

// ---------- 6. 自定义类型的命名空间 ----------
namespace ume {
    struct Player {
        string name;
        int hp;
    };
    void show(const Player &p) {
        cout << "  " << p.name << " HP=" << p.hp << "\n";
    }
}

int main() {
    cout << "=== 1. 命名空间解决重名 ===\n";
    cout << "  ume::version   = " << ume::version << "\n";
    cout << "  other::version = " << other::version << "\n";
    ume::hello();
    other::hello();

    cout << "\n=== 2. 嵌套命名空间 ===\n";
    ume::font::info();
    cout << "  a::b::c::deep = " << a::b::c::deep << "\n";

    cout << "\n=== 3. using 声明 ===\n";
    conflictDemo();

    cout << "\n=== 4. 匿名命名空间 ===\n";
    cout << "  hidden = " << hidden << "\n";
    onlyHere();

    cout << "\n=== 5. std 里的东西 ===\n";
    cout << "  std::string  : " << string("蒙古文 editor") << "\n";
    vector<int> v{1, 2, 3};
    cout << "  std::vector  : size=" << v.size() << "\n";
    cout << "  std::cout 就是本行用的这个输出流\n";

    cout << "\n=== 6. 自定义类型 ===\n";
    ume::Player p{"Archer", 100};
    ume::show(p);

    cout << "\n=== 7. 完全限定名 vs using ===\n";
    cout << "  全名: " << ume::font::count << "\n";
    {
        using namespace ume::font;
        cout << "  using namespace 之后: " << count << "\n";
    }

    cout << "\n=== 8. std:: 里的版本号 ===\n";
    cout << "  __cplusplus = " << __cplusplus << "\n";

    return 0;
}
