#include "umelayout.h"

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
    auto freeTopFor = [this, &area](qreal x0, qreal x1, int page) {
        qreal top = area.top();
        for (const WideItem &it : m_wideItems) {
            if (it.box.top() < area.top() - 0.01)
                continue;                      // 不在这一页
            if (it.box.top() >= area.top() + area.height() + 0.01)
                continue;
            if (it.box.right() > x0 + 0.01 && it.box.left() < x1 - 0.01)
                top = qMax(top, it.box.bottom());
        }
        Q_UNUSED(page);
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
        const bool isTableAnchor =
            table && table->firstCursorPosition().block() == b
            && UmeDoc::isWideBlock(b);
        const bool isImageBlock = !table && UmeDoc::isWideBlock(b);

        if (isTableAnchor || isImageBlock) {
            const UmeDoc::WideProps props = UmeDoc::wideProps(b);
            const qreal w = qBound(stripW, props.span * stripW,
                                   area.right() - area.left());
            const qreal h = qBound(8.0, props.heightPt, textH);

            const qreal boxX = (flow == Flow::Ltr) ? x : x - w;
            const qreal freeTop = freeTopFor(boxX, boxX + w, pageNo);
            qreal top = freeTop + props.offsetPt;
            top = qBound(area.top(), top, area.top() + qMax(0.0, textH - h));

            /* 放不下就换列，再不行换页 */
            const bool widthOver =
                (flow == Flow::Ltr) ? (x + w > area.right() + 0.01)
                                    : (x - w < area.left() - 0.01);
            const bool heightOver = (top + h > area.top() + textH + 0.01);
            if (widthOver || (heightOver && freeTop > area.top() + 0.5)) {
                resetFlow(true);
                x = (flow == Flow::Ltr) ? area.left() : area.right();
                top = area.top() + qMax(0.0, props.offsetPt);
                top = qBound(area.top(), top, area.top() + qMax(0.0, textH - h));
            }

            WideItem item;
            item.block = b;
            item.index = objIndex++;
            item.box = QRectF((flow == Flow::Ltr) ? x : x - w, top, w, h);
            item.props = props;
            m_wideItems.append(item);

            if (props.wrap == UmeDoc::WideWrap::Span)
                x += (flow == Flow::Ltr) ? w : -w;
            ++colInPage;

            if (isTableAnchor) {
                QTextBlock after = table->lastCursorPosition().block();
                if (after.isValid())
                    b = after;
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
            const qreal colW = qMax(minCol, tight + kPad * 2.0);

            /* 每条 line 都从「自己那条带的游标」开始：
               块首可能被上面的宽对象压住，后面的列则是满高。 */
            const qreal lineTop = top;

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

qreal UmeLayout::contentHeight() const
{
    return m_pageCount * m_page.paper.height() + (m_pageCount - 1) * kPageGap;
}

QRectF UmeLayout::pageRect(const PageSetup &page, int i)
{
    return QRectF(0.0, i * (page.paper.height() + kPageGap),
                  page.paper.width(), page.paper.height());
}
