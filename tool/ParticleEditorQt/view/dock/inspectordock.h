#ifndef INSPECTORDOCK_H
#define INSPECTORDOCK_H

#include <QDockWidget>
#include <QTreeWidget>
#include "iobserver.h"
#include <ParticleSettingModel.h>

namespace Ui {
class InspectorDock;
}



class InspectorDock : public QDockWidget , IObserver
{
    Q_OBJECT

public:
    explicit InspectorDock(QWidget *parent = 0);
    ~InspectorDock();

    QTreeWidget * getTreeWidget();
    void onNotice(int id);

//    ParticleData * getTreeWidgetData();
    QJsonObject getTreeWidgetData();

//    void setTreeWidgetData(ParticleData data);
    void setTreeWidgetData(QJsonObject data);

    void onNotice(NOTIS e);
private slots:
    void setData();
    void setData(int index);
    void setData(QString index);


private:
    Ui::InspectorDock *ui;
};

#endif // INSPECTORDOCK_H
