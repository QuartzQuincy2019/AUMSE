#include "umelayout.h"
#include "umelog.h"

#include <QFontMetricsF>
#include <QHash>
#include <QTextCursor>
#include <QTextFragment>
#include <QTextLayout>
#include <QTextTable>

/* 布局坐标（96dpi 像素）与画布单位（pt）的换算 */
static constexpr qreal kPxToPt = 72.0 / 96.0;

/* 字体度量缓存：同一支字体、同一字号只建一次 QFontMetricsF。
   汉字要走回退字体，第一次解析很贵（实测一次 relayout 586ms），
   按列重复构造会把这笔开销乘上列数。 */
struct MetricsEntry
{
    QFontMetricsF fm;
    explicit MetricsEntry(const QFont &f) : fm(f) {}
};

static QHash<QString, MetricsEntry> &metricsCache()
{
    static QHash<QString, MetricsEntry> cache;
    return cache;
}

namespace {

/* 单元格量宽用：基础字体（族名 + 字号） */
QFont baseFontForMetrics(QTextDocument *doc, const QTextBlock &b)
{
    QFont f = b.charFormat().font();
    if (f.family().isEmpty())
        f = doc ? doc->defaultFont() : QFont(QStringLiteral("Noto Sans Mongolian"));
    if (f.pointSizeF() <= 0.0)
        f.setPointSizeF(14.0);
    return f;
}

} // namespace

