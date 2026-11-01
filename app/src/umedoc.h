#pragma once

#include <QString>
#include <QUrl>
#include <QTextBlock>

class QTextDocument;
class QTextCursor;

/* 「宽对象」的文档层模型与操作。
   宽对象 = 表格 / 图片这类**在竖排里横跨多列**的块级对象。
   只做纯数据与表格结构操作，不含任何界面与绘制。 */
namespace UmeDoc {

enum class WideKind { None, Table, Image };

/* 排版方式 */
enum class WideWrap {
    Span,   /* 独占整列（列游标）：吃掉 K 列，后面的文字从它下游开始 */
    Bubble, /* 文本围绕：对象占一块矩形，下面的文字从它底下接着排 */
};

struct WideProps
{
    WideKind kind = WideKind::None;
    WideWrap wrap = WideWrap::Span;
    int span = 3;              /* 跨几列 */
    qreal heightPt = 120.0;    /* 沿列方向的高度 */
    qreal offsetPt = 0.0;      /* 拖曳产生的纵向偏移 */
    bool keepAspect = true;    /* 缩放是否保持比例 */
    qreal naturalW = 0.0;      /* 原始尺寸（用于「原始大小」按钮） */
    qreal naturalH = 0.0;
    qreal rotation = 0.0;      /* 旋转角度（度，顺时针） */
    bool flipH = false;        /* 水平镜像 */
    bool flipV = false;        /* 垂直镜像 */
    QString imagePath;         /* 图片对象：源文件路径 */

    bool isValid() const { return kind != WideKind::None; }
    bool operator==(const WideProps &o) const
    {
        return kind == o.kind && wrap == o.wrap && span == o.span
               && qFuzzyCompare(heightPt, o.heightPt)
               && qFuzzyCompare(offsetPt, o.offsetPt)
               && keepAspect == o.keepAspect
               && qFuzzyCompare(rotation, o.rotation)
               && flipH == o.flipH && flipV == o.flipV
               && imagePath == o.imagePath;
    }
    bool operator!=(const WideProps &o) const { return !(*this == o); }
};

/* 块格式里的自定义属性编号（避开 Qt 已用的段） */
enum PropId {
    PropKind = QTextFormat::UserProperty + 0x51,
    PropWrap,
    PropSpan,
    PropHeight,
    PropOffset,
    PropKeepAspect,
    PropNaturalW,
    PropNaturalH,
    PropRotation,
    PropImagePath,
    PropFlipH,
    PropFlipV,
};

/* 读 / 写块上的宽对象属性 */
WideProps wideProps(const QTextBlock &block);
void setWideProps(const QTextBlock &block, const WideProps &props);
bool isWideBlock(const QTextBlock &block);

/* 插入一个图片块（行外图片，列游标模式），返回新块 */
QTextBlock insertImageBlock(QTextCursor &cursor, const QString &path,
                            const QSizeF &naturalSizePt, const WideProps &props);

/* ---- 超链接 ---- */

void applyLink(QTextCursor &cursor, const QUrl &url, const QString &linkText);
QUrl linkAt(QTextCursor cursor);
QStringList allLinks(const QTextDocument *doc);
void removeLink(QTextCursor &cursor);

/* ---- 表格 ---- */

bool inTable(QTextCursor cursor);
QPair<int, int> tableSize(QTextCursor cursor);
void insertTable(QTextCursor &cursor, int rows, int cols);

bool changeTableRows(QTextCursor &cursor, int delta);
bool changeTableColumns(QTextCursor &cursor, int delta);

/* ---- 导出 ---- */

QString toHtml(const QTextDocument *doc, const QUrl &baseUrl = QUrl());

} // namespace UmeDoc
