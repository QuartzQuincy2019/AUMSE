#pragma once

#include <QString>

/* 开发期日志。
   · 默认关闭；设环境变量 UME_LOG=1 打开，或用 --log 指定文件。
   · 每行带毫秒时间戳与分类，方便按时间对齐「按下 1 键」那一下。
   · 只在打开时格式化字符串，关闭时几乎零开销。 */

void umeLogInit(bool enabled, const QString &path = QString());
bool umeLogEnabled();
void umeLogShut();

void umeLogWrite(const char *cat, const QString &msg);

/* 用法： UME_LOG("edit", QStringLiteral("insert pos=%1").arg(pos)); */
#define UME_LOG(cat, expr)                        \
    do {                                          \
        if (umeLogEnabled())                      \
            umeLogWrite(cat, (expr));             \
    } while (0)

/* 把控制字符、换行转义成可见形式，方便看输入法上屏串 */
QString umeLogEsc(const QString &s);
