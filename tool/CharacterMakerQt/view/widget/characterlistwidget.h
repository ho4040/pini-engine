#ifndef CHARACTERLISTWIDGET_H
#define CHARACTERLISTWIDGET_H

#include <lib/lib.h>

namespace Ui {
class Characterlistwidget;
}

class Characterlistwidget : public QDockWidget, IObserver
{
    Q_OBJECT

public:
    explicit Characterlistwidget(QWidget *parent = 0);
    ~Characterlistwidget();

    QTreeWidgetItem* addRoot(QString name);
    void addChild(QTreeWidgetItem *parent, QString name);

private slots:
    void on_charTreeWidget_customContextMenuRequested(const QPoint &pos);

    void insertRoot();
    void insertItem();
    void removeItem();

    void on_charTreeWidget_itemPressed(QTreeWidgetItem *item, int column);
    void on_charTreeWidget_itemDoubleClicked(QTreeWidgetItem *item, int column);

private:
    Ui::Characterlistwidget *ui;
    QMenu *charMenu;

    void onNotice(NOTIS e);
};

#endif // CHARACTERLISTWIDGET_H
