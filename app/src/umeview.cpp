#include "umeview.h"

#include "umesettings.h"
#include "umedoc.h"
#include "umeicons.h"
#include "umehit.h"
#include "umeinteract.h"
#include "umelog.h"

#include <QApplication>
#include <QClipboard>
#include <QCoreApplication>
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
#include <QTextTable>
#include <QDesktopServices>
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
    setCursor(UmeIcons::textIBeam());

    setFocusPolicy(Qt::StrongFocus);
    setAttribute(Qt::WA_InputMethodEnabled, true);   // 输入法要能往这里送
    setMouseTracking(true);

    m_vbar = new QScrollBar(Qt::Vertical, this);
    m_vbar->setSingleStep(20);
    connect(m_vbar, &QScrollBar::valueChanged, this, [this](int v) {
        m_scrollY = v;
        update();
    });

    /* 横向滚动条：多页并排时内容会宽于窗口，没有它右侧永远够不到 */
    m_hbar = new QScrollBar(Qt::Horizontal, this);
    m_hbar->setSingleStep(20);
    connect(m_hbar, &QScrollBar::valueChanged, this, [this](int v) {
        m_scrollX = v;
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

void UmeView::adoptColorAtCursor()
{
    if (!m_doc || m_cursor.hasSelection())
        return;

    /* 只收颜色，不动字体字号：字体要按脚本自动分配（见 insertTextByScript），
       跟着光标处的字走会把「汉字用中文字体」这条规则打乱。 */
    const QTextCharFormat at = m_cursor.charFormat();
    QColor col = at.foreground().color();
    if (!col.isValid())
        return;
    if (m_baseFormat.foreground().color() == col)
        return;

    m_baseFormat.setForeground(col);
    emit formatStateChanged();
}

/* ---------------- 宽对象（表格 / 图片） ---------------- */

UmeDoc::WideProps UmeView::currentWideObject() const
{
    if (!m_doc)
        return {};

    /* 优先级：光标所在的宽对象 > 已选中的宽对象。
       光标在表格里时必须是「这张表」，不能还停在之前选中的图片上；
       而插图后光标会落在图片之后的段落里，此时才回退到选中项。 */
    if (const QTextTable *table = m_cursor.currentTable()) {
        const QTextBlock first = table->firstCursorPosition().block();
        UmeDoc::WideProps p = UmeDoc::wideProps(first);
        if (!p.isValid()) {
            p.kind = UmeDoc::WideKind::Table;
            p.span = qBound(1, table->columns(), 12);
            p.heightPt = qMax(40.0, table->rows() * 28.0);
        }
        return p;
    }
    const UmeDoc::WideProps onCursor = UmeDoc::wideProps(m_cursor.block());
    if (onCursor.isValid())
        return onCursor;

    if (const UmeLayout::WideItem *item = selectedWideItem())
        return UmeDoc::wideProps(item->block);

    return onCursor;
}

void UmeView::applyWideObject(UmeDoc::WideProps props)
{
    if (!m_doc)
        return;

    QTextBlock target;
    if (const QTextTable *table = m_cursor.currentTable())
        target = table->firstCursorPosition().block();       /* 光标所在对象优先 */
    else if (UmeDoc::isWideBlock(m_cursor.block()))
        target = m_cursor.block();
    else if (const UmeLayout::WideItem *item = selectedWideItem())
        target = item->block;                                /* 否则用选中项 */
    else
        target = m_cursor.block();
    if (!target.isValid())
        return;

    /* 防误擦：kind 为空说明调用方的属性没取到（比如光标不在对象里）。
       直接写下去会把「宽对象」标记抹掉，整张表会散成普通段落。 */
    if (props.kind == UmeDoc::WideKind::None) {
        UME_LOG("wide", QStringLiteral("apply ignored: kind=None (refused)"));
        return;
    }

    /* 钳制：夸张的值会破坏整篇布局（跨列超过页宽、高度超过正文区、
       旋转任意角度导致命中测试失效） */
    {
        const QRectF area = m_settings ? m_settings->page().textArea() : QRectF();
        const qreal strip = qMax(8.0, m_minWidthForDrag);
        UmeDoc::WideProps bounded = props;
        const int maxSpan = area.isValid() ? qMax(1, int(area.width() / strip))
                                           : maxSpanForPage();
        bounded.span = qBound(1, props.span, qMin(maxSpan, 48));
        const qreal maxH = area.isValid() ? area.height() : 800.0;
        /* 表格可以跨页：高度上限给到 40 页，否则永远切不出第二段。
           图片仍然限一页内（跨页的图没有意义）。 */
        const qreal heightCap = (props.kind == UmeDoc::WideKind::Table)
                                    ? maxH * 40.0
                                    : maxH;
        bounded.heightPt = qBound(8.0, props.heightPt, heightCap);
        bounded.offsetPt = qBound(-maxH, props.offsetPt, maxH);
        /* 表格不旋转 */
        bounded.rotation = (props.kind == UmeDoc::WideKind::Table)
                               ? 0.0
                               : std::fmod(props.rotation, 360.0);
        if (bounded != props) {
            UME_LOG("wide", QStringLiteral("clamped span %1→%2 h %3→%4")
                                 .arg(props.span).arg(bounded.span)
                                 .arg(props.heightPt, 0, 'f', 1)
                                 .arg(bounded.heightPt, 0, 'f', 1));
            props = bounded;
        }
    }

    if (UME_LOG_EVERY("wide", 120))
        UME_LOG("wide", QStringLiteral("apply kind=%1 wrap=%2 span=%3 h=%4 off=%5 rot=%6")
                        .arg(int(props.kind)).arg(int(props.wrap))
                        .arg(props.span).arg(props.heightPt, 0, 'f', 1)
                        .arg(props.offsetPt, 0, 'f', 1).arg(props.rotation, 0, 'f', 1));
    UmeDoc::setWideProps(target, props);
    relayout();
    update();
    emit formatStateChanged();
}

void UmeView::nudgeWideObject(qreal dy)
{
    UmeDoc::WideProps p = currentWideObject();
    if (!p.isValid())
        return;
    p.offsetPt = qBound(-4000.0, p.offsetPt + dy, 4000.0);
    applyWideObject(p);
}

void UmeView::resizeWideObject(qreal newHeightPt, bool keepAspect)
{
    UmeDoc::WideProps p = currentWideObject();
    if (!p.isValid())
        return;

    const qreal h = qBound(8.0, newHeightPt, 4000.0);
    if (keepAspect && p.naturalH > 0.0) {
        const qreal ratio = p.naturalW / p.naturalH;
        const qreal w = h * ratio;
        const qreal strip = (m_colPitch > 0.0) ? m_colPitch : 20.0;
        p.span = qBound(1, qRound(w / strip), maxSpanForPage());
    }
    p.heightPt = h;
    applyWideObject(p);
}

void UmeView::changeTableRows(int delta)
{
    UME_LOG("wide", QStringLiteral("table rows %1").arg(delta));
    QTextCursor c = m_cursor;
    if (UmeDoc::changeTableRows(c, delta)) {
        m_cursor = c;
        afterEdit();
    }
}

void UmeView::changeTableColumns(int delta)
{
    UME_LOG("wide", QStringLiteral("table cols %1").arg(delta));
    QTextCursor c = m_cursor;
    if (!UmeDoc::changeTableColumns(c, delta))
        return;

    /* 跨列数跟着表格列数走 */
    const QPair<int, int> size = UmeDoc::tableSize(c);
    UmeDoc::WideProps p = currentWideObject();
    if (p.isValid()) {
        p.span = qBound(1, size.second, 12);
        applyWideObject(p);
    }
    m_cursor = c;
    afterEdit();
}

/* ---------------- 宽对象：绘制 ---------------- */

const QImage &UmeView::imageFor(const QString &path) const
{
    auto it = m_images.find(path);
    if (it != m_images.end())
        return it.value();

    QImage img(path);
    if (img.isNull())
        UME_LOG("image", QStringLiteral("load failed: %1").arg(path));
    it = m_images.insert(path, img);
    return it.value();
}

int UmeView::selectedWideObject() const
{
    const QVector<UmeLayout::WideItem> &items = m_layout.wideItems();
    for (int i = 0; i < items.size(); ++i) {
        if (items.at(i).block.position() == m_selectedWideBlock)
            return i;
    }
    return -1;
}

const UmeLayout::WideItem *UmeView::selectedWideItem() const
{
    if (m_selectedWideBlock < 0)
        return nullptr;
    for (const UmeLayout::WideItem &it : m_layout.wideItems()) {
        if (it.block.position() == m_selectedWideBlock)
            return &it;
    }
    return nullptr;
}

void UmeView::paintWideItems(QPainter &p) const
{
    for (const UmeLayout::WideItem &item : m_layout.wideItems()) {
        /* 盒子是页内坐标，画之前加上该页原点 —— 否则第二页的对象会画到第一页上 */
        const QRectF r = m_layout.docRect(item);

        if (item.props.kind == UmeDoc::WideKind::Table) {
            /* 表格：外框 + 网格 + 单元格文字（竖排） */
            p.save();
            p.setPen(QPen(QColor(0x88, 0x88, 0x88), 0.8));
            p.setBrush(Qt::NoBrush);
            p.drawRect(r);

            QTextCursor bc(item.block);
            QTextTable *table = bc.currentTable();
            if (table) {
                const int total = qMax(1, table->rows());
                const int cols = qMax(1, table->columns());
                /* 跨页片段只画本片段的行：按全表行数等分会把格子压扁 */
                const int firstRow = qBound(0, item.rowFirst, total - 1);
                const int lastRow = (item.rowLast < 0) ? total - 1
                                                       : qBound(0, item.rowLast, total - 1);
                const int shown = qMax(1, lastRow - firstRow + 1);

                for (int i = 1; i < shown; ++i) {
                    const qreal y = r.top() + r.height() * i / shown;
                    p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y));
                }
                for (int j = 1; j < cols; ++j) {
                    const qreal x = r.left() + r.width() * j / cols;
                    p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()));
                }
            }
            p.restore();

            paintTableCells(p, item, r);
            continue;
        }

        if (item.props.kind == UmeDoc::WideKind::Image && !item.props.imagePath.isEmpty()) {
            const QImage &img = imageFor(item.props.imagePath);
            if (img.isNull())
                continue;
            p.save();
            p.setRenderHint(QPainter::SmoothPixmapTransform, true);
            p.translate(r.center());
            if (!qFuzzyIsNull(item.props.rotation))
                p.rotate(item.props.rotation);
            if (item.props.flipH || item.props.flipV)
                p.scale(item.props.flipH ? -1.0 : 1.0, item.props.flipV ? -1.0 : 1.0);
            const QRectF target(-r.width() / 2.0, -r.height() / 2.0, r.width(), r.height());
            p.drawImage(target, img);
            p.restore();
        }
    }

    /* 控制手柄：只有选中图片/表格时才画 */
    const UmeLayout::WideItem *sel = selectedWideItem();
    if (!sel)
        return;

    const QVector<QRectF> hs = wideHandles(*sel);
    p.save();
    p.setBrush(QColor(255, 255, 255));
    p.setPen(QPen(QColor(0x0b, 0x67, 0xc2), 1.0));
    for (const QRectF &h : hs)
        p.drawRect(h);
    p.restore();
}

