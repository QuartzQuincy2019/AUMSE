#pragma once

#include <QImage>
#include <QTextCharFormat>
#include <QTextCursor>
#include <QTextDocument>
#include <QTextFragment>
#include <QTimer>
#include <QWidget>

#include "umelayout.h"
#include "umeformat.h"
#include "umepage.h"

class QScrollBar;
class UmeSettings;

/* 编辑区：竖排绘制 + 光标 + 命中 + 选区 + 键盘输入。
   它只读 UmeSettings，不认识工具栏、也不认识主窗口。 */
class UmeView : public QWidget
{
    Q_OBJECT
public:
    /* 载入新内容后调用：把当前字体整篇刷一遍，并同步块格式 */
    void resetBaseFont();

    explicit UmeView(QWidget *parent = nullptr);

    void setDocument(QTextDocument *doc);   // 不接管所有权
    QTextDocument *document() const { return m_doc; }

    /* 排版参数全从这个对象来；视图不自己存。 */
    void setSettings(UmeSettings *settings);
    UmeSettings *settings() const { return m_settings; }

    void setZoom(qreal zoom);
    qreal zoom() const { return m_zoom; }

    void relayout();

    /* 光标 */
    QTextCursor textCursor() const { return m_cursor; }
    void setTextCursor(const QTextCursor &c);

    /* 光标/选区上的格式状态（Word 语义：混合值用 mixed 标记） */
    UmeFormatState currentFormat() const;

    /* 用户改格式：有选区就改选区，没有就改「接下来输入的字」 */
    void applyFormatFamily(const QString &family);
    void applyFormatPointSize(qreal pt);
    void applyFormatColor(const QColor &c);

    /* 字符样式：粗体 / 斜体 / 下划线 / 删除线 / 上下标 */
    void applyCharStyle(int what, bool on);
    enum CharStyle { StyleBold, StyleItalic, StyleUnderline,
                     StyleStrikeOut, StyleSuper, StyleSub };

    /* ---- 为「链接 / 表格 / HTML」预留的接口 ---- */
    /* 插入链接：有选区就套在选区上，否则插入链接文字 */
    void insertLink(const QUrl &url, const QString &text = QString());
    /* 光标处的链接（没有则为空） */
    QUrl linkAtCursor() const;
    /* 插入 rows × cols 表格 */
    void insertTable(int rows, int cols);
    /* 导出 HTML（竖排 CSS 已注入） */
    QString toHtml() const;

    /* ---- 宽对象（表格 / 图片）：与文字格式完全解耦的一层 ---- */
    UmeDoc::WideProps currentWideObject() const;
    void applyWideObject(UmeDoc::WideProps props);
    void nudgeWideObject(qreal dy);
    void resizeWideObject(qreal newHeightPt, bool keepAspect);
    void changeTableRows(int delta);
    void changeTableColumns(int delta);
    QString wideObjectsProbe() const;
    /* 第 index 个宽对象的包围盒（不需要选中也能取） */
    QRectF wideItemBoxProbe(int index) const;
    int maxSpanForPageProbe() const { return maxSpanForPage(); }
    QSizeF contentSizeProbe() const { return m_layout.contentSize(); }
    void applyCharStyleProbe(int what, bool on) { applyCharStyle(what, on); }
    QRectF wideItemDocRectProbe(int i) const
    {
        const QVector<UmeLayout::WideItem> &it = m_layout.wideItems();
        return (i >= 0 && i < it.size()) ? m_layout.docRect(it.at(i)) : QRectF();
    }
    int wideItemPageProbe(int i) const
    {
        const QVector<UmeLayout::WideItem> &it = m_layout.wideItems();
        return (i >= 0 && i < it.size()) ? it.at(i).page : -1;
    }
    QRectF pageBoxProbe(int i) const { return m_layout.pageRectFor(i); }
    int tableFragmentCountProbe() const;
    QString tableFragmentsProbe() const;
    /* 该页上「起点低于页首」的列数；正常应为 0（除非被对象压住） */
    int colsOffTopProbe(int page) const;
    /* 滚动探针：{maxX, maxY, valueX, valueY, viewW, viewH} */
    QList<int> scrollRangeProbe() const;
    int pageCountProbe() const { return m_layout.pageCount(); }

    /* 插入行外图片（列游标模式） */
    void insertImage(const QString &path);
    /* 选中的宽对象（-1 表示没有）；选图片后才会出现控制手柄 */
    int selectedWideObject() const;
    void selectWideObject(int index);
    /* 删除选中的宽对象（Delete / Backspace） */
    void deleteSelectedWideObject();

