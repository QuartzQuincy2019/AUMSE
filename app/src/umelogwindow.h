#pragma once

#include <QDockWidget>

class QPlainTextEdit;
class QLineEdit;
class QCheckBox;
class QLabel;

/* 调试日志窗口：把 UmeLogSink 的实时日志显示出来，可按分类过滤。
   与主窗口只有一条信号连接，不影响编辑逻辑。 */
class UmeLogWindow : public QDockWidget
{
    Q_OBJECT
public:
    explicit UmeLogWindow(QWidget *parent = nullptr);

private:
    void appendLine(const QString &category, const QString &line);
    void rebuildFilter();
    bool categoryEnabled(const QString &category) const;
    void clearAll();

    QPlainTextEdit *m_view = nullptr;
    QLineEdit *m_search = nullptr;
    QLabel *m_counter = nullptr;
    QCheckBox *m_pause = nullptr;
    QStringList m_enabled;       // 当前勾选的分类
    int m_total = 0;
};
