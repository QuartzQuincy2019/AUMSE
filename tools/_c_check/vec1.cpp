// 校验 09：vector 与 array
#include <iostream>
#include <vector>
#include <array>
#include <algorithm>
#include <string>
using namespace std;

// 传 vector：用引用，避免拷贝
void printAll(const vector<int> &v) {
    for (int x : v) cout << x << " ";
    cout << endl;
}

// 传 array：必须带长度（模板参数）
void printArr(const array<int, 5> &a) {
    for (int x : a) cout << x << " ";
    cout << endl;
}

int main() {
    cout << "=== ① 裸数组的困境：长度写死 ===" << endl;
    int raw[5] = {1, 2, 3, 4, 5};
    cout << "裸数组只能装 5 个，sizeof = " << sizeof(raw) << endl;

    cout << "\n=== ② vector：能自动增长 ===" << endl;
    vector<int> v;                       // 一开始是空的
    cout << "初始 size = " << v.size() << endl;
    for (int i = 1; i <= 5; i++) v.push_back(i * 10);
    cout << "push_back 五次后 size = " << v.size() << endl;
    cout << "内容: "; printAll(v);

    v.push_back(60);
    cout << "再 push 一个，size = " << v.size() << "，内容: "; printAll(v);

    cout << "\n=== ③ 访问元素：[] 与 at 的区别 ===" << endl;
    cout << "v[0] = " << v[0] << ", v[5] = " << v[5] << endl;
    cout << "v.at(0) = " << v.at(0) << endl;
    cout << "（v.at(100) 会抛异常；v[100] 是未定义行为，不检查）" << endl;
    cout << "front = " << v.front() << ", back = " << v.back() << endl;

    cout << "\n=== ④ 遍历的三种写法 ===" << endl;
    cout << "下标:   ";
    for (size_t i = 0; i < v.size(); i++) cout << v[i] << " ";
    cout << endl;
    cout << "范围for: ";
    for (int x : v) cout << x << " ";
    cout << endl;
    cout << "迭代器: ";
    for (vector<int>::iterator it = v.begin(); it != v.end(); ++it) cout << *it << " ";
    cout << endl;

    cout << "\n=== ⑤ 初始化与预分配 ===" << endl;
    vector<int> a(3, 7);                 // 3 个 7
    cout << "vector<int> a(3,7): "; printAll(a);
    vector<int> b{1, 2, 3};              // 列表初始化
    cout << "vector<int> b{1,2,3}: "; printAll(b);
    vector<int> c;
    c.reserve(100);                      // 预留容量，避免反复搬内存
    cout << "reserve(100) 后 capacity = " << c.capacity() << ", size = " << c.size() << endl;

    cout << "\n=== ⑥ 插入与删除 ===" << endl;
    vector<int> d{10, 20, 30, 40};
    cout << "初始: "; printAll(d);
    d.insert(d.begin() + 1, 15);         // 在下标 1 处插入
    cout << "在下标1前插15: "; printAll(d);
    d.erase(d.begin() + 2);              // 删掉下标 2
    cout << "删掉下标2: "; printAll(d);
    d.pop_back();
    cout << "pop_back: "; printAll(d);
    d.clear();
    cout << "clear 后 size = " << d.size() << endl;

    cout << "\n=== ⑦ array：固定长度但更安全 ===" << endl;
    array<int, 5> ar = {5, 3, 8, 1, 9};
    cout << "内容: "; printArr(ar);
    cout << "size() = " << ar.size() << endl;
    cout << "ar[0] = " << ar[0] << ", ar.at(4) = " << ar.at(4) << endl;
    cout << "front = " << ar.front() << ", back = " << ar.back() << endl;

    cout << "\n=== ⑧ array 与裸数组的关键差别 ===" << endl;
    int raw2[5] = {5, 3, 8, 1, 9};
    array<int, 5> ar2 = {5, 3, 8, 1, 9};
    cout << "sizeof(裸数组) = " << sizeof(raw2) << "  （20 字节）" << endl;
    cout << "sizeof(array)  = " << sizeof(ar2) << "  （也是 20 字节）" << endl;
    cout << "array 能直接问长度: ar2.size() = " << ar2.size() << endl;
    cout << "array 能整体赋值:" << endl;
    array<int, 5> ar3;
    ar3 = ar2;                           // 裸数组不能这样
    cout << "  ar3 = ar2 之后: "; printArr(ar3);

    cout << "\n=== ⑨ 排序与查找（用标准库）===" << endl;
    vector<int> e{5, 3, 8, 1, 9, 2};
    cout << "排序前: "; printAll(e);
    sort(e.begin(), e.end());
    cout << "排序后: "; printAll(e);
    sort(e.begin(), e.end(), greater<int>());
    cout << "降序:   "; printAll(e);
    sort(e.begin(), e.end());

    auto it = find(e.begin(), e.end(), 8);
    if (it != e.end())
        cout << "找到 8，下标 " << (it - e.begin()) << endl;
    auto it2 = find(e.begin(), e.end(), 100);
    cout << "找 100: " << (it2 == e.end() ? "没找到" : "找到了") << endl;

    cout << "\n=== ⑩ 二维：vector 套 vector ===" << endl;
    vector<vector<int>> grid(3, vector<int>(4, 0));   // 3 行 4 列，全 0
    for (int r = 0; r < 3; r++)
        for (int c = 0; c < 4; c++)
            grid[r][c] = r * 10 + c;
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 4; c++) cout << grid[r][c] << " ";
        cout << endl;
    }
    cout << "行数 = " << grid.size() << ", 列数 = " << grid[0].size() << endl;

    cout << "\n=== ⑪ 字符串数组 ===" << endl;
    vector<string> names{"Archer", "Mage", "Knight"};
    for (const string &s : names) cout << s << " ";
    cout << endl;
    names.push_back("Healer");
    cout << "加一个后 size = " << names.size() << endl;

    cout << "\n=== ⑫ 用 vector 解决「运行时才知道长度」 ===" << endl;
    vector<int> nums;
    nums.reserve(4);
    for (int i = 1; i <= 4; i++) nums.push_back(i * i);
    cout << "平方数: "; printAll(nums);
    cout << "（不需要事先知道要存几个，也不用 malloc/free）" << endl;

    return 0;
}
