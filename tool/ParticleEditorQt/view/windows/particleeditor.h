#ifndef PARTICLEEDITOR_H
#define PARTICLEEDITOR_H

#include <QMainWindow>
#include <inspectordock.h>
#include <gldrawer.h>
#include "hierarchydock.h"
#include "animationdock.h"

namespace Ui {
class particleEditor;
}

class InspectorDock;

class particleEditor : public QMainWindow
{
    Q_OBJECT

public:
    explicit particleEditor(QWidget *parent = 0);
    ~particleEditor();



private slots:


    void on_actionSave_triggered();

    void on_actionOpen_triggered();

    void on_action_triggered();

private:



    Ui::particleEditor *ui;
    InspectorDock * m_InspectorDock;
    hierarchydock * m_HierarchyDock;
    animationdock * m_AnimaionDock;

    GLDrawer *m_GLDrawer;
};

#endif // PARTICLEEDITOR_H
