#pragma once

#include <QMainWindow>

class QLabel;
class QTextDocument;
class UmeLayoutBar;
class UmeSettings;
class UmeView;

/* 主窗口只做组装：
     布局控制区（UmeLayoutBar，右侧可停靠）
     编辑区（UmeView，中央）
   两边只共享 UmeSettings，彼此不认识。 */
class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

    bool openFile(const QString &path);
    bool saveFile(const QString &path);

    UmeView *view() const { return m_view; }
    UmeSettings *settings() const { return m_settings; }

private slots:
    void chooseOpen();
    void chooseSave();
    void refreshStatus();

private:
    void buildUi();
    void buildMenus();

    UmeSettings *m_settings = nullptr;
    UmeView *m_view = nullptr;
    UmeLayoutBar *m_layoutBar = nullptr;
    QTextDocument *m_doc = nullptr;
    QLabel *m_status = nullptr;
    QLabel *m_posLabel = nullptr;
    QString m_path;
};
