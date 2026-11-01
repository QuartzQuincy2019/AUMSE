#include "umeicons.h"

#include <QFont>
#include <QPainter>
#include <QPainterPath>
#include <QPixmap>

namespace {

constexpr int kSize = 20;

/* 统一画布：白底透明，深灰笔画，2x 设备像素保证清晰 */
QIcon makeIcon(const std::function<void(QPainter &)> &paint)
{
    QPixmap pm(kSize * 2, kSize * 2);
    pm.fill(Qt::transparent);
    QPainter p(&pm);
    p.setRenderHint(QPainter::Antialiasing, true);
    p.scale(2.0, 2.0);
    p.setPen(QColor(0x33, 0x33, 0x33));
    paint(p);
    p.end();
    pm.setDevicePixelRatio(2.0);
    return QIcon(pm);
}

/* 画一个字母，用作 B / I / U / S 的图标主体 */
void drawLetter(QPainter &p, const QString &text, bool bold, bool italic)
{
    QFont f(QStringLiteral("Times New Roman"));
    f.setPixelSize(14);
    f.setBold(bold);
    f.setItalic(italic);
    p.setFont(f);
    p.drawText(QRectF(0, 0, kSize, kSize - 4), Qt::AlignCenter, text);
}

} // namespace

namespace UmeIcons {

QIcon bold()
{
    return makeIcon([](QPainter &p) { drawLetter(p, QStringLiteral("B"), true, false); });
}

QIcon italic()
{
    return makeIcon([](QPainter &p) { drawLetter(p, QStringLiteral("I"), false, true); });
}

QIcon underline()
{
    return makeIcon([](QPainter &p) {
        drawLetter(p, QStringLiteral("U"), false, false);
        p.setPen(QPen(QColor(0x33, 0x33, 0x33), 1.6));
        p.drawLine(QPointF(4, 17), QPointF(16, 17));
    });
}

QIcon strikeOut()
{
    return makeIcon([](QPainter &p) {
        drawLetter(p, QStringLiteral("S"), false, false);
        p.setPen(QPen(QColor(0x33, 0x33, 0x33), 1.6));
        p.drawLine(QPointF(3, 12), QPointF(17, 12));
    });
}

QIcon superscript()
{
    return makeIcon([](QPainter &p) {
        QFont f(QStringLiteral("Times New Roman"));
        f.setPixelSize(12);
        p.setFont(f);
        p.drawText(QRectF(1, 4, 8, 12), Qt::AlignCenter, QStringLiteral("x"));
        QFont small = f;
        small.setPixelSize(8);
        p.setFont(small);
        p.drawText(QRectF(8, 0, 10, 8), Qt::AlignCenter, QStringLiteral("2"));
    });
}

QIcon subscript()
{
    return makeIcon([](QPainter &p) {
        QFont f(QStringLiteral("Times New Roman"));
        f.setPixelSize(12);
        p.setFont(f);
        p.drawText(QRectF(1, 1, 8, 12), Qt::AlignCenter, QStringLiteral("x"));
        QFont small = f;
        small.setPixelSize(8);
        p.setFont(small);
        p.drawText(QRectF(8, 10, 10, 8), Qt::AlignCenter, QStringLiteral("2"));
    });
}

QIcon fontFamily()
{
    return makeIcon([](QPainter &p) {
        QFont f(QStringLiteral("Times New Roman"));
        f.setPixelSize(14);
        p.setFont(f);
        p.drawText(QRectF(0, 0, kSize, kSize), Qt::AlignCenter, QStringLiteral("A"));
    });
}

/* 镜像图标：一个实心三角 + 一个空心三角，中间一条虚线轴 */
QIcon flipHorizontal()
{
    return makeIcon([](QPainter &p) {
        p.setPen(QPen(QColor(0x66, 0x66, 0x66), 1.0, Qt::DashLine));
        p.drawLine(QPointF(kSize / 2.0, 3), QPointF(kSize / 2.0, 17));

        p.setPen(Qt::NoPen);
        p.setBrush(QColor(0x33, 0x33, 0x33));
        QPainterPath solid;
        solid.moveTo(3, 5);
        solid.lineTo(3, 15);
        solid.lineTo(8, 10);
        solid.closeSubpath();
        p.drawPath(solid);

        p.setBrush(Qt::NoBrush);
        p.setPen(QPen(QColor(0x33, 0x33, 0x33), 1.2));
        QPainterPath hollow;
        hollow.moveTo(17, 5);
        hollow.lineTo(17, 15);
        hollow.lineTo(12, 10);
        hollow.closeSubpath();
        p.drawPath(hollow);
    });
}

QIcon flipVertical()
{
    return makeIcon([](QPainter &p) {
        p.setPen(QPen(QColor(0x66, 0x66, 0x66), 1.0, Qt::DashLine));
        p.drawLine(QPointF(3, kSize / 2.0), QPointF(17, kSize / 2.0));

        p.setPen(Qt::NoPen);
        p.setBrush(QColor(0x33, 0x33, 0x33));
        QPainterPath solid;
        solid.moveTo(5, 3);
        solid.lineTo(15, 3);
        solid.lineTo(10, 8);
        solid.closeSubpath();
        p.drawPath(solid);

        p.setBrush(Qt::NoBrush);
        p.setPen(QPen(QColor(0x33, 0x33, 0x33), 1.2));
        QPainterPath hollow;
        hollow.moveTo(5, 17);
        hollow.lineTo(15, 17);
        hollow.lineTo(10, 12);
        hollow.closeSubpath();
        p.drawPath(hollow);
    });
}

QCursor textIBeam()
{
    /* 横向 I 形光标 —— 参照「宽翼缘工字钢」的截面：
       两端是竖的**翼缘**，中间是粗的**腹板**，整块实心。
       直排里把工字钢转 90°，翼缘落在左右两侧。

       尺寸 32 逻辑单位（2 倍屏 64px）≈ 24pt，与 14pt 字的一行相当。
       热点在正中心：光标指示插入位置。 */
    constexpr int s = 32;
    QPixmap pm(s * 2, s * 2);
    pm.fill(Qt::transparent);
    QPainter p(&pm);
    p.setRenderHint(QPainter::Antialiasing, true);
    p.scale(2.0, 2.0);

    /* 翼缘（左右竖条）与腹板（中间横条）的尺寸 */
    const qreal top = 6.5;
    const qreal bot = s - 6.5;
    const qreal mid = s / 2.0;
    const qreal flangeW = 3.2;      /* 翼缘厚度（比腹板厚，整体要细） */
    const qreal webH = 1.9;         /* 腹板厚度（比翼缘薄） */
    const qreal left = 3.5;
    const qreal right = s - 3.5;

    const qreal fx1 = left + flangeW;
    const qreal fx2 = right - flangeW;
    const qreal wy1 = mid - webH / 2.0;
    const qreal wy2 = mid + webH / 2.0;

    /* 转 90° 的工字形轮廓：走一圈把腹板与翼缘连成一体 */
    QPainterPath shape;
    shape.moveTo(left, top);
    shape.lineTo(fx1, top);
    shape.lineTo(fx1, wy1);
    shape.lineTo(fx2, wy1);
    shape.lineTo(fx2, top);
    shape.lineTo(right, top);
    shape.lineTo(right, bot);
    shape.lineTo(fx2, bot);
    shape.lineTo(fx2, wy2);
    shape.lineTo(fx1, wy2);
    shape.lineTo(fx1, bot);
    shape.lineTo(left, bot);
    shape.closeSubpath();

    /* 白描边 + 深色填充：深色文字、彩色文字上都看得清 */
    QPen outline(QColor(255, 255, 255, 225), 1.8);
    outline.setJoinStyle(Qt::RoundJoin);
    p.setPen(outline);
    p.setBrush(QColor(0x22, 0x22, 0x22));
    p.drawPath(shape);
    p.setPen(Qt::NoPen);
    p.drawPath(shape);
    p.end();

    pm.setDevicePixelRatio(2.0);
    return QCursor(pm, s / 2, s / 2);
}

QCursor rotateCursor()
{
    constexpr int s = 24;
    QPixmap pm(s * 2, s * 2);
    pm.fill(Qt::transparent);
    QPainter p(&pm);
    p.setRenderHint(QPainter::Antialiasing, true);
    p.scale(2.0, 2.0);

    /* 圆弧 + 箭头，表示「转」 */
    p.setPen(QPen(QColor(0x33, 0x33, 0x33), 2.0, Qt::SolidLine, Qt::RoundCap));
    p.drawArc(QRectF(4, 4, 16, 16), 40 * 16, 270 * 16);

    p.setPen(Qt::NoPen);
    p.setBrush(QColor(0x33, 0x33, 0x33));
    QPainterPath arrow;
    arrow.moveTo(18.5, 2.5);
    arrow.lineTo(22.0, 7.5);
    arrow.lineTo(17.0, 8.0);
    arrow.closeSubpath();
    p.drawPath(arrow);
    p.end();

    pm.setDevicePixelRatio(2.0);
    return QCursor(pm, s / 2, s / 2);
}

} // namespace UmeIcons
