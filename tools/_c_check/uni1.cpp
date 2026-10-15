// 校验 09-F04：Unicode 与编码
#include <iostream>
#include <string>
#include <iomanip>
using namespace std;

// 按 UTF-8 规则把字节序列打印出来
void dumpBytes(const string &s, const char *label) {
    cout << label << " (" << s.size() << " 字节): ";
    for (unsigned char c : s) {
        cout << hex << uppercase << setw(2) << setfill('0') << (int)c << " ";
    }
    cout << dec << setfill(' ');
    cout << endl;
}

int main() {
    cout << "=== 1. 同一个「A」，不同编码字节数相同 ===" << endl;
    string a = "A";
    dumpBytes(a, "ASCII 里的 A");

    cout << "\n=== 2. 非 ASCII 字符：UTF-8 要几个字节 ===" << endl;
    string s1 = "\u00E9";            // é
    string s2 = "\u4E2D";            // 中
    string s3 = "\u182E";            // ᠮ 回鹘蒙文 MA
    string s4 = "\U0001F600";        // 😀
    dumpBytes(s1, "é  (U+00E9)");
    dumpBytes(s2, "中 (U+4E2D)");
    dumpBytes(s3, "ᠮ  (U+182E)  回鹘蒙文");
    dumpBytes(s4, "😀 (U+1F600)");

    cout << "\n=== 3. 关键：字节数 != 字符数 ===" << endl;
    cout << "「中」的 size() = " << s2.size()
         << "  但它只是 1 个字符" << endl;
    cout << "蒙文串示例:" << endl;
    string mongol = "\u182E\u1823\u1829\u182D\u1823\u182F";   // ᠮᠣᠩᠭᠣᠯ
    cout << "  ᠮᠣᠩᠭᠣᠯ 的 size() = " << mongol.size() << " 字节（6 个蒙文字母）" << endl;
    cout << "  用 strlen 得到 " << mongol.size() << "，那不是「几个字母」" << endl;

    cout << "\n=== 4. char 与 wchar_t ===" << endl;
    cout << "sizeof(char)    = " << sizeof(char) << endl;
    cout << "sizeof(wchar_t) = " << sizeof(wchar_t) << "  (Windows 上是 2)" << endl;
    wchar_t wc = L'\u182E';
    cout << "wchar_t 能装下 U+182E 吗？ " << (wc == 0x182E ? "能" : "不能") << endl;

    cout << "\n=== 5. U+182E 的码位与 UTF-8 编码对照 ===" << endl;
    unsigned int cp = 0x182E;
    cout << "码位 = U+" << hex << uppercase << cp << dec << endl;
    cout << "UTF-8 字节 = ";
    for (unsigned char c : s3) cout << hex << uppercase << setw(2) << setfill('0') << (int)c << " ";
    cout << dec << setfill(' ') << endl;
    cout << "（3 字节：因为 U+182E 落在 U+0800~U+FFFF 区间）" << endl;

    cout << "\n=== 6. 蒙文码位分布 ===" << endl;
    cout << "U+1800 ~ U+18AF  蒙文主区段（含标点、FVS）" << endl;
    cout << "U+1820 ~ U+18AA  传统蒙文字母" << endl;
    cout << "U+11660 ~ U+1167F 蒙文补充区段" << endl;

    return 0;
}
