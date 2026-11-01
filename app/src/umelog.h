#pragma once

#include <QObject>
#include <QString>

/* 开发期日志。
   · 默认开启；写文件，同时推给「调试窗口」（UmeLogWindow）。
   · 同一条连续重复时合并成「…（×N）」，避免刷屏。
   · 只在打开时才格式化字符串，关闭时几乎零开销。 */

class UmeLogSink : public QObject
{
    Q_OBJECT
public:
    void emitLine(const QString &category, const QString &line);

signals:
    /* 已合并好的整行（含时间戳） */
    void appended(const QString &category, const QString &line);
};

void umeLogInit(bool enabled, const QString &path = QString());
bool umeLogEnabled();
void umeLogShut();
UmeLogSink *umeLogSink();

void umeLogWrite(const char *cat, const QString &msg);

/* 节流：同一分类在 ms 毫秒内只放行一次 */
bool umeLogThrottle(const char *cat, int ms);

/* 用法： UME_LOG("edit", QStringLiteral("insert pos=%1").arg(pos)); */
#define UME_LOG(cat, expr)                        \
    do {                                          \
        if (umeLogEnabled())                      \
            umeLogWrite(cat, (expr));             \
    } while (0)

/* 用法： if (UME_LOG_EVERY("paint", 300)) { ... } */
#define UME_LOG_EVERY(cat, ms) (umeLogEnabled() && umeLogThrottle(cat, ms))

/* 把控制字符、换行转义成可见形式，方便看输入法上屏串 */
QString umeLogEsc(const QString &s);
