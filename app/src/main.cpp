#include "mainwindow.h"
#include "umeicons.h"
#include "umehit.h"
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
#include <QTextTable>
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

    printf("== 旋转命中 / 吸附 / 删除 ==\n");
    {
        QImage probe(80, 60, QImage::Format_RGB32);
        probe.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/rot-probe.png").arg(outDir);
        probe.save(path);

        QTextDocument rdoc;
        rdoc.setPlainText(QStringLiteral("对象命中测试"));
        UmeView rv;
        rv.setSettings(&settings);
        rv.setDocument(&rdoc);
        rv.setBaseFormat(font, pt);
        rv.insertImage(path);

        UmeDoc::WideProps p = rv.currentWideObject();
        rv.applyWideObject(p);

        /* ② 旋转 45° 后，点「旋转后包围盒的角」应当仍能选中：
              用对象中心的 x/y 偏移来模拟 */
        const QVector<QRectF> hs = rv.wideHandlesProbe();
        const QPointF corner = hs.value(0).center();
        (void)corner;
        printf("  手柄 0 中心 (%.1f, %.1f)\n", corner.x(), corner.y());

        p.rotation = 45.0;
        rv.applyWideObject(p);
        printf("  旋转 45° 后手柄 0 中心 (%.1f, %.1f)\n",
               rv.wideHandlesProbe().value(0).center().x(),
               rv.wideHandlesProbe().value(0).center().y());

        /* ③ 吸附：高度 63 → 应吸到行高网格附近 */
        p.rotation = 0.0;
        p.heightPt = 63.0;
        rv.applyWideObject(p);
        printf("  高度 63（未拖曳，不吸附）：%.1f\n", rv.currentWideObject().heightPt);

        /* ④ 删除 */
        const int before = rdoc.blockCount();
        rv.selectWideObject(0);
        rv.deleteSelectedWideObject();
        printf("  删除后：块数 %d → %d，宽对象 %s，选中 %d\n",
               before, rdoc.blockCount(), qPrintable(rv.wideObjectsProbe()),
               rv.selectedWideObject());
    }

    printf("== 表格单元格跟随格式 ==\n");
    {
        QTextDocument tdoc;
        tdoc.setPlainText(QStringLiteral("表格测试"));
        UmeView tv;
        tv.setSettings(&settings);
        tv.setDocument(&tdoc);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&tdoc);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(2, 2);

        /* 整篇刷红 */
        QTextCursor all(&tdoc);
        all.select(QTextCursor::Document);
        tv.setTextCursor(all);
        tv.applyFormatColor(QColor(QStringLiteral("#cc0000")));

        const QRectF box = tv.wideObjectsProbe().isEmpty()
                               ? QRectF()
                               : QRectF();
        Q_UNUSED(box);

        const QImage img = tv.renderPageImage(0, 1.0, false);
        int red = 0;
        int dark = 0;
        for (int y = 0; y < img.height(); ++y) {
            for (int x = 0; x < img.width(); ++x) {
                const QColor c = img.pixelColor(x, y);
                if (c.red() > 110 && c.green() < 90 && c.blue() < 90)
                    ++red;
                else if (c.red() < 70 && c.green() < 70 && c.blue() < 70)
                    ++dark;
            }
        }
        printf("  整篇上红后：红 %d  近黑 %d（表格里应是红字）\n", red, dark);
        img.save(QStringLiteral("%1/m6-table.png").arg(outDir));
    }

    printf("== 鼠标：旋转命中与拖角吸附 ==\n");
    {
        QImage probe(80, 60, QImage::Format_RGB32);
        probe.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/mouse-probe.png").arg(outDir);
        probe.save(path);

        QTextDocument mdoc;
        mdoc.setPlainText(QStringLiteral("鼠标测试"));
        UmeView mv;
        mv.setSettings(&settings);
        mv.setDocument(&mdoc);
        mv.setBaseFormat(font, pt);
        mv.insertImage(path);

        /* ② 转 45° 之后，点旋转后包围盒的左上角仍应选中该对象 */
        UmeDoc::WideProps mp = mv.currentWideObject();
        mp.rotation = 45.0;
        mv.applyWideObject(mp);

        /* 手柄只在「选中」时才有：先记下位置，再取消选中 */
        mv.selectWideObject(0);
        const QPointF corner = mv.wideHandlesProbe().value(0).center();
        mv.selectWideObject(-1);
        QMouseEvent press(QEvent::MouseButtonPress, corner, mv.mapToGlobal(corner.toPoint()),
                          Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&mv, &press);
        QMouseEvent release(QEvent::MouseButtonRelease, corner,
                            mv.mapToGlobal(corner.toPoint()),
                            Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&mv, &release);
        printf("  旋转 45° 点角上：选中索引 = %d（应为 0）\n", mv.selectedWideObject());

        /* ③ 拖右下角把高度从 60 拉到约 85，应吸到 4pt 网格 */
        UmeDoc::WideProps mp2 = mv.currentWideObject();
        mp2.rotation = 0.0;
        mp2.heightPt = 60.0;
        mv.applyWideObject(mp2);
        mv.selectWideObject(0);

        const QPointF br = mv.wideHandlesProbe().value(3).center();   // 右下
        QMouseEvent p2(QEvent::MouseButtonPress, br, mv.mapToGlobal(br.toPoint()),
                       Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&mv, &p2);
        const QPointF br2 = br + QPointF(0, 25);
        QMouseEvent m2(QEvent::MouseMove, br2, mv.mapToGlobal(br2.toPoint()),
                       Qt::NoButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&mv, &m2);
        printf("  拖右下角 +25pt：高度 = %.1f（60+25=85，4pt 网格应吸到 84）\n",
               mv.currentWideObject().heightPt);
        QMouseEvent r2(QEvent::MouseButtonRelease, br2, mv.mapToGlobal(br2.toPoint()),
                       Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&mv, &r2);
    }

    printf("== 拖动表格不能擦掉宽对象标记 ==\n");
    {
        QTextDocument gdoc;
        gdoc.setPlainText(QStringLiteral("表格前文字。"));
        UmeView gv;
        gv.setSettings(&settings);
        gv.setDocument(&gdoc);
        gv.setBaseFormat(font, pt);

        QTextCursor end(&gdoc);
        end.movePosition(QTextCursor::End);
        gv.setTextCursor(end);
        gv.insertTable(2, 3);
        printf("  插入后：%s\n", qPrintable(gv.wideObjectsProbe()));

        /* 光标先移出表格 —— 日志里出问题时的前置条件 */
        QTextCursor outside(&gdoc);
        outside.setPosition(0);
        gv.setTextCursor(outside);
        printf("  光标移出后 kind=%d（应为 0）\n", int(gv.currentWideObject().kind));

        /* 点表格本体，往下拖 8pt */
        const QPointF center = gv.wideItemBoxProbe(0).center();
        QMouseEvent press(QEvent::MouseButtonPress, center,
                          gv.mapToGlobal(center.toPoint()), Qt::LeftButton,
                          Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&gv, &press);

        const QPointF moved = center + QPointF(0, 8);
        QMouseEvent drag(QEvent::MouseMove, moved, gv.mapToGlobal(moved.toPoint()),
                         Qt::NoButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&gv, &drag);

        QMouseEvent release(QEvent::MouseButtonRelease, moved,
                            gv.mapToGlobal(moved.toPoint()), Qt::LeftButton,
                            Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&gv, &release);

        printf("  拖动后：%s\n", qPrintable(gv.wideObjectsProbe()));
        printf("  光标现在是否在表格内 = %d（应为 1）\n",
               int(gv.currentWideObject().kind == UmeDoc::WideKind::Table));
    }

    printf("== 表格不能压住文字 ==\n");
    {
        QTextDocument odoc;
        odoc.setPlainText(QStringLiteral("第一段文字。\n第二段文字。\n第三段文字。"));
        UmeView ov;
        ov.setSettings(&settings);
        ov.setDocument(&odoc);
        ov.setBaseFormat(font, pt);

        QTextCursor end(&odoc);
        end.movePosition(QTextCursor::End);
        ov.setTextCursor(end);
        ov.insertTable(2, 3);

        /* 把表格拖成负偏移（模拟用户往上拖） */
        UmeDoc::WideProps wp = ov.currentWideObject();
        wp.offsetPt = -120.0;
        ov.applyWideObject(wp);

        /* 检查：表格盒与任一文字列是否在 x 上重叠 */
        const QRectF box = ov.wideItemBoxProbe(0);
        printf("  表格盒 x %.1f–%.1f y %.1f–%.1f\n",
               box.left(), box.right(), box.top(), box.bottom());

        /* 用列探针取前若干列的左边界，看有没有落在表格 x 区间里 */
        const QString cols = ov.columnsProbe(8);
        printf("  列：%s\n", qPrintable(cols));
        printf("  表格左缘 = %.1f（应 ≥ 正文区左缘 56.7）\n", box.left());
    }

    printf("== 宽度不超过正文区 ==\n");
    {
        QImage big(400, 300, QImage::Format_RGB32);
        big.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/wide-probe.png").arg(outDir);
        big.save(path);

        QTextDocument wdoc;
        wdoc.setPlainText(QStringLiteral("宽度测试"));
        UmeView wv;
        wv.setSettings(&settings);
        wv.setDocument(&wdoc);
        wv.setBaseFormat(font, pt);
        wv.insertImage(path);

        const qreal areaW = settings.page().textArea().width();
        printf("  正文区宽 = %.1f pt\n", areaW);

        UmeDoc::WideProps wp = wv.currentWideObject();
        wp.span = 40;                       /* 故意设成远超页宽 */
        wv.applyWideObject(wp);
        const UmeDoc::WideProps after = wv.currentWideObject();
        printf("  请求 span=40 → 实际 span=%d（上限 %d）\n",
               after.span, wv.maxSpanForPageProbe());

        const QRectF box = wv.wideItemBoxProbe(0);
        printf("  落位 x %.1f–%.1f（正文区 56.7–%.1f）\n",
               box.left(), box.right(), 56.7 + areaW);
        printf("  是否越界 = %d（应为 0）\n",
               int(box.right() > 56.7 + areaW + 0.5));
    }

    printf("== 改宽度不跳页 ==\n");
    {
        QImage pic(300, 200, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/jump-probe.png").arg(outDir);
        pic.save(path);

        QTextDocument jdoc;
        jdoc.setPlainText(QStringLiteral("第一段文字。\n第二段文字。"));
        UmeView jv;
        jv.setSettings(&settings);
        jv.setDocument(&jdoc);
        jv.setBaseFormat(font, pt);

        QTextCursor end(&jdoc);
        end.movePosition(QTextCursor::End);
        jv.setTextCursor(end);
        jv.insertImage(path);

        /* 连续把 span 从 4 加到 18，记录每次的落位 */
        QStringList trace;
        for (int span = 4; span <= 18; span += 2) {
            UmeDoc::WideProps p = jv.currentWideObject();
            p.span = span;
            jv.applyWideObject(p);
            const QRectF box = jv.wideItemBoxProbe(0);
            trace << QStringLiteral("%1→x%2,w%3")
                         .arg(span).arg(box.left(), 0, 'f', 0).arg(box.width(), 0, 'f', 0);
        }
        printf("  %s\n", qPrintable(trace.join(QStringLiteral("  "))));
    }

    printf("== 两个对象不互相甩页 ==\n");
    {
        QImage a(200, 150, QImage::Format_RGB32);
        a.fill(QColor(0x2e, 0x75, 0xb6));
        const QString pa = QStringLiteral("%1/two-a.png").arg(outDir);
        a.save(pa);
        QImage b(120, 90, QImage::Format_RGB32);
        b.fill(QColor(0xc0, 0x50, 0x4d));
        const QString pb = QStringLiteral("%1/two-b.png").arg(outDir);
        b.save(pb);

        QTextDocument tdoc;
        tdoc.setPlainText(QStringLiteral("两图测试"));
        UmeView tv;
        tv.setSettings(&settings);
        tv.setDocument(&tdoc);
        tv.setBaseFormat(font, pt);
        tv.insertImage(pa);

        QTextCursor end(&tdoc);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertImage(pb);

        /* 把光标放到第一张图的块上，再逐步加宽 */
        QTextCursor first(&tdoc);
        for (QTextBlock b = tdoc.begin(); b.isValid(); b = b.next()) {
            if (UmeDoc::isWideBlock(b)) {
                first = QTextCursor(b);
                break;
            }
        }
        tv.setTextCursor(first);

        QStringList trace;
        for (int span = 8; span <= 20; span += 2) {
            UmeDoc::WideProps p = tv.currentWideObject();
            if (!p.isValid())
                break;
            p.span = span;
            tv.applyWideObject(p);
            trace << QStringLiteral("%1→%2")
                         .arg(span)
                         .arg(tv.wideObjectsProbe().section(QLatin1Char(' '), 0, 3));
        }
        printf("  加宽第一张：%s\n", qPrintable(trace.join(QLatin1Char(' '))));
        printf("  宽对象：%s\n", qPrintable(tv.wideObjectsProbe()));
    }

    printf("== 长文本按列高换列、不越界 ==\n");
    {
        /* 200 个 h：约 200 × 7.7 = 1540pt，正文区高 728.6 → 至少要 3 列 */
        QTextDocument ldoc;
        ldoc.setPlainText(QString(200, QLatin1Char('h')));
        UmeView lv;
        lv.setSettings(&settings);
        lv.setDocument(&ldoc);
        lv.setBaseFormat(font, pt);

        const QString cols = lv.columnsProbe(6);
        printf("  列：%s\n", qPrintable(cols));

        const QImage img = lv.renderPageImage(0, 1.0, false);
        int maxY = 0;
        int maxX = 0;
        for (int y = 0; y < img.height(); ++y) {
            for (int x = 0; x < img.width(); ++x) {
                const QColor c = img.pixelColor(x, y);
                if (c.red() < 120 && c.green() < 120 && c.blue() < 120) {
                    maxY = qMax(maxY, y);
                    maxX = qMax(maxX, x);
                }
            }
        }
        const QRectF area = settings.page().textArea();
        printf("  墨迹最下 %.1f，最右 %.1f；正文区 y≤%.1f x≤%.1f\n",
               qreal(maxY), qreal(maxX), area.bottom(), area.right());
        printf("  是否越界 = %d（应为 0）\n",
               int(maxY > area.bottom() + 1.0 || maxX > area.right() + 1.0));
    }

    printf("== 图片前后能继续输入 ==\n");
    {
        QImage pic(120, 90, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/para-probe.png").arg(outDir);
        pic.save(path);

        QTextDocument pd;
        pd.setPlainText(QStringLiteral("图片前。"));
        UmeView pv;
        pv.setSettings(&settings);
        pv.setDocument(&pd);
        pv.setBaseFormat(font, pt);
        pv.insertImage(path);

        printf("  插图后：块数=%d，光标在块 %d，该块是宽对象=%d\n",
               pd.blockCount(), pv.textCursor().blockNumber(),
               int(UmeDoc::isWideBlock(pv.textCursor().block())));

        /* 直接在光标处打字 —— 应落到图片之后的段落里 */
        pv.insertTextProbe(QStringLiteral("图后文字"));
        const QString all = pd.toPlainText();
        printf("  打字后：含「图后文字」=%d，块数=%d\n",
               int(all.contains(QStringLiteral("图后文字"))), pd.blockCount());

        /* 再验证「把光标放到图片块上再打字」也能自动建段落 */
        QTextCursor onImage(&pd);
        for (QTextBlock b = pd.begin(); b.isValid(); b = b.next()) {
            if (UmeDoc::isWideBlock(b)) {
                onImage = QTextCursor(b);
                break;
            }
        }
        pv.setTextCursor(onImage);
        pv.insertTextProbe(QStringLiteral("又一段"));
        printf("  在图片块上打字后：含「又一段」=%d，块数=%d\n",
               int(pd.toPlainText().contains(QStringLiteral("又一段"))), pd.blockCount());
    }

    printf("== 点图片下方继续输入 ==\n");
    {
        QImage pic(120, 90, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/under-probe.png").arg(outDir);
        pic.save(path);

        QTextDocument ud;
        ud.setPlainText(QStringLiteral("上方文字。"));
        UmeView uv;
        uv.setSettings(&settings);
        uv.setDocument(&ud);
        uv.setBaseFormat(font, pt);
        uv.insertImage(path);

        const QRectF box = uv.wideItemBoxProbe(0);
        printf("  图片盒 x %.1f–%.1f y %.1f–%.1f\n",
               box.left(), box.right(), box.top(), box.bottom());

        /* 点图片下方 20pt 处 */
        QTextCursor toTop(&ud);
        toTop.setPosition(0);
        uv.setTextCursor(toTop);
        QTextCursor before = uv.textCursor();
        const QPointF under(box.center().x(), box.bottom() + 20.0);
        QMouseEvent press(QEvent::MouseButtonPress, under,
                          uv.mapToGlobal(under.toPoint()), Qt::LeftButton,
                          Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&uv, &press);
        QMouseEvent release(QEvent::MouseButtonRelease, under,
                            uv.mapToGlobal(under.toPoint()), Qt::LeftButton,
                            Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&uv, &release);

        printf("  点击前块 %d → 点击后块 %d（应落在图片之后的段落）\n",
               before.blockNumber(), uv.textCursor().blockNumber());
        printf("  该块是宽对象 = %d（应为 0）\n",
               int(UmeDoc::isWideBlock(uv.textCursor().block())));
    }

    printf("== 整列 vs 环绕：后续文字位置 ==\n");
    {
        QImage pic(120, 90, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/mode-probe.png").arg(outDir);
        pic.save(path);

        QTextDocument mdoc;
        /* 图片之前一段、之后一段 */
        mdoc.setPlainText(QStringLiteral("前面的文字。"));
        UmeView mv;
        mv.setSettings(&settings);
        mv.setDocument(&mdoc);
        mv.setBaseFormat(font, pt);

        QTextCursor end(&mdoc);
        end.movePosition(QTextCursor::End);
        mv.setTextCursor(end);
        mv.insertImage(path);
        mv.insertTextProbe(QStringLiteral("后面的文字。"));

        UmeDoc::WideProps p = mv.currentWideObject();
        p.span = 4;
        p.heightPt = 120.0;

        p.wrap = UmeDoc::WideWrap::Span;
        mv.applyWideObject(p);
        const QString spanCols = mv.columnsProbe(4);
        const QRectF spanBox = mv.wideItemBoxProbe(0);

        p.wrap = UmeDoc::WideWrap::Bubble;
        mv.applyWideObject(p);
        const QString wrapCols = mv.columnsProbe(4);
        const QRectF wrapBox = mv.wideItemBoxProbe(0);

        printf("  【整列】盒 x%.1f–%.1f y%.1f–%.1f\n",
               spanBox.left(), spanBox.right(), spanBox.top(), spanBox.bottom());
        printf("         列：%s\n", qPrintable(spanCols));
        printf("  读回 wrap=%d（1 应为环绕）\n", int(mv.currentWideObject().wrap));
        printf("  【环绕】盒 x%.1f–%.1f y%.1f–%.1f\n",
               wrapBox.left(), wrapBox.right(), wrapBox.top(), wrapBox.bottom());
        printf("         列：%s\n", qPrintable(wrapCols));
    }

    printf("== 环绕模式下能选中下方文字 ==\n");
    {
        QImage pic(100, 80, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/wrap-probe.png").arg(outDir);
        pic.save(path);

        /* 空文档 → 先插图 → 再在「图片之后的段落」里输入文字 */
        QTextDocument bdoc;
        UmeView bv;
        bv.setSettings(&settings);
        bv.setDocument(&bdoc);
        bv.setBaseFormat(font, pt);
        bv.insertImage(path);
        bv.insertTextProbe(QStringLiteral("下方的文字内容。"));

        UmeDoc::WideProps wp = bv.currentWideObject();
        wp.wrap = UmeDoc::WideWrap::Bubble;
        wp.span = 3;
        wp.heightPt = 80.0;
        bv.applyWideObject(wp);
        printf("  环绕盒：%s\n", qPrintable(bv.wideObjectsProbe()));

        const QRectF box = bv.wideItemBoxProbe(0);
        QRectF textCol;
        for (int i = 0; i < 8; ++i) {
            const QRectF cb = bv.columnBoxProbe(i);
            if (!cb.isValid())
                break;
            if (cb.top() > box.bottom() - 0.5 && cb.width() > 1.0) {
                textCol = cb;
                break;
            }
        }
        printf("  对象下沿 %.1f；目标文字列 x%.1f–%.1f y%.1f–%.1f\n",
               box.bottom(), textCol.left(), textCol.right(),
               textCol.top(), textCol.bottom());

        const QPointF onText = textCol.isValid()
                                   ? QPointF(textCol.center().x(), textCol.top() + 20.0)
                                   : QPointF(box.center().x(), box.bottom() + 20.0);
        printf("  点击点 (%.1f, %.1f) 命中列 = %d\n",
               onText.x(), onText.y(), int(bv.hitsAnyColumnProbe(onText)));

        QMouseEvent press(QEvent::MouseButtonPress, onText,
                          bv.mapToGlobal(onText.toPoint()), Qt::LeftButton,
                          Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&bv, &press);
        QMouseEvent release(QEvent::MouseButtonRelease, onText,
                            bv.mapToGlobal(onText.toPoint()), Qt::LeftButton,
                            Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&bv, &release);

        const QTextCursor got = bv.textCursor();
        printf("  点击后停在块 %d：\"%s\"（应含「下方」）\n",
               got.blockNumber(), qPrintable(got.block().text().left(8)));
    }

    printf("== 命中模块（UmeHit）独立可用 ==\n");
    {
        /* 纯几何：不依赖视图与文档 */
        const QRectF box(100, 100, 80, 60);

        /* 手柄：未旋转时 0 号在左上，8 号在右侧外 14pt */
        const QVector<QPointF> pts = UmeHit::handlePoints(box);
        printf("  手柄数 = %d，0 号 (%.1f, %.1f)，8 号 (%.1f, %.1f)\n",
               int(pts.size()), pts[0].x(), pts[0].y(), pts[8].x(), pts[8].y());

        /* 命中左上角 → 0 号；命中中心 → 对象本体；命中远处 → 都没有 */
        printf("  90° 下点左上角 → 手柄 %d\n",
               UmeHit::handleAt(box, 90.0,
                                UmeInteract::rotatePoint(pts[0], box.center(), 90.0)));
        printf("  点中心 → 本体 = %d，手柄 = %d\n",
               int(UmeHit::boxContains(box, 0.0, box.center())),
               UmeHit::handleAt(box, 0.0, box.center()));
        printf("  点 (400,400) → 本体 = %d\n",
               int(UmeHit::boxContains(box, 0.0, QPointF(400, 400))));

        /* 列表版：两列 + 一个对象，验证优先级与「后放优先」 */
        QVector<UmeLayout::Column> cols(2);
        cols[0].box = QRectF(50, 50, 25, 700);
        cols[1].box = QRectF(75, 50, 25, 700);

        QVector<UmeLayout::WideItem> items(2);
        items[0].box = QRectF(120, 50, 60, 60);
        items[1].box = QRectF(120, 50, 60, 60);   // 完全重叠，后放的应在上面

        printf("  列命中 (60,300) = %d；对象命中 (150,80) = %d（重叠时应为 1）\n",
               UmeHit::columnAt(cols, QPointF(60, 300)),
               UmeHit::wideAt(items, QPointF(150, 80)));
        printf("  空白 (300,300)：列 = %d，对象 = %d\n",
               UmeHit::columnAt(cols, QPointF(300, 300)),
               UmeHit::wideAt(items, QPointF(300, 300)));

        PageSetup page = PageSetup::preset(QStringLiteral("A4"));
        printf("  页命中 (100,100) = %d；(100,2000) = %d\n",
               UmeHit::pageAt(page, 2, PageArrangement(), QPointF(100, 100)),
               UmeHit::pageAt(page, 2, PageArrangement(), QPointF(100, 2000)));
    }

    printf("== 环绕：右侧的列要回到页首 ==\n");
    {
        QImage pic(100, 80, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/wrap-fill.png").arg(outDir);
        pic.save(path);

        /* 图 -> 大量文字：文字先绕到图下方，超出图的 x 范围后应回到页首 */
        QTextDocument fdoc;
        UmeView fv;
        fv.setSettings(&settings);
        fv.setDocument(&fdoc);
        fv.setBaseFormat(font, pt);
        fv.insertImage(path);
        fv.insertTextProbe(QString(400, QLatin1Char('h')));

        UmeDoc::WideProps wp = fv.currentWideObject();
        wp.wrap = UmeDoc::WideWrap::Bubble;
        wp.span = 4;
        wp.heightPt = 600.0;
        fv.applyWideObject(wp);

        const QRectF box = fv.wideItemBoxProbe(0);
        printf("  图片盒 x%.1f–%.1f y%.1f–%.1f\n",
               box.left(), box.right(), box.top(), box.bottom());

        /* 统计：完全在图片右侧的列里，有多少列的 top 回到页首附近 */
        int rightCols = 0;
        int rightAtTop = 0;
        for (int i = 0; i < 60; ++i) {
            const QRectF cb = fv.columnBoxProbe(i);
            if (!cb.isValid())
                break;
            if (cb.left() >= box.right() - 0.5) {
                ++rightCols;
                if (cb.top() < box.bottom() - 1.0)
                    ++rightAtTop;
            }
        }
        printf("  图片右侧的列 %d 个，其中在页首的 %d 个\n", rightCols, rightAtTop);
    }

    printf("== 宽对象分区（图片 / 表格）==\n");
    {
        QImage pic(100, 80, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/zone.png").arg(outDir);
        pic.save(path);

        QTextDocument zdoc;
        zdoc.setPlainText(QStringLiteral("分区测试"));
        UmeView zv;
        zv.setSettings(&settings);
        zv.setDocument(&zdoc);
        zv.setBaseFormat(font, pt);

        printf("  初始：kind=%d\n", int(zv.currentWideObject().kind));

        zv.insertImage(path);
        printf("  选中图片：kind=%d（1=表格 2=图片），选中索引=%d\n",
               int(zv.currentWideObject().kind), zv.selectedWideObject());

        QTextCursor end(&zdoc);
        end.movePosition(QTextCursor::End);
        zv.setTextCursor(end);
        zv.insertTable(2, 2);
        printf("  选中表格：kind=%d，尺寸 %dx%d\n",
               int(zv.currentWideObject().kind),
               UmeDoc::tableSize(zv.textCursor()).first,
               UmeDoc::tableSize(zv.textCursor()).second);
    }

    printf("== 页面排布与纸张方向 ==\n");
    {
        PageSetup ps = PageSetup::preset(QStringLiteral("A4"));
        const qreal w = ps.paper.width();
        const qreal h = ps.paper.height();
        const qreal gap = UmeLayout::kPageGap;

        PageArrangement rows;                    /* 默认：每行 2 页 */
        printf("  默认 perRow=%d mode=%d\n", rows.perRow, int(rows.mode));

        /* 4 页，每行 2 页：两行两列 */
        QRectF p0 = UmeLayout::pageRectOf(ps, 0, rows);
        QRectF p1 = UmeLayout::pageRectOf(ps, 1, rows);
        QRectF p2 = UmeLayout::pageRectOf(ps, 2, rows);
        printf("  2×2：p0(%.0f,%.0f) p1(%.0f,%.0f) p2(%.0f,%.0f)\n",
               p0.left(), p0.top(), p1.left(), p1.top(), p2.left(), p2.top());
        const QSizeF s4 = UmeLayout::contentSizeOf(ps, 4, rows);
        printf("  内容尺寸 %.0f×%.0f（应为 %.0f×%.0f）\n",
               s4.width(), s4.height(), 2 * w + gap, 2 * h + gap);

        /* 无限横向 */
        PageArrangement horiz;
        horiz.mode = PageArrangement::Horizontal;
        const QRectF h3 = UmeLayout::pageRectOf(ps, 3, horiz);
        const QSizeF sh = UmeLayout::contentSizeOf(ps, 4, horiz);
        printf("  横向：p3(%.0f,%.0f)，内容 %.0f×%.0f（高度应为 1 页）\n",
               h3.left(), h3.top(), sh.width(), sh.height());

        /* 无限竖向 */
        PageArrangement vert;
        vert.mode = PageArrangement::Vertical;
        const QRectF v3 = UmeLayout::pageRectOf(ps, 3, vert);
        const QSizeF sv = UmeLayout::contentSizeOf(ps, 4, vert);
        printf("  竖向：p3(%.0f,%.0f)，内容 %.0f×%.0f（宽度应为 1 页）\n",
               v3.left(), v3.top(), sv.width(), sv.height());

        /* 纸张方向：横竖切换应对调宽高 */
        PageSetup land = PageSetup::preset(QStringLiteral("A4"));
        land.setOrientation(PageOrientation::Landscape);
        printf("  纵向 %.0f×%.0f → 横向 %.0f×%.0f\n",
               w, h, land.paper.width(), land.paper.height());
        land.setOrientation(PageOrientation::Landscape);   // 重复设置不应再翻
        printf("  重复设横向仍为 %.0f×%.0f\n",
               land.paper.width(), land.paper.height());
    }

    printf("== 排布模式贯通到视图 ==\n");
    {
        /* 用足够长的文本造出多页 */
        QTextDocument vd;
        vd.setPlainText(QString(3000, QLatin1Char('h')));
        UmeView vv;
        UmeSettings vs;
        vv.setSettings(&vs);
        vv.setDocument(&vd);
        vv.setBaseFormat(font, pt);

        auto describe = [&](const char *tag) {
            const QSizeF c = vv.contentSizeProbe();
            printf("  %s：页数 %d，内容 %.0f×%.0f\n", tag,
                   vv.pageCountProbe(), c.width(), c.height());
        };

        describe("默认（每行 2 页）");

        PageArrangement a = vs.arrangement();
        a.mode = PageArrangement::Horizontal;
        vs.setArrangement(a);
        describe("无限横向  ");

        a.mode = PageArrangement::Vertical;
        vs.setArrangement(a);
        describe("无限竖向  ");

        a.mode = PageArrangement::RowsOfN;
        a.perRow = 3;
        vs.setArrangement(a);
        describe("每行 3 页 ");
    }

    printf("== 连插两张图 ==\n");
    {
        QImage a(600, 400, QImage::Format_RGB32);
        a.fill(QColor(0x2e, 0x75, 0xb6));
        const QString pa = QStringLiteral("%1/two1.png").arg(outDir);
        a.save(pa);
        QImage b(566, 385, QImage::Format_RGB32);
        b.fill(QColor(0x22, 0x22, 0x22));
        const QString pb = QStringLiteral("%1/two2.png").arg(outDir);
        b.save(pb);

        QTextDocument d2;
        d2.setPlainText(QStringLiteral("前后都有字。"));
        UmeView v2;
        UmeSettings s2;
        v2.setSettings(&s2);
        v2.setDocument(&d2);
        v2.setBaseFormat(font, pt);

        s2.setOrientation(PageOrientation::Landscape);
        v2.insertImage(pa);
        v2.insertImage(pb);

        const QRectF area = s2.page().textArea();
        printf("  正文区 %.1f–%.1f（宽 %.1f）\n",
               area.left(), area.right(), area.width());
        printf("  宽对象：%s\n", qPrintable(v2.wideObjectsProbe()));

        int over = 0;
        for (int i = 0; i < 4; ++i) {
            const QRectF box = v2.wideItemBoxProbe(i);
            if (!box.isValid())
                break;
            if (box.right() > area.right() + 0.5)
                ++over;
            printf("    #%d x%.1f–%.1f w%.1f 越界=%d\n", i,
                   box.left(), box.right(), box.width(),
                   int(box.right() > area.right() + 0.5));
        }
        printf("  越界对象数 = %d（应为 0），页数 = %d\n",
               over, v2.pageCountProbe());
    }

    printf("== 跨页对象落在各自页内 ==\n");
    {
        QImage a(600, 400, QImage::Format_RGB32);
        a.fill(QColor(0x2e, 0x75, 0xb6));
        const QString pa = QStringLiteral("%1/x1.png").arg(outDir);
        a.save(pa);
        QImage b(600, 400, QImage::Format_RGB32);
        b.fill(QColor(0x22, 0x22, 0x22));
        const QString pb = QStringLiteral("%1/x2.png").arg(outDir);
        b.save(pb);

        QTextDocument xd;
        xd.setPlainText(QString(600, QLatin1Char('w')));
        UmeView xv;
        UmeSettings xs;
        xv.setSettings(&xs);
        xv.setDocument(&xd);
        xv.setBaseFormat(font, pt);

        xv.insertImage(pa);
        xv.insertImage(pb);
        printf("  页数 = %d\n", xv.pageCountProbe());

        for (int i = 0; i < 4; ++i) {
            const QRectF doc = xv.wideItemDocRectProbe(i);
            if (!doc.isValid())
                break;
            const int page = xv.wideItemPageProbe(i);
            const QRectF pageBox = xv.pageBoxProbe(page);
            printf("    #%d 页%d 内容坐标 x%.1f–%.1f y%.1f–%.1f；该页 y%.1f–%.1f 包含=%d\n",
                   i, page, doc.left(), doc.right(), doc.top(), doc.bottom(),
                   pageBox.top(), pageBox.bottom(),
                   int(pageBox.contains(doc)));
        }
    }

    printf("== 滚动范围覆盖到最后一页 ==\n");
    {
        QTextDocument sd;
        sd.setPlainText(QString(2500, QLatin1Char('h')));
        UmeView sv;
        UmeSettings ss;
        sv.setSettings(&ss);
        sv.setDocument(&sd);
        sv.setBaseFormat(font, pt);
        sv.resize(900, 600);
        sv.show();                       /* 触发 resizeEvent → updateScrollBars */

        const QSizeF cs = sv.contentSizeProbe();
        const QList<int> r = sv.scrollRangeProbe();
        printf("  页数 %d，内容 %.0f×%.0f，视图 %d×%d\n",
               sv.pageCountProbe(), cs.width(), cs.height(), r[4], r[5]);
        printf("  滚动范围 X=%d Y=%d\n", r[0], r[1]);
        printf("  能否到底：X %d，Y %d（应都能）\n",
               int(r[0] >= int(cs.width() - r[4]) - 2),
               int(r[1] >= int(cs.height() - r[5]) - 2));

        /* 切到无限竖向，范围应该变长 */
        PageArrangement a = ss.arrangement();
        a.mode = PageArrangement::Vertical;
        ss.setArrangement(a);
        const QList<int> r2 = sv.scrollRangeProbe();
        printf("  竖向排列后：内容高 %.0f，Y 范围 %d\n",
               sv.contentSizeProbe().height(), r2[1]);
        sv.hide();
    }

    printf("== 第 1 页的图不影响第 2 页排版 ==\n");
    {
        QImage pic(600, 400, QImage::Format_RGB32);
        pic.fill(QColor(0x2e, 0x75, 0xb6));
        const QString path = QStringLiteral("%1/pg.png").arg(outDir);
        pic.save(path);

        /* 短文字 + 高图 + 长文字，保证后面几页都是纯正文 */
        QTextDocument gd;
        gd.setPlainText(QStringLiteral("开头。"));
        UmeView gv;
        UmeSettings gs;
        gv.setSettings(&gs);
        gv.setDocument(&gd);
        gv.setBaseFormat(font, pt);

        QTextCursor end(&gd);
        end.movePosition(QTextCursor::End);
        gv.setTextCursor(end);
        gv.insertImage(path);
        UmeDoc::WideProps wp = gv.currentWideObject();
        wp.wrap = UmeDoc::WideWrap::Span;
        wp.span = 8;
        wp.heightPt = 300.0;
        gv.applyWideObject(wp);

        gv.insertTextProbe(QString(2400, QLatin1Char('h')));

        const QRectF box = gv.wideItemBoxProbe(0);
        const int pages = gv.pageCountProbe();
        printf("  图：页内 y%.1f–%.1f（h=%.0f），正文区顶 %.1f，共 %d 页\n",
               box.top(), box.bottom(), box.height(),
               gs.page().textArea().top(), pages);

        for (int p = 0; p < pages; ++p)
            printf("    第 %d 页：起点不在页首的列 = %d（应为 0）\n",
                   p + 1, gv.colsOffTopProbe(p));
    }

    printf("== 能选中第 2 页的图 ==\n");
    {
        QImage a(600, 500, QImage::Format_RGB32);
        a.fill(QColor(0x2e, 0x75, 0xb6));
        const QString pa = QStringLiteral("%1/sel1.png").arg(outDir);
        a.save(pa);
        QImage b(600, 500, QImage::Format_RGB32);
        b.fill(QColor(0xc0, 0x40, 0x40));
        const QString pb = QStringLiteral("%1/sel2.png").arg(outDir);
        b.save(pb);

        QTextDocument sd;
        sd.setPlainText(QStringLiteral("文字"));
        UmeView sv;
        UmeSettings ss;
        sv.setSettings(&ss);
        sv.setDocument(&sd);
        sv.setBaseFormat(font, pt);

        sv.insertImage(pa);
        UmeDoc::WideProps big = sv.currentWideObject();
        big.span = 12;
        big.heightPt = 500.0;
        sv.applyWideObject(big);
        sv.insertImage(pb);
        UmeDoc::WideProps big2 = sv.currentWideObject();
        big2.span = 12;
        big2.heightPt = 400.0;
        sv.applyWideObject(big2);
        printf("  页数 = %d，宽对象数 = %d\n", sv.pageCountProbe(),
               int(sv.wideObjectsProbe().count(QLatin1String("[x"))));
        for (int i = 0; i < 6; ++i) {
            const QRectF d = sv.wideItemDocRectProbe(i);
            if (!d.isValid())
                break;
            printf("    #%d 页%d 内容坐标 x%.1f–%.1f y%.1f–%.1f\n",
                   i, sv.wideItemPageProbe(i), d.left(), d.right(), d.top(), d.bottom());
        }

        /* 点第 2 张图的中心 */
        const QRectF second = sv.wideItemDocRectProbe(1);
        const QPointF hit = second.center();
        QMouseEvent press(QEvent::MouseButtonPress, hit, sv.mapToGlobal(hit.toPoint()),
                          Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&sv, &press);
        QMouseEvent release(QEvent::MouseButtonRelease, hit, sv.mapToGlobal(hit.toPoint()),
                            Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&sv, &release);

        printf("  点击后选中索引 = %d（应为 1）\n", sv.selectedWideObject());

        /* 改高度，确认只动第 2 张 */
        UmeDoc::WideProps p = sv.currentWideObject();
        p.heightPt = 200.0;
        sv.applyWideObject(p);
        for (int i = 0; i < 3; ++i) {
            const QRectF d = sv.wideItemDocRectProbe(i);
            if (!d.isValid())
                break;
            printf("    改后 #%d 高 %.1f\n", i, d.height());
        }
    }

    printf("== 表格跨页（整行切分）==\n");
    {
        QTextDocument td;
        td.setPlainText(QStringLiteral("表格前的文字。"));
        UmeView tv;
        UmeSettings ts;
        tv.setSettings(&ts);
        tv.setDocument(&td);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&td);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(10, 3);          /* 10 行：必然超过一页 */

        UmeDoc::WideProps wp = tv.currentWideObject();
        wp.span = 6;
        wp.heightPt = 1200.0;           /* 每行 120pt，一页约 6 行 */
        tv.applyWideObject(wp);

        printf("  页数 = %d，表格片段数 = %d\n", tv.pageCountProbe(),
               tv.tableFragmentCountProbe());
        printf("  片段：%s\n", qPrintable(tv.tableFragmentsProbe()));

        /* 每个片段的行区间不能重叠、不能跳行，且首尾相接 */
        const QString frags = tv.tableFragmentsProbe();
        printf("  行区间连续 = %d（应为 1）\n",
               int(frags.contains(QStringLiteral("rows 0-"))));
        tv.renderPageImage(0, 1.0, false).save(QStringLiteral("%1/table-p1.png").arg(outDir));
        tv.renderPageImage(1, 1.0, false).save(QStringLiteral("%1/table-p2.png").arg(outDir));
    }

    printf("== 单元格内多列文本 ==\n");
    {
        QTextDocument cd;
        cd.setPlainText(QStringLiteral("表"));
        UmeView cv;
        UmeSettings cs;
        cv.setSettings(&cs);
        cv.setDocument(&cd);
        cv.setBaseFormat(font, pt);

        QTextCursor end(&cd);
        end.movePosition(QTextCursor::End);
        cv.setTextCursor(end);
        cv.insertTable(1, 1);

        /* 往唯一单元格里塞 60 个字（用单元格自己的光标） */
        QTextTable *tbl = cv.textCursor().currentTable();
        QTextCursor cell = tbl ? tbl->cellAt(0, 0).firstCursorPosition()
                               : cv.textCursor();
        cell.insertText(QString(60, QChar(0x6C49)));    /* 汉字「汉」 */
        cv.setTextCursor(cell);

        UmeDoc::WideProps wp = cv.currentWideObject();
        wp.span = 4;
        wp.heightPt = 90.0;
        cv.applyWideObject(wp);

        printf("  cell text len = %d\n",
               int(tbl ? tbl->cellAt(0, 0).firstCursorPosition().block().text().size()
                        : -1));
        const QRectF box = cv.wideItemBoxProbe(0);
        printf("  表格 x%.1f–%.1f y%.1f–%.1f\n",
               box.left(), box.right(), box.top(), box.bottom());

        const QImage img = cv.renderPageImage(0, 1.0, false);
        /* 在格子内按 x 统计「有墨迹的条带数」 */
        const int x0 = int(box.left()) + 2;
        const int x1 = int(box.right()) - 2;
        const int y0 = int(box.top()) + 2;
        const int y1 = int(box.bottom()) - 2;
        int bands = 0;
        bool inBand = false;
        for (int x = x0; x < x1 && x < img.width(); ++x) {
            bool ink = false;
            for (int y = y0; y < y1 && y < img.height(); ++y) {
                const QColor c = img.pixelColor(x, y);
                if (c.red() < 120 && c.green() < 120 && c.blue() < 120) {
                    ink = true;
                    break;
                }
            }
            if (ink && !inBand) {
                ++bands;
                inBand = true;
            } else if (!ink) {
                inBand = false;
            }
        }
        printf("  单元格内墨迹条带数 = %d（>1 说明分成多列）\n", bands);
        img.save(QStringLiteral("%1/table-cell.png").arg(outDir));
    }

    printf("== 表格单元格：合适尺寸 / Enter 跳格 ==\n");
    {
        QTextDocument td;
        td.setPlainText(QStringLiteral("表"));
        UmeView tv;
        UmeSettings ts;
        tv.setSettings(&ts);
        tv.setDocument(&td);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&td);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(2, 3);

        QTextTable *tbl = tv.textCursor().currentTable();
        if (tbl) {
            /* 第 1 格塞长文本，看列宽是否按内容变宽 */
            tbl->cellAt(0, 0).firstCursorPosition().insertText(
                QString(40, QChar(0x6C49)));
            tbl->cellAt(0, 1).firstCursorPosition().insertText(QStringLiteral("短"));
        }
        tv.applyWideObject(tv.currentWideObject());
        printf("  表格盒：%s\n", qPrintable(tv.wideObjectsProbe()));

        /* Enter 跳格：从 (0,0) 开始，走完 6 格再一格应跳出表格 */
        tv.setTextCursor(tbl->cellAt(0, 0).firstCursorPosition());
        for (int i = 0; i < 6; ++i) {
            QKeyEvent key(QEvent::KeyPress, Qt::Key_Return, Qt::NoModifier);
            QApplication::sendEvent(&tv, &key);
            const QTextCursor c = tv.textCursor();
            QTextTableCell cell = tbl->cellAt(c);
            printf("  Enter#%d → 行 %d 列 %d%s\n", i + 1,
                   cell.isValid() ? cell.row() : -1,
                   cell.isValid() ? cell.column() : -1,
                   cell.isValid() ? "" : "（已跳出表格）");
        }

        tv.renderPageImage(0, 1.0, false).save(QStringLiteral("%1/table-cells2.png").arg(outDir));
    }

    printf("== 表格专用手柄 ==\n");
    {
        QTextDocument td;
        td.setPlainText(QStringLiteral("表"));
        UmeView tv;
        UmeSettings ts;
        tv.setSettings(&ts);
        tv.setDocument(&td);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&td);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(3, 3);
        tv.applyWideObject(tv.currentWideObject());

        /* 选中表格（点它本体） */
        const QRectF box = tv.wideItemDocRectProbe(0);
        QMouseEvent press(QEvent::MouseButtonPress, box.center(),
                          tv.mapToGlobal(box.center().toPoint()), Qt::LeftButton,
                          Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&tv, &press);
        QMouseEvent rel(QEvent::MouseButtonRelease, box.center(),
                        tv.mapToGlobal(box.center().toPoint()), Qt::LeftButton,
                        Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&tv, &rel);

        printf("  选中索引 = %d\n", tv.selectedWideObject());
        printf("  手柄数 = %d（3×3 应有 2 条列线 + 2 条行线 = 4）\n",
               int(tv.wideHandlesProbe().size()));

        /* 表格不允许旋转 */
        UmeDoc::WideProps p = tv.currentWideObject();
        p.rotation = 45.0;
        tv.applyWideObject(p);
        printf("  设 45° 后读回 rotation = %.1f（应为 0）\n",
               tv.currentWideObject().rotation);

        /* 拖第一条列分隔线 → 第 0 列变宽、第 1 列变窄 */
        const QVector<QRectF> hs = tv.wideHandlesProbe();
        if (!hs.isEmpty()) {
            const QPointF h = hs.first().center();
            QMouseEvent d0(QEvent::MouseButtonPress, h, tv.mapToGlobal(h.toPoint()),
                           Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &d0);
            const QPointF h2 = h + QPointF(12, 0);
            QMouseEvent d1(QEvent::MouseMove, h2, tv.mapToGlobal(h2.toPoint()),
                           Qt::NoButton, Qt::LeftButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &d1);
            QMouseEvent d2(QEvent::MouseButtonRelease, h2, tv.mapToGlobal(h2.toPoint()),
                           Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &d2);
            const UmeDoc::WideProps q = tv.currentWideObject();
            printf("  列宽：%s\n", qPrintable([&] {
                       QStringList s;
                       for (qreal w : q.colSizes)
                           s << QString::number(w, 'f', 1);
                       return s.join(QLatin1Char('/'));
                   }()));
        }
    }

    printf("== 整行/整列格式 ==\n");
    {
        QTextDocument td;
        td.setPlainText(QStringLiteral("表"));
        UmeView tv;
        UmeSettings ts;
        tv.setSettings(&ts);
        tv.setDocument(&td);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&td);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(3, 3);
        QTextTable *tbl = tv.textCursor().currentTable();
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                tbl->cellAt(i, j).firstCursorPosition().insertText(
                    QStringLiteral("%1%2").arg(i).arg(j));

        tv.applyWideObject(tv.currentWideObject());

        /* 选中第 1 行（点第 1 条行分隔线手柄） */
        const QRectF box = tv.wideItemDocRectProbe(0);
        const QVector<QRectF> hs = tv.wideHandlesProbe();
        /* 前 cols-1 个是列线，后面是行线 */
        int rowHandle = -1;
        for (int k = 0; k < hs.size(); ++k) {
            if (qAbs(hs[k].center().y() - box.top()) > 2.0) {
                rowHandle = k;
                break;
            }
        }
        if (rowHandle >= 0) {
            const QPointF h = hs[rowHandle].center();
            QMouseEvent pr(QEvent::MouseButtonPress, h, tv.mapToGlobal(h.toPoint()),
                           Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &pr);
            QMouseEvent rl(QEvent::MouseButtonRelease, h, tv.mapToGlobal(h.toPoint()),
                           Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &rl);
        }

        /* 加粗 —— 应该只作用于第 1 行 */
        const int idx = int(UmeView::StyleBold);
        tv.applyCharStyleProbe(idx, true);

        for (int i = 0; i < 3; ++i) {
            printf("  第 %d 行：", i);
            for (int j = 0; j < 3; ++j)
                printf("%d ", int(tbl->cellAt(i, j).format().fontWeight()));
            printf("\n");
        }
    }

    printf("== 拖行分隔线不失控 ==\n");
    {
        QTextDocument td;
        td.setPlainText(QStringLiteral("表"));
        UmeView tv;
        UmeSettings ts;
        tv.setSettings(&ts);
        tv.setDocument(&td);
        tv.setBaseFormat(font, pt);

        QTextCursor end(&td);
        end.movePosition(QTextCursor::End);
        tv.setTextCursor(end);
        tv.insertTable(4, 3);
        tv.applyWideObject(tv.currentWideObject());

        /* 选中表格本体 */
        const QRectF box0 = tv.wideItemDocRectProbe(0);
        QMouseEvent s0(QEvent::MouseButtonPress, box0.center(),
                       tv.mapToGlobal(box0.center().toPoint()),
                       Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
        QApplication::sendEvent(&tv, &s0);
        QMouseEvent s1(QEvent::MouseButtonRelease, box0.center(),
                       tv.mapToGlobal(box0.center().toPoint()),
                       Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
        QApplication::sendEvent(&tv, &s1);

        const qreal h0 = tv.wideItemDocRectProbe(0).height();
        printf("  初始表高 %.1f\n", h0);

        /* 找第一条行分隔线手柄（y 不在表格顶部的那个） */
        const QVector<QRectF> hs = tv.wideHandlesProbe();
        QPointF rowH(-1, -1);
        for (const QRectF &hr : hs) {
            if (qAbs(hr.center().y() - box0.top()) > 2.0) {
                rowH = hr.center();
                break;
            }
        }
        printf("  行线手柄 (%.1f, %.1f)，共 %d 个手柄\n",
               rowH.x(), rowH.y(), int(hs.size()));

        if (rowH.x() > 0) {
            QMouseEvent d0(QEvent::MouseButtonPress, rowH, tv.mapToGlobal(rowH.toPoint()),
                           Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &d0);
            /* 分 10 步往下拖 20pt，模拟真实拖动 */
            for (int i = 1; i <= 10; ++i) {
                const QPointF p = rowH + QPointF(0, 2.0 * i);
                QMouseEvent mv(QEvent::MouseMove, p, tv.mapToGlobal(p.toPoint()),
                               Qt::NoButton, Qt::LeftButton, Qt::NoModifier);
                QApplication::sendEvent(&tv, &mv);
            }
            const QPointF lastP = rowH + QPointF(0, 20);
            QMouseEvent up(QEvent::MouseButtonRelease, lastP,
                           tv.mapToGlobal(lastP.toPoint()),
                           Qt::LeftButton, Qt::NoButton, Qt::NoModifier);
            QApplication::sendEvent(&tv, &up);

            const qreal h1 = tv.wideItemDocRectProbe(0).height();
            printf("  拖 +20pt 后表高 %.1f（应约 %.1f，不该失控）\n", h1, h0 + 20);
            printf("  失控 = %d（应为 0）\n", int(h1 > h0 + 60));
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
