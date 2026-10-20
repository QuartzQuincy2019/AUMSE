# -*- coding: utf-8 -*-
"""把实测导出的键位表注入 mmkb.html。

页面上有两个占位符：
    var DUMP = /*__DATA__*/[];
    var NAMES = /*__NAMES__*/{};
本脚本从 %TEMP%\\mmkb_dump.json 读数据，生成这两个常量再替换掉。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML = r"E:\QKMansion\CSX10\w\UME\mmkb\mmkb.html"
DUMP = os.path.join(os.environ["TEMP"], "mmkb_dump.json")

NAMES = {
    0x1800: "MONGOLIAN BIRGA",
    0x1801: "MONGOLIAN ELLIPSIS",
    0x1802: "MONGOLIAN COMMA",
    0x1803: "MONGOLIAN FULL STOP",
    0x1804: "MONGOLIAN COLON",
    0x180A: "MONGOLIAN NIRUGU",
    0x180B: "FVS1",
    0x180C: "FVS2",
    0x180D: "FVS3",
    0x180E: "MVS 元音分隔符",
    0x180F: "FVS4",
    0x1820: "A ᠠ",
    0x1821: "E ᠡ",
    0x1822: "I ᠢ",
    0x1823: "O ᠣ",
    0x1824: "U ᠤ",
    0x1825: "OE ᠥ",
    0x1826: "UE ᠦ",
    0x1827: "EE ᠧ",
    0x1828: "NA ᠨ",
    0x1829: "ANG ᠩ",
    0x182A: "BA ᠪ",
    0x182B: "PA ᠫ",
    0x182C: "QA ᠬ",
    0x182D: "GA ᠭ",
    0x182E: "MA ᠮ",
    0x182F: "LA ᠯ",
    0x1830: "SA ᠰ",
    0x1831: "SHA ᠱ",
    0x1832: "TA ᠲ",
    0x1833: "DA ᠳ",
    0x1834: "CHA ᠴ",
    0x1835: "JA ᠵ",
    0x1836: "YA ᠶ",
    0x1837: "RA ᠷ",
    0x1838: "WA ᠸ",
    0x1839: "FA ᠹ",
    0x183A: "KA ᠺ",
    0x183B: "KHA ᠻ",
    0x183C: "TSA ᠼ",
    0x183D: "ZA ᠽ",
    0x183E: "HAA ᠾ",
    0x183F: "ZRA ᠿ",
    0x1840: "LHA ᡀ",
    0x1841: "ZHI ᡁ",
    0x1842: "CHI ᡂ",
    0x202F: "NNBSP 窄不间断空格",
    0x300A: "《",
    0x300B: "》",
}

dump = json.load(open(DUMP, encoding="utf-8-sig"))
# 保持 VK 升序，方便读
dump.sort(key=lambda e: e["vk"])
data = [{"vk": e["vk"], "plain": e["plain"], "shift": e["shift"]} for e in dump]

t = open(HTML, encoding="utf-8").read()
assert "/*__DATA__*/[]" in t, "找不到 DATA 占位符"
assert "/*__NAMES__*/{}" in t, "找不到 NAMES 占位符"

t = t.replace("/*__DATA__*/[]", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
t = t.replace("/*__NAMES__*/{}",
              json.dumps({str(k): v for k, v in NAMES.items()},
                         ensure_ascii=False, separators=(",", ":")))
open(HTML, "w", encoding="utf-8", newline="").write(t)

print("   注入 %d 个键；NAMES %d 条；文件 %d 字符"
      % (len(data), len(NAMES), len(t)))
