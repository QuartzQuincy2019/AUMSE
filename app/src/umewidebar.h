#pragma once

#include <QWidget>

#include "umedoc.h"

class QLabel;
class QRadioButton;
class QSpinBox;
class QDoubleSpinBox;
class QCheckBox;
class QPushButton;
class QToolButton;
class UmeView;

/* 「宽对象格式控制」——独立于文字格式与版面设置的一层。
   只在光标落在表格 / 图片这类横跨多列的对象里时启用。
   它只认 UmeDoc::WideProps，不碰文字格式，也不碰页面设置。 */
class UmeWideBar : public QWidget
{
    Q_OBJECT
public:
    explicit UmeWideBar(UmeView *view, QWidget *parent = nullptr);

private:
    void buildUi();
    void syncFromView();          // 光标/对象变化 → 控件
    void pushToView();            // 控件变化 → 视图（整份属性一起写回）

    UmeView *m_view = nullptr;
    bool m_syncing = false;

    QLabel *m_summary = nullptr;
    QRadioButton *m_spanRadio = nullptr;
    QRadioButton *m_wrapRadio = nullptr;
    QSpinBox *m_spanBox = nullptr;
    QDoubleSpinBox *m_heightBox = nullptr;
    QCheckBox *m_keepAspect = nullptr;
    QPushButton *m_originalBtn = nullptr;
    QPushButton *m_upBtn = nullptr;
    QPushButton *m_downBtn = nullptr;
    QPushButton *m_resetOffsetBtn = nullptr;
    QPushButton *m_rowAdd = nullptr;
    QPushButton *m_rowDel = nullptr;
    QPushButton *m_colAdd = nullptr;
    QPushButton *m_colDel = nullptr;

    /* 图片镜像 */
    QToolButton *m_mirrorHBtn = nullptr;
    QToolButton *m_mirrorVBtn = nullptr;
};
