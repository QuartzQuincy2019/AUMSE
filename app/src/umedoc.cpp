#include "umedoc.h"

#include <QTextBlock>
#include <QTextCursor>
#include <QTextDocument>
#include <QTextTable>

namespace {

/* 链接的默认样式：'#' 蓝 + 下划线。给用户改过颜色的不加蓝，只留下划线 */
constexpr QRgb kLinkBlue = 0x0b67c2;

int kindToInt(UmeDoc::WideKind k)
{
    switch (k) {
    case UmeDoc::WideKind::Table: return 1;
    case UmeDoc::WideKind::Image: return 2;
    default: return 0;
    }
}

UmeDoc::WideKind intToKind(int v)
{
    switch (v) {
    case 1: return UmeDoc::WideKind::Table;
    case 2: return UmeDoc::WideKind::Image;
    default: return UmeDoc::WideKind::None;
    }
}

} // namespace

namespace UmeDoc {

/* ---------------- 宽对象属性 ---------------- */

/* 表格的宽对象属性存在**表格格式**里：
   增删行列会重建单元格块，存在块上会丢。图片等则存块格式。 */
static QTextTable *tableOf(const QTextBlock &block)
{
    return block.isValid() ? QTextCursor(block).currentTable() : nullptr;
}

WideProps wideProps(const QTextBlock &block)
{
    WideProps p;
    if (!block.isValid())
        return p;

    QTextFormat fmt = block.blockFormat();
    if (QTextTable *table = tableOf(block)) {
        fmt = table->format();
        if (!fmt.hasProperty(PropKind) && table->rows() > 0 && table->columns() > 0)
            fmt = table->cellAt(0, 0).format();
    }
    if (!fmt.hasProperty(PropKind))
        return p;

    p.kind = intToKind(fmt.intProperty(PropKind));
    p.wrap = fmt.intProperty(PropWrap) == 1 ? WideWrap::Bubble : WideWrap::Span;
    p.span = qMax(1, fmt.intProperty(PropSpan));
    p.heightPt = fmt.doubleProperty(PropHeight);
    p.offsetPt = fmt.doubleProperty(PropOffset);
    p.keepAspect = fmt.boolProperty(PropKeepAspect);
    p.naturalW = fmt.doubleProperty(PropNaturalW);
    p.naturalH = fmt.doubleProperty(PropNaturalH);
    p.rotation = fmt.doubleProperty(PropRotation);
    p.imagePath = fmt.stringProperty(PropImagePath);
    p.flipH = fmt.boolProperty(PropFlipH);
    p.flipV = fmt.boolProperty(PropFlipV);
    return p;
}

void setWideProps(const QTextBlock &block, const WideProps &props)
{
    if (!block.isValid())
        return;

    QTextTable *table = tableOf(block);
    if (table) {
        QTextTableFormat tf = table->format();
        tf.setProperty(PropKind, kindToInt(props.kind));
        tf.setProperty(PropWrap, props.wrap == WideWrap::Bubble ? 1 : 0);
        tf.setProperty(PropSpan, qMax(1, props.span));
        tf.setProperty(PropHeight, props.heightPt);
        tf.setProperty(PropOffset, props.offsetPt);
        tf.setProperty(PropKeepAspect, props.keepAspect);
        tf.setProperty(PropNaturalW, props.naturalW);
        tf.setProperty(PropNaturalH, props.naturalH);
        tf.setProperty(PropRotation, props.rotation);
        tf.setProperty(PropImagePath, props.imagePath);
        tf.setProperty(PropFlipH, props.flipH);
        tf.setProperty(PropFlipV, props.flipV);
        table->setFormat(tf);
        return;
    }

    QTextCursor c(block);
    QTextBlockFormat bf = block.blockFormat();
    bf.setProperty(PropKind, kindToInt(props.kind));
    bf.setProperty(PropWrap, props.wrap == WideWrap::Bubble ? 1 : 0);
    bf.setProperty(PropSpan, qMax(1, props.span));
    bf.setProperty(PropHeight, props.heightPt);
    bf.setProperty(PropOffset, props.offsetPt);
    bf.setProperty(PropKeepAspect, props.keepAspect);
    bf.setProperty(PropNaturalW, props.naturalW);
    bf.setProperty(PropNaturalH, props.naturalH);
    bf.setProperty(PropRotation, props.rotation);
    bf.setProperty(PropImagePath, props.imagePath);
    bf.setProperty(PropFlipH, props.flipH);
    bf.setProperty(PropFlipV, props.flipV);
    c.setBlockFormat(bf);
}

QTextBlock insertImageBlock(QTextCursor &cursor, const QString &path,
                            const QSizeF &naturalSizePt, const WideProps &props)
{
    if (!cursor.document() || path.isEmpty())
        return QTextBlock();

    /* 图片块：空段落 + 宽对象属性；图片本身由视图按路径绘制。
       注意先移到**块尾**再插块 —— 停在块首插块时，原文本会被推进新块，
       结果「文本块」被当成图片对象跳过，整段文字消失（实测过）。 */
    QTextBlockFormat bf;
    bf.setBottomMargin(0);
    bf.setTopMargin(0);
    cursor.movePosition(QTextCursor::EndOfBlock);
    cursor.insertBlock(bf);
    const QTextBlock block = cursor.block();
    Q_ASSERT(block.text().isEmpty());

    WideProps p = props;
    p.kind = WideKind::Image;
    p.imagePath = path;
    p.naturalW = naturalSizePt.width();
    p.naturalH = naturalSizePt.height();
    setWideProps(block, p);
    return block;
}

bool isWideBlock(const QTextBlock &block)
{
    return wideProps(block).isValid();
}

/* ---------------- 超链接 ---------------- */

void applyLink(QTextCursor &cursor, const QUrl &url, const QString &linkText)
{
    if (!cursor.document() || url.isEmpty())
        return;

    QTextCharFormat fmt;
    fmt.setAnchor(true);
    fmt.setAnchorHref(url.toString());
    fmt.setFontUnderline(true);
    if (!fmt.hasProperty(QTextFormat::ForegroundBrush))
        fmt.setForeground(QColor(kLinkBlue));

    if (cursor.hasSelection()) {
        cursor.mergeCharFormat(fmt);
        return;
    }
    const QString text = linkText.isEmpty() ? url.toString() : linkText;
    cursor.insertText(text, fmt);
}

QUrl linkAt(QTextCursor cursor)
{
    const QTextCharFormat f = cursor.charFormat();
    if (f.isAnchor() && !f.anchorHref().isEmpty())
        return QUrl(f.anchorHref());

    QTextCursor prev = cursor;
    if (prev.position() > 0) {
        prev.setPosition(prev.position() - 1);
        const QTextCharFormat pf = prev.charFormat();
        if (pf.isAnchor() && !pf.anchorHref().isEmpty())
            return QUrl(pf.anchorHref());
    }
    return QUrl();
}

QStringList allLinks(const QTextDocument *doc)
{
    QStringList out;
    if (!doc)
        return out;

    for (QTextBlock b = doc->begin(); b.isValid(); b = b.next()) {
        for (auto it = b.begin(); !it.atEnd(); ++it) {
            const QTextFragment frag = it.fragment();
            if (!frag.isValid())
                continue;
            const QTextCharFormat f = frag.charFormat();
            if (!f.isAnchor() || f.anchorHref().isEmpty())
                continue;
            const QString href = f.anchorHref();
            if (!out.contains(href))
                out << href;
        }
    }
    return out;
}

void removeLink(QTextCursor &cursor)
{
    if (!cursor.hasSelection())
        return;
    QTextCharFormat fmt;
    fmt.setAnchor(false);
    fmt.clearProperty(QTextFormat::AnchorHref);
    cursor.mergeCharFormat(fmt);
}

/* ---------------- 表格 ---------------- */

bool inTable(QTextCursor cursor)
{
    return cursor.currentTable() != nullptr;
}

QPair<int, int> tableSize(QTextCursor cursor)
{
    if (QTextTable *t = cursor.currentTable())
        return {t->rows(), t->columns()};
    return {0, 0};
}

void insertTable(QTextCursor &cursor, int rows, int cols)
{
    if (!cursor.document() || rows <= 0 || cols <= 0)
        return;

    QTextTableFormat tf;
    tf.setCellPadding(4);
    tf.setCellSpacing(0);
    tf.setBorder(1);
    tf.setBorderBrush(QColor(0x99, 0x99, 0x99));

    QTextTable *table = cursor.insertTable(rows, cols, tf);
    if (!table)
        return;

    for (int c = 0; c < cols; ++c) {
        QTextTableCell cell = table->cellAt(0, c);
        QTextCharFormat head = cell.format();
        head.setFontWeight(QFont::Bold);
        cell.setFormat(head);

        QTextCursor cc = cell.firstCursorPosition();
        cc.insertText(QStringLiteral("列 %1").arg(c + 1), head);
    }

    cursor = (rows > 1) ? table->cellAt(1, 0).firstCursorPosition()
                        : table->cellAt(0, 0).firstCursorPosition();

    /* 表格所在的块打上宽对象属性，排版与面板据此识别 */
    WideProps p;
    p.kind = WideKind::Table;
    p.wrap = WideWrap::Span;
    p.span = qBound(1, cols, 12);
    p.heightPt = qMax(40.0, rows * 28.0);
    p.naturalW = p.span * 20.0;
    p.naturalH = p.heightPt;
    setWideProps(table->firstCursorPosition().block(), p);
}

bool changeTableRows(QTextCursor &cursor, int delta)
{
    QTextTable *t = cursor.currentTable();
    if (!t || delta == 0)
        return false;

    if (delta > 0) {
        const int row = qBound(0, t->cellAt(cursor).row() + 1, t->rows());
        t->insertRows(row, qMin(delta, 100));
        return true;
    }

    if (t->rows() <= 1)
        return false;
    const int row = qBound(0, t->cellAt(cursor).row(), t->rows() - 1);
    t->removeRows(row, qMin(-delta, t->rows() - 1));
    return true;
}

bool changeTableColumns(QTextCursor &cursor, int delta)
{
    QTextTable *t = cursor.currentTable();
    if (!t || delta == 0)
        return false;

    if (delta > 0) {
        const int col = qBound(0, t->cellAt(cursor).column() + 1, t->columns());
        t->insertColumns(col, qMin(delta, 100));
        return true;
    }

    if (t->columns() <= 1)
        return false;
    const int col = qBound(0, t->cellAt(cursor).column(), t->columns() - 1);
    t->removeColumns(col, qMin(-delta, t->columns() - 1));
    return true;
}

/* ---------------- 导出 ---------------- */

QString toHtml(const QTextDocument *doc, const QUrl &baseUrl)
{
    if (!doc)
        return QString();

    QString html = doc->toHtml();

    const QString css =
        QStringLiteral(
            "<style>"
            "body{margin:0;padding:0;}"
            "div.ume{"
            "  writing-mode:vertical-rl;"
            "  -webkit-writing-mode:vertical-rl;"
            "  -ms-writing-mode:tb-rl;"
            "  font-family:'Noto Sans Mongolian','SimSun','Times New Roman',serif;"
            "  line-height:1.5;"
            "}"
            "a{color:#0b67c2;text-decoration:underline;}"
            "table{border-collapse:collapse;}"
            "td,th{border:1px solid #999;padding:4px;}"
            "</style>");

    const int headEnd = html.indexOf(QStringLiteral("</head>"));
    if (headEnd >= 0)
        html.insert(headEnd, css);
    else
        html.prepend(css);

    if (baseUrl.isValid()) {
        const QString base = QStringLiteral("<base href=\"%1\">").arg(baseUrl.toString());
        const int h = html.indexOf(QStringLiteral("</head>"));
        if (h >= 0)
            html.insert(h, base);
    }
    return html;
}

} // namespace UmeDoc
