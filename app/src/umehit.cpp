#include "umehit.h"

#include "umeinteract.h"

namespace UmeHit {

QVector<QPointF> handlePoints(const QRectF &box)
{
    QVector<QPointF> pts;
    pts << box.topLeft() << box.topRight() << box.bottomLeft() << box.bottomRight()
        << QPointF(box.center().x(), box.top())
        << QPointF(box.center().x(), box.bottom())
        << QPointF(box.left(), box.center().y())
        << QPointF(box.right(), box.center().y());
    /* 第 9 个：旋转手柄，落在对象「上游侧」外 14pt */
    pts << QPointF(box.right() + 14.0, box.center().y());
    return pts;
}

QVector<QRectF> handleRects(const QRectF &box, qreal rotation)
{
    const QVector<QPointF> base = handlePoints(box);
    const QPointF c = box.center();

    QVector<QRectF> out;
    out.reserve(base.size());
    for (const QPointF &p : base) {
        const QPointF q = UmeInteract::rotatePoint(p, c, rotation);
        out.append(QRectF(q.x() - kHandleSize / 2.0, q.y() - kHandleSize / 2.0,
                          kHandleSize, kHandleSize));
    }
    return out;
}

int handleAt(const QRectF &box, qreal rotation, const QPointF &docPos)
{
    /* 反向旋转回对象本地坐标再判，否则对象转过之后手柄点不中 */
    const QPointF local =
        UmeInteract::rotatePoint(docPos, box.center(), -rotation);

    const QVector<QPointF> base = handlePoints(box);
    for (int i = 0; i < base.size(); ++i) {
        const QRectF r(base.at(i).x() - kHandleSize / 2.0,
                       base.at(i).y() - kHandleSize / 2.0, kHandleSize, kHandleSize);
        if (r.adjusted(-kHandleSlop, -kHandleSlop, kHandleSlop, kHandleSlop)
                .contains(local))
            return i;
    }
    return -1;
}

bool boxContains(const QRectF &box, qreal rotation, const QPointF &docPos, qreal slop)
{
    const QPointF local =
        UmeInteract::rotatePoint(docPos, box.center(), -rotation);
    return box.adjusted(-slop, -slop, slop, slop).contains(local);
}

int wideAt(const QVector<UmeLayout::WideItem> &items, const QPointF &docPos, qreal slop)
{
    for (int i = items.size() - 1; i >= 0; --i) {
        const UmeLayout::WideItem &it = items.at(i);
        if (boxContains(it.box, it.props.rotation, docPos, slop))
            return i;
    }
    return -1;
}

int columnAt(const QVector<UmeLayout::Column> &columns, const QPointF &docPos, qreal slop)
{
    for (int i = 0; i < columns.size(); ++i) {
        const QRectF box = columns.at(i).box;
        if (box.adjusted(-slop, -slop, slop, slop).contains(docPos))
            return i;
    }
    return -1;
}

int pageAt(const PageSetup &page, int pageCount,
           const PageArrangement &arrangement, const QPointF &docPos)
{
    for (int p = 0; p < pageCount; ++p) {
        if (UmeLayout::pageRectOf(page, p, arrangement).contains(docPos))
            return p;
    }
    return -1;
}

} // namespace UmeHit
