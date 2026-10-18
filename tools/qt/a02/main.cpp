// A02 探针：Qt 6 里怎么把「整形结果」画出来。
//
// 构建见 CMakeLists.txt；运行见 build.ps1。
//
// 本程序回答六个问题：
//   ① QRawFont 能不能直接从字体文件建，且与 HarfBuzz 用同一份数据
//   ② QTextLayout 是不是已经替我们调了 HarfBuzz（字形数 / 宽度对不对）
//   ③ QRawFont::glyphIndexesForString() 能不能代替整形（不能，要证明）
//   ④ QGlyphRun::setPositions() 的坐标是绝对的还是相对的（最容易错的地方）
//   ⑤ drawGlyphRun 与 QTextLayout::draw 画出来是不是同一张图（逐像素比）
//   ⑥ 轮廓能不能取出来拼 SVG（导出用）
#include <QGuiApplication>
#include <QImage>
#include <QPainter>
#include <QPainterPath>
#include <QRawFont>
#include <QTextLayout>
#include <QTextOption>
#include <QFontDatabase>
#include <QFontMetricsF>
#include <QFile>
#include <QTextStream>
#include <QDebug>
#include <QtMath>

static const QString FONT =
    QStringLiteral("E:/QKMansion/CSX10/w/UME/font/NotoSansMongolian-Regular.ttf");
static const QString OUTDIR = QStringLiteral("E:/QKMansion/CSX10/w/UME/.shots");

// ᠮᠣᠩᠭᠣᠯ = U+182E U+1823 U+1829 U+182D U+1823 U+182F
// 逐码位拼，避免 fromUcs4 的签名差异；也正好演示「QString 就是 UTF-16 码元」
static QString mongol() {
    static const ushort cps[] = {0x182E, 0x1823, 0x1829, 0x182D, 0x1823, 0x182F};
    QString s;
    for (ushort c : cps) s += QChar(c);
    return s;
}

