#include "umewidebar.h"

#include "umeicons.h"
#include "umeview.h"

#include <QCheckBox>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QRadioButton>
#include <QSpinBox>
#include <QToolButton>
#include <QVBoxLayout>

UmeWideBar::UmeWideBar(UmeView *view, QWidget *parent)
    : QWidget(parent)
    , m_view(view)
{
    buildUi();
    syncFromView();

    connect(m_view, &UmeView::formatStateChanged, this, &UmeWideBar::syncFromView);
    connect(m_view, &UmeView::cursorPositionChanged, this, [this](int, int) {
        syncFromView();
    });
}

void UmeWideBar::buildUi()
{
    auto *outer = new QVBoxLayout(this);
    outer->setContentsMargins(8, 8, 8, 8);
    outer->setSpacing(6);

    m_summary = new QLabel(this);
    m_summary->setWordWrap(true);
    outer->addWidget(m_summary);

    auto *modeRow = new QHBoxLayout;
    m_spanRadio = new QRadioButton(QStringLiteral("独占整列"), this);
    m_wrapRadio = new QRadioButton(QStringLiteral("文本围绕"), this);
    m_spanRadio->setToolTip(QStringLiteral("对象吃掉整列宽度，后面的文字从它下游开始"));
    m_wrapRadio->setToolTip(QStringLiteral("对象只占一块矩形，下面的文字从它底下接着排"));
    modeRow->addWidget(m_spanRadio);
    modeRow->addWidget(m_wrapRadio);
    modeRow->addStretch(1);
    outer->addLayout(modeRow);

    auto *form = new QFormLayout;
    form->setLabelAlignment(Qt::AlignLeft);

    m_spanBox = new QSpinBox(this);
    m_spanBox->setRange(1, 12);
    m_spanBox->setSuffix(QStringLiteral(" 列"));
    form->addRow(QStringLiteral("跨列数"), m_spanBox);

    m_heightBox = new QDoubleSpinBox(this);
    m_heightBox->setRange(8.0, 4000.0);
    m_heightBox->setDecimals(1);
    m_heightBox->setSingleStep(8.0);
    m_heightBox->setSuffix(QStringLiteral(" pt"));
    form->addRow(QStringLiteral("高度"), m_heightBox);

    m_keepAspect = new QCheckBox(QStringLiteral("缩放保持比例"), this);
    form->addRow(QString(), m_keepAspect);

    m_originalBtn = new QPushButton(QStringLiteral("原始尺寸"), this);
    form->addRow(QString(), m_originalBtn);

    auto *posRow = new QHBoxLayout;
    m_upBtn = new QPushButton(QStringLiteral("上移"), this);
    m_downBtn = new QPushButton(QStringLiteral("下移"), this);
    m_resetOffsetBtn = new QPushButton(QStringLiteral("复位"), this);
    posRow->addWidget(m_upBtn);
    posRow->addWidget(m_downBtn);
    posRow->addWidget(m_resetOffsetBtn);
    form->addRow(QStringLiteral("位置"), posRow);

    /* 图片格式区：只有图片才显示 */
    m_imageGroup = new QGroupBox(QStringLiteral("图片格式"), this);
    auto *imageForm = new QFormLayout(m_imageGroup);

    auto *mirrorRow = new QHBoxLayout;
    auto *mirrorLabel = new QLabel(QStringLiteral("图片"), this);
    mirrorLabel->setObjectName(QStringLiteral("mirrorLabel"));
    m_mirrorHBtn = new QToolButton(this);
    m_mirrorHBtn->setIcon(UmeIcons::flipHorizontal());
    m_mirrorHBtn->setIconSize(QSize(18, 18));
    m_mirrorHBtn->setCheckable(true);
    m_mirrorHBtn->setToolTip(QStringLiteral("水平镜像"));
    m_mirrorHBtn->setAutoRaise(true);
    m_mirrorVBtn = new QToolButton(this);
    m_mirrorVBtn->setIcon(UmeIcons::flipVertical());
    m_mirrorVBtn->setIconSize(QSize(18, 18));
    m_mirrorVBtn->setCheckable(true);
    m_mirrorVBtn->setToolTip(QStringLiteral("垂直镜像"));
    m_mirrorVBtn->setAutoRaise(true);
    mirrorRow->addWidget(mirrorLabel);
    mirrorRow->addWidget(m_mirrorHBtn);
    mirrorRow->addWidget(m_mirrorVBtn);
    mirrorRow->addStretch(1);
    imageForm->addRow(QStringLiteral("镜像"), mirrorRow);
    outer->addWidget(m_imageGroup);

    /* 表格格式区：只有表格才显示 */
    m_tableGroup = new QGroupBox(QStringLiteral("表格格式"), this);
    auto *tableForm = new QFormLayout(m_tableGroup);

    auto *tableRow = new QHBoxLayout;
    m_rowAdd = new QPushButton(QStringLiteral("+ 行"), this);
    m_rowDel = new QPushButton(QStringLiteral("− 行"), this);
    m_colAdd = new QPushButton(QStringLiteral("+ 列"), this);
    m_colDel = new QPushButton(QStringLiteral("− 列"), this);
    tableRow->addWidget(m_rowAdd);
    tableRow->addWidget(m_rowDel);
    tableRow->addWidget(m_colAdd);
    tableRow->addWidget(m_colDel);
    tableForm->addRow(QStringLiteral("行/列"), tableRow);
    outer->addWidget(m_tableGroup);

    outer->addLayout(form);
    outer->addStretch(1);

    /* 控件 → 视图 */
    auto changed = [this]() {
        if (!m_syncing)
            pushToView();
    };
    connect(m_spanRadio, &QRadioButton::toggled, this, changed);
    connect(m_spanBox, &QSpinBox::valueChanged, this, changed);
    connect(m_heightBox, &QDoubleSpinBox::valueChanged, this, changed);
    connect(m_keepAspect, &QCheckBox::toggled, this, changed);
    connect(m_mirrorHBtn, &QToolButton::clicked, this, [this](bool on) {
        if (m_syncing)
            return;
        UmeDoc::WideProps p = m_view->currentWideObject();
        if (!p.isValid())
            return;
        p.flipH = on;
        m_view->applyWideObject(p);
        syncFromView();
    });
    connect(m_mirrorVBtn, &QToolButton::clicked, this, [this](bool on) {
        if (m_syncing)
            return;
        UmeDoc::WideProps p = m_view->currentWideObject();
        if (!p.isValid())
            return;
        p.flipV = on;
        m_view->applyWideObject(p);
        syncFromView();
    });

    connect(m_originalBtn, &QPushButton::clicked, this, [this]() {
        UmeDoc::WideProps p = m_view->currentWideObject();
        if (!p.isValid() || p.naturalH <= 0.0)
            return;
        p.heightPt = p.naturalH;
        p.offsetPt = 0.0;
        m_view->applyWideObject(p);
        syncFromView();
    });
    connect(m_upBtn, &QPushButton::clicked, this, [this]() { m_view->nudgeWideObject(-8.0); });
    connect(m_downBtn, &QPushButton::clicked, this, [this]() { m_view->nudgeWideObject(8.0); });
    connect(m_resetOffsetBtn, &QPushButton::clicked, this, [this]() {
        UmeDoc::WideProps p = m_view->currentWideObject();
        if (!p.isValid())
            return;
        p.offsetPt = 0.0;
        m_view->applyWideObject(p);
    });

    connect(m_rowAdd, &QPushButton::clicked, this, [this]() { m_view->changeTableRows(1); });
    connect(m_rowDel, &QPushButton::clicked, this, [this]() { m_view->changeTableRows(-1); });
    connect(m_colAdd, &QPushButton::clicked, this, [this]() { m_view->changeTableColumns(1); });
    connect(m_colDel, &QPushButton::clicked, this, [this]() { m_view->changeTableColumns(-1); });
}