    /* 表格手柄：内部行/列分隔线上的小方块 */
    QVector<QRectF> tableHandles(const UmeLayout::WideItem &item) const;
    int hitTableHandle(const QPointF &docPos, int *axis, int *index) const;
    /* 在宽对象所在块之后插入一个可输入的段落，光标移过去 */
    void insertParagraphAfterWide();
    /* 探针：9 个控制手柄的矩形（文档坐标） */
    QVector<QRectF> wideHandlesProbe() const;

    /* 载入文档时设定基础格式（字体/字号/颜色） */
    void setBaseFormat(const QString &family, qreal pt, const QColor &color = Qt::black);

    /* 离屏渲染 */
    QImage renderPageImage(int page, qreal scale, bool withCaret = false) const;
    QImage renderAllPages(qreal scale) const;

    QSize sizeHint() const override;

    /* 自检探针 */
    QRectF caretRectProbe() const { return caretDocRect(); }
    QColor caretColorProbe() const { return caretColor(); }
    int layoutTableBlocksProbe() const { return m_layout.tableBlocks(); }
    bool hitsAnyColumnProbe(const QPointF &p) const { return hitsAnyColumn(p); }
    QRectF columnBoxProbe(int i) const;
    /* 探针：直接在当前光标处输入（自检用） */
    void insertTextProbe(const QString &t) { insertTextAtCursor(t); }
    /* 探针：返回手柄 0..8 对应的光标名（自检用） */
    QString cursorProbe() const;
    QVector<QRectF> selectionRectsProbe() const { return selectionDocRects(); }
    QTextCursor cursorAtWidgetPosProbe(const QPointF &widgetPos) const
    {
        return cursorAtDocPos(docPosFromWidget(widgetPos));
    }
    QString metricsProbe() const;
    QString glyphProbe() const;
    /* 前 n 列的「左边界 / 宽度」，用来验证重排只影响右侧 */
    QString columnsProbe(int n = 4) const;

    /* 竖排方向判定：true = 直立（汉字/假名/韩文），false = 随列旋转。
       括号、破折号、引号、拉丁字母、数字一律旋转 —— 竖排里它们本来就转着用。 */
    /* 竖排里一个字的摆法 */
    enum class GlyphPlace {
        Rotated,     /* 随列旋转：蒙文、拉丁、数字、括号、书名号、破折号 */
        Center,      /* 直立居中：汉字、假名、韩文、问号、叹号 */
        TopRight     /* 直立贴右上角：句号、逗号、顿号、冒号、分号、引号 */
    };
    static GlyphPlace placeFor(QChar ch);
    static bool isUprightScript(QChar ch);

    /* 显式字体栈：主字体 + 中文回退 + 拉丁回退。
       给全了 Qt 就不必去扫系统字体表（首次遇到汉字要几百毫秒）。 */
    static QStringList fallbackFamilies(const QString &primary);

    /* 本机可用的中文字体（汉字与中文标点都用它排） */
    static QString cjkFamily();

    /* 汉字 / 中文标点：要用中文字体排的那一类 */
    static bool isCjkLike(QChar ch);

    /* 按脚本切段插入，让汉字落到中文字体上 */
    void insertTextByScript(const QString &text);

