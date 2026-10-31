#pragma once

#include <QTextBlock>
#include <QTextDocument>
#include <QVector>
#include <QRectF>

#include "umepage.h"

/* 竖排布局：把 QTextDocument 排成「一列一列」，再按页面切分。

   几何模型（单位 pt）：
     · 一列就是 QTextLayout 的一条 line，line 的宽度 = 正文区高度
     · **每一列自己的宽度** = 这一列里最宽的字形 + 两侧留白
       （列与列不等宽，像 Word 的行高随该行最高字变化）
     · 列自左向右排；某列变宽只会把**它右边**的列推走，左边不动
     · 排到正文区右边界就换页 */
class UmeLayout
{
public:
    struct Column
    {
        int index = 0;       // 全文列序号
        int page = 0;        // 页号（0 起）
        int colInPage = 0;   // 页内列序（自左向右）
        QRectF box;          // 页面坐标；width = 本列实际宽度
        QTextBlock block;
        int lineIndex = 0;

        qreal inkAbove = 10.0;   // 基线到墨迹外缘（本列最宽的那个字）
        qreal inkW = 16.0;       // 本列墨迹宽度，光标/选区用它
    };

    /* minWidth = 列的最小宽度（空行/窄行都保证有这么宽） */
    void relayout(QTextDocument *doc, const PageSetup &page, qreal minWidth);

    const QVector<Column> &columns() const { return m_columns; }
    int pageCount() const { return m_pageCount; }
    qreal contentHeight() const;

    static constexpr qreal kPageGap = 24.0;
    static constexpr qreal kPad = 2.0;      // 墨迹两侧留白

    static QRectF pageRect(const PageSetup &page, int i);

private:
    QVector<Column> m_columns;
    int m_pageCount = 1;
    PageSetup m_page;
};
