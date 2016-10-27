#ifndef HIERARCHYLISTITEM_H
#define HIERARCHYLISTITEM_H

#include <QWidget>

namespace Ui {
class hierarchylistitem;
}

class hierarchylistitem : public QWidget
{
    Q_OBJECT

public:
    explicit hierarchylistitem(QWidget *parent = 0);
    ~hierarchylistitem();

private:
    Ui::hierarchylistitem *ui;
};

#endif // HIERARCHYLISTITEM_H
