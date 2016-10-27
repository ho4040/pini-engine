#include "inspectordock.h"
#include "ui_inspectordock.h"
#include "QComboBox"
#include "QTreeWidgetItem"
#include "QSpinBox"
#include "colorproperty.h"
#include "ParticleSettingModel.h"
#include "consts.h"
#include "pathproperty.h"
#include <QDebug>

InspectorDock::InspectorDock(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::InspectorDock)
{
    ui->setupUi(this);

    ParticleSettingModel::shared()->addListener(this);

    QTreeWidgetItem * item = ui->treeWidget->topLevelItem(0);

    while(item)
    {
        QString key = item->text(0);
        for(int i =0 ; i < item->childCount();i++)
        {
            QTreeWidgetItem* childItem = item->child(i);

            QString childKey =childItem->text(0);

            if (childKey == tr("IsLoop")
                    ||childKey == tr("IsAutoRemoveOnFinish")
                    ||childKey == tr("IsFixedRotation"))
            {
                QComboBox *w = new QComboBox;
                w->addItem("True");
                w->addItem("False");

                ui->treeWidget->setItemWidget(childItem,1,w);

                connect(w,SIGNAL(currentIndexChanged(int)),this,SLOT(setData(int)));

            }
            else if (childKey == tr("PositionType"))
            {
                QComboBox *w = new QComboBox;
                w->addItem("Free");
                w->addItem("relative");
                w->addItem("Grouped");

                ui->treeWidget->setItemWidget(childItem,1,w);
                connect(w,SIGNAL(currentIndexChanged(int)),this,SLOT(setData(int)));
            }
            else if (childKey == tr("Mode"))
            {
                QComboBox *w = new QComboBox;
                w->addItem("Radius");
                w->addItem("Gravity");

                ui->treeWidget->setItemWidget(childItem,1,w);

                connect(w,SIGNAL(currentIndexChanged(int)),this,SLOT(setData(int)));
            }
            else if (key == tr("Color") )
            {
                ColorProperty *w = new ColorProperty;
                ui->treeWidget->setItemWidget(childItem,1,w);

                QLineEdit * lineEdit = w->getLineEdit();

                connect(lineEdit,SIGNAL(textChanged(QString)),this,SLOT(setData(QString)));
            }
            else if (childKey == tr("TexturePath") )
            {
                PathProperty *w = new PathProperty;
                ui->treeWidget->setItemWidget(childItem,1,w);

                QLineEdit * lineEdit = w->getLineEdit();

                connect(lineEdit,SIGNAL(textChanged(QString)),this,SLOT(setData(QString)));
            }
            else if (childKey == tr("DestBlendFunc") ||childKey == tr("SrcBlendFunc"))
            {
                QComboBox *w = new QComboBox;
                w->addItem("GL_ZERO");
                w->addItem("GL_ONE");
                w->addItem("GL_SRC_COLOR");
                w->addItem("GL_ONE_MINUS_SRC_COLOR");
                w->addItem("GL_DST_COLOR");
                w->addItem("GL_ONE_MINUS_DST_COLOR");
                w->addItem("GL_SRC_ALPHA");
                w->addItem("GL_ONE_MINUS_SRC_ALPHA");
                w->addItem("GL_DST_ALPHA");
                w->addItem("GL_ONE_MINUS_DST_ALPHA");
                w->addItem("GL_SRC_ALPHA_SATURATE");

                ui->treeWidget->setItemWidget(childItem,1,w);
                connect(w,SIGNAL(currentIndexChanged(int)),this,SLOT(setData(int)));
            }
            else
            {
                QSpinBox * w = new QSpinBox;

                w->setMaximum(999);
                w->setMinimum(-999);
                ui->treeWidget->setItemWidget(childItem,1,w);
                connect(w,SIGNAL(valueChanged(int)),this,SLOT(setData(int)));
            }
            childItem->setExpanded(true);
        }

        item = ui->treeWidget->itemBelow(item);

    }

    setData();
    ui->treeWidget->expandAll();

}

InspectorDock::~InspectorDock()
{
    delete ui;
}

void InspectorDock::setData()
{
    ParticleSettingModel::shared()->setData( getTreeWidgetData());
}

void InspectorDock::setData(int index)
{
    ParticleSettingModel::shared()->setData( getTreeWidgetData());
}

