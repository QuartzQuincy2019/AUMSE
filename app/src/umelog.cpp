#include "umelog.h"

#include <QCoreApplication>
#include <QDateTime>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QHash>
#include <QTextStream>

namespace {

bool g_on = false;
QFile *g_file = nullptr;
QTextStream *g_stream = nullptr;
UmeLogSink *g_sink = nullptr;

/* 去重：上一条的分类/内容与重复次数 */
QString g_lastCat;
QString g_lastMsg;
int g_lastRepeat = 0;

/* 节流：分类 → 上次放行时刻 */
QElapsedTimer g_clock;
QHash<QString, qint64> g_throttle;

} // namespace

void UmeLogSink::emitLine(const QString &category, const QString &line)
{
    emit appended(category, line);
}

void umeLogInit(bool enabled, const QString &path)
{
    if (g_on || !enabled)
        return;

    QString p = path;
    if (p.isEmpty()) {
        /* 默认放 app/ 目录（开发时好找）；部署后该目录不存在就退回 exe 同目录 */
        const QString appDir = QStringLiteral(UME_LOG_DIR);
        const QString dir = QDir(appDir).exists() ? appDir
                                                  : QCoreApplication::applicationDirPath();
        p = QDir(dir).filePath(QStringLiteral("ume.log"));
    }

    g_file = new QFile(p);
    if (!g_file->open(QIODevice::WriteOnly | QIODevice::Truncate | QIODevice::Text)) {
        delete g_file;
        g_file = nullptr;
        return;
    }
    g_stream = new QTextStream(g_file);
    g_stream->setEncoding(QStringConverter::Utf8);
    g_clock.start();
    g_on = true;
    umeLogWrite("log", QStringLiteral("started, file=%1").arg(p));
}

bool umeLogEnabled()
{
    return g_on;
}

void umeLogShut()
{
    if (!g_on)
        return;
    g_stream->flush();
    g_file->close();
    delete g_stream;
    delete g_file;
    g_stream = nullptr;
    g_file = nullptr;
    g_on = false;
}

UmeLogSink *umeLogSink()
{
    if (!g_sink)
        g_sink = new UmeLogSink;
    return g_sink;
}

bool umeLogThrottle(const char *cat, int ms)
{
    if (!g_on)
        return false;
    const qint64 now = g_clock.isValid() ? g_clock.elapsed() : 0;
    const QString key = QLatin1String(cat);
    const qint64 last = g_throttle.value(key, -1000000);
    if (now - last < ms)
        return false;
    g_throttle[key] = now;
    return true;
}

void umeLogWrite(const char *cat, const QString &msg)
{
    if (!g_on || !g_stream)
        return;

    const QString category = QLatin1String(cat);

    /* 连续重复合并：只累加计数，等出现新内容时补一条「×N」 */
    if (category == g_lastCat && msg == g_lastMsg) {
        ++g_lastRepeat;
        return;
    }

    const QString ts = QDateTime::currentDateTime().toString(QStringLiteral("HH:mm:ss.zzz"));
    if (g_lastRepeat > 0) {
        *g_stream << ts << QLatin1String(" [") << g_lastCat
                  << QLatin1String("] ") << g_lastMsg
                  << QStringLiteral("  （同上 ×%1）").arg(g_lastRepeat + 1)
                  << QLatin1Char('\n');
        if (g_sink)
            g_sink->emitLine(g_lastCat,
                             QStringLiteral("%1 [%2] %3  （同上 ×%4）")
                                 .arg(ts, g_lastCat, g_lastMsg)
                                 .arg(g_lastRepeat + 1));
    }

    g_lastCat = category;
    g_lastMsg = msg;
    g_lastRepeat = 0;

    const QString line = QStringLiteral("%1 [%2] %3").arg(ts, category, msg);
    *g_stream << line << QLatin1Char('\n');
    g_stream->flush();          // 崩溃时也要留下最后几行

    if (g_sink)
        g_sink->emitLine(category, line);
}

QString umeLogEsc(const QString &s)
{
    QString out;
    out.reserve(s.size() + 8);
    for (const QChar c : s) {
        if (c == QLatin1Char('\n'))
            out += QLatin1String("\\n");
        else if (c == QLatin1Char('\r'))
            out += QLatin1String("\\r");
        else if (c == QLatin1Char('\t'))
            out += QLatin1String("\\t");
        else if (c.unicode() < 0x20)
            out += QStringLiteral("\\x%1").arg(int(c.unicode()), 2, 16, QLatin1Char('0'));
        else
            out += c;
    }
    return out;
}
