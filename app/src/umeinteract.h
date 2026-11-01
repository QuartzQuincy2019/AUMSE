#pragma once

#include <QPointF>
#include <QtMath>

/* 操作吸附 / 操作命中的公共规则。
   与文档、界面都无关，只放纯数学与常量，便于单独测试。 */
namespace UmeInteract {

/* 旋转吸附：用户大多想停在 0/45/90/135/180…，但手不可能那么准。
   离 45° 的倍数在容差以内就吸附过去。 */
constexpr qreal kSnapStepDegrees = 45.0;
constexpr qreal kSnapToleranceDegrees = 8.0;

/* 手柄命中容差（pt）：鼠标不可能精确停在 6pt 的手柄上 */
constexpr qreal kHandleHitSlop = 5.0;

/* 把角度归一化到 [0, 360) */
inline qreal normalizeDegrees(qreal deg)
{
    qreal d = std::fmod(deg, 360.0);
    if (d < 0.0)
        d += 360.0;
    return d;
}

/* 吸附到最近的 45° 倍数；超出容差返回原值（自由角度） */
inline qreal snapDegrees(qreal deg)
{
    const qreal d = normalizeDegrees(deg);
    const qreal nearest = qRound(d / kSnapStepDegrees) * kSnapStepDegrees;
    return (qAbs(d - nearest) <= kSnapToleranceDegrees) ? normalizeDegrees(nearest) : d;
}

/* 点绕中心的旋转（度，顺时针；屏幕坐标 y 向下） */
inline QPointF rotatePoint(const QPointF &p, const QPointF &center, qreal deg)
{
    const qreal rad = qDegreesToRadians(deg);
    const qreal cs = std::cos(rad);
    const qreal sn = std::sin(rad);
    const QPointF v = p - center;
    return center + QPointF(v.x() * cs - v.y() * sn, v.x() * sn + v.y() * cs);
}

/* 点相对中心的角度（度） */
inline qreal angleOf(const QPointF &p, const QPointF &center)
{
    return qRadiansToDegrees(std::atan2(p.y() - center.y(), p.x() - center.x()));
}

/* 旋转手柄拖曳的角度增量：以「对象中心」为轴，
   取拖曳起点与当前点相对中心的角度差（见设计图 L1 / L2 / θ）。 */
inline qreal dragAngleDelta(const QPointF &center, const QPointF &from, const QPointF &to)
{
    return angleOf(to, center) - angleOf(from, center);
}

} // namespace UmeInteract
