// 验证本机这份 HarfBuzz 能真出字形：与 A01 的 uharfbuzz 数字对拍。
//
// 编译（见 build.ps1）：
//   g++ hb_probe.cpp -I D:/libs/harfbuzz-mingw/include/harfbuzz \
//       -L D:/libs/harfbuzz-mingw/lib -lharfbuzz -o hb_probe.exe
//
// 期望输出与 A01 / report/harfbuzz-ground-truth.txt 一致：
//   5 个字形，推进 492 573 614 838 383，合计 2900
#include <hb.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

static const char *FONT = "E:/QKMansion/CSX10/w/UME/font/NotoSansMongolian-Regular.ttf";

static std::string utf8(const std::vector<unsigned> &cps) {
    std::string s;
    for (unsigned c : cps) {
        if (c < 0x80) s += char(c);
        else if (c < 0x800) { s += char(0xC0 | (c >> 6)); s += char(0x80 | (c & 0x3F)); }
        else if (c < 0x10000) {
            s += char(0xE0 | (c >> 12));
            s += char(0x80 | ((c >> 6) & 0x3F));
            s += char(0x80 | (c & 0x3F));
        } else {
            s += char(0xF0 | (c >> 18));
            s += char(0x80 | ((c >> 12) & 0x3F));
            s += char(0x80 | ((c >> 6) & 0x3F));
            s += char(0x80 | (c & 0x3F));
        }
    }
    return s;
}

int main() {
    printf("HarfBuzz 编译期版本: %s\n", HB_VERSION_STRING);
    printf("HarfBuzz 运行期版本: %s\n", hb_version_string());

    hb_blob_t *blob = hb_blob_create_from_file_or_fail(FONT);
    if (!blob) { printf("字体打不开: %s\n", FONT); return 1; }
    hb_face_t *face = hb_face_create(blob, 0);
    hb_font_t *font = hb_font_create(face);
    hb_font_set_scale(font, 64 * 64, 64 * 64);   /* 64px */
    hb_font_set_ppem(font, 64, 64);

    printf("字体: upem=%u  字形数=%u\n",
           hb_face_get_upem(face), hb_face_get_glyph_count(face));

    /* ᠮᠣᠩᠭᠣᠯ = U+182E U+1823 U+1829 U+182D U+1823 U+182F */
    const std::vector<unsigned> cps = {0x182E, 0x1823, 0x1829, 0x182D, 0x1823, 0x182F};
    const std::string text = utf8(cps);

    hb_buffer_t *buf = hb_buffer_create();
    hb_buffer_add_utf8(buf, text.c_str(), int(text.size()), 0, int(text.size()));
    hb_buffer_guess_segment_properties(buf);
    hb_shape(font, buf, nullptr, 0);

    unsigned n = hb_buffer_get_length(buf);
    hb_glyph_info_t *info = hb_buffer_get_glyph_infos(buf, nullptr);
    hb_glyph_position_t *pos = hb_buffer_get_glyph_positions(buf, nullptr);

    printf("码位 %zu 个 → 字形 %u 个\n", cps.size(), n);
    int total = 0;
    for (unsigned i = 0; i < n; ++i) {
        char name[64] = {0};
        hb_font_get_glyph_name(font, info[i].codepoint, name, sizeof(name));
        printf("  [%u] gid=%-5u %-28s adv=%-5d cluster=%u\n",
               i, info[i].codepoint, name[0] ? name : "(无名)",
               pos[i].x_advance, info[i].cluster);
        total += pos[i].x_advance;
    }
    printf("总推进 = %d（定点数，/64 = %.4f px）\n", total, total / 64.0);

    hb_buffer_destroy(buf);
    hb_font_destroy(font);
    hb_face_destroy(face);
    hb_blob_destroy(blob);
    return 0;
}