void UmeView::setLayoutFormats(QTextLayout *lay, const QTextBlock &block)
{
    if (!lay || !block.isValid())
        return;

    QList<QTextLayout::FormatRange> ranges;
    for (auto it = block.begin(); !it.atEnd(); ++it) {
        const QTextFragment frag = it.fragment();
        if (!frag.isValid())
            continue;
        QTextLayout::FormatRange r;
        r.start = frag.position() - block.position();
        r.length = frag.length();
        r.format = frag.charFormat();
        ranges.append(r);
    }
    lay->setFormats(ranges);
}

void UmeView::drawVerticalLine(QPainter &p, const QTextLayout *lay, const QTextLine &line,
                               const QTextBlock &block, const QRectF &r,
                               qreal baseX, qreal baseY, const QColor &fallbackInk) const
{
    if (!lay || !line.isValid() || !block.isValid())
        return;

    struct FmtSpan { qreal x0; qreal x1; QTextCharFormat fmt; };
    QVector<FmtSpan> spans;
    for (const QTextLayout::FormatRange &fr : lay->formats()) {
        const qreal x0 = line.cursorToX(fr.start);
        const qreal x1 = line.cursorToX(fr.start + fr.length);
        if (x1 > x0)
            spans.append({x0, x1, fr.format});
    }
    auto formatAt = [&spans](qreal x) -> QTextCharFormat {
        for (const FmtSpan &s : spans) {
            if (x >= s.x0 - 0.01 && x < s.x1)
                return s.fmt;
        }
        return QTextCharFormat();
    };
    auto colorAt = [&formatAt, fallbackInk](qreal x) {
        const QColor col = formatAt(x).foreground().color();
        return col.isValid() ? col : fallbackInk;
    };
    auto fmtAt = [&spans, this](qreal x) {
        for (const FmtSpan &s : spans) {
            if (x >= s.x0 - 0.01 && x < s.x1)
                return s.fmt.font();
        }
        QFont f(QStringLiteral("Noto Sans Mongolian"));
        f.setPointSizeF(m_metricsPt);
        return f;
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
            const QString blockText = block.text();
            auto charAtLineX = [&](qreal x) {
                const int p = line.xToCursor(x + 0.01);
                return (p >= 0 && p < blockText.size()) ? blockText.at(p) : QChar();
            };
            /* 直立与否必须逐字判：整段一判时，只要首字形落在空格/标点上，
               整段汉字就都被当成蒙文旋转了（实测「成吉思汗」就是这么躺倒的）。 */

            for (int k = 0; k < glyphs.size(); ++k) {
                const QPointF gp = k < pos.size() ? pos.at(k) : QPointF(0, 0);
                /* 该字形所在的字符：取格子中点反查（中点必定落在字符内部，
                   不像起点那样容易被舍到前一个字上）。 */
                /* 先算槽位（px），再用槽位中点反查字符 —— 中点必在字符内部，
                   单字形 run 也不会被判成前一个字。 */
                qreal slot = 0.0;
                if (k + 1 < pos.size()) {
                    slot = pos.at(k + 1).x() - gp.x();
                } else {
                    const qreal adv = rf.advancesForGlyphIndexes(
                                            QList<quint32>{glyphs.at(k)})
                                          .value(0).x();
                    const qreal remain = line.naturalTextWidth() - gp.x();
                    slot = (adv > 0.5) ? qMin(adv, qMax(remain, adv)) : remain;
                }
                if (slot <= 0.5)
                    slot = 19.0;   // 兜底：一个汉字宽（px）

                /* 取 0.35 而不是 0.5：正好落在字形「中点」时，
                   若该字形很窄，中点会压到下一个字符的起点上，
                   于是把下一字的汉字错判成这一格的内容（会画出一个小的重影）。 */
                const qreal midX = gp.x() + slot * 0.35;
                const QChar thisChar = charAtLineX(midX);
                const GlyphPlace place = placeFor(thisChar);
                const bool upright = place != GlyphPlace::Rotated;

                const QColor ink = colorAt(gp.x());

                /* 链接下划线：竖排里画成与列平行的细线，贴在墨迹左侧 */
                const QTextCharFormat gfmt = formatAt(gp.x());
                if (gfmt.fontUnderline() || gfmt.isAnchor()) {
                    const qreal ux = r.left() + UmeLayout::kPad - 1.2;
                    p.save();
                    p.setPen(QPen(ink, 0.8));
                    p.drawLine(QPointF(ux, baseY + gp.x() * kPxToPt),
                               QPointF(ux, baseY + (gp.x() + slot) * kPxToPt));
                    p.restore();
                }

                if (upright) {
                    /* 直立字：位置与格子都从「字符区间」推出 ——
                       用 cursorToX(字符起点) 和 cursorToX(字符终点)，
                       同一把尺子量出来，相邻两字必然首尾相接，不会重叠。 */
                    const QChar ch = thisChar;
                    if (ch.isNull())
                        continue;

                    /* 格子直接由字形位置推导：gp.x() 与 slot 都是布局单位，
                       与排版步进同源，不会出现「字距被多乘/少乘 0.75」。 */
                    const qreal y0 = gp.x() * kPxToPt;
                    const qreal cellH = qMax(slot * kPxToPt, 4.0);

                    /* 用「基线点」画，不用矩形：drawText(QRectF, …) 会把超出矩形的
                       笔画裁掉 —— 汉字下缘就是这么被吃掉的。 */
                    QFont f = fmtAt(midX);
                    /* 字号取格子大小：排版给的格子就是这一格的可用高度，
                       按它定字号最稳（不再用矩形画，不会切笔画）。 */
                    /* 字号按格子定，但钳在「半个字到两个字」之间：
                       格子算错时不至于画出米粒大小或顶天立地的怪字。 */
                    const qreal basePt = m_metricsPt > 0 ? m_metricsPt : 14.0;
                    const qreal px = qBound(basePt * 0.5, cellH, basePt * 2.0);
                    f.setPixelSize(qMax(1, qRound(px)));

                    const QFontMetricsF fmr(f);
                    const QString s(ch);

                    /* 按**墨迹**居中，而不是按字身（advance）居中：
                       中文标点（。、，？）的墨迹偏在字身一角，按字身居中会跑偏。 */
                    QRectF inkBox = fmr.tightBoundingRect(s);
                    if (inkBox.isEmpty())
                        inkBox = fmr.boundingRect(s);

                    qreal x = 0.0;
                    qreal baseline = 0.0;
                    if (place == GlyphPlace::TopRight) {
                        /* 竖排传统：句读贴格子**右上角** ——
                           右侧贴列框右缘，上侧贴格子起点。 */
                        const qreal pad = qMax(0.4, cellH * 0.04);
                        x = r.right() - pad - inkBox.right();
                        baseline = (baseY + y0 + pad) - inkBox.top();
                    } else {
                        const qreal cellCx = r.left() + r.width() / 2.0;
                        const qreal cellCy = baseY + y0 + cellH / 2.0;
                        x = cellCx - inkBox.center().x();
                        baseline = cellCy - inkBox.center().y();
                    }

                    p.save();
                    p.setFont(f);
                    p.setPen(ink);
                    p.drawText(QPointF(x, baseline), s);
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

void UmeView::paintTableCells(QPainter &p, const UmeLayout::WideItem &item,
                                const QRectF &box) const
{
    QTextCursor bc(item.block);
    QTextTable *table = bc.currentTable();
    if (!table)
        return;

    const int totalRows = qMax(1, table->rows());
    const int cols = qMax(1, table->columns());
    const int firstRow = qBound(0, item.rowFirst, totalRows - 1);
    const int lastRow = (item.rowLast < 0) ? totalRows - 1
                                           : qBound(0, item.rowLast, totalRows - 1);
    const int shown = lastRow - firstRow + 1;
    if (shown <= 0)
        return;

    /* 列宽 / 行高由排版算好（按内容），这里只消费 */
    QVector<qreal> colW = item.colWidths;
    if (colW.size() != cols) {
        colW.clear();
        for (int j = 0; j < cols; ++j)
            colW.append(box.width() / cols);
    }
    QVector<qreal> rowH = item.rowHeights;
    if (rowH.size() != shown) {
        rowH.clear();
        for (int i = 0; i < shown; ++i)
            rowH.append(box.height() / shown);
    }

    qreal y = box.top();
    for (int row = firstRow; row <= lastRow; ++row) {
        const qreal h = rowH.at(qMin(row - firstRow, rowH.size() - 1));
        qreal x = box.left();

        for (int j = 0; j < cols; ++j) {
            const qreal cw = colW.at(qMin(j, colW.size() - 1));
            const QRectF cellRect(x, y, cw, h);
            x += cw;

            const QTextTableCell cell = table->cellAt(row, j);
            if (!cell.isValid())
                continue;
            const QTextBlock b = cell.firstCursorPosition().block();
            if (!b.isValid() || b.text().isEmpty())
                continue;

            QTextLayout *lay = b.layout();
            if (!lay)
                continue;

            setLayoutFormats(lay, b);
            {
                QTextOption opt = lay->textOption();
                opt.setWrapMode(QTextOption::WrapAnywhere);
                lay->setTextOption(opt);
            }
            lay->beginLayout();
            for (;;) {
                QTextLine line = lay->createLine();
                if (!line.isValid())
                    break;
                line.setLineWidth(qMax(4.0, h - 4.0) / kPxToPt);
            }
            lay->endLayout();

            /* 单元格字号兜底颜色 */
            QColor cellInk = b.charFormat().foreground().color();
            if (!cellInk.isValid())
                cellInk = m_baseFormat.foreground().color();
            if (!cellInk.isValid())
                cellInk = QColor(0x11, 0x11, 0x11);

            qreal stepPx = 20.0;
            if (lay->lineCount() > 0)
                stepPx = qMax(8.0, lay->lineAt(0).height());
            const qreal colStep = stepPx * kPxToPt;

            p.save();
            p.setClipRect(cellRect);
            for (int k = 0; k < lay->lineCount(); ++k) {
                const qreal baseX = cellRect.right() - 2.0 - colStep * k;
                if (baseX - colStep < cellRect.left() - 0.5)
                    break;                          /* 格子放不下更多列 */
                const QRectF colRect(baseX - colStep, cellRect.top(), colStep,
                                     cellRect.height());
                /* 与正文完全同一套字形规则（直立 / 旋转 / 句读贴右上） */
                drawVerticalLine(p, lay, lay->lineAt(k), b, colRect, baseX,
                                 cellRect.top() + 2.0, cellInk);
            }
            p.restore();
        }
        y += h;
    }
}

/* ---------------- 宽对象：手柄与拖曳 ---------------- */

QVector<QPointF> UmeView::wideHandlePoints(const UmeLayout::WideItem &item) const
{
    return UmeHit::handlePoints(m_layout.docRect(item));
}

QVector<QRectF> UmeView::tableHandles(const UmeLayout::WideItem &item) const
{
    QVector<QRectF> out;
    const QRectF box = m_layout.docRect(item);
    const int cols = qMax(1, item.colWidths.size());
    const int rows = qMax(1, item.rowHeights.size());
    if (cols <= 1 && rows <= 1)
        return out;

    const qreal s = 8.0;
    /* 列分隔线：贴在表格上边缘 */
    qreal x = box.left();
    for (int j = 0; j + 1 < cols; ++j) {
        x += item.colWidths.value(j, box.width() / cols);
        out.append(QRectF(x - s / 2, box.top() - s / 2, s, s));
    }
    /* 行分隔线：贴在表格右边缘 */
    qreal y = box.top();
    for (int i = 0; i + 1 < rows; ++i) {
        y += item.rowHeights.value(i, box.height() / rows);
        out.append(QRectF(box.right() - s / 2, y - s / 2, s, s));
    }
    return out;
}

int UmeView::hitTableHandle(const QPointF &docPos, int *axis, int *index) const
{
    const UmeLayout::WideItem *item = selectedWideItem();
    if (!item || item->props.kind != UmeDoc::WideKind::Table)
        return -1;

    const QRectF box = m_layout.docRect(*item);
    const int cols = qMax(1, item->colWidths.size());
    const int rows = qMax(1, item->rowHeights.size());
    const qreal slop = UmeHit::kHandleSlop;

    qreal x = box.left();
    for (int j = 0; j + 1 < cols; ++j) {
        x += item->colWidths.value(j, box.width() / cols);
        if (qAbs(docPos.x() - x) <= slop && docPos.y() >= box.top() - slop
            && docPos.y() <= box.top() + slop + 4.0) {
            if (axis) *axis = 0;
            if (index) *index = j;
            return j;
        }
    }
    qreal y = box.top();
    for (int i = 0; i + 1 < rows; ++i) {
        y += item->rowHeights.value(i, box.height() / rows);
        if (qAbs(docPos.y() - y) <= slop && docPos.x() >= box.right() - slop - 4.0
            && docPos.x() <= box.right() + slop) {
            if (axis) *axis = 1;
            if (index) *index = i;
            return 1000 + i;
        }
    }
    return -1;
}

QVector<QRectF> UmeView::wideHandles(const UmeLayout::WideItem &item) const
{
    /* 表格不支持整体缩放/旋转，只给行/列分隔线手柄 */
    if (item.props.kind == UmeDoc::WideKind::Table)
        return tableHandles(item);

    return UmeHit::handleRects(m_layout.docRect(item), item.props.rotation);
}

int UmeView::hitWideHandle(const QPointF &docPos) const
{
    const UmeLayout::WideItem *item = selectedWideItem();
    if (!item)
        return -1;
    return UmeHit::handleAt(m_layout.docRect(*item), item->props.rotation, docPos);
}

int UmeView::hitWideItem(const QPointF &docPos) const
{
    /* 命中要用内容坐标；拷贝一份小数组换算，避免把坐标语义扩散到命中模块 */
    QVector<UmeLayout::WideItem> items = m_layout.wideItems();
    for (UmeLayout::WideItem &it : items)
        it.box = m_layout.docRect(it);
    return UmeHit::wideAt(items, docPos);
}

QVector<QRectF> UmeView::wideHandlesProbe() const
{
    const UmeLayout::WideItem *item = selectedWideItem();
    return item ? wideHandles(*item) : QVector<QRectF>();
}

int UmeView::maxSpanForPage() const
{
    const qreal strip = qMax(8.0, m_minWidthForDrag);
    const qreal areaW = m_settings ? m_settings->page().textArea().width() : 600.0;
    return qBound(1, int(areaW / strip), 48);
}

Qt::CursorShape UmeView::cursorForWideHandle(int index) const
{
    const UmeLayout::WideItem *item = selectedWideItem();
    if (!item)
        return Qt::ArrowCursor;

    /* 第 8 个是旋转手柄 */
    if (index == 8)
        return Qt::ArrowCursor;      // 由调用处换成自制旋转光标

    /* 手柄在「本地」朝外的方向角（屏幕坐标，y 向下） */
    static const qreal kLocalAngle[8] = {
        225.0,  // 0 左上
        315.0,  // 1 右上
        135.0,  // 2 左下
        45.0,   // 3 右下
        270.0,  // 4 上
        90.0,   // 5 下
        180.0,  // 6 左
        0.0,    // 7 右
    };

    /* 加上对象自身的旋转，再归到最近的 45°，决定是竖/横/斜光标 */
    qreal deg = UmeInteract::normalizeDegrees(kLocalAngle[qBound(0, index, 7)]
                                              + item->props.rotation);
    const int sector = qRound(deg / 45.0) % 8;

    switch (sector) {
    case 0:
    case 4:
        return Qt::SizeHorCursor;
    case 2:
    case 6:
        return Qt::SizeVerCursor;
    case 1:
    case 5:
        return Qt::SizeFDiagCursor;
    default:
        return Qt::SizeBDiagCursor;
    }
}

QString UmeView::cursorProbe() const
{
    QStringList out;
    for (int i = 0; i < 9; ++i) {
        const Qt::CursorShape s = cursorForWideHandle(i);
        const char *name = "?";
        switch (s) {
        case Qt::SizeHorCursor: name = "H"; break;
        case Qt::SizeVerCursor: name = "V"; break;
        case Qt::SizeFDiagCursor: name = "F"; break;
        case Qt::SizeBDiagCursor: name = "B"; break;
        default: name = "R"; break;       // 旋转
        }
        out << QStringLiteral("%1:%2").arg(i).arg(QLatin1String(name));
    }
    return out.join(QLatin1Char(' '));
}

void UmeView::insertParagraphAfterWide()
{
    QTextBlock block;
    if (const UmeLayout::WideItem *item = selectedWideItem())
        block = item->block;
    else
        block = m_cursor.block();
    if (!block.isValid() || !m_doc)
        return;

    QTextCursor after(block);
    after.setPosition(block.position() + block.length() - 1);
    after.insertBlock(QTextBlockFormat(), m_baseFormat);
    m_cursor = after;
    emit formatStateChanged();
    afterEdit();
    UME_LOG("wide", QStringLiteral("paragraph after block %1").arg(block.blockNumber()));
}

void UmeView::deleteSelectedWideObject()
{
    const UmeLayout::WideItem *item = selectedWideItem();
    if (!item)
        return;


    const QTextBlock block = item->block;
    QTextCursor c(block);
    if (QTextTable *table = c.currentTable()) {
        /* 表格：整张删掉 */
        QTextCursor del(table);
        del.setPosition(table->firstPosition());
        del.setPosition(table->lastPosition(), QTextCursor::KeepAnchor);
        del.removeSelectedText();
        UME_LOG("wide", QStringLiteral("delete table"));
    } else {
        /* 图片块：连块一起去掉（原来是空段落，只删字会留空行） */
        QTextCursor del(block);
        del.select(QTextCursor::BlockUnderCursor);
        del.removeSelectedText();
        if (del.block().text().isEmpty() && del.position() > 0)
            del.deletePreviousChar();
        UME_LOG("wide", QStringLiteral("delete image block"));
    }

    m_selectedWideBlock = -1;
    afterEdit();
}

void UmeView::selectWideObject(int index)
{
    const QVector<UmeLayout::WideItem> &items = m_layout.wideItems();
    if (index >= 0 && index < items.size())
        m_selectedWideBlock = items.at(index).block.position();
    else
        m_selectedWideBlock = -1;
    UME_LOG("wide", QStringLiteral("select index=%1 block=%2 (of %3)")
                        .arg(index).arg(m_selectedWideBlock).arg(items.size()));
    update();
}

void UmeView::applyWideDrag(const QPointF &docPos)
{
    const UmeLayout::WideItem *item = selectedWideItem();
    if (!item)
        return;

    /* ---- 表格：拖分隔线调这一行的高度 / 这一列的宽度 ---- */
    if (m_tableHandleAxis >= 0) {
        const QPointF delta = docPos - m_wideDragStart;
        UmeDoc::WideProps p = m_wideDragProps;
        if (m_tableHandleAxis == 0) {
            const int j = m_tableHandleIndex;
            if (j >= 0 && j < p.colSizes.size()) {
                p.colSizes[j] = qMax(12.0, p.colSizes.at(j) + delta.x());
                if (j + 1 < p.colSizes.size())
                    p.colSizes[j + 1] = qMax(12.0, p.colSizes.at(j + 1) - delta.x());
            }
        } else {
            const int i = m_tableHandleIndex;
            if (i >= 0 && i < p.rowSizes.size()) {
                p.rowSizes[i] = qMax(12.0, p.rowSizes.at(i) + delta.y());
                if (i + 1 < p.rowSizes.size())
                    p.rowSizes[i + 1] = qMax(12.0, p.rowSizes.at(i + 1) - delta.y());
            }
        }
        /* 同步总高/总宽，面板显示才和实际一致 */
        if (m_tableHandleAxis == 1 && !p.rowSizes.isEmpty()) {
            qreal sum = 0.0;
            for (qreal v : p.rowSizes)
                sum += v;
            p.heightPt = sum;
        }
        applyWideObject(p);
        return;
    }
    const QRectF r = item->box;
    UmeDoc::WideProps p = m_wideDragProps;
    const QPointF delta = docPos - m_wideDragStart;

    /* 吸附分两档：
       · 位置用「行高网格」（竖排里最自然，一行一行地挪）
       · 尺寸用 4pt 细网格（尺寸跳动要小，否则手感很糟） */
    const qreal posGrid = qMax(8.0, m_metricsPt * 1.4);
    const qreal sizeGrid = 4.0;
    auto snapTo = [](qreal v, qreal base, qreal grid, qreal tol) {
        const qreal rel = v - base;
        const qreal snapped = qRound(rel / grid) * grid;
        return (qAbs(rel - snapped) <= tol) ? base + snapped : v;
    };

    switch (m_wideDrag) {
    case WideDrag::Move: {
        /* 竖排里主要沿列方向移动；限制在正文区内 */
        qreal off = p.offsetPt + delta.y();
        const qreal areaTop = m_settings ? m_settings->page().textArea().top() : 0.0;
        const qreal targetTop = snapTo(r.top() + delta.y(), areaTop, posGrid, 4.0);
        off = p.offsetPt + (targetTop - r.top());
        p.offsetPt = qBound(-4000.0, off, 4000.0);
        break;
    }

    case WideDrag::ResizeLeft:
    case WideDrag::ResizeRight: {
        /* 左右两侧改的是「跨列数」 */
        const qreal strip = qMax(8.0, m_minWidthForDrag);
        const qreal dw = (m_wideDrag == WideDrag::ResizeRight) ? delta.x() : -delta.x();
        p.span = qBound(1, p.span + qRound(dw / strip), maxSpanForPage());
        break;
    }

    case WideDrag::Rotate: {
        /* 以**对象中心**为轴：θ = ∠(当前点 − 中心) − ∠(起点 − 中心)。
           这就是「L1 → L2 的夹角」那种算法，跟拖到哪儿无关，只看方向。 */
        const qreal delta = UmeInteract::dragAngleDelta(r.center(), m_wideDragStart,
                                                        docPos);
        const qreal raw = m_wideDragProps.rotation + delta;
        p.rotation = UmeInteract::snapDegrees(raw);

        if (!qFuzzyCompare(p.rotation, raw)) {
            UME_LOG("wide", QStringLiteral("snap %.1f° → %.1f°").arg(raw).arg(p.rotation));
        }
        break;
    }

    default: {
        /* 上下边与四角改高度；四角在保持比例时联动跨列 */
        const bool fromTop = (m_wideDrag == WideDrag::ResizeTop
                              || m_wideDrag == WideDrag::ResizeTL
                              || m_wideDrag == WideDrag::ResizeTR);
        const qreal dy = fromTop ? -delta.y() : delta.y();
        qreal newH = qBound(8.0, m_wideDragProps.heightPt + dy, 4000.0);

        /* 高度吸附到行高网格 */
        const qreal snapped = snapTo(newH, 0.0, sizeGrid, 2.0);
        if (!qFuzzyCompare(snapped, newH)) {
            UME_LOG("wide", QStringLiteral("snap height %1 → %2")
                                 .arg(newH, 0, 'f', 1)
                                 .arg(snapped, 0, 'f', 1));
            newH = snapped;
        }
        p.heightPt = newH;
        if (p.keepAspect && m_wideDragProps.naturalH > 0.0
            && (m_wideDrag == WideDrag::ResizeTL || m_wideDrag == WideDrag::ResizeTR
                || m_wideDrag == WideDrag::ResizeBL || m_wideDrag == WideDrag::ResizeBR)) {
            const qreal ratio = m_wideDragProps.naturalW / m_wideDragProps.naturalH;
            const qreal w = newH * ratio;
            const qreal strip = qMax(8.0, m_minWidthForDrag);
            p.span = qBound(1, qRound(w / strip), maxSpanForPage());
        }
        break;
    }
    }

    applyWideObject(p);
}

QRectF UmeView::wideItemBoxProbe(int index) const
{
    const QVector<UmeLayout::WideItem> &items = m_layout.wideItems();
    if (index < 0 || index >= items.size())
        return QRectF();
    return items.at(index).box;
}

QString UmeView::wideObjectsProbe() const
{
    QStringList out;
    const QVector<UmeLayout::WideItem> &items = m_layout.wideItems();
    for (const UmeLayout::WideItem &it : items) {
        out << QStringLiteral("%1:[x %2 y %3 w %4 h %5 span %6 %7]")
                   .arg(it.index)
                   .arg(it.box.left(), 0, 'f', 1)
                   .arg(it.box.top(), 0, 'f', 1)
                   .arg(it.box.width(), 0, 'f', 1)
                   .arg(it.box.height(), 0, 'f', 1)
                   .arg(it.props.span)
                   .arg(it.props.wrap == UmeDoc::WideWrap::Span
                            ? QStringLiteral("span")
                            : QStringLiteral("wrap"));
    }
    return out.isEmpty() ? QStringLiteral("-") : out.join(QStringLiteral("  "));
}

/* ---------------- 链接 / 表格 / 导出（预留能力） ---------------- */

void UmeView::insertLink(const QUrl &url, const QString &text)
{
    if (!m_doc || url.isEmpty())
        return;
    UME_LOG("link", QStringLiteral("insert url=%1 text=%2 sel=%3")
                         .arg(url.toString(), umeLogEsc(text))
                         .arg(int(m_cursor.hasSelection())));
    UmeDoc::applyLink(m_cursor, url, text);
    afterEdit();
}

QUrl UmeView::linkAtCursor() const
{
    return UmeDoc::linkAt(m_cursor);
}

void UmeView::insertImage(const QString &path)
{
    if (!m_doc || path.isEmpty())
        return;

    const QImage img = imageFor(path);
    if (img.isNull())
        return;

    /* 像素 → pt（96dpi），并限制最大尺寸，避免一插入就撑爆版面 */
    const qreal maxH = m_settings ? m_settings->page().textArea().height() : 700.0;
    qreal h = img.height() * 72.0 / 96.0;
    qreal w = img.width() * 72.0 / 96.0;
    if (h > maxH * 0.8) {
        const qreal k = maxH * 0.8 / h;
        h *= k;
        w *= k;
    }

    UmeDoc::WideProps p;
    p.kind = UmeDoc::WideKind::Image;
    p.wrap = UmeDoc::WideWrap::Span;        /* 默认：行外、列游标 */
    p.heightPt = h;
    p.span = qBound(1, qRound(w / qMax(8.0, m_minWidthForDrag)), 12);
    p.keepAspect = true;

    QTextCursor c = m_cursor;
    const QTextBlock block = UmeDoc::insertImageBlock(c, path, QSizeF(w, h), p);
    m_cursor = c;
    afterEdit();

    /* 图片块是空段落，光标若留在它上面，打字会写进图片里（看不见）。
       紧跟着补一个空段落，光标放进去 —— 用户可以直接在图片后继续输入。 */
    {
        QTextBlock imgBlock = block;
        if (imgBlock.isValid()) {
            QTextCursor after(imgBlock);
            QTextBlock last = imgBlock;
            QTextCursor probe(imgBlock);
            while (probe.currentTable())
                break;
            /* 图片块本身可能被后续块挤开，直接用块尾插新段 */
            after.setPosition(last.position() + last.length() - 1);
            after.insertBlock(QTextBlockFormat(), m_baseFormat);
            m_cursor = after;
        }
    }

    UME_LOG("image", QStringLiteral("insert %1 w=%2 h=%3 span=%4 block=%5")
                         .arg(path).arg(w, 0, 'f', 1).arg(h, 0, 'f', 1)
                         .arg(p.span).arg(block.blockNumber()));

    /* 插入后自动选中，手柄立刻可见 */
    for (int i = 0; i < m_layout.wideItems().size(); ++i) {
        if (m_layout.wideItems().at(i).block == block) {
            selectWideObject(i);
            break;
        }
    }
}

void UmeView::insertTable(int rows, int cols)
{
    if (!m_doc)
        return;
    UME_LOG("table", QStringLiteral("insert %1x%2").arg(rows).arg(cols));
    UmeDoc::insertTable(m_cursor, rows, cols);
    afterEdit();
}

QString UmeView::toHtml() const
{
    return UmeDoc::toHtml(m_doc);
}

void UmeView::insertTextByScript(const QString &text)
{
    /* 光标停在宽对象（图片）块上时，先补一个段落再输入，
       否则文字会被写进对象块、当作对象跳过而看不见。 */
    if (UmeDoc::isWideBlock(m_cursor.block())) {
        insertParagraphAfterWide();
    }

    const QString cjk = cjkFamily();
    int i = 0;
    while (i < text.size()) {
        const bool isCjk = cjk.isEmpty() ? false : isCjkLike(text.at(i));
        int j = i + 1;
        while (j < text.size()
               && (cjk.isEmpty() ? false : isCjkLike(text.at(j))) == isCjk)
            ++j;

        QTextCharFormat fmt = m_baseFormat;
        if (!cjk.isEmpty())
            fmt.setFontFamilies(fallbackFamilies(isCjk ? cjk
                                                       : m_metricsFamily));
        m_cursor.insertText(text.mid(i, j - i), fmt);
        i = j;
    }
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

    m_minWidthForDrag = minWidth;
    m_layout.setArrangement(m_settings->arrangement());
    m_layout.relayout(m_doc, m_settings->page(), minWidth,
                      m_settings->rightToLeft() ? UmeLayout::Flow::Rtl
                                                : UmeLayout::Flow::Ltr);

    if (UME_LOG_EVERY("layout", 150))
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

    /* 汉字与中文标点要落到**中文字体**上：
       否则 Qt 会用主字体（含蒙文的那支）给它们分步进，宽度只有一半，
       汉字之间就会互相压叠，标点也缩成米粒。 */
    const QString cjk = cjkFamily();
    if (!cjk.isEmpty()) {
        QTextCursor c(m_doc);
        c.beginEditBlock();
        for (QTextBlock b = m_doc->begin(); b.isValid(); b = b.next()) {
            const QString text = b.text();
            int i = 0;
            while (i < text.size()) {
                if (!isCjkLike(text.at(i))) {
                    ++i;
                    continue;
                }
                int j = i + 1;
                while (j < text.size() && isCjkLike(text.at(j)))
                    ++j;

                QTextCharFormat fmt;
                fmt.setFontFamilies(fallbackFamilies(cjk));
                QTextCursor rc(b);
                rc.setPosition(b.position() + i);
                rc.setPosition(b.position() + j, QTextCursor::KeepAnchor);
                rc.mergeCharFormat(fmt);
                i = j;
            }
        }
        c.endEditBlock();
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

    /* 选中了整行/整列：把格式套到那一行/列的所有单元格 */
    if ((m_tableRow >= 0 || m_tableCol >= 0) && m_cursor.currentTable()) {
        QTextTable *t = m_cursor.currentTable();
        int firstCol = 0, lastCol = t->columns() - 1;
        int firstRow = 0, lastRow = t->rows() - 1;
        if (m_tableCol >= 0) {
            firstCol = lastCol = qBound(0, m_tableCol, t->columns() - 1);
        } else {
            firstRow = lastRow = qBound(0, m_tableRow, t->rows() - 1);
        }
        for (int i = firstRow; i <= lastRow; ++i) {
            for (int j = firstCol; j <= lastCol; ++j) {
                QTextCursor cell = t->cellAt(i, j).firstCursorPosition();
                cell.movePosition(QTextCursor::EndOfBlock, QTextCursor::KeepAnchor);
                if (cell.hasSelection())
                    cell.mergeCharFormat(fmt);
                else
                    cell.setBlockCharFormat(fmt);
            }
        }
        afterEdit();
        UME_LOG("table", QStringLiteral("format row=%1 col=%2")
                             .arg(m_tableRow).arg(m_tableCol));
        return;
    }

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

void UmeView::applyCharStyle(int what, bool on)
{
    QTextCharFormat fmt;
    switch (what) {
    case StyleBold:
        fmt.setFontWeight(on ? QFont::Bold : QFont::Normal);
        break;
    case StyleItalic:
        fmt.setFontItalic(on);
        break;
    case StyleUnderline:
        fmt.setFontUnderline(on);
        break;
    case StyleStrikeOut:
        fmt.setFontStrikeOut(on);
        break;
    case StyleSuper:
        fmt.setVerticalAlignment(on ? QTextCharFormat::AlignSuperScript
                                    : QTextCharFormat::AlignNormal);
        break;
    case StyleSub:
        fmt.setVerticalAlignment(on ? QTextCharFormat::AlignSubScript
                                    : QTextCharFormat::AlignNormal);
        break;
    default:
        return;
    }
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

    bool sawAny = false;
    auto consider = [&s, &sawAny](const QTextCharFormat &f) {
        const bool firstSeen = !sawAny;
        sawAny = true;
        const QString fam = f.fontFamilies().toStringList().value(0);
        const qreal pt = f.fontPointSize();
        const QColor col = f.foreground().color();

        const bool bold = f.fontWeight() >= QFont::Bold;
        const bool italic = f.fontItalic();
        const bool underline = f.fontUnderline();
        const bool strike = f.fontStrikeOut();
        const int script = int(f.verticalAlignment()) == int(QTextCharFormat::AlignSuperScript) ? 1
                           : int(f.verticalAlignment()) == int(QTextCharFormat::AlignSubScript) ? -1
                                                                                              : 0;
        if (firstSeen) {
            s.bold = bold;
            s.italic = italic;
            s.underline = underline;
            s.strikeOut = strike;
            s.script = script;
        } else {
            if (s.bold != bold) s.boldMixed = true;
            if (s.italic != italic) s.italicMixed = true;
            if (s.underline != underline) s.underlineMixed = true;
            if (s.strikeOut != strike) s.strikeMixed = true;
            if (s.script != script) s.scriptMixed = true;
        }

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
    return m_layout.docRect(c);
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

QRectF UmeView::columnBoxProbe(int i) const
{
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    if (i < 0 || i >= cols.size())
        return QRectF();
    return cols.at(i).box;
}

bool UmeView::hitsAnyColumn(const QPointF &docPos) const
{
    return UmeHit::columnAt(m_layout.columns(), docPos) >= 0;
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
    /* screen_x = −y：墨迹横向落在 [基线 − inkBottom, 基线 − inkTop]。
       要让墨迹的中心正好压在列框中心：
           基线 − (inkTop+inkBottom)/2 = 列框中心
       —— 只按「宽度」居中会把蒙文整体推偏，汉字却是按列框居中的，
       两条竖中线就会差一两 pt（实测 1.3pt，看着很别扭）。 */
    const qreal center = r.left() + r.width() / 2.0;
    return center + (c.inkTop + c.inkBottom) / 2.0;
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
    adoptColorAtCursor();
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
    insertTextByScript(text);
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

    /* 单元格里按 Enter：跳到右边一个单元格；没有就下一行第一个；
       已经是最后一个就跳出表格。 */
    if ((event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter)
        && !m_doc) {
        // 无文档，交给默认处理
    } else if (event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) {
        if (QTextTable *table = m_cursor.currentTable()) {
            if (selectedWideObject() < 0) {          /* 选中对象时 Enter 另有含义 */
                const QTextTableCell cell = table->cellAt(m_cursor);
                const int r = cell.row();
                const int c = cell.column();
                QTextCursor next;
                if (c + 1 < table->columns()) {
                    next = table->cellAt(r, c + 1).firstCursorPosition();
                } else if (r + 1 < table->rows()) {
                    next = table->cellAt(r + 1, 0).firstCursorPosition();
                } else {
                    /* 最后一个单元格：跳到表格之后的段落 */
                    next = QTextCursor(m_doc);
                    next.setPosition(table->lastCursorPosition().position());
                    next.movePosition(QTextCursor::NextBlock);
                    if (next.currentTable()) {
                        /* 表格后面还没有段落：先建一个 */
                        QTextCursor mk(m_doc);
                        mk.setPosition(table->lastCursorPosition().position());
                        mk.movePosition(QTextCursor::EndOfBlock);
                        mk.insertBlock(QTextBlockFormat(), m_baseFormat);
                        next = mk;
                    }
                }
                setTextCursor(next);
                UME_LOG("table", QStringLiteral("enter → cell row=%1 col=%2")
                                     .arg(r).arg(c));
                event->accept();
                return;
            }
        }
    }

    /* 选中了宽对象：Delete / Backspace 删掉它，Esc 取消选中。
       这两个键不能落到「删一个字符」的逻辑里。 */
    if (m_selectedWideBlock >= 0) {
        if (event->key() == Qt::Key_Delete || event->key() == Qt::Key_Backspace) {
            deleteSelectedWideObject();
            event->accept();
            return;
        }
        if (event->key() == Qt::Key_Escape) {
            selectWideObject(-1);
            event->accept();
            return;
        }
        if (event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) {
            insertParagraphAfterWide();
            selectWideObject(-1);
            event->accept();
            return;
        }
    }

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

    /* 节流：绘制日志 300ms 内只放行一次，否则拖拽时刷屏 */
    if (m_doc && m_doc->revision() != m_paintedRevision && UME_LOG_EVERY("paint", 300)) {
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
    p.translate(-m_scrollX / m_zoom, -m_scrollY / m_zoom);

    const PageSetup &page = m_settings->page();
    for (int i = 0; i < m_layout.pageCount(); ++i) {
        const QRectF r = m_layout.pageRectFor(i);
        p.setPen(Qt::NoPen);
        p.setBrush(QColor(0, 0, 0, 40));
        p.drawRect(r.translated(0, 2));
        p.setBrush(Qt::white);
        p.drawRect(r);
    }

    if (m_settings->marginGuides())
        paintGuides(p);

    paintSelection(p);
    paintWideItems(p);
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
        const QRectF r = m_layout.pageRectFor(i);
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

        /* 兜底：把绘制限制在列框内。
           布局若因任何原因给出的行比列还长，也不会画到页边距外面去。 */
        p.save();
        p.setClipRect(r.adjusted(-1.0, -1.0, 1.0, 1.0));

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
        /* 格式区间只记录「与块格式不同」的部分：整段同色时 spans 是空的。
           所以兜底必须回落到块格式 → 基础格式，不能写死一个黑色。 */
        QColor columnInk = c.block.charFormat().foreground().color();
        if (!columnInk.isValid())
            columnInk = m_baseFormat.foreground().color();
        if (!columnInk.isValid())
            columnInk = QColor(0x11, 0x11, 0x11);

        /* 取该位置的字形格式：颜色、下划线（链接）、斜体等都要用 */
        auto formatAt = [&spans](qreal x) -> QTextCharFormat {
            for (const FmtSpan &s : spans) {
                if (x >= s.x0 - 0.01 && x < s.x1)
                    return s.fmt;
            }
            return QTextCharFormat();
        };
        auto colorAt = [&formatAt, columnInk](qreal x) {
            const QColor col = formatAt(x).foreground().color();
            return col.isValid() ? col : columnInk;
        };

        drawVerticalLine(p, lay, line, c.block, r, baseX, baseY, columnInk);

        p.restore();
    }
}

QColor UmeView::caretColor() const
{
    /* 光标颜色 = 接下来要输入的文字颜色。
       浅色（比如黄色、白色）在白纸上会看不见，这时压暗到可见为止。 */
    QColor caretInk = m_baseFormat.foreground().color();
    if (!caretInk.isValid())
        caretInk = QColor(0x11, 0x11, 0x11);
    const qreal luma = 0.299 * caretInk.redF() + 0.587 * caretInk.greenF()
                       + 0.114 * caretInk.blueF();
    if (luma > 0.72)
        caretInk = caretInk.darker(220);
    return caretInk;
}

void UmeView::paintCaret(QPainter &p) const
{
    if (!hasFocus() || !m_blinkOn)
        return;
    const QRectF r = caretDocRect();
    if (r.isNull())
        return;

    p.setPen(QPen(caretColor(), 2.0));
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

    /* Ctrl + 点击链接：交给系统打开 */
    if (event->modifiers() & Qt::ControlModifier) {
        const QTextCursor hit = cursorAtDocPos(docPosFromWidget(event->position()));
        const QUrl url = UmeDoc::linkAt(hit);
        if (!url.isEmpty()) {
            UME_LOG("link", QStringLiteral("open %1").arg(url.toString()));
            QDesktopServices::openUrl(url);
            event->accept();
            return;
        }
    }

    const QPointF docPos = docPosFromWidget(event->position());

    /* 宽对象优先：先看手柄，再看对象本体 */
    /* 表格：行/列分隔线手柄（不允许整体缩放与旋转） */
    {
        int taxis = -1;
        int tindex = -1;
        if (hitTableHandle(docPos, &taxis, &tindex) >= 0) {
            m_tableHandleAxis = taxis;
            m_tableHandleIndex = tindex;
            m_wideDrag = WideDrag::Move;
            m_wideDragStart = docPos;
            m_wideDragProps = currentWideObject();
            /* 关键：把当前行列尺寸**快照**下来。
               拖动过程中不能再从 item 取当前值，否则每帧会把上次的增长再加一遍。 */
            if (const UmeLayout::WideItem *it = selectedWideItem()) {
                if (m_wideDragProps.colSizes.size() != it->colWidths.size())
                    m_wideDragProps.colSizes = it->colWidths;
                if (m_wideDragProps.rowSizes.size() != it->rowHeights.size())
                    m_wideDragProps.rowSizes = it->rowHeights;
            }
            UME_LOG("table", QStringLiteral("handle drag axis=%1 index=%2")
                                 .arg(taxis).arg(tindex));
            event->accept();
            return;
        }
    }

    const int handle = hitWideHandle(docPos);
    if (handle >= 0) {
        static const WideDrag kResize[9] = {
            WideDrag::ResizeTL, WideDrag::ResizeTR, WideDrag::ResizeBL,
            WideDrag::ResizeBR, WideDrag::ResizeTop, WideDrag::ResizeBottom,
            WideDrag::ResizeLeft, WideDrag::ResizeRight, WideDrag::Rotate,
        };
        m_wideDrag = kResize[qBound(0, handle, 8)];
        m_wideDragStart = docPos;
        m_wideDragProps = currentWideObject();
        UME_LOG("wide", QStringLiteral("drag begin handle=%1").arg(handle));
        event->accept();
        return;
    }

    const int itemIndex = hitWideItem(docPos);
    if (itemIndex >= 0) {
        selectWideObject(itemIndex);
        m_wideDrag = WideDrag::Move;
        m_wideDragStart = docPos;

        /* 先把光标移进对象所在块，再取属性 —— 顺序反了会取到空属性，
           拖一下就把「这是一张表」的标记写没了（实测整张表散成普通段落）。 */
        const QTextBlock block = m_layout.wideItems().at(itemIndex).block;
        QTextCursor inside(block);
        setTextCursor(inside);
        m_wideDragProps = currentWideObject();
        event->accept();
        return;
    }

    selectWideObject(-1);

    /* 点在「某个宽对象下方、且 x 与之重叠」的**空白处**：
       光标落到该对象之后的段落 —— 这就是「图片下方继续输入」。

       注意必须先判断「点没点到文字」：环绕模式下对象下方的同一列就是正文，
       若一律跳转到对象之后的段落，那段文字就永远选不中了（实测如此）。 */
    if (!hitsAnyColumn(docPos)) {
        const QVector<UmeLayout::WideItem> &items = m_layout.wideItems();
        for (int i = items.size() - 1; i >= 0; --i) {
            const UmeLayout::WideItem &it = items.at(i);
            /* 用内容坐标：对象盒子是页内坐标，不换算会命中到别的页的对象 */
            const QRectF doc = m_layout.docRect(it);
            const bool xInside = docPos.x() >= doc.left() - 1.0
                                 && docPos.x() <= doc.right() + 1.0;
            if (!xInside || docPos.y() <= doc.bottom())
                continue;

            const int before = m_doc ? m_doc->blockCount() : 0;
            selectedWideObject();       // 只是读一下，不改状态
            QTextCursor after(it.block);
            after.setPosition(it.block.position() + it.block.length() - 1);
            after.movePosition(QTextCursor::NextBlock);
            if (after.block() == it.block) {
                /* 后面没有段落了：就地补一个 */
                after = QTextCursor(it.block);
                after.setPosition(it.block.position() + it.block.length() - 1);
                after.insertBlock(QTextBlockFormat(), m_baseFormat);
            }
            setTextCursor(after);
            UME_LOG("wide", QStringLiteral("click under object → block %1（原 %2 块）")
                                .arg(after.blockNumber()).arg(before));
            event->accept();
            return;
        }
    }

    QTextCursor cur = cursorAtDocPos(docPos);
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
    /* 正在拖宽对象：只更新对象，不动文字选区 */
    if (m_wideDrag != WideDrag::None) {
        applyWideDrag(docPosFromWidget(event->position()));
        event->accept();
        return;
    }

    const QPointF hoverPos = docPosFromWidget(event->position());

    /* ① 悬停在控制手柄上：换成缩放 / 旋转光标 */
    const int hoverHandle = hitWideHandle(hoverPos);
    if (hoverHandle >= 0) {
        if (hoverHandle == 8)
            setCursor(UmeIcons::rotateCursor());
        else
            setCursor(cursorForWideHandle(hoverHandle));
        event->accept();
        return;
    }

    /* ② 悬停在宽对象本体上：移动光标 */
    if (hitWideItem(hoverPos) >= 0) {
        setCursor(Qt::SizeAllCursor);
        event->accept();
        return;
    }

    /* ③ 悬停在链接上给手型提示 */
    {
        const QTextCursor hit = cursorAtDocPos(hoverPos);
        /* 竖排正文用**横向** I 形光标；Qt 的 IBeam 是竖的，方向不对 */
        setCursor(UmeDoc::linkAt(hit).isEmpty() ? UmeIcons::textIBeam()
                                                : QCursor(Qt::PointingHandCursor));
    }

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
    if (m_wideDrag != WideDrag::None) {
        UME_LOG("wide", QStringLiteral("drag end"));
        m_wideDrag = WideDrag::None;

    /* 点了一下分隔线手柄但没拖动 → 选中它左边那一列 / 上边那一行 */
    if (m_tableHandleAxis >= 0 && m_tableHandleIndex >= 0) {
        if (m_tableHandleAxis == 0) {
            m_tableCol = m_tableHandleIndex;
            m_tableRow = -1;
        } else {
            m_tableRow = m_tableHandleIndex;
            m_tableCol = -1;
        }
        UME_LOG("table", QStringLiteral("select row=%1 col=%2")
                             .arg(m_tableRow).arg(m_tableCol));
        update();
    }
    m_tableHandleAxis = -1;
    m_tableHandleIndex = -1;
        event->accept();
        return;
    }
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
    /* 横向：触控板横滑，或 Shift + 滚轮 */
    const int dx = event->angleDelta().x();
    const int dy = event->angleDelta().y();
    if (m_hbar && (dx != 0 || (event->modifiers() & Qt::ShiftModifier))) {
        const int delta = dx != 0 ? dx : dy;
        const int maxX = int(m_layout.contentSize().width() * m_zoom) - width();
        m_scrollX = qBound(0.0, m_scrollX - delta, qreal(qMax(0, maxX)));
        m_hbar->setValue(int(m_scrollX));
        if (dx == 0) {
            event->accept();
            return;
        }
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

QList<int> UmeView::scrollRangeProbe() const
{
    QList<int> out;
    out << (m_hbar ? m_hbar->maximum() : -1)
        << (m_vbar ? m_vbar->maximum() : -1)
        << int(m_scrollX) << int(m_scrollY)
        << width() << height();
    return out;
}

void UmeView::updateScrollBars()
{
    if (!m_vbar)
        return;
    const QSizeF content = m_layout.contentSize();
    const qreal contentH = content.height() * m_zoom;
    const qreal contentW = content.width() * m_zoom;

    const int w = m_vbar->sizeHint().width();
    const int hh = m_hbar ? m_hbar->sizeHint().height() : 0;

    const int maxY = qMax(0, int(contentH - height() + hh));
    m_vbar->setRange(0, maxY);
    m_vbar->setPageStep(qMax(1, height() - hh));
    m_vbar->setGeometry(width() - w, 0, w, height() - hh);

    if (m_hbar) {
        const int maxX = qMax(0, int(contentW - width() + w));
        m_hbar->setRange(0, maxX);
        m_hbar->setPageStep(qMax(1, width() - w));
        m_hbar->setGeometry(0, height() - hh, width() - w, hh);
        if (m_scrollX > maxX)
            m_scrollX = maxX;
        m_hbar->setValue(int(m_scrollX));
    }

    if (m_scrollY > maxY)
        m_scrollY = maxY;
    m_vbar->setValue(int(m_scrollY));
}

QSize UmeView::sizeHint() const
{
    const QSizeF content = m_layout.contentSize();
    const qreal w = content.width() > 0 ? content.width()
                                        : (m_settings ? m_settings->page().paper.width() : 595.0);
    return QSize(int(w * m_zoom) + 40, 900);
}

/* ---------------- 竖排方向 ---------------- */

QString UmeView::cjkFamily()
{
    static QString cached;
    if (!cached.isEmpty())
        return cached;
    if (!QCoreApplication::instance())
        return QString();

    const QStringList fams = QFontDatabase::families();
    for (const char *f : {"SimSun", "Microsoft YaHei", "Noto Sans CJK SC",
                          "Source Han Sans SC", "SimHei", "KaiTi"}) {
        if (fams.contains(QLatin1String(f))) {
            cached = QLatin1String(f);
            return cached;
        }
    }
    return QString();
}

bool UmeView::isCjkLike(QChar ch)
{
    /* 「用中文字体排」与「怎么摆」是两件事：
       问号叹号要旋转排，但它们仍属于中文标点，必须用中文字体的步进，
       否则只占半个字宽，会把前后汉字挤在一起。 */
    const ushort u = ch.unicode();
    if ((u >= 0x4E00 && u <= 0x9FFF) || (u >= 0x3400 && u <= 0x4DBF)
        || (u >= 0xF900 && u <= 0xFAFF) || (u >= 0x3040 && u <= 0x30FF)
        || (u >= 0xAC00 && u <= 0xD7AF) || (u >= 0x3100 && u <= 0x312F))
        return true;

    switch (u) {
    case 0x3001: case 0x3002:                       // 、。
    case 0xFF0C: case 0xFF0E:                       // ，．
    case 0xFF1A: case 0xFF1B:                       // ：；
    case 0xFF01: case 0xFF1F:                       // ！？
    case 0x201C: case 0x201D: case 0x2018: case 0x2019:   // 引号
        return true;
    default:
        return false;
    }
}

QStringList UmeView::fallbackFamilies(const QString &primary)
{
    /* 只把「本机真的装了」的字体加进栈里：硬写一个不存在的族名，
       Qt 会退回豆腐块，还白搭一次字体查找。 */
    /* 不能写成 static const … = QFontDatabase::families()：
       静态初始化可能发生在 QApplication 之前，那时字体库还是空的，
       缓存下来的就是「一个都没有」—— 于是字体栈里没有中文回退，
       排版按主字体步进（窄），汉字互相压叠。 */
    static QStringList installed;
    if (installed.isEmpty() && QCoreApplication::instance())
        installed = QFontDatabase::families();

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

    static bool logged = false;
    if (!logged) {
        logged = true;
        UME_LOG("font", QStringLiteral("stack=%1 (installed=%2)")
                              .arg(fams.join(QLatin1Char(',')))
                              .arg(installed.size()));
    }
    return fams;
}

UmeView::GlyphPlace UmeView::placeFor(QChar ch)
{
    const ushort u = ch.unicode();

    /* 句读、冒号分号、引号：竖排传统是**贴格子右上角**，不旋转。 */
    switch (u) {
    case 0x3001:   // 、
    case 0x3002:   // 。
    case 0xFF0C:   // ，
    case 0xFF0E:   // ．
    case 0xFF1A:   // ：
    case 0xFF1B:   // ；
    case 0x201C:   // “
    case 0x201D:   // ”
    case 0x2018:   // ‘
    case 0x2019:   // ’
        return GlyphPlace::TopRight;
    default:
        break;
    }

    /* 汉字 / 假名 / 韩文 / 注音：直立居中 */
    if ((u >= 0x4E00 && u <= 0x9FFF) || (u >= 0x3400 && u <= 0x4DBF)
        || (u >= 0xF900 && u <= 0xFAFF) || (u >= 0x3040 && u <= 0x30FF)
        || (u >= 0xAC00 && u <= 0xD7AF) || (u >= 0x3100 && u <= 0x312F))
        return GlyphPlace::Center;

    /* 问号叹号也属于「点号」：按 W3C clreq 与 GB/T 15834，
       点号「直、横排方向一致」，也就是**不旋转**，直排时同样贴右上角。 */
    if (u == 0xFF01 || u == 0xFF1F || u == 0x3007)   // ！？〇(占位)
        return GlyphPlace::TopRight;

    /* 其余（蒙文、拉丁、数字、括号、书名号、破折号、省略号）随列旋转 */
    return GlyphPlace::Rotated;
}

bool UmeView::isUprightScript(QChar ch)
{
    const GlyphPlace p = placeFor(ch);
    return p == GlyphPlace::Center || p == GlyphPlace::TopRight;
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

int UmeView::colsOffTopProbe(int page) const
{
    const qreal top = m_settings ? m_settings->page().textArea().top() : 0.0;
    int n = 0;
    for (const UmeLayout::Column &c : m_layout.columns()) {
        if (c.page != page)
            continue;
        if (c.box.top() > top + 0.5)
            ++n;
    }
    return n;
}

int UmeView::tableFragmentCountProbe() const
{
    int n = 0;
    for (const UmeLayout::WideItem &it : m_layout.wideItems())
        if (it.props.kind == UmeDoc::WideKind::Table)
            ++n;
    return n;
}

QString UmeView::tableFragmentsProbe() const
{
    QStringList out;
    for (const UmeLayout::WideItem &it : m_layout.wideItems()) {
        if (it.props.kind != UmeDoc::WideKind::Table)
            continue;
        out << QStringLiteral("p%1 rows %2-%3 y%4 h%5")
                   .arg(it.page).arg(it.rowFirst).arg(it.rowLast)
                   .arg(it.box.top(), 0, 'f', 1)
                   .arg(it.box.height(), 0, 'f', 1);
    }
    return out.join(QStringLiteral("  "));
}

QString UmeView::columnsProbe(int n) const
{
    QStringList out;
    const QVector<UmeLayout::Column> &cols = m_layout.columns();
    for (int i = 0; i < cols.size() && i < n; ++i) {
        /* 页内坐标 + 页码：跨页排版时要能看出第 2 页是否从页首开始 */
        out << QStringLiteral("%1:[p%2 y%3 left %4 w %5]")
                   .arg(i)
                   .arg(cols[i].page)
                   .arg(cols[i].box.top(), 0, 'f', 1)
                   .arg(cols[i].box.left(), 0, 'f', 1)
                   .arg(cols[i].box.width(), 0, 'f', 1);
    }
    return out.join(QStringLiteral("  "));
}

/* ---------------- 离屏渲染 ---------------- */

QImage UmeView::renderPageImage(int page, qreal scale, bool withCaret) const
{
    if (!m_settings)
        return QImage();

    const PageSetup &ps = m_settings->page();
    const QRectF pr = m_layout.pageRectFor(page);
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
    paintWideItems(p);
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
    const QSizeF totalSize = m_layout.contentSize();

    QImage img(QSize(qMax(1, int(totalSize.width() * scale)),
                     qMax(1, int(totalSize.height() * scale))),
               QImage::Format_ARGB32_Premultiplied);
    img.fill(QColor(0x6e, 0x6e, 0x72));

    QPainter p(&img);
    p.scale(scale, scale);
    p.setRenderHint(QPainter::TextAntialiasing, true);

    for (int i = 0; i < n; ++i)
        p.fillRect(m_layout.pageRectFor(i), Qt::white);

    paintSelection(p);
    paintWideItems(p);
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
