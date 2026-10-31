#include "umeview.h"

#include "umesettings.h"
#include "umelog.h"

#include <QApplication>
#include <QClipboard>
#include <QFontDatabase>
#include <QFontMetricsF>
#include <QInputMethodEvent>
#include <QKeyEvent>
#include <QMimeData>
#include <QMouseEvent>
#include <QGlyphRun>
#include <QPainter>
#include <QPainterPath>
#include <QRawFont>
#include <QScrollBar>
#include <QTextBlock>
#include <QTextBlockFormat>
#include <QTextDocumentFragment>
#include <QTextLayout>
#include <QElapsedTimer>
#include <QWheelEvent>

#include <limits>

namespace {

constexpr qreal kAutoEmFactor = 1.7;     // 列距下限：字号 × 1.7
constexpr qreal kAutoInkFactor = 1.3;    // 列距下限：墨迹宽 × 1.3
constexpr int kBlinkMs = 600;
/* QTextLayout 的坐标是「96dpi 像素」（glyph 位置、字形轮廓都是），
   而我们的画布单位是 pt —— 画字时统一乘 72/96。 */
constexpr qreal kPxToPt = 72.0 / 96.0;

} // namespace

UmeView::UmeView(QWidget *parent)
    : QWidget(parent)
{
    setFocusPolicy(Qt::StrongFocus);
    setAttribute(Qt::WA_InputMethodEnabled, true);   // 输入法要能往这里送
    setMouseTracking(true);

    m_vbar = new QScrollBar(Qt::Vertical, this);
    m_vbar->setSingleStep(20);
    connect(m_vbar, &QScrollBar::valueChanged, this, [this](int v) {
        m_scrollY = v;
        update();
    });

    m_blink.setInterval(kBlinkMs);
    connect(&m_blink, &QTimer::timeout, this, [this]() {
        m_blinkOn = !m_blinkOn;
        update();
    });
    m_blink.start();
}

/* ---------------- 与设置解耦 ---------------- */

void UmeView::setSettings(UmeSettings *settings)
{
    if (m_settings == settings)
        return;
    if (m_settings)
        disconnect(m_settings, nullptr, this, nullptr);
    m_settings = settings;
    if (m_settings) {
        /* 版面设置（纸张/边距/最小列宽/辅助线）变了就重排 */
        connect(m_settings, &UmeSettings::layoutChanged, this, [this]() {
            relayout();
            update();
        });
        connect(m_settings, &QObject::destroyed, this, [this]() { m_settings = nullptr; });
    }
    relayout();
    update();
}

void UmeView::setDocument(QTextDocument *doc)
{
    m_doc = doc;
    m_cursor = QTextCursor(m_doc);
    resetBaseFont();        // 新内容先统一成当前字体
    relayout();
    update();
}

void UmeView::resetBaseFont()
{
    m_appliedFamily.clear();   // 强制下次 apply 生效
    m_appliedPt = 0.0;

    /* 载入时定下版面度量基准：列距与基线以后只跟它走 */
    m_metricsFamily = m_baseFormat.fontFamilies().toStringList().value(0);
    m_metricsPt = m_baseFormat.fontPointSize() > 0 ? m_baseFormat.fontPointSize() : 14.0;

    applyBaseFontToDocument();
}

void UmeView::setZoom(qreal zoom)
{
    m_zoom = qBound(0.2, zoom, 8.0);
    updateScrollBars();
    update();
}

/* ---------------- 布局 ---------------- */

void UmeView::relayout()
{
    if (!m_doc || !m_settings)
        return;

    /* 度量只认「版面基准」：列距、基线不随选区格式跳动。
       基准在载入时确定，或在没有任何选区时改字体才会更新。 */
    const QString metricsFamily = m_metricsFamily.isEmpty()
                                      ? QStringLiteral("Noto Sans Mongolian")
                                      : m_metricsFamily;
    const qreal metricsPt = m_metricsPt > 0.0 ? m_metricsPt : 14.0;

    QFont metricsFont;
    metricsFont.setFamilies(fallbackFamilies(metricsFamily));
    metricsFont.setPointSizeF(metricsPt);

    const QFontMetricsF fm(metricsFont);
    m_ascent = fm.ascent();
    m_descent = fm.descent();
    /* 蒙文在水平布局里本身就是旋转过的，它的墨迹高度 = 竖排列宽要留的量 */
    /* 墨迹边界要按「整套蒙文字母」量，不能只拿一个词当样本 ——
       不同字体、不同字母的升部/降部差别很大，取小了首列就会压进页边距。 */
    QString sample;
    for (ushort c = 0x1820; c <= 0x1878; ++c)
        sample.append(QChar(c));
    const QRectF ink = fm.tightBoundingRect(sample);
    m_inkW = qMax(0.0, ink.height());

    /* 基线偏移用「字体度量」而不是实测墨迹：
       tightBoundingRect 量的是孤立形，实际排版用的是上下文形（init/medi/fina、
       连字），个别字形会比孤立形更靠外 —— Noto 实测就差 8.7pt。
       把基线放在 ascent 处，墨迹一定落在列内，不会压进页边距。 */
    m_inkAbove = qMax(qreal(0.0), m_ascent);
    m_inkBelow = qMax(qreal(0.0), m_descent);

    m_autoPitch = qMax(metricsPt * kAutoEmFactor,
                       m_inkW * kAutoInkFactor);
    m_colPitch = m_settings->columnPitchIsAuto() ? m_autoPitch
                                                 : m_settings->columnPitch();

    /* 每列宽度由内容决定；这里只给一个「最小列宽」兜底。
       手动填了列距时，就把那个值当最小列宽。 */
    const qreal minWidth = m_settings->columnPitchIsAuto()
                               ? qMax(metricsPt * 1.2, m_inkW)
                               : m_settings->columnPitch();
    QElapsedTimer timer;
    timer.start();

    int frags = 0;
    for (QTextBlock b = m_doc->begin(); b.isValid(); b = b.next())
        for (auto it = b.begin(); !it.atEnd(); ++it)
            if (it.fragment().isValid())
                ++frags;

    m_layout.relayout(m_doc, m_settings->page(), minWidth);

    UME_LOG("layout", QStringLiteral("blocks=%1 frags=%2 cols=%3 pages=%4 pitch=%5 "
                                     "metrics=%6/%7 took=%8ms")
                           .arg(m_doc->blockCount())
                           .arg(frags)
                           .arg(m_layout.columns().size())
                           .arg(m_layout.pageCount())
                           .arg(m_colPitch, 0, 'f', 1)
                           .arg(metricsFamily)
                           .arg(metricsPt, 0, 'f', 1)
                           .arg(timer.elapsed()));
    updateScrollBars();
}

