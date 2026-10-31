#pragma once

#include <QObject>
#include <QString>

#include "umepage.h"

/* 排版设置：页面、字体、字号、列距、辅助线。
   —— 这一份东西同时被「布局控制区」写、被「编辑区」读，
   两边互不认识，只共享这个对象。它变了就发 changed()，
   视图收到后重排一次。 */
class UmeSettings : public QObject
{
    Q_OBJECT
public:
    explicit UmeSettings(QObject *parent = nullptr) : QObject(parent) {}

    const PageSetup &page() const { return m_page; }
    void setPage(const PageSetup &p)
    {
        if (p.paper == m_page.paper && qFuzzyCompare(p.mLeft, m_page.mLeft)
            && qFuzzyCompare(p.mRight, m_page.mRight)
            && qFuzzyCompare(p.mTop, m_page.mTop)
            && qFuzzyCompare(p.mBottom, m_page.mBottom))
            return;
        m_page = p;
        emit layoutChanged();
    }

    /* 最小列宽；<= 0 表示自动（按内容算列宽） */
    qreal columnPitch() const { return m_pitch; }
    void setColumnPitch(qreal pt)
    {
        if (qFuzzyCompare(pt, m_pitch))
            return;
        m_pitch = pt;
        emit layoutChanged();
    }
    bool columnPitchIsAuto() const { return m_pitch <= 0.0; }

    bool marginGuides() const { return m_guides; }
    void setMarginGuides(bool on)
    {
        if (on == m_guides)
            return;
        m_guides = on;
        emit layoutChanged();
    }

signals:
    /* 页面 / 最小列宽 / 辅助线 变了 —— 需要整篇重排 */
    void layoutChanged();

private:
    PageSetup m_page;
    qreal m_pitch = 0.0;
    bool m_guides = true;
};