    /* 光标落在已着色的文字上时，把该颜色收作插入色 */
    void adoptColorAtCursor();

signals:
    void formatStateChanged();
    void cursorPositionChanged(int blockNumber, int columnInPage);
    void documentEdited();

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void mouseDoubleClickEvent(QMouseEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
    void inputMethodEvent(QInputMethodEvent *event) override;
    QVariant inputMethodQuery(Qt::InputMethodQuery query) const override;
    void wheelEvent(QWheelEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    /* 几何 */
    QRectF columnDocRect(const UmeLayout::Column &c) const;
    /* 字形在列里的落点：墨迹居中于列框 */
    qreal columnInkLeft(const UmeLayout::Column &c) const;
    QRectF caretDocRect() const;

    /* 光标颜色 = 接下来要输入的文字颜色（浅色自动压暗） */
    QColor caretColor() const;
    QVector<QRectF> selectionDocRects() const;
    QTextCursor cursorAtDocPos(const QPointF &docPos) const;
    int columnIndexForCursor() const;
    /* 这个点是否落在某一列的文字区域里（用于判断「空白处」） */
    bool hitsAnyColumn(const QPointF &docPos) const;
    QPointF docPosFromWidget(const QPointF &widgetPos) const;

    /* 绘制 */
    void paintDocument(QPainter &p) const;
    void paintGuides(QPainter &p) const;
    void paintSelection(QPainter &p) const;
    void paintCaret(QPainter &p) const;

    /* ---- 宽对象：绘制与交互 ---- */
    enum class WideDrag {
        None, Move, ResizeTL, ResizeTR, ResizeBL, ResizeBR,
        ResizeTop, ResizeBottom, ResizeLeft, ResizeRight, Rotate
    };
    const QImage &imageFor(const QString &path) const;
    void paintWideItems(QPainter &p) const;
    /* 画一条竖排列：正文与单元格共用，保证字形规则一致 */
    void drawVerticalLine(QPainter &p, const QTextLayout *lay,
                          const QTextLine &line, const QTextBlock &block,
                          const QRectF &columnRect, qreal baseX, qreal baseY,
                          const QColor &fallbackInk) const;

    void paintTableCells(QPainter &p, const UmeLayout::WideItem &item,
                         const QRectF &box) const;
    /* 把块的片段格式交给 layout —— 我们自己 beginLayout，不喂格式就只有默认样式 */
    static void setLayoutFormats(QTextLayout *lay, const QTextBlock &block);
    const UmeLayout::WideItem *selectedWideItem() const;
    /* 未旋转时 9 个手柄的中心点（四角 + 四边中点 + 旋转手柄） */
    QVector<QPointF> wideHandlePoints(const UmeLayout::WideItem &item) const;
    QVector<QRectF> wideHandles(const UmeLayout::WideItem &item) const;
    int hitWideHandle(const QPointF &docPos) const;
    /* 手柄 → 光标：方向随对象旋转一起转 */
    Qt::CursorShape cursorForWideHandle(int index) const;
    /* 本页最多能放几列（对象宽度不得超过正文区宽） */
    int maxSpanForPage() const;
    int hitWideItem(const QPointF &docPos) const;
    void applyWideDrag(const QPointF &docPos);

    mutable QHash<QString, QImage> m_images;   // 绘制期懒加载
    /* 选中的宽对象用**块位置**记，不用数组下标：
       每次重排都会重建 wideItems，下标会漂（实测选第 2 页的图却改到第 1 页）。 */
    int m_selectedWideBlock = -1;

    /* 表格专用手柄：0 = 调列宽（拖竖线），1 = 调行高（拖横线） */
    /* 选中的整行 / 整列（-1 = 没选）。格式会作用到该行/列全部单元格。 */
    int m_tableRow = -1;
    int m_tableCol = -1;

    int m_tableHandleAxis = -1;
    int m_tableHandleIndex = -1;
    WideDrag m_wideDrag = WideDrag::None;
    QPointF m_wideDragStart;
    UmeDoc::WideProps m_wideDragProps;
    void paintPreedit(QPainter &p) const;

    /* 移动 */
    void moveVertical(int dir, bool extend);
    void moveColumn(int dir, bool extend);
    void moveToColumnEdge(bool toEnd, bool extend);

    /* 编辑 */
    void insertTextAtCursor(const QString &text);
    void deleteChar(bool forward);
    void insertParagraph();
    void afterEdit();

    /* 把设置里的字体/字号真正刷到文档上。
       QTextDocument 只在「插入文字」那一刻把当时的字体记进片段格式，
       之后改 defaultFont 不会影响已有文字 —— 不刷的话，
       改字号只会改列距（= 行间距），字形一点不变。 */
    /* 整篇刷成基础格式（载入文件后用） */
    void applyBaseFontToDocument();

    /* 把 format 合并到选区（没有选区就并入基础格式） */
    void mergeFormatIntoSelection(const QTextCharFormat &fmt);

    void ensureCursorVisible();
    void restartBlink();
    void updateScrollBars();

    QTextDocument *m_doc = nullptr;
    UmeSettings *m_settings = nullptr;
    qreal m_zoom = 1.0;

    UmeLayout m_layout;
    qreal m_colPitch = 20.0;
    /* 拖曳缩放时用的「一列宽」，relayout 时记下 */
    qreal m_minWidthForDrag = 20.0;
    qreal m_autoPitch = 20.0;
    qreal m_ascent = 14.0;
    qreal m_descent = 4.0;
    qreal m_inkW = 16.0;        /* 实测墨迹宽度：给列距和光标用 */
    qreal m_inkAbove = 10.0;
    qreal m_inkBelow = 0.0;
    qreal m_inkPad = 2.0;

    qreal m_scrollY = 0.0;
    QScrollBar *m_vbar = nullptr;
    QScrollBar *m_hbar = nullptr;
    qreal m_scrollX = 0.0;

    QTextCursor m_cursor;
    bool m_blinkOn = true;
    QTimer m_blink;
    bool m_dragging = false;
    int m_dragAnchor = -1;      /* 拖曳起点（文档位置），别丢 */

    int m_paintedRevision = -1;   // 上一次画过的文档版本
    QString m_preedit;              // 输入法未上屏的串

    QTextCharFormat m_baseFormat;   // 当前基础字体（插入新字时用）
    /* 版面度量基准：列距、基线偏移只认这一组值。
       改选区字体时**不能**动它 —— 否则整页的列位置都会跟着跳。 */
    QString m_metricsFamily;
    qreal m_metricsPt = 0.0;

    QString m_appliedFamily;        // 上次整篇刷过的字体
    qreal m_appliedPt = 0.0;
};