void UmeView::applyBaseFontToDocument()
{
    if (!m_doc || !m_settings)
        return;

    const QString family = m_baseFormat.fontFamilies().toStringList().value(0,
                                        QStringLiteral("Noto Sans Mongolian"));
    const qreal pt = m_baseFormat.fontPointSize() > 0 ? m_baseFormat.fontPointSize() : 14.0;

    QFont f;
    f.setFamilies(fallbackFamilies(family));
    f.setPointSizeF(pt);
    if (m_doc->defaultFont() != f)
        m_doc->setDefaultFont(f);

    if (m_appliedFamily == family && qFuzzyCompare(m_appliedPt, pt))
        return;                     // 已经刷过，不动撤销栈
    m_appliedFamily = family;
    m_appliedPt = pt;

    QTextCursor c(m_doc);
    c.beginEditBlock();
    c.select(QTextCursor::Document);
    c.mergeCharFormat(m_baseFormat);
    c.endEditBlock();

    for (QTextBlock b = m_doc->begin(); b.isValid(); b = b.next()) {
        QTextCursor bc(b);
        bc.setBlockCharFormat(m_baseFormat);
    }
}

void UmeView::mergeFormatIntoSelection(const QTextCharFormat &fmt)
{
    UME_LOG("format", QStringLiteral("sel=%1 fam=%2 pt=%3 col=%4")
                          .arg(int(m_cursor.hasSelection()))
                          .arg(fmt.fontFamilies().toStringList().value(0))
                          .arg(fmt.fontPointSize(), 0, 'f', 1)
                          .arg(fmt.foreground().color().name()));
    if (!m_doc)
        return;

    if (m_cursor.hasSelection()) {
        QTextCursor c = m_cursor;
        c.mergeCharFormat(fmt);
        m_cursor = c;
    } else {
        /* 没有选区：只改「接下来输入的字」与所在块的块格式 */
        m_baseFormat.merge(fmt);
        QTextCursor c = m_cursor;
        c.setBlockCharFormat(m_baseFormat);
        m_cursor = c;
    }
    /* 列宽是按内容算的：改了字号（尤其改大）必须立刻重排，
       否则这一列还是旧宽度，大字会压到右边那一列上。 */
    relayout();
    ensureCursorVisible();
    emit formatStateChanged();
    emit documentEdited();
    update();
}

void UmeView::applyFormatFamily(const QString &family)
{
    QTextCharFormat fmt;
    fmt.setFontFamilies(fallbackFamilies(family));
    mergeFormatIntoSelection(fmt);
}

void UmeView::applyFormatPointSize(qreal pt)
{
    QTextCharFormat fmt;
    fmt.setFontPointSize(pt);
    mergeFormatIntoSelection(fmt);
}

void UmeView::applyFormatColor(const QColor &c)
{
    QTextCharFormat fmt;
    fmt.setForeground(c);
    mergeFormatIntoSelection(fmt);
}

void UmeView::setBaseFormat(const QString &family, qreal pt, const QColor &color)
{
    m_baseFormat = QTextCharFormat();
    m_baseFormat.setFontFamilies(fallbackFamilies(family));
    m_baseFormat.setFontPointSize(pt);
    m_baseFormat.setForeground(color);
    m_appliedFamily.clear();
    m_appliedPt = 0.0;
    if (m_doc)
        applyBaseFontToDocument();
    relayout();
    update();
}

UmeFormatState UmeView::currentFormat() const
{
    UmeFormatState s;
    if (!m_doc)
        return s;

    auto consider = [&s](const QTextCharFormat &f) {
        const QString fam = f.fontFamilies().toStringList().value(0);
        const qreal pt = f.fontPointSize();
        const QColor col = f.foreground().color();

        if (s.family.isEmpty() && !s.familyMixed) {
            s.family = fam;
        } else if (s.family != fam) {
            s.familyMixed = true;
        }
        if (s.pointSize <= 0.0 && !s.sizeMixed) {
            s.pointSize = pt;
        } else if (!qFuzzyCompare(s.pointSize, pt)) {
            s.sizeMixed = true;
        }
        if (!s.color.isValid() && !s.colorMixed) {
            s.color = col;
        } else if (s.color != col) {
            s.colorMixed = true;
        }
    };

    if (m_cursor.hasSelection()) {
        const int a = m_cursor.selectionStart();
        const int b = m_cursor.selectionEnd();
        for (QTextBlock blk = m_doc->findBlock(a); blk.isValid() && blk.position() < b;
             blk = blk.next()) {
            for (auto it = blk.begin(); !it.atEnd(); ++it) {
                const QTextFragment fr = it.fragment();
                if (!fr.isValid())
                    continue;
                const int fs = fr.position();
                const int fe = fs + fr.length();
                if (fe <= a || fs >= b)
                    continue;
                consider(fr.charFormat());
            }
        }
    } else {
        consider(m_cursor.charFormat().isValid() ? m_cursor.charFormat() : m_baseFormat);
    }

    if (s.familyMixed)
        s.family.clear();
    if (s.sizeMixed)
        s.pointSize = 0.0;
    if (s.colorMixed)
        s.color = QColor();
    if (!s.color.isValid() && !s.colorMixed)
        s.color = Qt::black;
    return s;
}

