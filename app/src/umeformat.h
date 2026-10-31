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

    bool operator==(const UmeFormatState &o) const
    {
        return family == o.family && qFuzzyCompare(pointSize, o.pointSize)
               && color == o.color && familyMixed == o.familyMixed
               && sizeMixed == o.sizeMixed && colorMixed == o.colorMixed;
    }
    bool operator!=(const UmeFormatState &o) const { return !(*this == o); }
};
