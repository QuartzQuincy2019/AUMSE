#pragma once

#include <QToolBar>

#include "umeformat.h"

class QComboBox;
class QDoubleSpinBox;
class QToolButton;
class UmeView;

/* 「开始」工具栏：字体、字号、颜色。
   它只做两件事：
     · 光标/选区一变，把控件显示成对应的值（混合值就留空）
     · 用户一改，把值交给视图去应用到选区 */
class UmeFormatBar : public QToolBar
{
    Q_OBJECT
public:
    explicit UmeFormatBar(UmeView *view, QWidget *parent = nullptr);

private:
    void buildUi();
    void syncFromView();

    UmeView *m_view = nullptr;
    QComboBox *m_fontBox = nullptr;
    QDoubleSpinBox *m_sizeBox = nullptr;
    QToolButton *m_colorBtn = nullptr;
    bool m_syncing = false;   // 防止「同步控件」反过来触发应用
};