int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);

    // ---------- ① 字体：直接从文件建 QRawFont ----------
    // 关键：HarfBuzz 那边用 hb_blob_create_from_file_or_fail(同一个路径)，
    // 这里 QRawFont 也从同一个文件建 —— 两边拿到的是同一份字形编号空间。
    //
    // ⚠ 但只有 QRawFont 是不够的：QFont(familyName) 是按**族名**找字体，
    // 没注册进 QFontDatabase 就找不到，会退回默认字体。
    // 实测（不注册时）：QTextLayout 给出 6 个字形、编号全是 1（.notdef）、
    // 每个推进正好 1 em —— 看起来「能排」，其实一个真字都没有。
    const int fid = QFontDatabase::addApplicationFont(FONT);
    const QStringList fams = QFontDatabase::applicationFontFamilies(fid);
    qInfo().noquote() << "① 注册字体："
                      << (fams.isEmpty() ? QString("失败") : fams.join(", "));
    QRawFont raw(FONT, 64.0, QFont::PreferDefaultHinting);
    qInfo().noquote() << "   QRawFont：" << raw.familyName()
                      << " 有效:" << raw.isValid()
                      << " upem:" << raw.unitsPerEm()
                      << " ascent/descent/leading:" << raw.ascent() << raw.descent() << raw.leading();

    const QString text = mongol();

    // ---------- ② QTextLayout = Qt 替你调 HarfBuzz ----------
    QFont f(fams.value(0));
    f.setPixelSize(64);
    QTextLayout layout(text, f);
    QTextOption opt;
    opt.setWrapMode(QTextOption::NoWrap);
    layout.setTextOption(opt);
    layout.beginLayout();
    QTextLine line = layout.createLine();
    line.setLineWidth(10000);
    layout.endLayout();

    int nGlyphs = 0;
    QStringList allPos;
    qInfo().noquote() << "② QTextLayout 的 glyph runs：";
    for (const QGlyphRun &gr : line.glyphRuns()) {
        const QVector<quint32> idx = gr.glyphIndexes();
        const QVector<QPointF> pos = gr.positions();
        nGlyphs += int(idx.size());
        QStringList ids, pxs;
        for (int i = 0; i < idx.size(); ++i) {
            ids << QString::number(idx[i]);
            if (i < pos.size()) pxs << QString::number(pos[i].x(), 'f', 1);
        }
        qInfo().noquote() << "     字形号:" << ids.join(" ");
        qInfo().noquote() << "     位置  :" << pxs.join(" ");
        allPos << pxs;
    }
    const qreal w = QFontMetricsF(f).horizontalAdvance(text);
    qInfo().noquote() << "   字形数:" << nGlyphs
                      << "  行宽:" << QString::number(w, 'f', 1)
                      << "  （64px / UPEM 1000 时，1 em = 64px）";

    // ---------- ③ glyphIndexesForString：只查 cmap，不做整形 ----------
    const QVector<quint32> naive = raw.glyphIndexesForString(text);
    QStringList nv;
    for (quint32 g : naive) nv << QString::number(g);
    qInfo().noquote() << "③ glyphIndexesForString（只查 cmap）："
                      << naive.size() << "个字形：" << nv.join(" ");
    qInfo().noquote() << "   → 与 QTextLayout 的" << nGlyphs
                      << "个相比：" << (naive.size() == nGlyphs ? "数量相同" : "数量不同");

    // ---------- ④ positions 是相对 run 原点 ----------
    if (!line.glyphRuns().isEmpty() && !line.glyphRuns().first().positions().isEmpty()) {
        qInfo().noquote() << "④ positions() 首项 x ="
                          << QString::number(line.glyphRuns().first().positions().first().x(), 'f', 1)
                          << "（从 0 起 → 相对 run 原点，不是屏幕绝对坐标）";
    }

    // ---------- ⑤ 两种画法逐像素比较 ----------
    const int W = 420, H = 260;
    QImage a(W, H, QImage::Format_ARGB32_Premultiplied);
    a.fill(Qt::white);
    {
        QPainter p(&a);
        p.setRenderHint(QPainter::Antialiasing, true);
        p.setRenderHint(QPainter::TextAntialiasing, true);
        p.translate(24, 120);
        layout.draw(&p, QPointF(0, 0));
    }
    a.save(OUTDIR + "/a02-textlayout.png");

    QImage b(W, H, QImage::Format_ARGB32_Premultiplied);
    b.fill(Qt::white);
    {
        QPainter p(&b);
        p.setRenderHint(QPainter::Antialiasing, true);
        p.setRenderHint(QPainter::TextAntialiasing, true);
        p.translate(24, 120);
        for (const QGlyphRun &gr : line.glyphRuns()) {
            p.drawGlyphRun(QPointF(0, 0), gr);   // 位置已在 run 里，这里只给原点
        }
    }
    b.save(OUTDIR + "/a02-glyphrun.png");

    int diff = 0, firstDiff = -1;
    for (int y = 0; y < H; ++y) {
        const QRgb *ra = reinterpret_cast<const QRgb *>(a.constScanLine(y));
        const QRgb *rb = reinterpret_cast<const QRgb *>(b.constScanLine(y));
        for (int x = 0; x < W; ++x) {
            if (ra[x] != rb[x]) {
                ++diff;
                if (firstDiff < 0) firstDiff = y * W + x;
            }
        }
    }
    qInfo().noquote() << "⑤ 逐像素比较：不同像素" << diff << "个"
                      << (diff == 0 ? "（完全相同）"
                                    : QString("（首个不同在 %1,%2）")
                                          .arg(firstDiff % W).arg(firstDiff / W));

    // ---------- ⑥ 轮廓 → QPainterPath → SVG ----------
    QPainterPath all;
    qreal pen = 0;
    for (quint32 g : naive) {          // 故意用未整形的字形号，对比形态
        QPainterPath gp = raw.pathForGlyph(g);
        all.addPath(gp.translated(pen, 0));
        pen += gp.boundingRect().width() + 6;
    }
    qInfo().noquote() << "⑥ pathForGlyph 拼出的路径：元素数" << all.elementCount()
                      << " 包围盒" << all.boundingRect();

    QImage c(W, H, QImage::Format_ARGB32_Premultiplied);
    c.fill(Qt::white);
    {
        QPainter p(&c);
        p.setRenderHint(QPainter::Antialiasing, true);
        p.translate(16, 80);
        p.fillPath(all, QColor("#1a1509"));
    }
    c.save(OUTDIR + "/a02-path.png");

    QFile svg(OUTDIR + "/a02-path.svg");
    if (svg.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream ts(&svg);
        ts << "<?xml version=\"1.0\"?>\n"
              "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"420\" height=\"260\">"
              "<rect width=\"100%\" height=\"100%\" fill=\"#fff\"/>\n";
        QString d;
        qreal cx = 16, cy = 80;
        for (int i = 0; i < all.elementCount(); ++i) {
            const QPainterPath::Element e = all.elementAt(i);
            switch (e.type) {
            case QPainterPath::MoveToElement:
                d += QString("M%1 %2 ").arg(e.x + cx, 0, 'f', 2).arg(e.y + cy, 0, 'f', 2);
                break;
            case QPainterPath::LineToElement:
                d += QString("L%1 %2 ").arg(e.x + cx, 0, 'f', 2).arg(e.y + cy, 0, 'f', 2);
                break;
            case QPainterPath::CurveToElement:
                d += QString("C");
                break;
            case QPainterPath::CurveToDataElement:
                d += QString("%1 %2 ").arg(e.x + cx, 0, 'f', 2).arg(e.y + cy, 0, 'f', 2);
                break;
            }
        }
        ts << "<path d=\"" << d << "\" fill=\"#1a1509\"/>\n</svg>\n";
        qInfo().noquote() << "⑦ 已写 SVG，path data 长度" << d.size();
    }

    // ---------- ⑦ 竖排：整体旋转 ----------
    QImage v(H, W, QImage::Format_ARGB32_Premultiplied);
    v.fill(Qt::white);
    {
        QPainter p(&v);
        p.setRenderHint(QPainter::Antialiasing, true);
        p.translate(v.width() - 90, 24);   // 旋转基点：右上
        p.rotate(90);                       // 顺时针 90°，横排结果立起来
        for (const QGlyphRun &gr : line.glyphRuns()) {
            p.drawGlyphRun(QPointF(0, 0), gr);
        }
    }
    v.save(OUTDIR + "/a02-vertical.png");
    qInfo().noquote() << "⑧ 竖排图已保存（横排结果整体 rotate(90)）";

    return 0;
}