void InspectorDock::setData(QString index)
{
    ParticleSettingModel::shared()->setData( getTreeWidgetData());
}



void InspectorDock::onNotice(NOTIS e){
    if(e == ALL_UPDATE)
    {
        QJsonObject data = ParticleSettingModel::shared()->getData();
        setTreeWidgetData(data);
    }
}



QTreeWidget* InspectorDock::getTreeWidget()
{
    return ui->treeWidget;
}



QJsonObject  InspectorDock::getTreeWidgetData()
{

    QTreeWidgetItem * item = ui->treeWidget->topLevelItem(0);

    QJsonObject root;
    while(item)
    {
        QString key = item->text(0);
        QJsonObject child;
        for(int i =0 ; i < item->childCount();i++)
        {
            QTreeWidgetItem* childItem = item->child(i);

            QString childKey = childItem->text(0);

            if (childKey == "IsLoop"
                    ||childKey == "IsAutoRemoveOnFinish"
                    ||childKey == tr("IsFixedRotation"))
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->currentText());
            }
            else if (childKey == "PositionType")
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->currentText());
            }
            else if (childKey == "Mode")
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->currentText());
            }
            else if (key == tr("Color") )
            {
                ColorProperty *  w = (ColorProperty *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->text());

            }
            else if (childKey == tr("TexturePath") )
            {
                PathProperty *  w = (PathProperty *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->text());
            }
            else if (childKey == tr("DestBlendFunc") ||childKey == tr("SrcBlendFunc"))
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->currentText());
            }
            else
            {
                QSpinBox *  w = (QSpinBox *)ui->treeWidget->itemWidget(childItem,1);


                child.insert(childKey,w->value());
            }

            root.insert(key,child);
        }
        item = ui->treeWidget->itemBelow(item);

    }

    return root;
}


void InspectorDock::setTreeWidgetData(QJsonObject data)
{
    ui->treeWidget->blockSignals(true);
    QTreeWidgetItem * item = ui->treeWidget->topLevelItem(0);

    while(item)
    {

        QString key = item->text(0);
        QJsonObject childJson = data.value(key).toObject();


        for(int i =0 ; i < item->childCount();i++)
        {

            QTreeWidgetItem* childItem = item->child(i);

            QString childKey = childItem->text(0);



            if (childKey == "IsLoop"
                    ||childKey == "IsAutoRemoveOnFinish"
                    ||childKey == tr("IsFixedRotation"))
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);
                QString value = childJson.value(childKey).toString();
                int index = w->findText(value);
                w->setCurrentIndex(index);

            }
            else if (childKey == "PositionType")
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);
                QString value = childJson.value(childKey).toString();
                int index = w->findText(value);
                w->setCurrentIndex(index);

            }
            else if (childKey == "Mode")
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);
                QString value = childJson.value(childKey).toString();
                int index = w->findText(value);
                w->setCurrentIndex(index);

            }
            else if (key == tr("Color") )
            {

                ColorProperty *  w = (ColorProperty *)ui->treeWidget->itemWidget(childItem,1);
                QLineEdit * lineEdit = w->getLineEdit();

                lineEdit->blockSignals(true);
                QString value = childJson.value(childKey).toString();

                w->setText(value);
                lineEdit->blockSignals(false);
            }
            else if (childKey == tr("TexturePath") )
            {
                PathProperty *  w = (PathProperty *)ui->treeWidget->itemWidget(childItem,1);
                QLineEdit * lineEdit = w->getLineEdit();

                lineEdit->blockSignals(true);
                QString value = childJson.value(childKey).toString();

                w->setText(value);
                lineEdit->blockSignals(false);
            }
            else if (childKey == tr("DestBlendFunc") ||childKey == tr("SrcBlendFunc"))
            {
                QComboBox *  w = (QComboBox *)ui->treeWidget->itemWidget(childItem,1);
                QString value = childJson.value(childKey).toString();
                int index = w->findText(value);
                w->setCurrentIndex(index);

            }
            else
            {
                QSpinBox *  w = (QSpinBox *)ui->treeWidget->itemWidget(childItem,1);

                int value =childJson.value(childKey).toInt();
                w->setValue(value);

            }


        }
        item = ui->treeWidget->itemBelow(item);

    }
    ui->treeWidget->blockSignals(false);

}






















