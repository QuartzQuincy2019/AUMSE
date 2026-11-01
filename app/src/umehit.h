#pragma once

#include <QPointF>
#include <QRectF>
#include <QVector>

#include "umelayout.h"

/* 对象命中：**只读**版面结果（列 / 宽对象），回答「这个点是什么」。
   与「定位」（UmeLayout 负责放哪）解耦，也与视图状态（滚动、缩放）解耦 ——
   传进来的 docPos 必须已经是文档坐标。 */
namespace UmeHit {

/* 手柄几�� */
constexpr qreal kHandleSize = 6.0;
constexpr qreal kHandleSlop = 5.0;

/* 9 个手柄的中心点（未旋转定位，调用方按 rotation 旋转即可）：
   0 左上 1 右上 2 左下 3 右下 4 上 5 下 6 左 7 右 8 旋转 */
QVector<QPointF> handlePoints(const QRectF &box);

/* 手柄矩形（已按 rotation 绕中心旋转） */
QVector<QRectF> handleRects(const QRectF &box, qreal rotation);

/* 命中的手柄序号；没命中返回 -1。旋转会先反算回对象本地坐标。 */
int handleAt(const QRectF &box, qreal rotation, const QPointF &docPos);

/* 点是否落在（可旋转的）对象矩形内 */
bool boxContains(const QRectF &box, qreal rotation, const QPointF &docPos,
                 qreal slop = 1.0);

/* 命中的宽对象序号；没有返回 -1。后放的优先（与绘制顺序一致）。 */
int wideAt(const QVector<UmeLayout::WideItem> &items, const QPointF &docPos,
           qreal slop = 1.0);

/* 命中的文字列序号；没有返回 -1 */
int columnAt(const QVector<UmeLayout::Column> &columns, const QPointF &docPos,
             qreal slop = 1.0);

/* 命中的页号；不在任何页上返回 -1 */
int pageAt(const PageSetup &page, int pageCount,
           const PageArrangement &arrangement, const QPointF &docPos);

} // namespace UmeHit
