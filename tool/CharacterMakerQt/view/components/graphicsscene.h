#ifndef GRAPHICSSCENE_H
#define GRAPHICSSCENE_H

#include <lib/lib.h>

class GraphicsScene : public QGraphicsScene
{
public:
    GraphicsScene();
    GraphicsScene(qreal x, qreal y, qreal width, qreal height, QObject *parent = 0);

    QPointF getTimelineMousePos();

	void keyFrameLineUpdate(int keyFrameIndex);

protected:
    void mouseMoveEvent(QGraphicsSceneMouseEvent *move);
    void mousePressEvent(QGraphicsSceneMouseEvent *e);
    void drawForeground(QPainter * painter, const QRectF & rect);

private:
	QPointF	_mousePos;
	QPointF	_redLinePos;
};

#endif // GRAPHICSSCENE_H
