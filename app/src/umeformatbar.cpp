#include "umeformatbar.h"

#include "umeview.h"
#include "umelayoutbar.h"   // 复用 availableFamilies()

#include <QColorDialog>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QFontDatabase>
#include <QLabel>
#include <QPainter>
#include <QPixmap>
#include <QToolButton>

namespace {

/* 颜色按钮上的小色块；混合色时画一条斜线 */
QIcon swatch(const QColor &c, bool mixed)
{
    QPixmap pm(18, 18);
    pm.fill(Qt::transparent);
    QPainter p(&pm);
    p.setRenderHint(QPainter::Antialiasing, true);
    if (mixed) {
        p.setPen(QPen(QColor(0x88, 0x88, 0x88), 1));
        p.setBrush(Qt::white);
        p.drawRect(1, 1, 15, 15);
        p.setPen(QPen(QColor(0xcc, 0x33, 0x33), 2));
        p.drawLine(2, 16, 16, 2);
    } else {
        p.setPen(QPen(QColor(0x99, 0x99, 0x99), 1));
        p.setBrush(c);
        p.drawRect(1, 1, 15, 15);
    }
    p.end();
    return QIcon(pm);
}

} // namespace

UmeFormatBar::UmeFormatBar(UmeView *view, QWidget *parent)
    : QToolBar(parent)
    , m_view(view)
{
    setWindowTitle(QStringLiteral("开始"));
    setMovable(false);
    buildUi();
    syncFromView();

    connect(m_view, &UmeView::formatStateChanged, this, &UmeFormatBar::syncFromView);
}

void UmeFormatBar::buildUi()
{
    addWidget(new QLabel(QStringLiteral(" 字体 "), this));

    m_fontBox = new QComboBox(this);
    m_fontBox->addItems(UmeLayoutBar::availableFamilies());
    m_fontBox->setMinimumWidth(200);
    m_fontBox->setPlaceholderText(QStringLiteral("多种字体"));   // index = -1 时显示
    m_fontBox->setToolTip(QStringLiteral("选中文本的字体；多种字体混排时留空"));
    addWidget(m_fontBox);

    addWidget(new QLabel(QStringLiteral("  字号 "), this));
    m_sizeBox = new QDoubleSpinBox(this);
    m_sizeBox->setRange(1.0, 200.0);
    m_sizeBox->setDecimals(1);
    m_sizeBox->setSingleStep(1.0);
    m_sizeBox->setSuffix(QStringLiteral(" pt"));
    m_sizeBox->setSpecialValueText(QStringLiteral("多种"));      // value = minimum 时
    m_sizeBox->setToolTip(QStringLiteral("选中文本的字号；多种字号混排时留空"));
    addWidget(m_sizeBox);

    addWidget(new QLabel(QStringLiteral("  颜色 "), this));
    m_colorBtn = new QToolButton(this);
    m_colorBtn->setToolTip(QStringLiteral("选中文本的颜色；多种颜色混排时留空"));
    addWidget(m_colorBtn);

    /* 用户改控件 → 应用到选区（同步期间不响应，避免回环） */
    connect(m_fontBox, &QComboBox::currentIndexChanged, this, [this](int idx) {
        if (m_syncing || idx < 0)
            return;
        m_view->applyFormatFamily(UmeLayoutBar::familyOf(m_fontBox->currentText()));
    });
    connect(m_sizeBox, &QDoubleSpinBox::valueChanged, this, [this](double v) {
        if (m_syncing || v <= m_sizeBox->minimum())
            return;
        m_view->applyFormatPointSize(v);
    });
    connect(m_colorBtn, &QToolButton::clicked, this, [this]() {
        const QColor c = QColorDialog::getColor(
            m_view->currentFormat().color.isValid() ? m_view->currentFormat().color
                                                    : Qt::black,
            this, QStringLiteral("文字颜色"));
        if (c.isValid())
            m_view->applyFormatColor(c);
    });
}

void UmeFormatBar::syncFromView()
{
    const UmeFormatState s = m_view->currentFormat();

    m_syncing = true;

    if (s.familyMixed) {
        m_fontBox->setCurrentIndex(-1);           // 留空，显示 placeholder
    } else {
        const int idx = m_fontBox->findText(
            s.family, Qt::MatchStartsWith);
        m_fontBox->setCurrentIndex(idx);
    }

    if (s.sizeMixed) {
        m_sizeBox->setValue(m_sizeBox->minimum());   // 显示「多种」
    } else if (s.pointSize > 0.0) {
        m_sizeBox->setValue(s.pointSize);
    }

    m_colorBtn->setIcon(swatch(s.colorMixed ? Qt::white : s.color, s.colorMixed));

    m_syncing = false;
}
