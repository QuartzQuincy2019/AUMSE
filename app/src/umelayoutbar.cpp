#include "umelayoutbar.h"

#include "umesettings.h"

#include <QCheckBox>
#include <QComboBox>
#include <QDoubleSpinBox>
#include <QFontDatabase>
#include <QFormLayout>
#include <QInputDialog>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>

UmeLayoutBar::UmeLayoutBar(UmeSettings *settings, QWidget *parent)
    : QWidget(parent)
    , m_settings(settings)
{
    buildUi();
    refreshSummary();
    connect(m_settings, &UmeSettings::layoutChanged, this, &UmeLayoutBar::refreshSummary);
}

QStringList UmeLayoutBar::availableFamilies()
{
    QStringList out;
    const QStringList families = QFontDatabase::families();

    if (families.contains(QStringLiteral("Noto Sans Mongolian")))
        out << QStringLiteral("Noto Sans Mongolian（内置）");

    for (const QString &f : {QStringLiteral("Mongolian Baiti"),
                             QStringLiteral("Menk Qimed Tig")}) {
        if (families.contains(f))
            out << f;
    }
    if (out.isEmpty())
        out << QStringLiteral("Noto Sans Mongolian");
    return out;
}

QString UmeLayoutBar::familyOf(const QString &label)
{
    const int i = label.indexOf(QStringLiteral("（"));
    return i < 0 ? label : label.left(i);
}

void UmeLayoutBar::buildUi()
{
    auto *form = new QFormLayout;
    form->setLabelAlignment(Qt::AlignRight);

    m_pitchBox = new QDoubleSpinBox(this);
    m_pitchBox->setRange(0.0, 200.0);
    m_pitchBox->setDecimals(1);
    m_pitchBox->setSingleStep(1.0);
    m_pitchBox->setValue(m_settings->columnPitch());
    m_pitchBox->setSpecialValueText(QStringLiteral("自动"));
    m_pitchBox->setSuffix(QStringLiteral(" pt"));
    m_pitchBox->setToolTip(
        QStringLiteral("列宽按每列内容自动计算；这里填的是「最小列宽」，0 = 自动"));
    form->addRow(QStringLiteral("最小列宽"), m_pitchBox);

    m_guideBox = new QCheckBox(QStringLiteral("显示页边距辅助线"), this);
    m_guideBox->setChecked(m_settings->marginGuides());
    form->addRow(QString(), m_guideBox);

    auto *pageBtn = new QPushButton(QStringLiteral("纸张与页边距…"), this);
    form->addRow(QString(), pageBtn);

    m_summary = new QLabel(this);
    m_summary->setWordWrap(true);
    m_summary->setStyleSheet(QStringLiteral("color:#666;font-size:12px"));

    auto *lay = new QVBoxLayout(this);
    lay->addLayout(form);
    lay->addWidget(m_summary);
    lay->addStretch(1);
    setLayout(lay);

    connect(m_pitchBox, &QDoubleSpinBox::valueChanged, m_settings,
            &UmeSettings::setColumnPitch);
    connect(m_guideBox, &QCheckBox::toggled, m_settings, &UmeSettings::setMarginGuides);
    connect(pageBtn, &QPushButton::clicked, this, &UmeLayoutBar::choosePage);
}

void UmeLayoutBar::choosePage()
{
    const QStringList names = PageSetup::presetNames();
    bool ok = false;
    const QString name = QInputDialog::getItem(
        this, QStringLiteral("纸张"), QStringLiteral("纸张尺寸："), names, 0, false, &ok);
    if (!ok)
        return;

    PageSetup page = PageSetup::preset(name);
    page.mLeft = m_settings->page().mLeft;
    page.mRight = m_settings->page().mRight;
    page.mTop = m_settings->page().mTop;
    page.mBottom = m_settings->page().mBottom;

    if (name == QStringLiteral("自定义")) {
        const QString spec = QInputDialog::getText(
            this, QStringLiteral("自定义纸张"),
            QStringLiteral("按「宽mm,高mm,左,右,上,下」填写："),
            QLineEdit::Normal, QStringLiteral("210,297,20,20,20,20"), &ok);
        if (!ok || spec.isEmpty())
            return;
        const QStringList parts = spec.split(QLatin1Char(','), Qt::SkipEmptyParts);
        if (parts.size() == 6) {
            auto mm2pt = [](double mm) { return mm * 72.0 / 25.4; };
            page.paper = QSizeF(mm2pt(parts[0].toDouble()), mm2pt(parts[1].toDouble()));
            page.mLeft = mm2pt(parts[2].toDouble());
            page.mRight = mm2pt(parts[3].toDouble());
            page.mTop = mm2pt(parts[4].toDouble());
            page.mBottom = mm2pt(parts[5].toDouble());
        }
    }
    m_settings->setPage(page);
}

void UmeLayoutBar::refreshSummary()
{
    const PageSetup &p = m_settings->page();
    m_summary->setText(
        QStringLiteral("纸张 %1 × %2 pt\n边距 左%3 右%4 上%5 下%6 pt\n最小列宽 %7")
            .arg(int(p.paper.width()))
            .arg(int(p.paper.height()))
            .arg(int(p.mLeft))
            .arg(int(p.mRight))
            .arg(int(p.mTop))
            .arg(int(p.mBottom))
            .arg(m_settings->columnPitchIsAuto()
                     ? QStringLiteral("自动")
                     : QString::number(m_settings->columnPitch(), 'f', 1)));
}
