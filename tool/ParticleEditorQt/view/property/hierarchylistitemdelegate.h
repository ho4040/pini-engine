#ifndef HIERARCHYLISTITEMDELEGATE_H
#define HIERARCHYLISTITEMDELEGATE_H

#include <QItemDelegate>

class hierarchylistitem;
class HierarchyListModel;

class HierarchyListItemDelegate : public QItemDelegate
{
public:
    HierarchyListItemDelegate();
    ~HierarchyListItemDelegate();

//    virtual void paint(QPainter * painter, const QStyleOptionViewItem & option, const QModelIndex & index) const;
//    virtual QSize sizeHint(const QStyleOptionViewItem & option, const QModelIndex & index) const;
protected:
    hierarchylistitem * _itemWidget;
    HierarchyListModel* m_pModel;

    QPixmap mIconUnlock;
    QPixmap mIconLock;
    QPixmap mIconVisible;
    QPixmap mIconInvisible;
};

#endif // HIERARCHYLISTITEMDELEGATE_H
