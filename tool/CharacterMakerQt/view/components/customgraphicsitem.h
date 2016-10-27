#ifndef CUSTOMGRAPHICSITEM_H
#define CUSTOMGRAPHICSITEM_H

#include <lib/lib.h>

class CustomGraphicsItem : public QGraphicsItem
{
public:

	CustomGraphicsItem();
	CustomGraphicsItem(qreal x, qreal y, qreal w, qreal h);

	QRectF boundingRect() const;
	void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget = 0);
	void setBrush(const QBrush &brush);
	void setItemIndex(int index);
	void setLayerIndex(int index);
	void setShapeType(QString type);
	void setTextInfo(QString textInfo);
	int getItemIndex();
	int getLayerIndex();

protected:

private:
	int _layerIndex;
	int _itemIndex;
	QRectF _boundingRect;
	QBrush _brush;
	QString _shapeType;
	QString _textInfo;
};

#endif // CUSTOMGRAPHICSITEM_H
