#include "mainwindow.h"
#include "umeicons.h"
#include "umedoc.h"
#include "umeinteract.h"
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
#include <QFileInfo>
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

    printf("== 只给选区上色 ==\n");
    {
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(5, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.applyFormatColor(QColor(QStringLiteral("#cc0000")));

        const UmeFormatState mixed = view.currentFormat();
        printf("  选 5 字上红：colorMixed=%d  color=%s\n",
               int(mixed.colorMixed),
               qPrintable(mixed.color.isValid() ? mixed.color.name()
                                                : QStringLiteral("-")));

        sel.setPosition(0);
        sel.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        const UmeFormatState s3 = view.currentFormat();
        printf("  只看前 3 字（全红）：colorMixed=%d  color=%s\n",
               int(s3.colorMixed), qPrintable(s3.color.name()));

        /* 跨「红→黑」边界：应当报混合 */
        sel.setPosition(0);
        sel.setPosition(9, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        const UmeFormatState mixedRange = view.currentFormat();
        printf("  跨红黑边界：colorMixed=%d\n", int(mixedRange.colorMixed));

        /* 像素级验证：渲染一页，红与黑都要有 */
        {
            sel.setPosition(0);
            sel.setPosition(5, QTextCursor::KeepAnchor);
            view.setTextCursor(sel);
            view.applyFormatColor(QColor(QStringLiteral("#cc0000")));

            const QImage img = view.renderPageImage(0, 1.0, false);
            int red = 0;
            int dark = 0;
            for (int y = 0; y < img.height(); ++y) {
                for (int x = 0; x < img.width(); ++x) {
                    const QColor c = img.pixelColor(x, y);
                    if (c.red() > 120 && c.green() < 90 && c.blue() < 90)
                        ++red;
                    else if (c.red() < 80 && c.green() < 80 && c.blue() < 80)
                        ++dark;
                }
            }
            printf("  渲染像素：红 %d  黑 %d\n", red, dark);
            img.save(QStringLiteral("%1/m4-color.png").arg(outDir));
        }

        /* 光标颜色：把光标放进红色文字里，画的应是红色 */
        {
            QTextCursor cur(&doc);
            cur.setPosition(3);
            view.setTextCursor(cur);
            view.setFocus();

            const QRectF cr = view.caretRectProbe();
            const QImage img = view.renderPageImage(0, 1.0, true);
            int red = 0;
            int dark = 0;
            for (int y = int(cr.top()) - 1; y <= int(cr.bottom()) + 1; ++y) {
                for (int x = int(cr.left()) - 1; x <= int(cr.right()) + 1; ++x) {
                    if (x < 0 || y < 0 || x >= img.width() || y >= img.height())
                        continue;
                    const QColor c = img.pixelColor(x, y);
                    if (c.red() > 120 && c.green() < 90 && c.blue() < 90)
                        ++red;
                    else if (c.red() < 80 && c.green() < 80 && c.blue() < 80)
                        ++dark;
                }
            }
            printf("  光标颜色探针（红色文字处） = %s\n",
                   qPrintable(view.caretColorProbe().name()));

            /* 浅色要自动压暗，否则黄光标在白纸上等于隐形 */
            view.applyFormatColor(QColor(QStringLiteral("#ffff00")));
            printf("  换成亮黄后 = %s（应比 #ffff00 暗）\n",
                   qPrintable(view.caretColorProbe().name()));
            view.applyFormatColor(QColor(QStringLiteral("#cc0000")));
            printf("  光标处像素：红 %d  黑 %d（光标矩形 x %.1f–%.1f）\n",
                   red, dark, cr.left(), cr.right());
        }

        /* 整篇再统一回黑，避免影响后面的渲染 */
        QTextCursor all(&doc);
        all.select(QTextCursor::Document);
        view.setTextCursor(all);
        view.applyFormatColor(Qt::black);
    }

    printf("== 链接 / 表格 / HTML ==\n");
    {
        /* 链接：套在选区上 */
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(5, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);
        view.insertLink(QUrl(QStringLiteral("https://example.com/")));

        sel.setPosition(3);
        view.setTextCursor(sel);
        printf("  光标处链接 = %s\n", qPrintable(view.linkAtCursor().toString()));

        const QStringList links = UmeDoc::allLinks(&doc);
        printf("  文档内链接数 = %d，首个 = %s\n",
               int(links.size()), qPrintable(links.value(0)));

        /* 表格：插到文档末尾 */
        QTextCursor end(&doc);
        end.movePosition(QTextCursor::End);
        view.setTextCursor(end);
        view.insertTable(2, 3);
        printf("  光标在表格内 = %d，规格 = %dx%d\n",
               int(UmeDoc::inTable(view.textCursor())),
               UmeDoc::tableSize(view.textCursor()).first,
               UmeDoc::tableSize(view.textCursor()).second);
        printf("  表格段落数 = %d，列数 = %d\n",
               view.layoutTableBlocksProbe(), view.columnsProbe(9).count(QLatin1Char('[')));

        /* HTML 导出 */
        const QString html = view.toHtml();
        printf("  HTML 长度 = %d，含 <a href = %d，含 writing-mode = %d\n",
               int(html.size()),
               int(html.contains(QStringLiteral("<a href"))),
               int(html.contains(QStringLiteral("writing-mode"))));
        printf("  HTML 含 <table = %d\n", int(html.contains(QStringLiteral("<table"))));
    }

    printf("== 宽对象：独占整列 / 文本围绕 ==\n");
    {
        /* 干净的文档：三段文字 + 一张表 */
        QTextDocument wdoc;
        wdoc.setPlainText(QStringLiteral("第一段文字。\n第二段文字。\n第三段文字。"));

        UmeView wview;
        wview.setSettings(&settings);
        wview.setDocument(&wdoc);
        wview.setBaseFormat(font, pt);

        QTextCursor end(&wdoc);
        end.movePosition(QTextCursor::End);
        wview.setTextCursor(end);
        wview.insertTable(2, 3);

        UmeDoc::WideProps p = wview.currentWideObject();
        printf("  插入后：kind=%d span=%d 高=%.1f\n",
               int(p.kind), p.span, p.heightPt);
        printf("  独占整列：%s\n", qPrintable(wview.wideObjectsProbe()));
        printf("  列数 = %d\n", int(wview.columnsProbe(12).count(QLatin1Char('['))));

        /* 改 3 列、高 120，切换文本围绕 */
        p.span = 3;
        p.heightPt = 120.0;
        p.wrap = UmeDoc::WideWrap::Span;
        wview.applyWideObject(p);
        const QString spanProbe = wview.wideObjectsProbe();

        p.wrap = UmeDoc::WideWrap::Bubble;
        wview.applyWideObject(p);
        const QString wrapProbe = wview.wideObjectsProbe();

        printf("  span 落位：%s\n", qPrintable(spanProbe));
        printf("  wrap 落位：%s\n", qPrintable(wrapProbe));

        /* 缩放与行列 */
        wview.resizeWideObject(200.0, false);
        printf("  改高 200 后：%s\n", qPrintable(wview.wideObjectsProbe()));

        wview.changeTableRows(1);
        wview.changeTableColumns(-1);
        const QPair<int, int> size = UmeDoc::tableSize(wview.textCursor());
        printf("  +1 行 −1 列后：%dx%d\n", size.first, size.second);

        wview.nudgeWideObject(10.0);
        printf("  下移 10pt：%s\n", qPrintable(wview.wideObjectsProbe()));
    }

    printf("== 从右到左 / 图片与手柄 ==\n");
    {
        QTextDocument rdoc;
        rdoc.setPlainText(QStringLiteral("第一段。\n第二段。\n第三段。"));
        UmeView rview;
        rview.setSettings(&settings);
        rview.setDocument(&rdoc);
        rview.setBaseFormat(font, pt);

        const QString ltr = rview.columnsProbe(3);
        settings.setRightToLeft(true);
        const QString rtl = rview.columnsProbe(3);
        settings.setRightToLeft(false);
        printf("  从左到右：%s\n", qPrintable(ltr));
        printf("  从右到左：%s\n", qPrintable(rtl));
    }

    printf("== 插图与手柄 ==\n");
    {
        /* 造一张 120x80 的图 */
        const QString png = QStringLiteral("%1/mkimage.png").arg(outDir);
        QImage img(120, 80, QImage::Format_RGB32);
        img.fill(QColor(0x2e, 0x75, 0xb6));
        img.save(png);

        QTextDocument idoc;
        idoc.setPlainText(QStringLiteral("图片前后都有文字。"));
        UmeView iview;
        iview.setSettings(&settings);
        iview.setDocument(&idoc);
        iview.setBaseFormat(font, pt);

        iview.insertImage(png);
        printf("  宽对象：%s\n", qPrintable(iview.wideObjectsProbe()));
        printf("  选中索引 = %d，手柄数 = %d\n",
               iview.selectedWideObject(), int(iview.wideHandlesProbe().size()));

        const UmeDoc::WideProps ip = iview.currentWideObject();
        printf("  属性：kind=%d span=%d 高=%.1f 旋转=%.1f 路径=%s\n",
               int(ip.kind), ip.span, ip.heightPt, ip.rotation,
               qPrintable(QFileInfo(ip.imagePath).fileName()));

        iview.renderPageImage(0, 1.5, false)
            .save(QStringLiteral("%1/m5-image.png").arg(outDir));
        iview.resizeWideObject(200.0, true);
        printf("  改高 200（等比）：%s\n", qPrintable(iview.wideObjectsProbe()));
    }

    printf("== 吸附与命中（纯数学）==\n");
    {
        const qreal degs[] = {0.0, 3.0, 20.0, 43.5, 46.0, 88.0, 133.0, 178.0, 270.0};
        QStringList snapped;
        for (qreal d : degs)
            snapped << QStringLiteral("%1→%2").arg(d).arg(UmeInteract::snapDegrees(d), 0, 'f', 0);
        printf("  吸附：%s\n", qPrintable(snapped.join(QStringLiteral("  "))));

        /* 中心角度差：起点在正右、当前在正下 → +90° */
        const QPointF c(100, 100);
        printf("  90° 拖曳：%+.1f\n",
               UmeInteract::dragAngleDelta(c, QPointF(150, 100), QPointF(100, 150)));

        /* 旋转后手柄位置：转 90° 后，「右侧」手柄应跑到下方 */
        const QPointF p = UmeInteract::rotatePoint(QPointF(150, 100), c, 90.0);
        printf("  点(150,100) 绕中心转 90° → (%.1f, %.1f)\n", p.x(), p.y());
    }

    printf("== 字符样式与镜像 ==\n");
    {
        QTextCursor sel(&doc);
        sel.setPosition(0);
        sel.setPosition(6, QTextCursor::KeepAnchor);
        view.setTextCursor(sel);

        view.applyCharStyle(UmeView::StyleBold, true);
        view.applyCharStyle(UmeView::StyleItalic, true);
        const UmeFormatState s = view.currentFormat();
        printf("  加粗+倾斜：bold=%d italic=%d mixed(b/i)=%d/%d\n",
               int(s.bold), int(s.italic), int(s.boldMixed), int(s.italicMixed));

        view.applyCharStyle(UmeView::StyleBold, false);
        const UmeFormatState s2 = view.currentFormat();
        printf("  取消加粗：bold=%d italic=%d\n", int(s2.bold), int(s2.italic));

        /* 混合：只给前 3 字加下划线，再看 0..6 */
        QTextCursor part(&doc);
        part.setPosition(0);
        part.setPosition(3, QTextCursor::KeepAnchor);
        view.setTextCursor(part);
        view.applyCharStyle(UmeView::StyleUnderline, true);

        QTextCursor whole(&doc);
        whole.setPosition(0);
        whole.setPosition(6, QTextCursor::KeepAnchor);
        view.setTextCursor(whole);
        printf("  跨下划线边界：underlineMixed=%d\n",
               int(view.currentFormat().underlineMixed));
    }

    printf("== 光标图形 ==\n");
    {
        const QPixmap ib = UmeIcons::textIBeam().pixmap();
        const QPixmap rb = UmeIcons::rotateCursor().pixmap();
        printf("  I 形光标 %dx%d，旋转光标 %dx%d\n",
               ib.width(), ib.height(), rb.width(), rb.height());
        ib.scaled(ib.width() * 6, ib.height() * 6, Qt::KeepAspectRatio,
                  Qt::SmoothTransformation)
            .save(QStringLiteral("%1/cursor-ibeam.png").arg(outDir));
        rb.scaled(rb.width() * 6, rb.height() * 6, Qt::KeepAspectRatio,
                  Qt::SmoothTransformation)
            .save(QStringLiteral("%1/cursor-rotate.png").arg(outDir));
    }

    printf("== 手柄光标 ==\n");
    {
        /* 复用上面插图那次的视图：选中图片后旋转 0 / 45 / 90 看映射 */
        QImage probeImg(60, 40, QImage::Format_RGB32);
        probeImg.fill(QColor(0x2e, 0x75, 0xb6));
        const QString probePath = QStringLiteral("%1/cursor-probe.png").arg(outDir);
        probeImg.save(probePath);

        QTextDocument cdoc;
        cdoc.setPlainText(QStringLiteral("图片"));
        UmeView cview;
        cview.setSettings(&settings);
        cview.setDocument(&cdoc);
        cview.setBaseFormat(font, pt);
        cview.insertImage(probePath);

        UmeDoc::WideProps p = cview.currentWideObject();
        for (qreal deg : {0.0, 45.0, 90.0}) {
            p.rotation = deg;
            cview.applyWideObject(p);
            printf("  旋转 %3.0f°：%s\n", deg, qPrintable(cview.cursorProbe()));
        }
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
    const QCommandLineOption optHtml(QStringLiteral("html"),
        QStringLiteral("导出 HTML 到指定文件"), QStringLiteral("file"));
    const QCommandLineOption optColor(QStringLiteral("color"),
        QStringLiteral("文字颜色，如 #cc0000"), QStringLiteral("rgb"));
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
    parser.addOption(optHtml);
    parser.addOption(optColor);
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
        view.setBaseFormat(font, pt,
                           parser.isSet(optColor) ? QColor(parser.value(optColor))
                                                  : QColor(Qt::black));

        {
            const QTextBlock b0 = doc.begin();
            const QFont f0 = b0.charFormat().font();
            printf("font arg=%s\n  doc.defaultFont=%s\n  block0 format font=%s / %f pt\n",
                   qPrintable(font),
                   qPrintable(doc.defaultFont().family()),
                   qPrintable(f0.family()), f0.pointSizeF());
        }

        const qreal scale = parser.value(optScale).toDouble();

        if (parser.isSet(optHtml)) {
            QFile out(parser.value(optHtml));
            if (out.open(QIODevice::WriteOnly | QIODevice::Text)) {
                out.write(view.toHtml().toUtf8());
                out.close();
                printf("html -> %s\n", qPrintable(parser.value(optHtml)));
            } else {
                printf("无法写入 %s\n", qPrintable(parser.value(optHtml)));
            }
        }

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