/* ---------------- 几何 ---------------- */

QRectF UmeView::columnDocRect(const UmeLayout::Column &c) const
{
    const QRectF pageRect = UmeLayout::pageRect(m_settings->page(), c.page);
    return c.box.translated(0.0, pageRect.top());
}

QPointF UmeView::docPosFromWidget(const QPointF &widgetPos) const
{
    return QPointF(widgetPos.x() / m_zoom,
                   (widgetPos.y() + m_scrollY) / m_zoom);
}

QTextCursor UmeView::cursorAtDocPos(const QPointF &docPos) const
{
    if (!m_doc)
        return QTextCursor();

    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    if (cols.isEmpty())
        return QTextCursor(m_doc);

    int best = 0;
    qreal bestDist = std::numeric_limits<qreal>::max();
    for (int i = 0; i < cols.size(); ++i) {
        const QRectF r = columnDocRect(cols[i]);
        const qreal dy = (docPos.y() < r.top()) ? (r.top() - docPos.y())
                        : (docPos.y() > r.bottom()) ? (docPos.y() - r.bottom())
                                                    : 0.0;
        const qreal dx = (docPos.x() < r.left()) ? (r.left() - docPos.x())
                        : (docPos.x() > r.right()) ? (docPos.x() - r.right())
                                                   : 0.0;
        const qreal d = dy * 100.0 + dx;
        if (d < bestDist) {
            bestDist = d;
            best = i;
        }
    }

    const UmeLayout::Column &c = cols[best];
    QTextLayout *lay = c.block.layout();
    if (!lay || c.lineIndex >= lay->lineCount())
        return QTextCursor(m_doc);

    const QTextLine line = lay->lineAt(c.lineIndex);
    const QRectF r = columnDocRect(c);
    /* 反过来：屏幕 pt → 布局 px */
    const qreal u = qBound(0.0, (docPos.y() - r.top()) / kPxToPt, line.width());

    int rel = line.xToCursor(u);
    rel = qBound(line.textStart(), rel, line.textStart() + line.textLength());

    QTextCursor cur(m_doc);
    cur.setPosition(c.block.position() + rel);
    return cur;
}

int UmeView::columnIndexForCursor() const
{
    if (!m_doc)
        return -1;
    const QTextBlock blk = m_cursor.block();
    const int blockPos = m_cursor.position() - blk.position();

    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    int lastOfBlock = -1;
    for (int i = 0; i < cols.size(); ++i) {
        if (cols[i].block != blk)
            continue;
        QTextLayout *lay = blk.layout();
        if (!lay || cols[i].lineIndex >= lay->lineCount())
            continue;
        const QTextLine line = lay->lineAt(cols[i].lineIndex);
        if (blockPos >= line.textStart()
            && blockPos <= line.textStart() + line.textLength()) {
            return i;
        }
        lastOfBlock = i;
    }
    return lastOfBlock;
}

qreal UmeView::columnInkLeft(const UmeLayout::Column &c) const
{
    const QRectF r = columnDocRect(c);
    /* rotate(90) 之后局部 −y（字形上部）映射到屏幕 +x，
       所以墨迹落在基线的 +x 侧；把墨迹居中到列框里即可。 */
    return r.left() + (r.width() - c.inkW) / 2.0;
}

QRectF UmeView::caretDocRect() const
{
    if (!m_doc)
        return QRectF();

    const int idx = columnIndexForCursor();
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    if (idx < 0 || idx >= cols.size())
        return QRectF();

    const UmeLayout::Column &c = cols[idx];
    QTextLayout *lay = c.block.layout();
    if (!lay || c.lineIndex >= lay->lineCount())
        return QRectF();

    const QTextLine line = lay->lineAt(c.lineIndex);
    const QRectF r = columnDocRect(c);
    const int blockPos = qBound(line.textStart(),
                                m_cursor.position() - c.block.position(),
                                line.textStart() + line.textLength());
    /* cursorToX 给的是 96dpi 像素，画布是 pt —— 必须换算，否则光标会往下多走 33% */
    const qreal u = line.cursorToX(blockPos) * kPxToPt;

    /* 光标是一个「有点厚度」的矩形，不能是零高度：
       QRectF 零高度时 isValid() 为 false，paintCaret 会直接返回，
       光标就永远不显示（之前就是这个坑）。 */
    const qreal inkL = columnInkLeft(c);
    const qreal inkR = inkL + c.inkW;
    const qreal y = r.top() + u;
    return QRectF(QPointF(inkL, y - 1.0), QPointF(inkR, y + 1.0));
}

