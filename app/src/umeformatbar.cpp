#include "umeformatbar.h"

#include "umeicons.h"
#include "umeview.h"
#include "umelayoutbar.h"   // 复用 availableFamilies()

#include <QActionGroup>
#include <QColorDialog>
#include <QMenu>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QFontDatabase>
#include <QLabel>
#include <QPainter>
#include <QPixmap>
#include <QGridLayout>
#include <QToolButton>
#include <QWidgetAction>

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

    /* 字符样式：图标按钮，可选中（表示当前选区就是这种样式） */
    struct StyleSpec { QToolButton **slot; QIcon icon; QString tip; int what; };
    const StyleSpec specs[] = {
        {&m_boldBtn, UmeIcons::bold(), QStringLiteral("加粗"), UmeView::StyleBold},
        {&m_italicBtn, UmeIcons::italic(), QStringLiteral("倾斜"), UmeView::StyleItalic},
        {&m_underlineBtn, UmeIcons::underline(), QStringLiteral("下划线"),
         UmeView::StyleUnderline},
        {&m_strikeBtn, UmeIcons::strikeOut(), QStringLiteral("删除线"),
         UmeView::StyleStrikeOut},
        {&m_superBtn, UmeIcons::superscript(), QStringLiteral("上标"), UmeView::StyleSuper},
        {&m_subBtn, UmeIcons::subscript(), QStringLiteral("下标"), UmeView::StyleSub},
    };

    addWidget(new QLabel(QStringLiteral("  "), this));
    for (const StyleSpec &spec : specs) {
        auto *btn = new QToolButton(this);
        btn->setIcon(spec.icon);
        btn->setIconSize(QSize(18, 18));
        btn->setCheckable(true);
        btn->setToolTip(spec.tip);
        btn->setAutoRaise(true);
        addWidget(btn);
        *spec.slot = btn;

        const int what = spec.what;
        connect(btn, &QToolButton::clicked, this, [this, btn, what](bool on) {
            if (m_syncing) {
                btn->setChecked(!on);
                return;
            }
            m_view->applyCharStyle(what, on);
        });
    }

    addWidget(new QLabel(QStringLiteral("  颜色 "), this));
    m_colorBtn = new QToolButton(this);
    m_colorBtn->setToolTip(QStringLiteral("选中文本的颜色；多种颜色混排时留空"));
    m_colorBtn->setPopupMode(QToolButton::InstantPopup);
    m_colorBtn->setMenu(buildColorMenu());
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
    /* 颜色由菜单处理，见 buildColorMenu() */
}

namespace {

/* 常用色板：黑白灰 + 常用彩色，够日常标注用 */
const char *const kPalette[] = {
    "#000000", "#3a3a3a", "#7f7f7f", "#b0b0b0",
    "#c00000", "#e36c0a", "#bf9000", "#548235",
    "#2e75b6", "#1f4e79", "#7030a0", "#a03070",
};

} // namespace

QMenu *UmeFormatBar::buildColorMenu()
{
    auto *menu = new QMenu(this);

    auto *autoAct = menu->addAction(QStringLiteral("自动（黑色）"));
    connect(autoAct, &QAction::triggered, this, [this]() {
        m_view->applyFormatColor(Qt::black);
    });

    menu->addSeparator();
    menu->addAction(QStringLiteral("常用颜色"))->setEnabled(false);

    /* 色板用网格：四行三列，每个色块做成带图标的动作 */
    auto *grid = new QWidget(menu);
    auto *layout = new QGridLayout(grid);
    layout->setContentsMargins(8, 4, 8, 4);
    layout->setSpacing(4);

    int i = 0;
    for (const char *hex : kPalette) {
        const QColor c{QString::fromLatin1(hex)};
        auto *btn = new QToolButton(grid);
        btn->setIcon(swatch(c, false));
        btn->setIconSize(QSize(18, 18));
        btn->setAutoRaise(true);
        btn->setToolTip(c.name(QColor::HexRgb));
        connect(btn, &QToolButton::clicked, this, [this, c, menu]() {
            m_view->applyFormatColor(c);
            menu->hide();
        });
        layout->addWidget(btn, i / 4, i % 4);
        ++i;
    }

    auto *gridAct = new QWidgetAction(menu);
    gridAct->setDefaultWidget(grid);
    menu->addAction(gridAct);

    menu->addSeparator();
    auto *moreAct = menu->addAction(QStringLiteral("更多颜色…"));
    connect(moreAct, &QAction::triggered, this, [this]() {
        const UmeFormatState s = m_view->currentFormat();
        const QColor c = QColorDialog::getColor(
            s.color.isValid() && !s.colorMixed ? s.color : QColor(Qt::black),
            this, QStringLiteral("文字颜色"));
        if (c.isValid())
            m_view->applyFormatColor(c);
    });

    return menu;
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

    m_boldBtn->setChecked(s.bold && !s.boldMixed);
    m_italicBtn->setChecked(s.italic && !s.italicMixed);
    m_underlineBtn->setChecked(s.underline && !s.underlineMixed);
    m_strikeBtn->setChecked(s.strikeOut && !s.strikeMixed);
    m_superBtn->setChecked(s.script == 1 && !s.scriptMixed);
    m_subBtn->setChecked(s.script == -1 && !s.scriptMixed);

    m_syncing = false;
}