void UmeLayout::relayout(QTextDocument *doc, const PageSetup &page, qreal minWidth,
                         Flow flow)
{
    m_columns.clear();
    m_wideItems.clear();
    m_stripCursor.clear();
    m_page = page;

    if (!doc)
        return;

    const QRectF area = page.textArea();
    const qreal textH = area.height();          // 一列能有多长（pt）
    const qreal minCol = qMax(4.0, minWidth);

    /* 宽对象按「一条带 = 最小列宽」折算宽度 */
    const qreal stripW = qMax(8.0, minCol);

    /* 宽对象把「与它在 x 上重叠」的列往下推：这就是「文本围绕」。
       不再用固定宽度的条带 —— 列宽是按内容变的，条带模型对不齐。 */
    /* 盒子是**页内**坐标，所以必须先按页过滤：
       否则第 1 页的图会把第 2 页的列也往下推（实测第 2 页正文整体下沉）。 */
    auto freeTopFor = [this, &area](qreal x0, qreal x1, int page) {
        qreal top = area.top();
        for (const WideItem &it : m_wideItems) {
            if (it.page != page)
                continue;                      // 不在这一页
            if (it.box.right() > x0 + 0.01 && it.box.left() < x1 - 0.01)
                top = qMax(top, it.box.bottom());
        }
        return top;
    };

    int pageNo = 0;
    int colInPage = 0;
    int colIndex = 0;
    int objIndex = 0;
    qreal x = (flow == Flow::Ltr) ? area.left() : area.right();

    /* 换页 / 换列的游标也要一起重置 */
    auto resetFlow = [&](bool newPage) {
        if (newPage) {
            ++pageNo;
            m_stripCursor.clear();
        }
        colInPage = 0;
        x = (flow == Flow::Ltr) ? area.left() : area.right();
    };

    int tableBlocks = 0;
    for (QTextBlock b = doc->begin(); b.isValid(); b = b.next()) {
        QTextCursor bc(b);
        QTextTable *table = bc.currentTable();
        if (table)
            ++tableBlocks;

        /* ---- 宽对象：表格与图片都走这里 ---- */
        /* 表格：只要这一块是表格的首块就当宽对象排 —— 不依赖属性是否还在。
           属性丢了就用默认值补上（自愈）：否则整张表会散成一堆普通段落。 */
        const bool isTableAnchor = table && table->firstCursorPosition().block() == b;
        const bool isImageBlock = !table && UmeDoc::isWideBlock(b);

        if (isTableAnchor || isImageBlock) {
            UmeDoc::WideProps props = UmeDoc::wideProps(b);
            if (isTableAnchor && !props.isValid()) {
                props.kind = UmeDoc::WideKind::Table;
                props.wrap = UmeDoc::WideWrap::Span;
                props.span = qBound(1, table->columns(), 12);
                props.heightPt = qMax(40.0, table->rows() * 28.0);
                props.naturalW = props.span * 20.0;
                props.naturalH = props.heightPt;
            }

            const qreal areaW = area.right() - area.left();
            qreal w = qBound(stripW, props.span * stripW, areaW);

            if (flow == Flow::Ltr) {
                qreal safeX = x;
                for (const Column &c : m_columns) {
                    if (c.page != pageNo)
                        continue;
                    safeX = qMax(safeX, c.box.right());
                }
                for (const WideItem &other : m_wideItems) {
                    if (other.page != pageNo)
                        continue;
                    if (other.box.bottom() <= area.top() + 0.01
                        || other.box.top() >= area.top() + textH + 0.01)
                        continue;
                    safeX = qMax(safeX, other.box.right());
                }
                x = qMax(x, safeX);
            }

            const qreal minKeep = qMax(stripW, 20.0);
            {
                const qreal remain = (flow == Flow::Ltr) ? area.right() - x
                                                         : x - area.left();
                if (w > remain + 0.01 && remain >= minKeep)
                    w = remain;
            }

            if ((flow == Flow::Ltr) ? (x + w > area.right() + 0.01)
                                    : (x - w < area.left() - 0.01)) {
                resetFlow(true);
                x = (flow == Flow::Ltr) ? area.left() : area.right();
            }

            if (isTableAnchor) {
                const int rows = qMax(1, table->rows());
                const int cols = qMax(1, table->columns());

                /* 「合适」尺寸：按单元格内容估。
                   竖排里「沿列的长度」= 这段文字在水平方向的宽度。 */
                QFontMetricsF fm(baseFontForMetrics(doc, b));
                const qreal lineW = qMax(12.0, fm.height() * 1.15);

                QVector<qreal> needLen(rows * cols, 0.0);
                qreal maxLen = 0.0;
                for (int i = 0; i < rows; ++i) {
                    for (int j = 0; j < cols; ++j) {
                        const QTextTableCell cell = table->cellAt(i, j);
                        if (!cell.isValid())
                            continue;
                        const QString txt = cell.firstCursorPosition().block().text();
                        const qreal len = txt.isEmpty() ? 0.0 : fm.horizontalAdvance(txt);
                        needLen[i * cols + j] = len;
                        maxLen = qMax(maxLen, len);
                    }
                }

                /* 行高：一行至少两个字高；用户拖过高度就按用户的 */
                qreal wantH = props.heightPt;
                if (wantH <= 0.0)
                    wantH = qMax(rows * lineW * 2.0, maxLen * 0.6);
                wantH = qBound(rows * lineW * 2.0, wantH, textH * 40.0);
                QVector<qreal> rowHs(rows, 0.0);
                if (props.rowSizes.size() == rows) {
                    for (int i = 0; i < rows; ++i)
                        rowHs[i] = qMax(10.0, props.rowSizes.at(i));
                } else {
                    for (int i = 0; i < rows; ++i)
                        rowHs[i] = qMin(qMax(lineW * 2.0, wantH / rows), textH);
                }

                /* 列宽：按各列内容占比分配，空列至少一个字宽 */
                QVector<qreal> colNeed(cols, 0.0);
                for (int j = 0; j < cols; ++j)
                    for (int i = 0; i < rows; ++i)
                        colNeed[j] = qMax(colNeed[j], needLen[i * cols + j]);

                qreal needSum = 0.0;
                for (int j = 0; j < cols; ++j)
                    needSum += qMax(lineW, colNeed[j]);

                QVector<qreal> colW(cols, 0.0);
                for (int j = 0; j < cols; ++j) {
                    const qreal share = needSum > 0.0 ? qMax(lineW, colNeed[j]) / needSum
                                                      : 1.0 / cols;
                    colW[j] = qMax(lineW, w * share);
                }
                /* 用户拖过分隔线就用他的列宽（按表宽归一化） */
                if (props.colSizes.size() == cols) {
                    qreal s = 0.0;
                    for (qreal v : props.colSizes)
                        s += qMax(6.0, v);
                    if (s > 0.0)
                        for (int j = 0; j < cols; ++j)
                            colW[j] = qMax(6.0, props.colSizes.at(j)) * w / s;
                }

                qreal sumW = 0.0;
                for (int j = 0; j < cols; ++j)
                    sumW += colW[j];
                if (sumW > 0.0)
                    for (int j = 0; j < cols; ++j)
                        colW[j] = colW[j] * w / sumW;

                int r = 0;
                while (r < rows) {
                    const qreal bx0 = (flow == Flow::Ltr) ? x : x - w;
                    const qreal freeTop = freeTopFor(bx0, bx0 + w, pageNo);
                    qreal top = freeTop + (r == 0 ? props.offsetPt : 0.0);
                    top = qBound(area.top(), top,
                                 area.top() + qMax(0.0, textH - rowHs.at(r)));

                    const qreal avail = area.top() + textH - top;
                    /* 逐行累计，放不下就切（单元格不拆） */
                    qreal hh = 0.0;
                    int last = r;
                    for (int i = r; i < rows; ++i) {
                        const qreal add = rowHs.at(i);
                        if (i > r && hh + add > avail + 0.01)
                            break;
                        hh += add;
                        last = i;
                    }

                    WideItem item;
                    item.block = b;
                    item.index = objIndex++;
                    item.page = pageNo;
                    item.box = QRectF(bx0, top, w, hh);
                    item.props = props;
                    item.rowFirst = r;
                    item.rowLast = last;
                    item.colWidths = colW;
                    item.rowHeights.clear();
                    for (int i = r; i <= last; ++i)
                        item.rowHeights.append(rowHs.at(i));
                    m_wideItems.append(item);

                    UME_LOG("table", QStringLiteral("page %1 rows %2-%3/%4 x=%5 y=%6 w=%7 h=%8")
                                         .arg(pageNo).arg(r).arg(last).arg(rows - 1)
                                         .arg(item.box.left(), 0, 'f', 1)
                                         .arg(item.box.top(), 0, 'f', 1)
                                         .arg(w, 0, 'f', 1)
                                         .arg(hh, 0, 'f', 1));

                    r = last + 1;
                    if (r < rows) {
                        resetFlow(true);
                        x = (flow == Flow::Ltr) ? area.left() : area.right();
                    }
                }

                ++colInPage;
                if (props.wrap == UmeDoc::WideWrap::Span)
                    x += (flow == Flow::Ltr) ? w : -w;
                if (QTextBlock after = table->lastCursorPosition().block(); after.isValid())
                    b = after;
                continue;
            }

            {
                const qreal h = qBound(8.0, props.heightPt, textH);
                const qreal bx0 = (flow == Flow::Ltr) ? x : x - w;
                const qreal freeTop = freeTopFor(bx0, bx0 + w, pageNo);
                qreal top = freeTop + props.offsetPt;
                top = qBound(area.top(), top, area.top() + qMax(0.0, textH - h));

                if (top + h > area.top() + textH + 0.01 && freeTop > area.top() + 0.5) {
                    resetFlow(true);
                    x = (flow == Flow::Ltr) ? area.left() : area.right();
                    top = area.top() + qMax(0.0, props.offsetPt);
                    top = qBound(area.top(), top, area.top() + qMax(0.0, textH - h));
                }

                WideItem item;
                item.block = b;
                item.index = objIndex++;
                item.page = pageNo;
                item.box = QRectF((flow == Flow::Ltr) ? x : x - w, top, w, h);
                item.props = props;
                m_wideItems.append(item);

                if (UME_LOG_EVERY("wide", 200))
                    UME_LOG("wide", QStringLiteral("place#%1 page=%2 x=%3 y=%4 w=%5 h=%6 kind=%7")
                                        .arg(item.index).arg(pageNo)
                                        .arg(item.box.left(), 0, 'f', 1)
                                        .arg(item.box.top(), 0, 'f', 1)
                                        .arg(w, 0, 'f', 1).arg(h, 0, 'f', 1)
                                        .arg(int(props.kind)));

                if (props.wrap == UmeDoc::WideWrap::Span)
                    x += (flow == Flow::Ltr) ? w : -w;
                ++colInPage;
            }
            continue;
        }

        QTextLayout *lay = b.layout();
        if (!lay)
            continue;

        /* 我们绕开了 QTextDocument 的默认排版，自己 beginLayout，
           所以必须**自己**把格式区间交给 layout —— 不然 formats() 是空的，
           绘制时按区间取颜色、取字体都会拿不到东西。 */
        {
            QList<QTextLayout::FormatRange> ranges;
            for (auto it = b.begin(); !it.atEnd(); ++it) {
                const QTextFragment frag = it.fragment();
                if (!frag.isValid())
                    continue;
                QTextLayout::FormatRange r;
                r.start = frag.position() - b.position();
                r.length = frag.length();
                r.format = frag.charFormat();
                ranges.append(r);
            }
            lay->setFormats(ranges);
        }

        /* 这一列从哪里开始：同页宽对象与它 x 重叠时，从对象下沿开始 */
        const qreal colLeftEstimate = (flow == Flow::Ltr) ? x : x - stripW;
        const qreal top = freeTopFor(colLeftEstimate, colLeftEstimate + stripW, pageNo);
        const qreal availH = qMax(12.0, area.top() + textH - top);

        /* 手工布局的 textOption 默认是 WordWrap —— 长单词（比如一长串 h）
           不会断开，整段挤在一条 line 里，最后被列裁剪吃掉。
           竖排里本来就没有「西文单词」的概念，一律允许任意处换行。 */
        {
            QTextOption opt = lay->textOption();
            opt.setWrapMode(QTextOption::WrapAnywhere);
            lay->setTextOption(opt);
        }

        /* 自己跑一遍 layout：line 宽度 = 本列可用高度（px） */
        lay->beginLayout();
        for (;;) {
            QTextLine line = lay->createLine();
            if (!line.isValid())
                break;
            line.setLineWidth(availH / kPxToPt);
        }
        lay->endLayout();

        const int lineCount = lay->lineCount();
        for (int i = 0; i < lineCount; ++i) {
            const QTextLine line = lay->lineAt(i);

            /* 这一列里的字：按片段各自的字体量墨迹，取最宽的那个 */
            qreal inkW = 0.0;      /* 列宽：名义行高，保证大字号也不越界 */
            qreal tight = 0.0;     /* 墨迹宽度：光标与选区高亮贴这个宽度 */
            qreal above = 0.0;
            qreal tTop = 0.0;      /* 墨迹上界（局部 y，负值） */
            qreal tBottom = 0.0;   /* 墨迹下界 */
            for (auto it = b.begin(); !it.atEnd(); ++it) {
                const QTextFragment frag = it.fragment();
                if (!frag.isValid())
                    continue;
                /* 只算落在本行里的片段 */
                const int fs = frag.position() - b.position();
                const int fe = fs + frag.length();
                if (fe <= line.textStart() || fs >= line.textStart() + line.textLength())
                    continue;

                const QFont ff = frag.charFormat().font();
                const QString key = ff.family() + QLatin1Char('/')
                                    + QString::number(ff.pointSizeF(), 'f', 2);
                auto itCache = metricsCache().find(key);
                if (itCache == metricsCache().end())
                    itCache = metricsCache().insert(key, MetricsEntry(ff));
                const QFontMetricsF &fm = itCache->fm;

                /* 蒙文在水平布局里是「躺倒」的，它的行高就是竖排列宽要留的量。
                   这里必须用**名义行高**（ascent+descent），不能用 tightBoundingRect：
                   墨迹量的是孤立形，实际排版用上下文形，个别字形会超出墨迹框
                   （大字号时尤其明显，直接压到右边那一列上）。 */
                const qreal box = fm.ascent() + fm.descent();
                inkW = qMax(inkW, box);
                /* 墨迹只取前 16 个字符：整段量会触发逐字回退查询，慢得离谱 */
                const QRectF tb = fm.tightBoundingRect(frag.text().left(16));
                if (tb.height() > 0.0) {
                    tight = qMax(tight, tb.height());
                    tTop = qMin(tTop, tb.top());
                    tBottom = qMax(tBottom, tb.bottom());
                }
                above = qMax(above, fm.ascent());
            }
            if (inkW <= 0.0)
                inkW = minCol * 0.6;
            if (tight <= 0.0)
                tight = inkW * 0.6;
            if (above <= 0.0)
                above = minCol * 0.7;

            /* 列宽贴合墨迹：字形是居中画在列里的（columInkLeft），
               所以不需要按名义行高留富余；大字号靠 tight 自己撑开。 */
            /* 文本列同样不越出正文区（超大字号时列会变很宽） */
            const qreal colW = qMin(qMax(minCol, tight + kPad * 2.0),
                                    area.right() - area.left());

            /* 每条 line 都从「自己那条带的游标」开始：
               块首可能被上面的宽对象压住，后面的列则是满高。 */
            /* 每条 line 各自算空闲顶部：
               与上面的宽对象 x 重叠 → 从对象下沿开始；不重叠 → 回到页首。
               以前整块共用块首的 top，绕行之后的列全被钉在对象下沿。 */
            const qreal lineTop = freeTopFor(
                (flow == Flow::Ltr) ? x : x - colW,
                (flow == Flow::Ltr) ? x + colW : x, pageNo);

            /* 放不下就换页：只看下游还有没有位置，上游的列一律不动 */
            const bool overflow = (flow == Flow::Ltr) ? (x + colW > area.right() + 0.01)
                                                      : (x - colW < area.left() - 0.01);
            if (colInPage > 0 && overflow)
                resetFlow(true);

            Column c;
            c.index = colIndex++;
            c.page = pageNo;
            c.colInPage = colInPage;
            c.block = b;
            c.lineIndex = i;
            c.inkW = tight;
            c.inkTop = tTop;
            c.inkBottom = tBottom;
            c.inkAbove = above;
            c.box = QRectF((flow == Flow::Ltr) ? x : x - colW, lineTop, colW,
                           area.top() + textH - lineTop);
            m_columns.append(c);


            x += (flow == Flow::Ltr) ? colW : -colW;
            ++colInPage;
        }
    }

    m_pageCount = qMax(1, pageNo + 1);
    m_tableBlocks = tableBlocks;
}

