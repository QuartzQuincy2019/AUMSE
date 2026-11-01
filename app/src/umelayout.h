#pragma once

#include <QHash>
#include <QRectF>
#include <QSizeF>
#include <QTextBlock>
#include <QTextDocument>
#include <QVector>

#include "umedoc.h"
#include "umepage.h"

/* 页面在画布上的排布方式（视图菜单里可切） */
struct PageArrangement
{
    enum Mode {
        RowsOfN,      /* 每行 N 页，满了向下换行（默认 N=2） */
        Horizontal,   /* 无限横向：所有页排成一行 */
        Vertical,     /* 无限竖向：所有页排成一列 */
    };

    Mode mode = RowsOfN;
    int perRow = 2;   /* RowsOfN 时的每行页数 */

    bool operator==(const PageArrangement &o) const
    {
        return mode == o.mode && perRow == o.perRow;
    }
    bool operator!=(const PageArrangement &o) const { return !(*this == o); }
};

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
        int index = 0;
        int page = 0;
        int colInPage = 0;
        QRectF box;          // 页面坐标；width = 本列实际宽度
        QTextBlock block;
        int lineIndex = 0;

        qreal inkAbove = 10.0;
        qreal inkW = 16.0;
        qreal inkTop = 0.0;
        qreal inkBottom = 0.0;
    };

    /* 宽对象在版面里的落位（表格、图片） */
    struct WideItem
    {
        QTextBlock block;
        int index = 0;
        int page = 0;
        QRectF box;
        UmeDoc::WideProps props;

        /* 表格跨页：本片段覆盖的行区间（闭）。图片恒 0 / -1（= 全部）。 */
        int rowFirst = 0;
        int rowLast = -1;

        /* 表格：按内容算出的列宽与行高（pt）。图片为空。 */
        QVector<qreal> colWidths;
        QVector<qreal> rowHeights;
    };

    enum class Flow { Ltr, Rtl };

    void relayout(QTextDocument *doc, const PageSetup &page, qreal minWidth,
                  Flow flow = Flow::Ltr);

    const QVector<Column> &columns() const { return m_columns; }
    const QVector<WideItem> &wideItems() const { return m_wideItems; }
    int pageCount() const { return m_pageCount; }
    int tableBlocks() const { return m_tableBlocks; }

    /* ---- 页面排布：画布上多页怎么摆 ---- */
    void setArrangement(const PageArrangement &a) { m_arrangement = a; }
    const PageArrangement &arrangement() const { return m_arrangement; }

    /* 第 i 页在内容坐标系里的矩形（含页间距） */
    QRectF pageRectFor(int i) const;
    /* 所有页合起来占多大（滚动条范围用） */
    QSizeF contentSize() const;
    /* 纯函数版本：便于渲染与测试 */
    static QRectF pageRectOf(const PageSetup &page, int i,
                             const PageArrangement &a);
    static QSizeF contentSizeOf(const PageSetup &page, int pageCount,
                                const PageArrangement &a);

    /* 页内坐标 → 内容坐标（加该页原点）。绘制/命中一律用这个。 */
    QPointF pageOrigin(int page) const;
    QRectF docRect(const WideItem &item) const;
    QRectF docRect(const Column &c) const;

    static constexpr qreal kPageGap = 24.0;
    static constexpr qreal kPad = 2.0;      // 墨迹两侧留白

private:
    QVector<Column> m_columns;
    QVector<WideItem> m_wideItems;
    int m_pageCount = 1;
    int m_tableBlocks = 0;
    PageSetup m_page;
    PageArrangement m_arrangement;

    QHash<int, qreal> m_stripCursor;
};