QVector<QRectF> UmeView::selectionDocRects() const
{
    QVector<QRectF> out;
    if (!m_doc || !m_cursor.hasSelection())
        return out;

    const int selStart = m_cursor.selectionStart();
    const int selEnd = m_cursor.selectionEnd();

    for (const UmeLayout::Column &c : m_layout.columns()) {
        const int blockStart = c.block.position();
        const int blockEnd = blockStart + c.block.length() - 1;
        if (blockEnd < selStart || blockStart > selEnd)
            continue;

        QTextLayout *lay = c.block.layout();
        if (!lay || c.lineIndex >= lay->lineCount())
            continue;
        const QTextLine line = lay->lineAt(c.lineIndex);

        const int a = qMax(selStart - blockStart, line.textStart());
        const int b = qMin(selEnd - blockStart, line.textStart() + line.textLength());
        if (b <= a)
            continue;

        const QRectF r = columnDocRect(c);
        const qreal y0 = r.top() + line.cursorToX(a) * kPxToPt;
        const qreal y1 = r.top() + line.cursorToX(b) * kPxToPt;
        /* 高亮贴住墨迹：字形画在 [left+pad, left+pad+inkW] 这一段，
           高亮跟它对齐才不会左右各空一条。 */
        const qreal x0 = columnInkLeft(c);
        out.append(QRectF(QPointF(x0, y0), QPointF(x0 + c.inkW, y1)));
    }
    return out;
}

/* ---------------- 光标 ---------------- */

void UmeView::setTextCursor(const QTextCursor &c)
{
    UME_LOG("cursor", QStringLiteral("pos=%1 anchor=%2 sel=%3")
                          .arg(c.position()).arg(c.anchor())
                          .arg(int(c.hasSelection())));
    m_cursor = c;
    restartBlink();
    ensureCursorVisible();

    const int idx = columnIndexForCursor();
    emit cursorPositionChanged(m_cursor.blockNumber(),
                               idx < 0 ? 0 : m_layout.columns()[idx].colInPage);
    emit formatStateChanged();
    update();
}

void UmeView::restartBlink()
{
    m_blinkOn = true;
    m_blink.start();
}

void UmeView::ensureCursorVisible()
{
    const QRectF r = caretDocRect();
    if (!r.isValid())
        return;

    const qreal top = r.top() * m_zoom;
    const qreal bottom = r.bottom() * m_zoom;
    const qreal margin = 40.0;

    if (top - margin < m_scrollY)
        m_scrollY = qMax(0.0, top - margin);
    else if (bottom + margin > m_scrollY + height())
        m_scrollY = bottom + margin - height();

    m_scrollY = qBound(0.0, m_scrollY, qreal(m_vbar->maximum()));
    m_vbar->setValue(int(m_scrollY));
}

/* ---------------- 编辑 ---------------- */

void UmeView::insertTextAtCursor(const QString &text)
{
    if (!m_doc || text.isEmpty())
        return;
    UME_LOG("edit", QStringLiteral("insert pos=%1 len=%2 text=%3")
                        .arg(m_cursor.position()).arg(text.size())
                        .arg(umeLogEsc(text)));
    m_cursor.insertText(text, m_baseFormat);
    afterEdit();
}

void UmeView::deleteChar(bool forward)
{
    if (!m_doc)
        return;
    UME_LOG("edit", QStringLiteral("delete pos=%1 forward=%2 sel=%3")
                        .arg(m_cursor.position()).arg(int(forward))
                        .arg(int(m_cursor.hasSelection())));
    if (m_cursor.hasSelection()) {
        m_cursor.removeSelectedText();
    } else if (forward) {
        m_cursor.deleteChar();
    } else {
        m_cursor.deletePreviousChar();
    }
    afterEdit();
}

void UmeView::insertParagraph()
{
    if (!m_doc)
        return;
    UME_LOG("edit", QStringLiteral("insertBlock pos=%1").arg(m_cursor.position()));
    m_cursor.insertBlock(QTextBlockFormat(), m_baseFormat);
    afterEdit();
}

void UmeView::afterEdit()
{
    /* 文档变了就得重排：M2 先整篇重排（文档规模不大），
       以后按脏块增量重排 —— 接口不用改。 */
    relayout();
    restartBlink();
    ensureCursorVisible();
    emit documentEdited();
    update();
}

/* ---------------- 键盘 ---------------- */

void UmeView::moveVertical(int dir, bool extend)
{
    QTextCursor c = m_cursor;
    c.movePosition(dir < 0 ? QTextCursor::PreviousCharacter
                           : QTextCursor::NextCharacter,
                   extend ? QTextCursor::KeepAnchor : QTextCursor::MoveAnchor);
    setTextCursor(c);
}

void UmeView::moveColumn(int dir, bool extend)
{
    const int idx = columnIndexForCursor();
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    if (idx < 0 || cols.isEmpty())
        return;

    const int target = idx + dir;
    if (target < 0 || target >= cols.size())
        return;

    const QRectF dst = columnDocRect(cols[target]);
    const qreal y = qBound(dst.top(), caretDocRect().top(), dst.bottom() - 1.0);

    QTextCursor c = cursorAtDocPos(QPointF(dst.left() + 1.0, y));
    if (extend)
        c.setPosition(c.position(), QTextCursor::KeepAnchor);
    setTextCursor(c);
}

void UmeView::moveToColumnEdge(bool toEnd, bool extend)
{
    const int idx = columnIndexForCursor();
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    if (idx < 0)
        return;

    const UmeLayout::Column &c = cols[idx];
    QTextLayout *lay = c.block.layout();
    if (!lay || c.lineIndex >= lay->lineCount())
        return;
    const QTextLine line = lay->lineAt(c.lineIndex);
    const int pos = c.block.position()
                    + (toEnd ? line.textStart() + line.textLength() : line.textStart());

    QTextCursor cur = m_cursor;
    cur.setPosition(pos, extend ? QTextCursor::KeepAnchor : QTextCursor::MoveAnchor);
    setTextCursor(cur);
}

