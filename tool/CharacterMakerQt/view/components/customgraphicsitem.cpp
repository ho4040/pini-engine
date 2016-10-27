#include "customgraphicsitem.h"

CustomGraphicsItem::CustomGraphicsItem()
{
}

CustomGraphicsItem::CustomGraphicsItem(qreal x, qreal y, qreal w, qreal h)
{
	_brush = Qt::white;
	_boundingRect.setRect(x, y, w, h);
}

QRectF CustomGraphicsItem::boundingRect() const
{
	return _boundingRect;
}

void CustomGraphicsItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget)
{

	painter->setBrush(_brush);

	if("RECT" == _shapeType)
	{
		painter->setBrush(Qt::white);
		painter->drawRect(_boundingRect);
		painter->drawText(_boundingRect, Qt::AlignCenter, QString::number(_itemIndex));
	}
	else if("FILLRECT" == _shapeType)
	{
		painter->drawRect(_boundingRect);
		painter->setOpacity(0.2);
		painter->fillRect(_boundingRect, Qt::blue);
	}
	else if("TIMELINE_NAME" == _shapeType)
	{
		painter->drawRect(_boundingRect);
		painter->drawText(_boundingRect, Qt::AlignCenter, _textInfo);
	}
	else if("SELECT_TIMELINE_NAME" == _shapeType)
	{
		painter->drawRect(_boundingRect);
		painter->drawText(_boundingRect, Qt::AlignCenter, _textInfo);
		painter->setOpacity(0.2);
		painter->fillRect(_boundingRect, Qt::red);
	}

	QGraphicsItem::update();
}

void CustomGraphicsItem::setBrush(const QBrush &brush)
{
	_brush = brush;
}
void CustomGraphicsItem::setItemIndex(int index)
{
	_itemIndex = index;
}

void CustomGraphicsItem::setLayerIndex(int index)
{
	_layerIndex = index;
}

void CustomGraphicsItem::setShapeType(QString type)
{
	_shapeType = type;
}

void CustomGraphicsItem::setTextInfo(QString textInfo)
{
	_textInfo = textInfo;
}

int CustomGraphicsItem::getItemIndex()
{
	return _itemIndex;
}

int CustomGraphicsItem::getLayerIndex()
{
	return _layerIndex;
}
