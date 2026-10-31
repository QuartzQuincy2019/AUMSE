#include "umelayout.h"

#include <QFontMetricsF>
#include <QTextFragment>
#include <QTextLayout>

void UmeLayout::relayout(QTextDocument *doc, const PageSetup &page, qreal minWidth)
{
    m_columns.clear();
    m_page = page;

    if (!doc)
        return;

    const QRectF area = page.textArea();
    const qreal textH = area.height();          // 一列能有多长 = 一条 line 的宽度
    const qreal right = area.right();
    const qreal minCol = qMax(4.0, minWidth);

    int pageNo = 0;
    int colInPage = 0;
    int colIndex = 0;
    qreal x = area.left();

    for (QTextBlock b = doc->begin(); b.isValid(); b = b.next()) {
        QTextLayout *lay = b.layout();
        if (!lay)
            continue;

        /* 自己跑一遍 layout：line 宽度 = 正文区高度 */
        lay->beginLayout();
        for (;;) {
            QTextLine line = lay->createLine();
            if (!line.isValid())
                break;
            line.setLineWidth(textH);
        }
        lay->endLayout();

        const int lineCount = lay->lineCount();
        for (int i = 0; i < lineCount; ++i) {
            const QTextLine line = lay->lineAt(i);

            /* 这一列里的字：按片段各自的字体量墨迹，取最宽的那个 */
            qreal inkW = 0.0;
            qreal above = 0.0;
            for (auto it = b.begin(); !it.atEnd(); ++it) {
                const QTextFragment frag = it.fragment();
                if (!frag.isValid())
                    continue;
                /* 只算落在本行里的片段 */
                const int fs = frag.position() - b.position();
                const int fe = fs + frag.length();
                if (fe <= line.textStart() || fs >= line.textStart() + line.textLength())
                    continue;

                const QFontMetricsF fm(frag.charFormat().font());
                /* 蒙文在水平布局里是「躺倒」的，它的行高就是竖排列宽要留的量。
                   这里必须用**名义行高**（ascent+descent），不能用 tightBoundingRect：
                   墨迹量的是孤立形，实际排版用上下文形，个别字形会超出墨迹框
                   （大字号时尤其明显，直接压到右边那一列上）。 */
                const qreal box = fm.ascent() + fm.descent();
                inkW = qMax(inkW, box);
                above = qMax(above, fm.ascent());
            }
            if (inkW <= 0.0)
                inkW = minCol * 0.6;
            if (above <= 0.0)
                above = minCol * 0.7;

            const qreal colW = qMax(minCol, inkW + kPad * 2.0);

            /* 放不下就换页：只看右边还有没有位置，左边的列一律不动 */
            if (colInPage > 0 && x + colW > right + 0.01) {
                ++pageNo;
                colInPage = 0;
                x = area.left();
            }

            Column c;
            c.index = colIndex++;
            c.page = pageNo;
            c.colInPage = colInPage;
            c.block = b;
            c.lineIndex = i;
            c.inkW = inkW;
            c.inkAbove = above;
            c.box = QRectF(x, area.top(), colW, textH);
            m_columns.append(c);

            x += colW;
            ++colInPage;
        }
    }

    m_pageCount = qMax(1, pageNo + 1);
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
