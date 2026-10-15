// 同一个程序：C 写法 vs C++ 写法（doc 10 用）
#include <cstdio>       // C 风格
#include <cstring>
#include <cstdlib>

#include <iostream>     // C++ 风格
#include <string>
#include <vector>
#include <algorithm>

// ---------------- C 写法 ----------------
struct CPlayer {
    char name[32];
    int  hp;
};

// 函数只能放在外面，第一个参数得自己传指针
void c_player_init(CPlayer *p, const char *n, int hp) {
    strncpy(p->name, n, sizeof(p->name) - 1);
    p->name[sizeof(p->name) - 1] = '\0';
    p->hp = hp;
}
void c_player_hit(CPlayer *p, int d) {
    p->hp -= d;
    if (p->hp < 0) p->hp = 0;
}
void c_player_show(const CPlayer *p) {
    printf("  [C ] %s HP=%d\n", p->name, p->hp);
}

// 数组要靠 malloc，还得自己 free
void c_demo() {
    printf("=== C 写法 ===\n");
    int n = 3;
    CPlayer *team = (CPlayer *)malloc(sizeof(CPlayer) * n);
    if (team == NULL) return;

    c_player_init(&team[0], "Archer", 100);
    c_player_init(&team[1], "Mage", 80);
    c_player_init(&team[2], "Knight", 150);

    for (int i = 0; i < n; i++) c_player_hit(&team[i], 30);
    for (int i = 0; i < n; i++) c_player_show(&team[i]);

    free(team);          // 忘了这行就泄漏
}

// ---------------- C++ 写法 ----------------
namespace ume {
    struct Player {
        std::string name;            // 不用管长度
        int hp = 100;                // 有默认值

        // 函数就放在类型里
        void hit(int d) {
            hp -= d;
            if (hp < 0) hp = 0;
        }
        void show() const {
            std::cout << "  [C++] " << name << " HP=" << hp << "\n";
        }
    };
}

void cpp_demo() {
    std::cout << "=== C++ 写法 ===\n";

    // 会自动增长的数组，不用 malloc / free
    std::vector<ume::Player> team;

    team.push_back({"Archer", 100});
    team.push_back({"Mage", 80});
    team.push_back({"Knight", 150});

    for (auto &p : team) p.hit(30);      // 范围 for + 引用
    for (const auto &p : team) p.show();
}

int main() {
    c_demo();
    std::cout << "\n";
    cpp_demo();
    return 0;
}
