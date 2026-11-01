#include "umelogwindow.h"

#include "umelog.h"

#include <QCheckBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QVBoxLayout>

namespace {
const char *const kCategories[] = {
    "log", "layout", "edit", "cursor", "ime", "format", "wide", "image", "table", "font", "paint",
};
}

UmeLogWindow::UmeLogWindow(QWidget *parent)
    : QDockWidget(QStringLiteral("调试日志"), parent)
{
    setObjectName(QStringLiteral("umeLogDock"));

    auto *body = new QWidget(this);
    auto *outer = new QVBoxLayout(body);
    outer->setContentsMargins(6, 6, 6, 6);
    outer->setSpacing(4);

    /* 第一行：搜索 + 暂停 + 清空 */
    auto *tools = new QHBoxLayout;
    m_search = new QLineEdit(body);
    m_search->setPlaceholderText(QStringLiteral("过滤关键字…"));
    m_search->setClearButtonEnabled(true);
    m_pause = new QCheckBox(QStringLiteral("暂停"), body);
    auto *clearBtn = new QPushButton(QStringLiteral("清空"), body);
    tools->addWidget(m_search, 1);
    tools->addWidget(m_pause);
    tools->addWidget(clearBtn);
    outer->addLayout(tools);

    /* 第二行：分类勾选 */
    auto *cats = new QHBoxLayout;
    cats->setSpacing(6);
    for (const char *c : kCategories) {
        auto *box = new QCheckBox(QLatin1String(c), body);
        box->setChecked(true);
        m_enabled << QLatin1String(c);
        connect(box, &QCheckBox::toggled, this, [this, name = QString(QLatin1String(c))](bool on) {
            if (on) {
                if (!m_enabled.contains(name))
                    m_enabled << name;
            } else {
                m_enabled.removeAll(name);
            }
        });
        cats->addWidget(box);
    }
    cats->addStretch(1);
    outer->addLayout(cats);

    m_view = new QPlainTextEdit(body);
    m_view->setReadOnly(true);
    m_view->setMaximumBlockCount(4000);       // 自动丢弃最旧的，防止长跑内存涨
    m_view->setLineWrapMode(QPlainTextEdit::NoWrap);
    QFont mono = m_view->font();
    mono.setFamilies({QStringLiteral("Consolas"), QStringLiteral("Courier New")});
    mono.setPointSizeF(9.0);
    m_view->setFont(mono);
    outer->addWidget(m_view, 1);

    m_counter = new QLabel(body);
    outer->addWidget(m_counter);

    setWidget(body);

    connect(umeLogSink(), &UmeLogSink::appended, this, &UmeLogWindow::appendLine);
    connect(clearBtn, &QPushButton::clicked, this, &UmeLogWindow::clearAll);
    connect(m_search, &QLineEdit::textChanged, this, &UmeLogWindow::rebuildFilter);
}

bool UmeLogWindow::categoryEnabled(const QString &category) const
{
    return m_enabled.contains(category);
}

void UmeLogWindow::appendLine(const QString &category, const QString &line)
{
    if (m_pause->isChecked())
        return;
    if (!categoryEnabled(category))
        return;

    const QString needle = m_search->text().trimmed();
    if (!needle.isEmpty() && !line.contains(needle, Qt::CaseInsensitive))
        return;

    m_view->appendPlainText(line);
    ++m_total;
    m_counter->setText(QStringLiteral("共 %1 行（最多保留 4000 行）").arg(m_total));
}

void UmeLogWindow::rebuildFilter()
{
    /* 搜索词变化时不做回溯过滤（日志是流式的），只提示当前条件 */
    const QString needle = m_search->text().trimmed();
    m_counter->setText(needle.isEmpty()
                           ? QStringLiteral("共 %1 行").arg(m_total)
                           : QStringLiteral("共 %1 行，仅显示包含「%2」的新行")
                                 .arg(m_total)
                                 .arg(needle));
}

void UmeLogWindow::clearAll()
{
    m_view->clear();
    m_total = 0;
    m_counter->setText(QStringLiteral("已清空"));
}