void UmeView::keyPressEvent(QKeyEvent *event)
{
    if (!m_doc) {
        QWidget::keyPressEvent(event);
        return;
    }

    const bool shift = event->modifiers() & Qt::ShiftModifier;
    const bool ctrl = event->modifiers() & Qt::ControlModifier;

    if (ctrl) {
        switch (event->key()) {
        case Qt::Key_Z:
            if (shift)
                m_doc->redo();
            else
                m_doc->undo();
            afterEdit();
            event->accept();
            return;
        case Qt::Key_Y:
            m_doc->redo();
            afterEdit();
            event->accept();
            return;
        case Qt::Key_A: {
            QTextCursor c(m_doc);
            c.select(QTextCursor::Document);
            setTextCursor(c);
            event->accept();
            return;
        }
        case Qt::Key_C:
        case Qt::Key_X: {
            if (!m_cursor.hasSelection())
                return;
            QMimeData *md = new QMimeData;
            md->setText(m_cursor.selection().toPlainText());
            md->setHtml(m_cursor.selection().toHtml());
            QApplication::clipboard()->setMimeData(md);
            if (event->key() == Qt::Key_X) {
                m_cursor.removeSelectedText();
                afterEdit();
            }
            event->accept();
            return;
        }
        case Qt::Key_V: {
            const QMimeData *md = QApplication::clipboard()->mimeData();
            if (!md)
                return;
            if (md->hasHtml())
                m_cursor.insertHtml(md->html());
            else if (md->hasText())
                m_cursor.insertText(md->text());
            afterEdit();
            event->accept();
            return;
        }
        default:
            break;
        }
    }

    switch (event->key()) {
    case Qt::Key_Up:
        moveVertical(-1, shift);
        event->accept();
        return;
    case Qt::Key_Down:
        moveVertical(+1, shift);
        event->accept();
        return;
    case Qt::Key_Left:
        moveColumn(-1, shift);
        event->accept();
        return;
    case Qt::Key_Right:
        moveColumn(+1, shift);
        event->accept();
        return;
    case Qt::Key_Home:
        moveToColumnEdge(false, shift);
        event->accept();
        return;
    case Qt::Key_End:
        moveToColumnEdge(true, shift);
        event->accept();
        return;
    case Qt::Key_Backspace:
        deleteChar(false);
        event->accept();
        return;
    case Qt::Key_Delete:
        deleteChar(true);
        event->accept();
        return;
    case Qt::Key_Return:
    case Qt::Key_Enter:
        insertParagraph();
        event->accept();
        return;
    case Qt::Key_PageUp:
        m_scrollY = qMax(0.0, m_scrollY - height() * 0.9);
        m_vbar->setValue(int(m_scrollY));
        event->accept();
        return;
    case Qt::Key_PageDown:
        m_scrollY = qMin(qreal(m_vbar->maximum()), m_scrollY + height() * 0.9);
        m_vbar->setValue(int(m_scrollY));
        event->accept();
        return;
    default:
        break;
    }

    /* 普通字符（含空格、标点、蒙文、汉字） */
    const QString text = event->text();
    if (!text.isEmpty() && text.at(0).isPrint()) {
        insertTextAtCursor(text);
        event->accept();
        return;
    }

    QWidget::keyPressEvent(event);
}

/* ---------------- 输入法 ---------------- */

void UmeView::inputMethodEvent(QInputMethodEvent *event)
{
    UME_LOG("ime", QStringLiteral("preedit=%1 commit=%2")
                       .arg(umeLogEsc(event->preeditString()))
                       .arg(umeLogEsc(event->commitString())));
    if (!event->commitString().isEmpty())
        insertTextAtCursor(event->commitString());

    m_preedit = event->preeditString();   // M3 再做带下划线的浮层
    event->accept();
}

QVariant UmeView::inputMethodQuery(Qt::InputMethodQuery query) const
{
    switch (query) {
    case Qt::ImEnabled:
        return true;
    case Qt::ImCursorRectangle: {
        const QRectF r = caretDocRect();
        return QRect(int(r.left() * m_zoom),
                     int((r.top() * m_zoom) - m_scrollY),
                     int(m_inkW * m_zoom), 2);
    }
    case Qt::ImSurroundingText:
        return m_doc ? m_doc->toPlainText() : QString();
    case Qt::ImCursorPosition:
        return m_cursor.position();
    case Qt::ImAnchorPosition:
        return m_cursor.anchor();
    default:
        return QVariant();
    }
}

/* ---------------- 绘制 ---------------- */

void UmeView::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    if (!m_settings)
        return;

    if (m_doc && m_doc->revision() != m_paintedRevision) {
        m_paintedRevision = m_doc->revision();
        const int cols = m_layout.columns().size();
        QString first = QStringLiteral("-");
        if (cols > 0) {
            const QRectF r = columnDocRect(m_layout.columns().first());
            first = QStringLiteral("%1,%2 w%3").arg(r.left(), 0, 'f', 1)
                        .arg(r.top(), 0, 'f', 1).arg(r.width(), 0, 'f', 1);
        }
        UME_LOG("paint", QStringLiteral("rev=%1 cols=%2 blocks=%3 firstCol=%4")
                             .arg(m_doc->revision())
                             .arg(cols)
                             .arg(m_doc->blockCount())
                             .arg(first));
    }

    QPainter p(this);
    p.fillRect(rect(), QColor(0x6e, 0x6e, 0x72));

    p.save();
    p.scale(m_zoom, m_zoom);
    p.translate(0.0, -m_scrollY / m_zoom);

    const PageSetup &page = m_settings->page();
    for (int i = 0; i < m_layout.pageCount(); ++i) {
        const QRectF r = UmeLayout::pageRect(page, i);
        p.setPen(Qt::NoPen);
        p.setBrush(QColor(0, 0, 0, 40));
        p.drawRect(r.translated(0, 2));
        p.setBrush(Qt::white);
        p.drawRect(r);
    }

    if (m_settings->marginGuides())
        paintGuides(p);

    paintSelection(p);
    paintDocument(p);
    paintCaret(p);
    p.restore();
}

