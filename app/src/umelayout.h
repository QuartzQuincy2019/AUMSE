#pragma once

#include <QHash>
#include <QRectF>
#include <QTextBlock>
#include <QTextDocument>
#include <QVector>

#include "umedoc.h"
#include "umepage.h"

/* 竖排布局：把 QTextDocument 排成「一列一列」，再按页面切分。

   几何模型（单位 pt）：
     · 一列就是 QTextLayout 的一条 line，line 的宽度 = 该列可用高度
     · **每一列自己的宽度** = 这一列里最宽的字形 + 两侧留白
     · 列按 Flow 方向推进；某列变宽只会把下游的列推走
     · 排到正文区边界就换页
     · 宽对象（表格/图片）横跨 K 列，占一块矩形；它下面的文字能不能继续，
       由 WideWrap 决定（独占整列 / 文本围绕） */
class UmeLayout
{
public:
    struct Column
    {
        int index = 0;       // 全文列序号
        int page = 0;        // 页号（0 起）
        int colInPage = 0;   // 页内列序
        QRectF box;          // 页面坐标；width = 本列实际宽度
        QTextBlock block;
        int lineIndex = 0;

        qreal inkAbove = 10.0;   // 基线到墨迹外缘（本列最宽的那个字）
        qreal inkW = 16.0;       // 本列墨迹宽度，光标/选区用它
        /* 墨迹在「局部 y」上的上下界（相对基线，向上为负）。
           rotate(90) 后 screen_x = −y，所以这两个值决定墨迹落在屏幕上的
           横向位置与宽度；只按宽度居中会让蒙文整体偏一两 pt。 */
        qreal inkTop = 0.0;
        qreal inkBottom = 0.0;
    };

    /* 宽对象在版面里的落位（表格、图片） */
    struct WideItem
    {
        QTextBlock block;          // 锚定块（表格首格首段 / 图片所在块）
        int index = 0;
        QRectF box;                // 页面坐标
        UmeDoc::WideProps props;
    };

    /* 列的推进方向：Ltr 自左向右（默认），Rtl 自右向左（预留接口） */
    enum class Flow { Ltr, Rtl };

    /* minWidth = 列的最小宽度（空行/窄行都保证有这么宽） */
    void relayout(QTextDocument *doc, const PageSetup &page, qreal minWidth,
                  Flow flow = Flow::Ltr);

    const QVector<Column> &columns() const { return m_columns; }
    const QVector<WideItem> &wideItems() const { return m_wideItems; }
    int pageCount() const { return m_pageCount; }
    /* 落在表格单元格里的段落数 */
    int tableBlocks() const { return m_tableBlocks; }
    qreal contentHeight() const;

    static constexpr qreal kPageGap = 24.0;
    static constexpr qreal kPad = 2.0;      // 墨迹两侧留白

    static QRectF pageRect(const PageSetup &page, int i);

private:
    QVector<Column> m_columns;
    QVector<WideItem> m_wideItems;
    int m_pageCount = 1;
    int m_tableBlocks = 0;
    PageSetup m_page;

    /* 列游标：某个 x 区间已经被用到哪一段（y）。宽对象用它实现「文本围绕」。 */
    QHash<int, qreal> m_stripCursor;
};
