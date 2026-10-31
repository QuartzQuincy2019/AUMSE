#include "umelog.h"

#include <QCoreApplication>
#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QTextStream>

namespace {

bool g_on = false;
QFile *g_file = nullptr;
QTextStream *g_stream = nullptr;

} // namespace

void umeLogInit(bool enabled, const QString &path)
{
    if (g_on)
        return;
    if (!enabled)
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

void umeLogWrite(const char *cat, const QString &msg)
{
    if (!g_on || !g_stream)
        return;
    const QString ts = QDateTime::currentDateTime().toString(QStringLiteral("HH:mm:ss.zzz"));
    *g_stream << ts << QLatin1String(" [") << QLatin1String(cat) << QLatin1String("] ")
              << msg << QLatin1Char('\n');
    g_stream->flush();          // 崩溃时也要留下最后几行
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