void UmeWideBar::syncFromView()
{
    const UmeDoc::WideProps p = m_view->currentWideObject();
    const bool wide = p.isValid();

    m_syncing = true;

    setEnabled(wide);
    if (!wide) {
        m_summary->setText(QStringLiteral("未选中宽对象：点一下图片或表格"));
        if (m_imageGroup)
            m_imageGroup->setVisible(false);
        if (m_tableGroup)
            m_tableGroup->setVisible(false);
        m_syncing = false;
        return;
    }

    const QString kind = (p.kind == UmeDoc::WideKind::Table) ? QStringLiteral("表格")
                                                             : QStringLiteral("图片");
    m_summary->setText(QStringLiteral("%1　跨 %2 列　高 %3 pt%4")
                           .arg(kind)
                           .arg(p.span)
                           .arg(p.heightPt, 0, 'f', 1)
                           .arg(qFuzzyIsNull(p.offsetPt)
                                    ? QString()
                                    : QStringLiteral("　偏移 %1 pt")
                                          .arg(p.offsetPt, 0, 'f', 1)));

    m_spanRadio->setChecked(p.wrap == UmeDoc::WideWrap::Span);
    m_wrapRadio->setChecked(p.wrap == UmeDoc::WideWrap::Bubble);
    m_spanBox->setValue(p.span);
    m_heightBox->setValue(p.heightPt);
    m_keepAspect->setChecked(p.keepAspect);
    m_mirrorHBtn->setChecked(p.flipH);
    m_mirrorVBtn->setChecked(p.flipV);

    /* 按对象类型切换两个分区 */
    const bool isTable = (p.kind == UmeDoc::WideKind::Table);
    const bool isImage = (p.kind == UmeDoc::WideKind::Image);
    m_imageGroup->setVisible(isImage);
    m_tableGroup->setVisible(isTable);

    m_rowAdd->setEnabled(isTable);
    m_rowDel->setEnabled(isTable);
    m_colAdd->setEnabled(isTable);
    m_colDel->setEnabled(isTable);

    m_syncing = false;
}

void UmeWideBar::pushToView()
{
    UmeDoc::WideProps p = m_view->currentWideObject();
    if (!p.isValid())
        return;

    p.wrap = m_spanRadio->isChecked() ? UmeDoc::WideWrap::Span : UmeDoc::WideWrap::Bubble;
    p.span = m_spanBox->value();
    p.heightPt = m_heightBox->value();
    p.keepAspect = m_keepAspect->isChecked();
    m_view->applyWideObject(p);
}
