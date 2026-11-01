#pragma once

#include <QColor>
#include <QString>

/* 光标 / 选区上的格式状态。
   每个字段都可能是「多种值混在一起」—— Word 的做法是把这个框留空。
   用 mixed 标记，而不是用一个魔法值。 */
struct UmeFormatState
{
    QString family;
    qreal pointSize = 0.0;
    QColor color;

    bool familyMixed = false;
    bool sizeMixed = false;
    bool colorMixed = false;

    /* 字符样式：粗体/斜体/下划线/删除线/上下标 */
    bool bold = false;
    bool italic = false;
    bool underline = false;
    bool strikeOut = false;
    int script = 0;                 /* 0 正常，1 上标，-1 下标 */

    bool boldMixed = false;
    bool italicMixed = false;
    bool underlineMixed = false;
    bool strikeMixed = false;
    bool scriptMixed = false;

    bool operator==(const UmeFormatState &o) const
    {
        return family == o.family && qFuzzyCompare(pointSize, o.pointSize)
               && color == o.color && familyMixed == o.familyMixed
               && sizeMixed == o.sizeMixed && colorMixed == o.colorMixed
               && bold == o.bold && italic == o.italic
               && underline == o.underline && strikeOut == o.strikeOut
               && script == o.script && boldMixed == o.boldMixed
               && italicMixed == o.italicMixed
               && underlineMixed == o.underlineMixed
               && strikeMixed == o.strikeMixed && scriptMixed == o.scriptMixed;
    }
    bool operator!=(const UmeFormatState &o) const { return !(*this == o); }
};
