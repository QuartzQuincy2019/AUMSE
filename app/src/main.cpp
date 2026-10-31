#include "mainwindow.h"
#include "umelog.h"
#include "umesettings.h"
#include "umeview.h"

#include <QApplication>
#include <QCommandLineParser>
#include <QDir>
#include <QFile>
#include <QFontDatabase>
#include <QFontInfo>
#include <QImage>
#include <QImageWriter>
#include <QKeyEvent>
#include <QMouseEvent>
#include <QTextBlock>
#include <QTextCharFormat>
#include <QTextDocument>
#include <QInputMethodEvent>
#include <QTextFragment>

namespace {

/* 自检：不靠人手点，用真实的 QKeyEvent 驱动视图，
   把光标、选区、命中、打字结果都打出来，顺便出图。 */
int selfTest(const QString &path, const QString &outDir, const QString &font,
             qreal pt, const PageSetup &page)
{
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "无法打开 %s\n", qPrintable(path));
        return 2;
    }
    QTextDocument doc;
    doc.setPlainText(QString::fromUtf8(f.readAll()));

    UmeSettings settings;
    settings.setPage(page);

    UmeView view;
    view.setSettings(&settings);
    view.setDocument(&doc);
    view.setBaseFormat(font, pt);
    view.resize(1000, 900);
    view.show();
    view.activateWindow();
    view.setFocus();

    auto press = [&view](int key, Qt::KeyboardModifiers mods = Qt::NoModifier,
                         const QString &text = QString()) {
        QKeyEvent ev(QEvent::KeyPress, key, mods, text);
        QApplication::sendEvent(&view, &ev);
    };

    auto report = [&view](const char *label) {
        const QTextCursor c = view.textCursor();
        const QRectF r = view.caretRectProbe();
        printf("  %-20s pos=%3d  sel=[%3d,%3d]  caret=(%.1f, %.1f)\n",
               label, c.position(), c.selectionStart(), c.selectionEnd(),
               r.left(), r.top());
    };

    printf("== 度量 ==\n  %s\n", qPrintable(view.metricsProbe()));

    /* 字号/字体是否真的作用到字形：量同一条 line 的推进宽度 */
    {
        auto lineWidth = [&]() {
            const QTextBlock b = doc.begin();
            QTextLayout *lay = b.layout();
            return (lay && lay->lineCount()) ? lay->lineAt(0).naturalTextWidth() : -1.0;
        };
        const qreal w14 = lineWidth();
        view.applyFormatPointSize(28.0);
        const qreal w28 = lineWidth();
        view.setBaseFormat(font, 28.0);
        view.setDocument(&doc);
        view.applyFormatPointSize(pt);
        view.setBaseFormat(font, pt);
        view.setDocument(&doc);

        printf("== 字号是否作用于字形 ==\n");
        printf("  14pt 行宽 %.1f pt   28pt 行宽 %.1f pt   比值 %.2f\n",
               w14, w28, w14 > 0 ? w28 / w14 : 0.0);
        printf("  字体族（文档默认）= %s\n",
               qPrintable(doc.defaultFont().family()));
    }

    printf("== 载入后字体（应等于设置里的字体）==\n");
    view.resetBaseFont();
    {
        const QTextBlock b0 = doc.begin();
        const QFont f0 = b0.charFormat().font();
        const UmeFormatState st = view.currentFormat();
        printf("  block0 = %s / %.1f pt   (format = %s / %.1f)\n",
               qPrintable(f0.family()), f0.pointSizeF(),
               qPrintable(st.family), st.pointSize);
    }

    printf("== 只改选区（Word 语义）==\n");
    auto fragSizes = [&doc]() {
        QStringList out;
        for (QTextBlock b = doc.begin(); b.isValid(); b = b.next()) {
            for (auto it = b.begin(); !it.atEnd(); ++it) {
                const QTextFragment f = it.fragment();
                if (f.isValid())
                    out << QString::number(f.charFormat().fontPointSize(), 'f', 0)
                               + QStringLiteral("(") + QString::number(f.length()) + QLatin1Char(')');
            }
        }
        return out.join(QStringLiteral(" "));
    };
    printf("  改前：%s\n", qPrintable(fragSizes()));
    {
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.applyFormatPointSize(30.0);
        printf("  选中前 3 字后把字号改到 30 → %s\n", qPrintable(fragSizes()));

        /* 混合格式：选区横跨 30pt 与 14pt，应当报 mixed */
        sel.setPosition(0);
        sel.setPosition(8, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        const UmeFormatState mixed = view.currentFormat();
        printf("  混合选区：sizeMixed=%d  pointSize=%.1f\n",
               int(mixed.sizeMixed), mixed.pointSize);
        sel.setPosition(0);
        sel.setPosition(8, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.applyFormatPointSize(pt);
        const UmeFormatState after = view.currentFormat();
        printf("  再统一成 %.1f 后：sizeMixed=%d  pointSize=%.1f\n",
               pt, int(after.sizeMixed), after.pointSize);
    }

    printf("== 只给选区换字体：版面不能动 ==\n");
    {
        printf("  改前列几何：%s\n", qPrintable(view.columnsProbe(4)));
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.applyFormatFamily(QStringLiteral("Mongolian Baiti"));
        printf("  换后列几何：%s\n", qPrintable(view.columnsProbe(4)));
        view.applyFormatFamily(font);
    }

    printf("== 键盘移动 ==\n");
    report("initial");
    for (int i = 0; i < 3; ++i) { press(Qt::Key_Down); report("Down"); }
    press(Qt::Key_Right); report("Right (next column)");
    press(Qt::Key_Left);  report("Left (back)");
    press(Qt::Key_Home);  report("Home");
    press(Qt::Key_End);   report("End");

    printf("== 选区（Shift+Down x3）==\n");
    press(Qt::Key_Home);
    for (int i = 0; i < 3; ++i)
        press(Qt::Key_Down, Qt::ShiftModifier);
    report("Shift+Down x3");
    printf("  selection rects = %d\n", int(view.selectionRectsProbe().size()));

    printf("== 命中测试 ==\n");
    for (const QPointF &p : {QPointF(100, 140), QPointF(130, 240)}) {
        const QTextCursor c = view.cursorAtWidgetPosProbe(p);
        printf("  click (%.0f, %.0f) -> pos=%d\n", p.x(), p.y(), c.position());
    }

    printf("== 大字号必须撑开本列 ==\n");
    {
        printf("  改前：%s\n", qPrintable(view.columnsProbe(3)));
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.applyFormatPointSize(80.0);
        printf("  前 3 字改 80pt：%s\n", qPrintable(view.columnsProbe(3)));
        view.applyFormatPointSize(pt);
        printf("  还原后：%s\n", qPrintable(view.columnsProbe(3)));
    }

    printf("== 选区矩形 vs 列框 ==\n");
    {
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        const QVector<QRectF> rs = view.selectionRectsProbe();
        printf("  列：%s\n", qPrintable(view.columnsProbe(1)));
        printf("  选区矩形数=%d\n", int(rs.size()));
        for (const QRectF &r : rs)
            printf("    rect x %.1f–%.1f  y %.1f–%.1f\n",
                   r.left(), r.right(), r.top(), r.bottom());
        printf("  光标 x %.1f–%.1f\n",
               view.caretRectProbe().left(), view.caretRectProbe().right());
    }

    printf("== 行内逐位置 x ==\n");
    {
        const QTextBlock b = doc.begin();
        QTextLayout *lay = b.layout();
        const QTextLine line = lay->lineAt(0);
        QStringList xs;
        for (int p = line.textStart(); p <= line.textStart() + line.textLength(); ++p)
            xs << QStringLiteral("%1:%2").arg(p).arg(line.cursorToX(p), 0, 'f', 1);
        printf("  %s\n", qPrintable(xs.join(QLatin1Char(' '))));
        printf("  line.width=%.1f naturalTextWidth=%.1f inlineTextLength=%d\n",
               line.width(), line.naturalTextWidth(), line.textLength());
    }

    printf("== 模拟输入法：MENGGU -> 上屏蒙古 ==\n");
    {
        view.setTextCursor(QTextCursor(&doc));   // 光标回到开头
        press(Qt::Key_End);                      // 到第一列末尾

        QInputMethodEvent pre(QStringLiteral("MENGGU"), {});
        QApplication::sendEvent(&view, &pre);
        printf("  发 preedit 后：doc 长度=%d\n", doc.toPlainText().size());

        QInputMethodEvent commit;
        commit.setCommitString(QStringLiteral("\u8499\u53E4"));
        QApplication::sendEvent(&view, &commit);
        printf("  上屏后：doc 长度=%d，末尾=%s\n",
               doc.toPlainText().size(),
               qPrintable(doc.toPlainText().right(4)));
        printf("  列几何：%s\n", qPrintable(view.columnsProbe(3)));
    }

    printf("== 拖曳选中 ==\n");
    {
        /* 两点的文档位置先用命中测试量出来，再模拟按下 / 移动 / 抬起 */
        const QPointF p1(80, 120);
        const QPointF p2(80, 190);
        const int pos1 = view.cursorAtWidgetPosProbe(p1).position();
        const int pos2 = view.cursorAtWidgetPosProbe(p2).position();

        QMouseEvent press(QEvent::MouseButtonPress, p1, view.mapToGlobal(p1),
                          Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&view, &press);
        QMouseEvent move(QEvent::MouseMove, p2, view.mapToGlobal(p2),
                         Qt::NoButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&view, &move);

        const QTextCursor c = view.textCursor();
        printf("  按下=%d 拖到=%d → 选中 [%d,%d]  %s\n",
               pos1, pos2, c.selectionStart(), c.selectionEnd(),
               (c.selectionStart() == qMin(pos1, pos2)
                && c.selectionEnd() == qMax(pos1, pos2)) ? "OK" : "错误");

        QMouseEvent rel(QEvent::MouseButtonRelease, p2, view.mapToGlobal(p2),
                        Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&view, &rel);
    }

    printf("== 打字 ==\n");
    press(Qt::Key_Home);
    const int lenBefore = doc.toPlainText().size();

    /* 直接给 QKeyEvent 蒙文文本，模拟输入法上屏 */
    const QString typed = QString::fromUtf8("\u182E\u1823\u1829\u182D\u1823\u182F");
    for (const QChar &ch : typed)
        press(0, Qt::NoModifier, QString(ch));
    report("typed monggol");
    printf("  doc length %d -> %d (+%d)\n", lenBefore, doc.toPlainText().size(),
           doc.toPlainText().size() - lenBefore);
    printf("  first 6 chars: %s\n", qPrintable(doc.toPlainText().left(6)));

    printf("== 退格 ==\n");
    press(Qt::Key_Backspace);
    press(Qt::Key_Backspace);
    report("Backspace x2");
    printf("  first 6 chars: %s\n", qPrintable(doc.toPlainText().left(6)));

    printf("== 撤销 ==\n");
    press(Qt::Key_Z, Qt::ControlModifier);
    report("Ctrl+Z");
    printf("  first 6 chars: %s\n", qPrintable(doc.toPlainText().left(6)));

    printf("== 复制粘贴 ==\n");
    press(Qt::Key_Home);
    for (int i = 0; i < 3; ++i)
        press(Qt::Key_Down, Qt::ShiftModifier);
    press(Qt::Key_C, Qt::ControlModifier);
    press(Qt::Key_End);
    const int lenBeforePaste = doc.toPlainText().size();
    press(Qt::Key_V, Qt::ControlModifier);
    printf("  Ctrl+C then Ctrl+V: length %d -> %d\n", lenBeforePaste,
           doc.toPlainText().size());

    press(Qt::Key_Home);
    press(Qt::Key_Down);
    const QImage img = view.renderPageImage(0, 2.0, true);
    const QString out = QDir(outDir).filePath(QStringLiteral("m2-typing.png"));
    QImageWriter(out, "PNG").write(img);
    printf("  wrote %s\n", qPrintable(out));
    return 0;
}

} // namespace

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    /* 开发期默认写日志；设 UME_LOG=0 可关掉 */
    const QByteArray logEnv = qgetenv("UME_LOG");
    umeLogInit(logEnv != "0");
    app.setApplicationName(QStringLiteral("UME"));

    QFontDatabase::addApplicationFont(QStringLiteral(UME_FONT_DIR)
                                      + QStringLiteral("/NotoSansMongolian-Regular.ttf"));

    QCommandLineParser parser;
    parser.setApplicationDescription(QStringLiteral("UME · 回鹘蒙文编辑器"));
    parser.addHelpOption();

    const QCommandLineOption optRender(QStringLiteral("render"),
        QStringLiteral("离屏渲染纯文本文件"), QStringLiteral("file"));
    const QCommandLineOption optSelftest(QStringLiteral("selftest"),
        QStringLiteral("光标 / 命中 / 选区 / 打字 自检"), QStringLiteral("file"));
    const QCommandLineOption optOut(QStringLiteral("out"),
        QStringLiteral("输出 PNG 路径（--render）"), QStringLiteral("png"));
    const QCommandLineOption optOutDir(QStringLiteral("outdir"),
        QStringLiteral("自检出图目录"), QStringLiteral("dir"), QStringLiteral("."));
    const QCommandLineOption optPage(QStringLiteral("page"),
        QStringLiteral("只渲染第几页（1 起）"), QStringLiteral("n"));
    const QCommandLineOption optScale(QStringLiteral("scale"),
        QStringLiteral("渲染倍率，默认 2"), QStringLiteral("x"), QStringLiteral("2"));
    const QCommandLineOption optFont(QStringLiteral("font"),
        QStringLiteral("字体族名，默认 Noto Sans Mongolian"), QStringLiteral("family"));
    const QCommandLineOption optLog(QStringLiteral("log"),
        QStringLiteral("写日志到指定文件（开发期排查用）"),
        QStringLiteral("file"));
    const QCommandLineOption optCaret(QStringLiteral("caret"),
        QStringLiteral("渲染时画出光标（配合 --render）"));
    const QCommandLineOption optSel(QStringLiteral("sel"),
        QStringLiteral("渲染时选中 [起,止] 两个文档位置"), QStringLiteral("a,b"));
    const QCommandLineOption optFonts(QStringLiteral("fonts"),
        QStringLiteral("列出本机可用的字体族"));
    const QCommandLineOption optSize(QStringLiteral("size"),
        QStringLiteral("字号 pt，默认 14"), QStringLiteral("pt"), QStringLiteral("14"));
    const QCommandLineOption optPaper(QStringLiteral("paper"),
        QStringLiteral("纸张：A4 / B5 / 16开 / Letter"), QStringLiteral("name"),
        QStringLiteral("A4"));
    const QCommandLineOption optMargin(QStringLiteral("margin"),
        QStringLiteral("页边距 pt，1 个或 4 个（左,右,上,下）"),
        QStringLiteral("pt"), QStringLiteral("56.7"));
    const QCommandLineOption optPitch(QStringLiteral("pitch"),
        QStringLiteral("列距 pt，0 = 自动"), QStringLiteral("pt"), QStringLiteral("0"));
    const QCommandLineOption optGuiCheck(QStringLiteral("guicheck"),
        QStringLiteral("只构造主窗口，检查是否崩溃"));

    parser.addOption(optRender);
    parser.addOption(optSelftest);
    parser.addOption(optOut);
    parser.addOption(optOutDir);
    parser.addOption(optPage);
    parser.addOption(optScale);
    parser.addOption(optFont);
    parser.addOption(optSize);
    parser.addOption(optPaper);
    parser.addOption(optMargin);
    parser.addOption(optFonts);
    parser.addOption(optLog);
    parser.addOption(optCaret);
    parser.addOption(optSel);
    parser.addOption(optGuiCheck);
    parser.addOption(optPitch);
    parser.addPositionalArgument(QStringLiteral("file"),
        QStringLiteral("要打开的文件（图形界面模式）"));
    parser.process(app);

    if (parser.isSet(optLog))
        umeLogInit(true, parser.value(optLog));

    PageSetup page = PageSetup::preset(parser.value(optPaper));
    const QStringList ms = parser.value(optMargin).split(QLatin1Char(','));
    if (!ms.isEmpty()) {
        const qreal v = ms[0].toDouble();
        page.mLeft = page.mRight = page.mTop = page.mBottom = v;
        if (ms.size() == 4) {
            page.mLeft = ms[0].toDouble();
            page.mRight = ms[1].toDouble();
            page.mTop = ms[2].toDouble();
            page.mBottom = ms[3].toDouble();
        }
    }

    const QString font = parser.isSet(optFont) ? parser.value(optFont)
                                               : QStringLiteral("Noto Sans Mongolian");
    const qreal pt = parser.value(optSize).toDouble();

    if (parser.isSet(optFonts)) {
        const QStringList fams = QFontDatabase::families();
        printf("families: %d\n", int(fams.size()));
        for (const QString &f : fams) {
            if (f.contains(QStringLiteral("Mongol"), Qt::CaseInsensitive)
                || f.contains(QStringLiteral("Menk"), Qt::CaseInsensitive)
                || f.contains(QStringLiteral("Amglang"), Qt::CaseInsensitive)
                || f.contains(QStringLiteral("Qimed"), Qt::CaseInsensitive))
                printf("  %s\n", qPrintable(f));
        }
        QFont probe(QStringLiteral("Menk Qimed Tig"));
        printf("QFontInfo(Menk Qimed Tig).family() = %s\n",
               qPrintable(QFontInfo(probe).family()));
        return 0;
    }

    if (parser.isSet(optGuiCheck)) {
        MainWindow w;
        printf("MainWindow constructed ok\n");
        return 0;
    }

    if (parser.isSet(optSelftest))
        return selfTest(parser.value(optSelftest), parser.value(optOutDir), font, pt, page);

    if (parser.isSet(optRender)) {
        QFile f(parser.value(optRender));
        if (!f.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "Cannot open %s\n", qPrintable(f.fileName()));
            return 2;
        }
        QTextDocument doc;
        doc.setPlainText(QString::fromUtf8(f.readAll()));

        UmeSettings settings;
        settings.setPage(page);
        settings.setColumnPitch(parser.value(optPitch).toDouble());

        UmeView view;
        view.setSettings(&settings);
        view.setDocument(&doc);
        view.setBaseFormat(font, pt);

        {
            const QTextBlock b0 = doc.begin();
            const QFont f0 = b0.charFormat().font();
            printf("font arg=%s\n  doc.defaultFont=%s\n  block0 format font=%s / %f pt\n",
                   qPrintable(font),
                   qPrintable(doc.defaultFont().family()),
                   qPrintable(f0.family()), f0.pointSizeF());
        }

        const qreal scale = parser.value(optScale).toDouble();

        if (parser.isSet(optSel)) {
            const QStringList ab = parser.value(optSel).split(QLatin1Char(','));
            if (ab.size() == 2) {
                QTextCursor cur(&doc);
                cur.setPosition(ab[0].toInt());
                cur.setPosition(ab[1].toInt(), QTextCursor::KeepAnchor);
                view.setTextCursor(cur);
            }
        }

        printf("[glyph] %s\n", qPrintable(view.glyphProbe()));
        const bool withCaret = parser.isSet(optCaret);

        QImage img = parser.isSet(optPage)
                         ? view.renderPageImage(parser.value(optPage).toInt() - 1, scale,
                                                withCaret)
                         : view.renderAllPages(scale);

        const QString out = parser.isSet(optOut) ? parser.value(optOut)
                                                 : QStringLiteral("out.png");
        if (img.isNull()) {
            fprintf(stderr, "empty image\n");
            return 3;
        }
        if (!img.save(out)) {
            fprintf(stderr, "cannot write %s\n", qPrintable(out));
            return 3;
        }
        printf("rendered -> %s (%d x %d)\n", qPrintable(out), img.width(), img.height());
        return 0;
    }

    MainWindow w;
    const QStringList pos = parser.positionalArguments();
    if (!pos.isEmpty())
        w.openFile(pos.first());
    w.show();
    return app.exec();
}
