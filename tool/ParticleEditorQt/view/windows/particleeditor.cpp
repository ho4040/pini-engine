#include "particleeditor.h"
#include "ui_particleeditor.h"
#include "inspectordock.h"
#include "filemanager.h"
#include "gldrawer.h"
#include <QFileDialog>
#include <QGridLayout>
#include <QVBoxLayout>
#include "hierarchydock.h"
#include "animationdock.h"


particleEditor::particleEditor(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::particleEditor)
{
    ui->setupUi(this);
    m_InspectorDock = new InspectorDock;
    this->addDockWidget(Qt::RightDockWidgetArea,m_InspectorDock);

//    m_HierarchyDock = new hierarchydock;
//    this->addDockWidget(Qt::LeftDockWidgetArea,m_HierarchyDock);

//    m_AnimaionDock = new animationdock;
//    this->addDockWidget(Qt::BottomDockWidgetArea,m_AnimaionDock);

    m_InspectorDock->getTreeWidget()->expandAll();


    m_GLDrawer = new GLDrawer();
    ui->tabWidget->addTab(m_GLDrawer,"particle");
}

particleEditor::~particleEditor()
{
    delete ui;
}




void particleEditor::on_actionSave_triggered()
{
    QFileDialog* pDialog = new QFileDialog(this);
    QString path = pDialog->getSaveFileName(this,"save");
    delete pDialog;

    FileManager::shared()->save(path);
}

void particleEditor::on_actionOpen_triggered()
{
    QFileDialog* pDialog = new QFileDialog(this);
    QString path = pDialog->getOpenFileName(this,"load");
    delete pDialog;

    FileManager::shared()->open(path);
}

void particleEditor::on_action_triggered()
{
    QFileDialog* pDialog = new QFileDialog(this);
    QString path = pDialog->getOpenFileName(this,"load");
    delete pDialog;
    ParticleSettingModel::shared()->setBackGroundImagePath(path);
}


