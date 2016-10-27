#ifndef FRAMEINFOWIDGET_H
#define FRAMEINFOWIDGET_H

#include <QDockWidget>
#include <lib/lib.h>

namespace Ui {
class FrameInfoWidget;
}

class FrameInfoWidget : public QDockWidget, IObserver
{
    Q_OBJECT

public:
    explicit FrameInfoWidget(QWidget *parent = 0);
    ~FrameInfoWidget();

private slots:
    void on_undoButton_clicked();

private:
    Ui::FrameInfoWidget *ui;
    void onNotice(NOTIS e);
};

#endif // FRAMEINFOWIDGET_H
