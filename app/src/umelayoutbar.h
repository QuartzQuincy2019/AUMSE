#pragma once

#include <QWidget>

class QCheckBox;
class QComboBox;
class QDoubleSpinBox;
class QLabel;
class UmeSettings;

/* 布局控制区：只负责改 UmeSettings，不碰文档、不碰视图。
   左边是编辑区，这里就是那块「布局」面板 —— 两块之间只有
   UmeSettings 一个数据通道。 */
class UmeLayoutBar : public QWidget
{
    Q_OBJECT
public:
    explicit UmeLayoutBar(UmeSettings *settings, QWidget *parent = nullptr);

    /* 可选字体：内置 Noto 一定在；Baiti / Qimed 只按族名探测 */
    static QStringList availableFamilies();
    static QString familyOf(const QString &label);

private:
    void buildUi();
    void choosePage();
    void refreshSummary();

    UmeSettings *m_settings = nullptr;
    QComboBox *m_fontBox = nullptr;
    QDoubleSpinBox *m_sizeBox = nullptr;
    QDoubleSpinBox *m_pitchBox = nullptr;
    QCheckBox *m_guideBox = nullptr;
    QLabel *m_summary = nullptr;
};