void UmeView::paintGuides(QPainter &p) const
{
    QPen pen(QColor(0x2f, 0x6f, 0xd0, 90));
    pen.setStyle(Qt::DashLine);
    pen.setWidthF(0.8);
    p.setPen(pen);
    p.setBrush(Qt::NoBrush);

    const PageSetup &page = m_settings->page();
    for (int i = 0; i < m_layout.pageCount(); ++i) {
        const QRectF r = UmeLayout::pageRect(page, i);
        p.drawRect(page.textArea().translated(r.topLeft()));
    }
}

void UmeView::paintSelection(QPainter &p) const
{
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(0x33, 0x99, 0xff, 90));
    for (const QRectF &r : selectionDocRects())
        p.drawRect(r);
}

void UmeView::paintDocument(QPainter &p) const
{
    p.setRenderHint(QPainter::TextAntialiasing, true);
    p.setRenderHint(QPainter::Antialiasing, true);

    for (const UmeLayout::Column &c : m_layout.columns()) {
        QTextLayout *lay = c.block.layout();
        if (!lay || c.lineIndex >= lay->lineCount())
            continue;

        const QTextLine line = lay->lineAt(c.lineIndex);
        const QRectF r = columnDocRect(c);

        /* rotate(90) 后：局部 x → 屏幕 +y（沿列向下），局部 y → 屏幕 −x。
           基线放在「列左 + 留白 + 本列最大 ascent」处，墨迹不会越界。 */
        const qreal baseX = columnInkLeft(c);
        const qreal baseY = r.top();

        /* 格式区间 → 行内 x 区间，这样能按「字形在行里的位置」取颜色。
           （glyph run 不直接给字符下标，按 x 反查最省事。） */
        struct FmtSpan { qreal x0; qreal x1; QTextCharFormat fmt; };
        QVector<FmtSpan> spans;
        for (const QTextLayout::FormatRange &fr : lay->formats()) {
            const qreal x0 = line.cursorToX(fr.start);
            const qreal x1 = line.cursorToX(fr.start + fr.length);
            if (x1 > x0)
                spans.append({x0, x1, fr.format});
        }
        auto fmtAt = [&spans, this](qreal x) {
            for (const FmtSpan &s : spans) {
                if (x >= s.x0 - 0.01 && x < s.x1)
                    return s.fmt.font();
            }
            QFont f(QStringLiteral("Noto Sans Mongolian"));
            f.setPointSizeF(m_metricsPt);
            return f;
        };
        auto colorAt = [&spans](qreal x) {
            for (const FmtSpan &s : spans) {
                if (x >= s.x0 - 0.01 && x < s.x1)
                    return s.fmt.foreground().color();
            }
            return QColor(0x11, 0x11, 0x11);
        };

        /* 默认的检索标志里没有 rawFont，拿到的 run 画不出东西 —— 必须显式要。 */
        const QList<QGlyphRun> runs = line.glyphRuns(
            -1, -1,
            QTextLayout::RetrieveGlyphIndexes | QTextLayout::RetrieveGlyphPositions
                | QTextLayout::RetrieveStringIndexes | QTextLayout::RetrieveString);
        for (const QGlyphRun &gr : runs) {
            const QRawFont rf = gr.rawFont();
            const QList<quint32> glyphs = gr.glyphIndexes();
            const QList<QPointF> pos = gr.positions();
            const QString src = gr.sourceString();

            /* 整段都是「直立类」才直立。判断依据不是 sourceString
               （Qt 常常给空串），而是「这个 run 落在哪个字符上」——
               用它在行内的 x 反查。 */
            const QString blockText = c.block.text();
            auto charAtLineX = [&](qreal x) {
                const int p = line.xToCursor(x + 0.01);
                return (p >= 0 && p < blockText.size()) ? blockText.at(p) : QChar();
            };
            bool upright = false;
            if (!glyphs.isEmpty() && !pos.isEmpty()) {
                upright = isUprightScript(charAtLineX(pos.first().x()));
            }

            for (int k = 0; k < glyphs.size(); ++k) {
                const QPointF gp = k < pos.size() ? pos.at(k) : QPointF(0, 0);

                /* 本槽位的长度：用下一个字形的推进量，最后一个用行宽补 */
                qreal slot = 0.0;
                if (k + 1 < pos.size()) {
                    slot = pos.at(k + 1).x() - gp.x();
                } else {
                    /* 最后一个字形：剩余长度要用「实际文字宽度」算。
                       line.width() 是换行宽度（整列高），拿它当槽位会把
                       最后一个字推到整列底下 —— 就是「古」跑到很下面那个 bug。 */
                    slot = line.naturalTextWidth() - gp.x();
                }
                if (slot <= 0.5)
                    slot = rf.advancesForGlyphIndexes(QList<quint32>{glyphs.at(k)})
                               .value(0).x();

                const QColor ink = colorAt(gp.x());

                if (upright) {
                    /* 直立字：位置与格子都从「字符区间」推出 ——
                       用 cursorToX(字符起点) 和 cursorToX(字符终点)，
                       同一把尺子量出来，相邻两字必然首尾相接，不会重叠。 */
                    const int idx = line.xToCursor(gp.x() + 0.01);
                    const QChar ch = (idx >= 0 && idx < blockText.size())
                                         ? blockText.at(idx)
                                         : QChar();
                    if (ch.isNull())
                        continue;

                    const qreal y0 = line.cursorToX(idx) * kPxToPt;
                    const qreal y1 = line.cursorToX(idx + 1) * kPxToPt;
                    const qreal cellH = qMax(y1 - y0, 4.0);

                    /* 字号直接取「布局分配的格宽」：这样字形永远和步进一样大，
                       不管这个字是主字体给的还是回退字体给的，都不会重叠。
                       （格子来自 cursorToX 的字符区间，与光标/选区同一把尺子。） */
                    QFont f = fmtAt(gp.x());
                    f.setPixelSize(qMax(1, qRound(cellH)));

                    p.save();
                    p.setFont(f);
                    p.setPen(ink);
                    p.drawText(QRectF(r.left() + (r.width() - cellH) / 2.0,
                                      baseY + y0, cellH, cellH),
                               Qt::AlignCenter, QString(ch));
                    p.restore();
                } else {
                    /* 旋转支：同样用轮廓画。QPainter::drawGlyphRun 在离屏渲染里
                       不出墨（实测墨迹为 0），轮廓法两条路一致，颜色也好控。 */
                    const QPainterPath path = rf.pathForGlyph(glyphs.at(k));
                    if (path.isEmpty())
                        continue;
                    p.save();
                    p.translate(baseX, baseY);
                    p.rotate(90);
                    p.scale(kPxToPt, kPxToPt);
                    p.translate(gp.x(), 0);
                    p.fillPath(path, ink);
                    p.restore();
                }
            }
        }
    }
}

