#ifndef MYGRAPHICSVIEW_H
#define MYGRAPHICSVIEW_H

#include <lib/lib.h>

class MyGraphicsView : public QGraphicsView
{
    Q_OBJECT

public:
    explicit MyGraphicsView(QWidget *parent = 0);

signals:
    void sendMousePoint(QPointF point);

public slots:
    void mousePressEvent(QMouseEvent * e);
    void mouseMoveEvent (QMouseEvent *move);

private:
    QGraphicsScene * scene;
};

#endif // MYGRAPHICSVIEW_H
