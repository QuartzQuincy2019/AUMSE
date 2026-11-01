#include "mainwindow.h"

#include "umelayoutbar.h"
#include "umesettings.h"
#include <QInputDialog>
#include <QLineEdit>
#include <QDialog>
#include <QDialogButtonBox>
#include <QFormLayout>
#include <QSpinBox>
#include <QToolBar>
#include "umeformatbar.h"
#include "umewidebar.h"
#include "umeview.h"

#include <QAction>
#include <QDockWidget>
#include <QFile>
#include <QFileDialog>
#include <QFileInfo>
#include <QFontDatabase>
#include <QLabel>
#include <QMenuBar>
#include <QMessageBox>
#include <QStatusBar>
#include <QTextDocument>
#include <QTextStream>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    /* 内置字体先加载，工具栏要按族名列表 */
    QFontDatabase::addApplicationFont(QStringLiteral(UME_FONT_DIR)
                                      + QStringLiteral("/NotoSansMongolian-Regular.ttf"));

    m_settings = new UmeSettings(this);
    m_doc = new QTextDocument(this);
    m_doc->setUndoRedoEnabled(true);

    buildUi();
    buildMenus();
    refreshStatus();

    /* 初始基础格式：内置 Noto 14pt 黑 */
    m_view->setBaseFormat(QStringLiteral("Noto Sans Mongolian"), 14.0, Qt::black);

    resize(1080, 940);
    setWindowTitle(QStringLiteral("UME · 回鹘蒙文编辑器"));
}

void MainWindow::buildUi()
{
    m_view = new UmeView(this);
    m_view->setSettings(m_settings);
    m_view->setDocument(m_doc);
    setCentralWidget(m_view);

    /* 「开始」工具栏只管文字格式：字体、字号、颜色 */
    addToolBar(Qt::TopToolBarArea, new UmeFormatBar(m_view, this));

    /* 布局控制区独立成停靠面板：可以关掉、可以拖走，
       与编辑区之间只有 UmeSettings 一条通道。 */
    auto *dock = new QDockWidget(QStringLiteral("布局控制"), this);
    m_layoutBar = new UmeLayoutBar(m_settings, dock);
    m_layoutBar->setMinimumWidth(260);
    dock->setWidget(m_layoutBar);
    dock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    addDockWidget(Qt::RightDockWidgetArea, dock);

    /* 「宽对象格式」：独立一层，与文字格式、版面设置互不共享状态。
       与布局控制并成标签页，避免右侧被占太宽。 */
    auto *wideDock = new QDockWidget(QStringLiteral("宽对象格式"), this);
    wideDock->setObjectName(QStringLiteral("umeWideDock"));
    wideDock->setWidget(new UmeWideBar(m_view, wideDock));
    addDockWidget(Qt::RightDockWidgetArea, wideDock);
    tabifyDockWidget(dock, wideDock);
    dock->raise();

    m_status = new QLabel(this);
    statusBar()->addWidget(m_status, 1);
    m_posLabel = new QLabel(this);
    statusBar()->addPermanentWidget(m_posLabel);

    connect(m_view, &UmeView::cursorPositionChanged, this, [this](int block, int col) {
        m_posLabel->setText(QStringLiteral("段 %1 · 第 %2 列").arg(block + 1).arg(col + 1));
    });
    connect(m_view, &UmeView::documentEdited, this, &MainWindow::refreshStatus);
    connect(m_settings, &UmeSettings::layoutChanged, this, &MainWindow::refreshStatus);

    m_view->setFocus();
}

void MainWindow::buildMenus()
{
    QMenu *file = menuBar()->addMenu(QStringLiteral("文件"));
    file->addAction(QStringLiteral("打开…"), QKeySequence::Open, this, &MainWindow::chooseOpen);
    file->addAction(QStringLiteral("另存为…"), QKeySequence::SaveAs, this, &MainWindow::chooseSave);

    file->addAction(QStringLiteral("导出 HTML…"), this, [this]() {
        const QString path = QFileDialog::getSaveFileName(
            this, QStringLiteral("导出 HTML"), QString(),
            QStringLiteral("HTML (*.html)"));
        if (path.isEmpty())
            return;
        QFile out(path);
        if (!out.open(QIODevice::WriteOnly | QIODevice::Text)) {
            statusBar()->showMessage(QStringLiteral("写入失败：%1").arg(path), 4000);
            return;
        }
        out.write(m_view->toHtml().toUtf8());
        out.close();
        statusBar()->showMessage(QStringLiteral("已导出 %1").arg(path), 4000);
    });

    /* 插入功能区：图片 / 表格 / 链接 */
    auto *insertBar = addToolBar(QStringLiteral("插入"));
    insertBar->setObjectName(QStringLiteral("umeInsertBar"));
    insertBar->setMovable(false);
    insertBar->addAction(QStringLiteral("图片…"), this, [this]() {
        const QString path = QFileDialog::getOpenFileName(
            this, QStringLiteral("插入图片"), QString(),
            QStringLiteral("图片 (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"));
        if (path.isEmpty())
            return;
        m_view->insertImage(path);
        statusBar()->showMessage(QStringLiteral("已插入图片 %1").arg(path), 3000);
    });
    insertBar->addAction(QStringLiteral("表格…"), this, [this]() { insertTableDialog(); });
    insertBar->addAction(QStringLiteral("链接…"), this, [this]() { insertLinkDialog(); });

    QMenu *insert = menuBar()->addMenu(QStringLiteral("插入"));
    insert->addAction(QStringLiteral("超链接…"), this, [this]() {
        bool ok = false;
        const QString url = QInputDialog::getText(
            this, QStringLiteral("插入超链接"), QStringLiteral("网址"),
            QLineEdit::Normal, QStringLiteral("https://"), &ok);
        if (!ok || url.trimmed().isEmpty())
            return;
        m_view->insertLink(QUrl(url.trimmed()));
        statusBar()->showMessage(QStringLiteral("已插入链接 %1").arg(url.trimmed()), 3000);
    });
    insert->addAction(QStringLiteral("图片…"), this, [this]() {
        const QString path = QFileDialog::getOpenFileName(
            this, QStringLiteral("插入图片"), QString(),
            QStringLiteral("图片 (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"));
        if (!path.isEmpty())
            m_view->insertImage(path);
    });
    insert->addAction(QStringLiteral("表格…"), this, [this]() { insertTableDialog(); });

    QMenu *edit = menuBar()->addMenu(QStringLiteral("编辑"));
    edit->addAction(QStringLiteral("撤销"), QKeySequence::Undo, this, [this]() {
        m_doc->undo();
        m_view->relayout();
    });
    edit->addAction(QStringLiteral("重做"), QKeySequence::Redo, this, [this]() {
        m_doc->redo();
        m_view->relayout();
    });
}

