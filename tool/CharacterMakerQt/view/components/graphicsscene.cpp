#include "graphicsscene.h"

GraphicsScene::GraphicsScene()
{
}
GraphicsScene::GraphicsScene(qreal x, qreal y, qreal width, qreal height, QObject *parent)
    : QGraphicsScene(x, y, width, height, parent)
{

}

QPointF GraphicsScene::getTimelineMousePos()
{
	return _mousePos;
}

void GraphicsScene::keyFrameLineUpdate(int keyFrameIndex)
{
	_redLinePos.setX(KEYFRAMESTARTX + (keyFrameIndex * KEYFRAMESIZEX) + KEYFRAMESIZEX / 2);
}

void GraphicsScene::mouseMoveEvent(QGraphicsSceneMouseEvent *move)
{
    //qDebug() << "x : " << move->scenePos().x()<< "  " << "y : " << move->scenePos().y() << endl;

}

void GraphicsScene::mousePressEvent(QGraphicsSceneMouseEvent *e)
{
	//qDebug() << "mousePressEvent" << endl;

    _mousePos = e->scenePos();

	CustomGraphicsItem *item = (CustomGraphicsItem*)this->itemAt(_mousePos,QTransform());

    if(e->button() == Qt::LeftButton)
    {
		if(item)
		{
			int layerIndex = item->getLayerIndex();
			int keyFrameindex = item->getItemIndex();

			CommandListModel::shared()->runCommand(new LayerSelectCmd(layerIndex));
			CommandListModel::shared()->runCommand(new KeyFrameSelectCmd(keyFrameindex));
		}
    }
    else if(e->button() == Qt::RightButton)
    {
//		QGraphicsRectItem *pSelectItem = (QGraphicsRectItem *)this->itemAt(e->scenePos().rx(),e->scenePos().ry(),QTransform());
//		if(pSelectItem)
//		{
//			pSelectItem->setBrush(Qt::blue);
//		}
    }
}

void GraphicsScene::drawForeground(QPainter * painter, const QRectF & rect)
{
//	if(CurrentFrameModel::shared()->getKeyFrame())
	if(CurrentLayerModel::shared()->getLayer())
	{
		painter->setPen(QPen(Qt::red, 1));
		//painter->drawLine(_mousePos.x(), rect.top(), _mousePos.x(), rect.bottom());
		painter->drawLine(_redLinePos.x(), rect.top(), _redLinePos.x(), rect.bottom());
	}
}