void UmeView::paintCaret(QPainter &p) const
{
    if (!hasFocus() || !m_blinkOn)
        return;
    const QRectF r = caretDocRect();
    if (r.isNull())
        return;

    p.setPen(QPen(QColor(0x11, 0x11, 0x11), 2.0));
    const qreal y = r.center().y();
    p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y));
}

void UmeView::paintPreedit(QPainter &p) const
{
    Q_UNUSED(p);   // M3：带下划线的预编辑浮层
}

/* ---------------- 鼠标 ---------------- */

void UmeView::mousePressEvent(QMouseEvent *event)
{
    if (event->button() != Qt::LeftButton) {
        QWidget::mousePressEvent(event);
        return;
    }
    setFocus();

    QTextCursor cur = cursorAtDocPos(docPosFromWidget(event->position()));
    if (event->modifiers() & Qt::ShiftModifier)
        cur.setPosition(cur.position(), QTextCursor::KeepAnchor);
    setTextCursor(cur);

    /* 记住这次按下的位置当锚点 —— 拖曳时的选区是「锚点 → 当前点」，
       不是「文档开头 → 当前点」。 */
    m_dragAnchor = cur.anchor();
    m_dragging = true;
    event->accept();
}

void UmeView::mouseMoveEvent(QMouseEvent *event)
{
    if (!m_dragging || !m_doc) {
        QWidget::mouseMoveEvent(event);
        return;
    }
    const QTextCursor hit = cursorAtDocPos(docPosFromWidget(event->position()));
    QTextCursor cur(m_doc);
    /* 新 cursor 的 anchor 默认在文档开头，必须先落锚点再设活动端，
       否则会变成「从第 1 个字一直选到这里」。 */
    cur.setPosition(m_dragAnchor >= 0 ? m_dragAnchor : hit.position());
    cur.setPosition(hit.position(), QTextCursor::KeepAnchor);
    m_cursor = cur;
    emit formatStateChanged();
    ensureCursorVisible();
    update();
    event->accept();
}

void UmeView::mouseReleaseEvent(QMouseEvent *event)
{
    m_dragging = false;
    m_dragAnchor = -1;
    QWidget::mouseReleaseEvent(event);
}

void UmeView::mouseDoubleClickEvent(QMouseEvent *event)
{
    QTextCursor c = cursorAtDocPos(docPosFromWidget(event->position()));
    c.select(QTextCursor::WordUnderCursor);
    setTextCursor(c);
    event->accept();
}

void UmeView::wheelEvent(QWheelEvent *event)
{
    if (event->modifiers() & Qt::ControlModifier) {
        const qreal step = event->angleDelta().y() > 0 ? 1.1 : 1.0 / 1.1;
        setZoom(m_zoom * step);
        event->accept();
        return;
    }
    m_scrollY = qBound(0.0, m_scrollY - event->angleDelta().y(), qreal(m_vbar->maximum()));
    m_vbar->setValue(int(m_scrollY));
    event->accept();
}

void UmeView::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
    updateScrollBars();
}

void UmeView::updateScrollBars()
{
    if (!m_vbar)
        return;
    const qreal contentH = m_layout.contentHeight() * m_zoom;
    const int maxScroll = qMax(0, int(contentH - height()));
    m_vbar->setRange(0, maxScroll);
    m_vbar->setPageStep(qMax(1, height()));
    const int w = m_vbar->sizeHint().width();
    m_vbar->setGeometry(width() - w, 0, w, height());
    if (m_scrollY > maxScroll)
        m_scrollY = maxScroll;
    m_vbar->setValue(int(m_scrollY));
}

QSize UmeView::sizeHint() const
{
    const qreal w = m_settings ? m_settings->page().paper.width() : 595.0;
    return QSize(int(w * m_zoom) + 40, 900);
}

/* ---------------- 竖排方向 ---------------- */

QStringList UmeView::fallbackFamilies(const QString &primary)
{
    /* 只把「本机真的装了」的字体加进栈里：硬写一个不存在的族名，
       Qt 会退回豆腐块，还白搭一次字体查找。 */
    static const QStringList installed = QFontDatabase::families();

    QStringList fams{primary};
    const QStringList cjk = {QStringLiteral("SimSun"),
                             QStringLiteral("Microsoft YaHei"),
                             QStringLiteral("Noto Sans CJK SC"),
                             QStringLiteral("Source Han Sans SC")};
    const QStringList latin = {QStringLiteral("Times New Roman"),
                               QStringLiteral("Noto Serif")};

    for (const QString &f : cjk) {
        if (installed.contains(f)) {
            fams << f;
            break;
        }
    }
    for (const QString &f : latin) {
        if (installed.contains(f)) {
            fams << f;
            break;
        }
    }
    return fams;
}