QRectF UmeLayout::pageRectOf(const PageSetup &page, int i,
                             const PageArrangement &a)
{
    const qreal pw = page.paper.width();
    const qreal ph = page.paper.height();

    int col = 0;
    int row = 0;
    switch (a.mode) {
    case PageArrangement::Horizontal:
        col = i;
        row = 0;
        break;
    case PageArrangement::Vertical:
        col = 0;
        row = i;
        break;
    case PageArrangement::RowsOfN:
    default: {
        const int per = qMax(1, a.perRow);
        col = i % per;
        row = i / per;
        break;
    }
    }

    return QRectF(col * (pw + kPageGap), row * (ph + kPageGap), pw, ph);
}

QSizeF UmeLayout::contentSizeOf(const PageSetup &page, int pageCount,
                               const PageArrangement &a)
{
    const int n = qMax(1, pageCount);
    const qreal pw = page.paper.width();
    const qreal ph = page.paper.height();

    int cols = 1;
    int rows = 1;
    switch (a.mode) {
    case PageArrangement::Horizontal:
        cols = n;
        rows = 1;
        break;
    case PageArrangement::Vertical:
        cols = 1;
        rows = n;
        break;
    case PageArrangement::RowsOfN:
    default: {
        const int per = qMax(1, a.perRow);
        cols = qMin(per, n);
        rows = (n + per - 1) / per;
        break;
    }
    }

    const qreal w = cols * pw + qMax(0, cols - 1) * kPageGap;
    const qreal h = rows * ph + qMax(0, rows - 1) * kPageGap;
    return QSizeF(w, h);
}

QPointF UmeLayout::pageOrigin(int page) const
{
    const QRectF r = pageRectFor(page);
    return QPointF(r.left(), r.top());
}

QRectF UmeLayout::docRect(const WideItem &item) const
{
    const QPointF o = pageOrigin(item.page);
    return item.box.translated(o.x(), o.y());
}

QRectF UmeLayout::docRect(const Column &c) const
{
    const QPointF o = pageOrigin(c.page);
    return c.box.translated(o.x(), o.y());
}

QRectF UmeLayout::pageRectFor(int i) const
{
    return pageRectOf(m_page, i, m_arrangement);
}

QSizeF UmeLayout::contentSize() const
{
    return contentSizeOf(m_page, m_pageCount, m_arrangement);
}
