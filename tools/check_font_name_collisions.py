"""查字体族名「撞名」——同一族名注册了不止一份。

为什么需要它：Windows 允许同一个族名同时存在于
  HKLM\\...\\Fonts（系统级，人人可用）
  HKCU\\...\\Fonts（当前用户级，仅本人可用）
两份字体族名相同、文件不同，DirectWrite 只会挑一份；实测见过浏览器
两边都匹配不上、直接回退到别的字体。蒙科立那套字体就是这种装法：
系统级 8103 与用户级 8102 同名，Menk Qagan Tig 还有 MQG8F02/MQG8103 冲突。

用法：python tools/check_font_name_collisions.py [--all]
      默认只列撞名的族；--all 连没撞的一起列。
"""
import os
import sys

# Windows 控制台默认 GBK，中文与符号会直接抛 UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    import winreg
except ImportError:                     # 非 Windows
    sys.exit('本脚本只用来看 Windows 的字体注册表。')

HIVES = (
    ('HKLM', winreg.HKEY_LOCAL_MACHINE,
     r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'),
    ('HKCU', winreg.HKEY_CURRENT_USER,
     r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'),
)
SUFFIX = ' (TrueType)'


def read_hive(root, path):
    """返回 {族名: [文件名, ...]}；族名去掉 '(TrueType)' 之类后缀。"""
    out = {}
    try:
        key = winreg.OpenKey(root, path)
    except OSError:
        return out
    with key:
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            i += 1
            fam = name
            for suf in (SUFFIX, ' (OpenType)', ' (All res)'):
                fam = fam.replace(suf, '')
            out.setdefault(fam.strip(), []).append(os.path.basename(str(value)))
    return out


def main():
    show_all = '--all' in sys.argv
    seen = {}
    for tag, root, path in HIVES:
        for fam, files in read_hive(root, path).items():
            for f in files:
                seen.setdefault(fam, []).append((tag, f))

    dup = {k: v for k, v in seen.items() if len(v) > 1}
    target = seen if show_all else dup

    print('字体族名总数 : %d' % len(seen))
    print('撞名的族     : %d' % len(dup))
    print()
    for fam in sorted(target, key=str.lower):
        recs = target[fam]
        mark = '!! ' if len(recs) > 1 else '   '
        print('%s%-28s %s' % (mark, fam, '  '.join('%s:%s' % r for r in recs)))

    if dup:
        print()
        print('处理建议：同一族名只留一份。想保留系统级那份，就删掉用户级那一份')
        print('（文件在 %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts\\），反之亦然；')
        print('删完重启浏览器，让它重新拉一次系统字体列表。')


if __name__ == '__main__':
    main()