bool UmeView::isUprightScript(QChar ch)
{
    switch (ch.script()) {
    case QChar::Script_Han:
    case QChar::Script_Hiragana:
    case QChar::Script_Katakana:
    case QChar::Script_Hangul:
    case QChar::Script_Bopomofo:
        return true;
    default:
        /* Common 类（括号、破折号、引号、空格）算旋转 —— 竖排里它们转着排 */
        return false;
    }
}

/* ---------------- 探针 ---------------- */

QString UmeView::metricsProbe() const
{
    QString out = QStringLiteral("ascent=%1 descent=%2 inkAbove=%3 inkBelow=%4 pitch=%5")
                      .arg(m_ascent, 0, 'f', 1)
                      .arg(m_descent, 0, 'f', 1)
                      .arg(m_inkAbove, 0, 'f', 1)
                      .arg(m_inkBelow, 0, 'f', 1)
                      .arg(m_colPitch, 0, 'f', 1);
    if (!m_layout.columns().isEmpty()) {
        const QRectF r = columnDocRect(m_layout.columns().first());
        out += QStringLiteral("  firstColumn.left=%1").arg(r.left(), 0, 'f', 1);
    }
    return out;
}

QString UmeView::glyphProbe() const
{
    QStringList out;
    if (!m_doc)
        return QStringLiteral("no doc");
    const QTextBlock b = m_doc->begin();
    QTextLayout *lay = b.layout();
    if (!lay || lay->lineCount() == 0)
        return QStringLiteral("no line");
    const QTextLine line = lay->lineAt(0);
    const QList<QGlyphRun> runs = line.glyphRuns(
        -1, -1,
        QTextLayout::RetrieveGlyphIndexes | QTextLayout::RetrieveGlyphPositions
            | QTextLayout::RetrieveStringIndexes | QTextLayout::RetrieveString);

    out << QStringLiteral("runs=%1 lineWidth=%2").arg(runs.size()).arg(line.width());
    for (const QGlyphRun &gr : runs) {
        const QRawFont rf = gr.rawFont();
        QStringList ps;
        const QList<QPointF> pos = gr.positions();
        for (int i = 0; i < pos.size() && i < 4; ++i)
            ps << QStringLiteral("%1").arg(pos.at(i).x(), 0, 'f', 1);
        out << QStringLiteral("[%1 glyphs=%2 rf=%3 pos=%4]")
                   .arg(gr.sourceString().isEmpty() ? QStringLiteral("?")
                                                    : gr.sourceString())
                   .arg(gr.glyphIndexes().size())
                   .arg(rf.familyName())
                   .arg(ps.join(QLatin1Char(',')));
    }
    return out.join(QLatin1Char(' '));
}

QString UmeView::columnsProbe(int n) const
{
    QStringList out;
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    for (int i = 0; i < cols.size() && i < n; ++i) {
        const QRectF r = columnDocRect(cols[i]);
        out << QStringLiteral("%1:[left %2, w %3]")
                   .arg(i)
                   .arg(r.left(), 0, 'f', 1)
                   .arg(r.width(), 0, 'f', 1);
    }
    return out.join(QStringLiteral("  "));
}

/* ---------------- 离屏渲染 ---------------- */

QImage UmeView::renderPageImage(int page, qreal scale, bool withCaret) const
{
    if (!m_settings)
        return QImage();

    const PageSetup &ps = m_settings->page();
    const QRectF pr = UmeLayout::pageRect(ps, page);
    QImage img(QSize(int(pr.width() * scale), int(pr.height() * scale)),
               QImage::Format_ARGB32_Premultiplied);
    img.fill(Qt::white);

    QPainter p(&img);
    p.scale(scale, scale);
    p.translate(-pr.topLeft());
    p.setRenderHint(QPainter::TextAntialiasing, true);
    p.setRenderHint(QPainter::Antialiasing, true);

    if (m_settings->marginGuides()) {
        QPen pen(QColor(0x2f, 0x6f, 0xd0, 90));
        pen.setStyle(Qt::DashLine);
        pen.setWidthF(0.8);
        p.setPen(pen);
        p.setBrush(Qt::NoBrush);
        p.drawRect(ps.textArea());
    }

    paintSelection(p);
    paintDocument(p);

    if (withCaret) {
        const QRectF cr = caretDocRect();
        if (!cr.isNull()) {
            p.setPen(QPen(QColor(0x11, 0x11, 0x11), 2.0));
            const qreal y = cr.center().y();
            p.drawLine(QPointF(cr.left(), y), QPointF(cr.right(), y));
        }
    }

    p.end();
    return img;
}

QImage UmeView::renderAllPages(qreal scale) const
{
    if (!m_settings)
        return QImage();

    const PageSetup &ps = m_settings->page();
    const int n = m_layout.pageCount();
    const qreal totalH = m_layout.contentHeight();

    QImage img(QSize(int(ps.paper.width() * scale), int(totalH * scale)),
               QImage::Format_ARGB32_Premultiplied);
    img.fill(QColor(0x6e, 0x6e, 0x72));

    QPainter p(&img);
    p.scale(scale, scale);
    p.setRenderHint(QPainter::TextAntialiasing, true);

    for (int i = 0; i < n; ++i)
        p.fillRect(UmeLayout::pageRect(ps, i), Qt::white);

    paintSelection(p);
    paintDocument(p);

    const QRectF cr = caretDocRect();
    if (!cr.isNull()) {
        p.setPen(QPen(QColor(0x11, 0x11, 0x11), 2.0));
        const qreal y = cr.center().y();
        p.drawLine(QPointF(cr.left(), y), QPointF(cr.right(), y));
    }

    p.end();
    return img;
}
