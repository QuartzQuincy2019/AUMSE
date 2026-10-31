#pragma once

#include <QList>
#include <QRectF>
#include <QSizeF>
#include <QString>

/* 页面设置：纸张尺寸 + 四边独立页边距。
   单位一律用 pt（1pt = 1/72 英寸）—— QPainter 在未缩放时 1 单位 = 1pt，
   打印与导出都按这个单位走，屏幕显示再乘 zoom。 */
struct PageSetup
{
    QSizeF paper{595.0, 842.0};   // 默认 A4
    qreal mLeft = 56.7;           // 2 cm
    qreal mRight = 56.7;
    qreal mTop = 56.7;
    qreal mBottom = 56.7;

    /* 正文区（页面坐标，原点在纸张左上角） */
    QRectF textArea() const
    {
        const qreal w = qMax(1.0, paper.width() - mLeft - mRight);
        const qreal h = qMax(1.0, paper.height() - mTop - mBottom);
        return QRectF(mLeft, mTop, w, h);
    }

    QSizeF paperSize() const { return paper; }

    /* 预置纸张。名字用中文，界面上直接显示。 */
    static QList<QString> presetNames()
    {
        return {QStringLiteral("A4"), QStringLiteral("B5"),
                QStringLiteral("16 开"), QStringLiteral("Letter"),
                QStringLiteral("自定义")};
    }

    static PageSetup preset(const QString &name)
    {
        PageSetup p;
        if (name == QStringLiteral("B5")) {
            p.paper = QSizeF(499.0, 709.0);       // 176 × 250 mm
        } else if (name == QStringLiteral("16 开")) {
            p.paper = QSizeF(524.4, 737.0);       // 185 × 260 mm
        } else if (name == QStringLiteral("Letter")) {
            p.paper = QSizeF(612.0, 792.0);       // 8.5 × 11 in
        } else if (name == QStringLiteral("A4")) {
            p.paper = QSizeF(595.0, 842.0);
        }
        return p;
    }
};
