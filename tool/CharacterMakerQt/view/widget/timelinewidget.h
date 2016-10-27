#ifndef TIMELINEWIDGET_H
#define TIMELINEWIDGET_H

#include <lib/lib.h>

namespace Ui {
class TimelineWidget;
}

class GraphicsScene;

class TimelineWidget : public QDockWidget, IObserver
{
    Q_OBJECT

public:
    explicit TimelineWidget(QWidget *parent = 0);
    ~TimelineWidget();
    void drawTimelineLayer();
	void drawTimelineName();

private slots:
    void on_sb_totalFrame_valueChanged(int arg1);
    void on_sb_totalFrame_editingFinished();
    void on_cb_emotionList_currentIndexChanged(const QString &arg1);
    void on_sb_frameDelay_valueChanged(int arg1);
    void on_sb_frameDelay_editingFinished();
    void on_timelineView_customContextMenuRequested(const QPoint &pos);
    void insertKeyFrame();
    void deleteKeyFrame();
    void insertLayer();
	void deleteLayer();

protected:
    void mouseMoveEvent(QMouseEvent * event);

private:
    Ui::TimelineWidget *ui;
    GraphicsScene* scene;
    QGraphicsEllipseItem *ellipse;
    QGraphicsRectItem *rectangle;

    QMenu *_ptimeLineMenu;

    void onNotice(NOTIS e);
    int fileNum;
};

#endif // TIMELINEWIDGET_H