bool MainWindow::openFile(const QString &path)
{
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) {
        QMessageBox::warning(this, QStringLiteral("打开失败"), f.errorString());
        return false;
    }
    const QString text = QString::fromUtf8(f.readAll());
    f.close();

    if (path.endsWith(QStringLiteral(".html"), Qt::CaseInsensitive)
        || path.endsWith(QStringLiteral(".htm"), Qt::CaseInsensitive))
        m_doc->setHtml(text);
    else
        m_doc->setPlainText(text);

    m_path = path;
    m_view->resetBaseFont();     // 新文件统一成当前基础格式
    m_view->relayout();
    m_view->setTextCursor(QTextCursor(m_doc));
    m_view->update();
    refreshStatus();
    setWindowTitle(QStringLiteral("UME · ") + QFileInfo(path).fileName());
    m_view->setFocus();
    return true;
}

bool MainWindow::saveFile(const QString &path)
{
    QFile f(path);
    if (!f.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        QMessageBox::warning(this, QStringLiteral("保存失败"), f.errorString());
        return false;
    }
    const bool asHtml = path.endsWith(QStringLiteral(".html"), Qt::CaseInsensitive);
    const QString text = asHtml ? m_doc->toHtml() : m_doc->toPlainText();
    f.write(text.toUtf8());
    f.close();

    m_path = path;
    setWindowTitle(QStringLiteral("UME · ") + QFileInfo(path).fileName());
    return true;
}

void MainWindow::insertTableDialog()
{
    QDialog dlg(this);
    dlg.setWindowTitle(QStringLiteral("插入表格"));

    auto *form = new QFormLayout(&dlg);
    auto *rows = new QSpinBox(&dlg);
    rows->setRange(1, 200);
    rows->setValue(3);
    auto *cols = new QSpinBox(&dlg);
    cols->setRange(1, 20);
    cols->setValue(4);
    form->addRow(QStringLiteral("行数"), rows);
    form->addRow(QStringLiteral("列数"), cols);

    auto *hint = new QLabel(QStringLiteral("默认按「行外对象 + 列游标」插入，"
                                           "之后可在「宽对象格式」里改成文本围绕。"),
                            &dlg);
    hint->setWordWrap(true);
    form->addRow(hint);

    auto *buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel,
                                         &dlg);
    form->addRow(buttons);
    connect(buttons, &QDialogButtonBox::accepted, &dlg, &QDialog::accept);
    connect(buttons, &QDialogButtonBox::rejected, &dlg, &QDialog::reject);

    if (dlg.exec() != QDialog::Accepted)
        return;

    m_view->insertTable(rows->value(), cols->value());
    statusBar()->showMessage(
        QStringLiteral("已插入 %1×%2 表格").arg(rows->value()).arg(cols->value()), 3000);
}

void MainWindow::insertLinkDialog()
{
    bool ok = false;
    const QString url = QInputDialog::getText(
        this, QStringLiteral("插入超链接"), QStringLiteral("网址"),
        QLineEdit::Normal, QStringLiteral("https://"), &ok);
    if (!ok || url.trimmed().isEmpty())
        return;
    m_view->insertLink(QUrl(url.trimmed()));
    statusBar()->showMessage(QStringLiteral("已插入链接 %1").arg(url.trimmed()), 3000);
}

void MainWindow::chooseOpen()
{
    const QString path = QFileDialog::getOpenFileName(
        this, QStringLiteral("打开"), QString(),
        QStringLiteral("文本 (*.txt *.html *.htm);;所有文件 (*)"));
    if (!path.isEmpty())
        openFile(path);
}

void MainWindow::chooseSave()
{
    const QString path = QFileDialog::getSaveFileName(
        this, QStringLiteral("另存为"), m_path,
        QStringLiteral("纯文本 (*.txt);;HTML (*.html)"));
    if (!path.isEmpty())
        saveFile(path);
}

void MainWindow::refreshStatus()
{
    if (!m_status)
        return;
    const PageSetup &p = m_settings->page();
    m_status->setText(
        QStringLiteral("纸张 %1 × %2 pt　边距 左%3 右%4 上%5 下%6 pt　最小列宽 %7")
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
