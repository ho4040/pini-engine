/********************************************************************************
** Form generated from reading UI file 'inspectordock.ui'
**
** Created by: Qt User Interface Compiler version 5.2.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_INSPECTORDOCK_H
#define UI_INSPECTORDOCK_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QDockWidget>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QTreeWidget>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_InspectorDock
{
public:
    QWidget *dockWidgetContents;
    QGridLayout *gridLayout;
    QTreeWidget *treeWidget;

    void setupUi(QDockWidget *InspectorDock)
    {
        if (InspectorDock->objectName().isEmpty())
            InspectorDock->setObjectName(QStringLiteral("InspectorDock"));
        InspectorDock->resize(1087, 613);
        dockWidgetContents = new QWidget();
        dockWidgetContents->setObjectName(QStringLiteral("dockWidgetContents"));
        gridLayout = new QGridLayout(dockWidgetContents);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        treeWidget = new QTreeWidget(dockWidgetContents);
        QBrush brush(QColor(0, 0, 0, 255));
        brush.setStyle(Qt::NoBrush);
        QBrush brush1(QColor(140, 140, 140, 255));
        brush1.setStyle(Qt::SolidPattern);
        QFont font;
        font.setPointSize(12);
        font.setBold(true);
        font.setWeight(75);
        font.setStrikeOut(false);
        QBrush brush2(QColor(0, 0, 0, 255));
        brush2.setStyle(Qt::Dense5Pattern);
        QBrush brush3(QColor(0, 0, 0, 255));
        brush3.setStyle(Qt::NoBrush);
        QFont font1;
        font1.setPointSize(12);
        font1.setBold(true);
        font1.setWeight(75);
        QTreeWidgetItem *__qtreewidgetitem = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem->setFont(0, font);
        __qtreewidgetitem->setBackground(0, brush1);
        __qtreewidgetitem->setForeground(0, brush);
        QTreeWidgetItem *__qtreewidgetitem1 = new QTreeWidgetItem(__qtreewidgetitem);
        __qtreewidgetitem1->setFlags(Qt::ItemIsSelectable|Qt::ItemIsEditable|Qt::ItemIsDragEnabled|Qt::ItemIsUserCheckable|Qt::ItemIsEnabled);
        __qtreewidgetitem1->setBackground(1, brush3);
        __qtreewidgetitem1->setForeground(1, brush2);
        QTreeWidgetItem *__qtreewidgetitem2 = new QTreeWidgetItem(__qtreewidgetitem);
        __qtreewidgetitem2->setFlags(Qt::ItemIsSelectable|Qt::ItemIsEditable|Qt::ItemIsDragEnabled|Qt::ItemIsUserCheckable|Qt::ItemIsEnabled);
        QTreeWidgetItem *__qtreewidgetitem3 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem3->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem3);
        QTreeWidgetItem *__qtreewidgetitem4 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem4->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem4);
        new QTreeWidgetItem(__qtreewidgetitem4);
        new QTreeWidgetItem(__qtreewidgetitem4);
        new QTreeWidgetItem(__qtreewidgetitem4);
        QTreeWidgetItem *__qtreewidgetitem5 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem5->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem5);
        new QTreeWidgetItem(__qtreewidgetitem5);
        new QTreeWidgetItem(__qtreewidgetitem5);
        new QTreeWidgetItem(__qtreewidgetitem5);
        new QTreeWidgetItem(__qtreewidgetitem5);
        new QTreeWidgetItem(__qtreewidgetitem5);
        QTreeWidgetItem *__qtreewidgetitem6 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem6->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem6);
        new QTreeWidgetItem(__qtreewidgetitem6);
        QTreeWidgetItem *__qtreewidgetitem7 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem7->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem7);
        new QTreeWidgetItem(__qtreewidgetitem7);
        new QTreeWidgetItem(__qtreewidgetitem7);
        new QTreeWidgetItem(__qtreewidgetitem7);
        new QTreeWidgetItem(__qtreewidgetitem7);
        QTreeWidgetItem *__qtreewidgetitem8 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem8->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem8);
        new QTreeWidgetItem(__qtreewidgetitem8);
        new QTreeWidgetItem(__qtreewidgetitem8);
        new QTreeWidgetItem(__qtreewidgetitem8);
        QTreeWidgetItem *__qtreewidgetitem9 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem9->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem9);
        new QTreeWidgetItem(__qtreewidgetitem9);
        new QTreeWidgetItem(__qtreewidgetitem9);
        new QTreeWidgetItem(__qtreewidgetitem9);
        new QTreeWidgetItem(__qtreewidgetitem9);
        new QTreeWidgetItem(__qtreewidgetitem9);
        QTreeWidgetItem *__qtreewidgetitem10 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem10->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        new QTreeWidgetItem(__qtreewidgetitem10);
        QTreeWidgetItem *__qtreewidgetitem11 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem11->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem11);
        new QTreeWidgetItem(__qtreewidgetitem11);
        new QTreeWidgetItem(__qtreewidgetitem11);
        new QTreeWidgetItem(__qtreewidgetitem11);
        QTreeWidgetItem *__qtreewidgetitem12 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem12->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem12);
        QTreeWidgetItem *__qtreewidgetitem13 = new QTreeWidgetItem(treeWidget);
        __qtreewidgetitem13->setFont(0, font1);
        new QTreeWidgetItem(__qtreewidgetitem13);
        new QTreeWidgetItem(__qtreewidgetitem13);
        new QTreeWidgetItem(__qtreewidgetitem13);
        new QTreeWidgetItem(__qtreewidgetitem13);
        treeWidget->setObjectName(QStringLiteral("treeWidget"));
        treeWidget->setItemsExpandable(true);
        treeWidget->setExpandsOnDoubleClick(true);

        gridLayout->addWidget(treeWidget, 0, 0, 1, 1);

        InspectorDock->setWidget(dockWidgetContents);

        retranslateUi(InspectorDock);

        QMetaObject::connectSlotsByName(InspectorDock);
    } // setupUi

    void retranslateUi(QDockWidget *InspectorDock)
    {
        InspectorDock->setWindowTitle(QApplication::translate("InspectorDock", "Inspector", 0));
        QTreeWidgetItem *___qtreewidgetitem = treeWidget->headerItem();
        ___qtreewidgetitem->setText(1, QApplication::translate("InspectorDock", "value", 0));
        ___qtreewidgetitem->setText(0, QApplication::translate("InspectorDock", "property", 0));

        const bool __sortingEnabled = treeWidget->isSortingEnabled();
        treeWidget->setSortingEnabled(false);
        QTreeWidgetItem *___qtreewidgetitem1 = treeWidget->topLevelItem(0);
        ___qtreewidgetitem1->setText(0, QApplication::translate("InspectorDock", "Angle", 0));
        QTreeWidgetItem *___qtreewidgetitem2 = ___qtreewidgetitem1->child(0);
        ___qtreewidgetitem2->setText(0, QApplication::translate("InspectorDock", "Angle", 0));
        QTreeWidgetItem *___qtreewidgetitem3 = ___qtreewidgetitem1->child(1);
        ___qtreewidgetitem3->setText(0, QApplication::translate("InspectorDock", "AngleVar", 0));
        QTreeWidgetItem *___qtreewidgetitem4 = treeWidget->topLevelItem(1);
        ___qtreewidgetitem4->setText(0, QApplication::translate("InspectorDock", "Loop", 0));
        QTreeWidgetItem *___qtreewidgetitem5 = ___qtreewidgetitem4->child(0);
        ___qtreewidgetitem5->setText(0, QApplication::translate("InspectorDock", "IsLoop", 0));
        QTreeWidgetItem *___qtreewidgetitem6 = treeWidget->topLevelItem(2);
        ___qtreewidgetitem6->setText(0, QApplication::translate("InspectorDock", "Size", 0));
        QTreeWidgetItem *___qtreewidgetitem7 = ___qtreewidgetitem6->child(0);
        ___qtreewidgetitem7->setText(0, QApplication::translate("InspectorDock", "EndSize", 0));
        QTreeWidgetItem *___qtreewidgetitem8 = ___qtreewidgetitem6->child(1);
        ___qtreewidgetitem8->setText(0, QApplication::translate("InspectorDock", "EndSizeVar", 0));
        QTreeWidgetItem *___qtreewidgetitem9 = ___qtreewidgetitem6->child(2);
        ___qtreewidgetitem9->setText(0, QApplication::translate("InspectorDock", "StartSize", 0));
        QTreeWidgetItem *___qtreewidgetitem10 = ___qtreewidgetitem6->child(3);
        ___qtreewidgetitem10->setText(0, QApplication::translate("InspectorDock", "StartSizeVar", 0));
        QTreeWidgetItem *___qtreewidgetitem11 = treeWidget->topLevelItem(3);
        ___qtreewidgetitem11->setText(0, QApplication::translate("InspectorDock", "Radius", 0));
        QTreeWidgetItem *___qtreewidgetitem12 = ___qtreewidgetitem11->child(0);
        ___qtreewidgetitem12->setText(0, QApplication::translate("InspectorDock", "EndRadius", 0));
        QTreeWidgetItem *___qtreewidgetitem13 = ___qtreewidgetitem11->child(1);
        ___qtreewidgetitem13->setText(0, QApplication::translate("InspectorDock", "EndRadiusVar", 0));
        QTreeWidgetItem *___qtreewidgetitem14 = ___qtreewidgetitem11->child(2);
        ___qtreewidgetitem14->setText(0, QApplication::translate("InspectorDock", "RotatePerSecond", 0));
        QTreeWidgetItem *___qtreewidgetitem15 = ___qtreewidgetitem11->child(3);
        ___qtreewidgetitem15->setText(0, QApplication::translate("InspectorDock", "RotatePerSecondVar", 0));
        QTreeWidgetItem *___qtreewidgetitem16 = ___qtreewidgetitem11->child(4);
        ___qtreewidgetitem16->setText(0, QApplication::translate("InspectorDock", "StartRadius", 0));
        QTreeWidgetItem *___qtreewidgetitem17 = ___qtreewidgetitem11->child(5);
        ___qtreewidgetitem17->setText(0, QApplication::translate("InspectorDock", "StartRadiusVar", 0));
        QTreeWidgetItem *___qtreewidgetitem18 = treeWidget->topLevelItem(4);
        ___qtreewidgetitem18->setText(0, QApplication::translate("InspectorDock", "Life", 0));
        QTreeWidgetItem *___qtreewidgetitem19 = ___qtreewidgetitem18->child(0);
        ___qtreewidgetitem19->setText(0, QApplication::translate("InspectorDock", "Life", 0));
        QTreeWidgetItem *___qtreewidgetitem20 = ___qtreewidgetitem18->child(1);
        ___qtreewidgetitem20->setText(0, QApplication::translate("InspectorDock", "LifeVar", 0));
        QTreeWidgetItem *___qtreewidgetitem21 = treeWidget->topLevelItem(5);
        ___qtreewidgetitem21->setText(0, QApplication::translate("InspectorDock", "Position", 0));
        QTreeWidgetItem *___qtreewidgetitem22 = ___qtreewidgetitem21->child(0);
        ___qtreewidgetitem22->setText(0, QApplication::translate("InspectorDock", "PositionType", 0));
        QTreeWidgetItem *___qtreewidgetitem23 = ___qtreewidgetitem21->child(1);
        ___qtreewidgetitem23->setText(0, QApplication::translate("InspectorDock", "PosVarX", 0));
        QTreeWidgetItem *___qtreewidgetitem24 = ___qtreewidgetitem21->child(2);
        ___qtreewidgetitem24->setText(0, QApplication::translate("InspectorDock", "PosVarY", 0));
        QTreeWidgetItem *___qtreewidgetitem25 = ___qtreewidgetitem21->child(3);
        ___qtreewidgetitem25->setText(0, QApplication::translate("InspectorDock", "SourcePositionX", 0));
        QTreeWidgetItem *___qtreewidgetitem26 = ___qtreewidgetitem21->child(4);
        ___qtreewidgetitem26->setText(0, QApplication::translate("InspectorDock", "SourcePositionY", 0));
        QTreeWidgetItem *___qtreewidgetitem27 = treeWidget->topLevelItem(6);
        ___qtreewidgetitem27->setText(0, QApplication::translate("InspectorDock", "Spin", 0));
        QTreeWidgetItem *___qtreewidgetitem28 = ___qtreewidgetitem27->child(0);
        ___qtreewidgetitem28->setText(0, QApplication::translate("InspectorDock", "EndSpin", 0));
        QTreeWidgetItem *___qtreewidgetitem29 = ___qtreewidgetitem27->child(1);
        ___qtreewidgetitem29->setText(0, QApplication::translate("InspectorDock", "EndSpinVar", 0));
        QTreeWidgetItem *___qtreewidgetitem30 = ___qtreewidgetitem27->child(2);
        ___qtreewidgetitem30->setText(0, QApplication::translate("InspectorDock", "StartSpin", 0));
        QTreeWidgetItem *___qtreewidgetitem31 = ___qtreewidgetitem27->child(3);
        ___qtreewidgetitem31->setText(0, QApplication::translate("InspectorDock", "StartSpinVar", 0));
        QTreeWidgetItem *___qtreewidgetitem32 = treeWidget->topLevelItem(7);
        ___qtreewidgetitem32->setText(0, QApplication::translate("InspectorDock", "Mode", 0));
        QTreeWidgetItem *___qtreewidgetitem33 = ___qtreewidgetitem32->child(0);
        ___qtreewidgetitem33->setText(0, QApplication::translate("InspectorDock", "Duration", 0));
        QTreeWidgetItem *___qtreewidgetitem34 = ___qtreewidgetitem32->child(1);
        ___qtreewidgetitem34->setText(0, QApplication::translate("InspectorDock", "EmissionRate", 0));
        QTreeWidgetItem *___qtreewidgetitem35 = ___qtreewidgetitem32->child(2);
        ___qtreewidgetitem35->setText(0, QApplication::translate("InspectorDock", "IsAutoRemoveOnFinish", 0));
        QTreeWidgetItem *___qtreewidgetitem36 = ___qtreewidgetitem32->child(3);
        ___qtreewidgetitem36->setText(0, QApplication::translate("InspectorDock", "Mode", 0));
        QTreeWidgetItem *___qtreewidgetitem37 = ___qtreewidgetitem32->child(4);
        ___qtreewidgetitem37->setText(0, QApplication::translate("InspectorDock", "TotalParticles", 0));
        QTreeWidgetItem *___qtreewidgetitem38 = ___qtreewidgetitem32->child(5);
        ___qtreewidgetitem38->setText(0, QApplication::translate("InspectorDock", "Temp", 0));
        QTreeWidgetItem *___qtreewidgetitem39 = treeWidget->topLevelItem(8);
        ___qtreewidgetitem39->setText(0, QApplication::translate("InspectorDock", "Move", 0));
        QTreeWidgetItem *___qtreewidgetitem40 = ___qtreewidgetitem39->child(0);
        ___qtreewidgetitem40->setText(0, QApplication::translate("InspectorDock", "GravityAngle", 0));
        QTreeWidgetItem *___qtreewidgetitem41 = ___qtreewidgetitem39->child(1);
        ___qtreewidgetitem41->setText(0, QApplication::translate("InspectorDock", "GravitySpeed", 0));
        QTreeWidgetItem *___qtreewidgetitem42 = ___qtreewidgetitem39->child(2);
        ___qtreewidgetitem42->setText(0, QApplication::translate("InspectorDock", "RadialAccel", 0));
        QTreeWidgetItem *___qtreewidgetitem43 = ___qtreewidgetitem39->child(3);
        ___qtreewidgetitem43->setText(0, QApplication::translate("InspectorDock", "RadialAccelVar", 0));
        QTreeWidgetItem *___qtreewidgetitem44 = ___qtreewidgetitem39->child(4);
        ___qtreewidgetitem44->setText(0, QApplication::translate("InspectorDock", "Speed", 0));
        QTreeWidgetItem *___qtreewidgetitem45 = ___qtreewidgetitem39->child(5);
        ___qtreewidgetitem45->setText(0, QApplication::translate("InspectorDock", "SpeedVar", 0));
        QTreeWidgetItem *___qtreewidgetitem46 = ___qtreewidgetitem39->child(6);
        ___qtreewidgetitem46->setText(0, QApplication::translate("InspectorDock", "TagentialAccel", 0));
        QTreeWidgetItem *___qtreewidgetitem47 = ___qtreewidgetitem39->child(7);
        ___qtreewidgetitem47->setText(0, QApplication::translate("InspectorDock", "TagentiAlAccelVar", 0));
        QTreeWidgetItem *___qtreewidgetitem48 = treeWidget->topLevelItem(9);
        ___qtreewidgetitem48->setText(0, QApplication::translate("InspectorDock", "Texture", 0));
        QTreeWidgetItem *___qtreewidgetitem49 = ___qtreewidgetitem48->child(0);
        ___qtreewidgetitem49->setText(0, QApplication::translate("InspectorDock", "DestBlendFunc", 0));
        QTreeWidgetItem *___qtreewidgetitem50 = ___qtreewidgetitem48->child(1);
        ___qtreewidgetitem50->setText(0, QApplication::translate("InspectorDock", "SrcBlendFunc", 0));
        QTreeWidgetItem *___qtreewidgetitem51 = ___qtreewidgetitem48->child(2);
        ___qtreewidgetitem51->setText(0, QApplication::translate("InspectorDock", "TextureImageData", 0));
        QTreeWidgetItem *___qtreewidgetitem52 = ___qtreewidgetitem48->child(3);
        ___qtreewidgetitem52->setText(0, QApplication::translate("InspectorDock", "TexturePath", 0));
        QTreeWidgetItem *___qtreewidgetitem53 = treeWidget->topLevelItem(10);
        ___qtreewidgetitem53->setText(0, QApplication::translate("InspectorDock", "Scale", 0));
        QTreeWidgetItem *___qtreewidgetitem54 = ___qtreewidgetitem53->child(0);
        ___qtreewidgetitem54->setText(0, QApplication::translate("InspectorDock", "Scale", 0));
        QTreeWidgetItem *___qtreewidgetitem55 = treeWidget->topLevelItem(11);
        ___qtreewidgetitem55->setText(0, QApplication::translate("InspectorDock", "Color", 0));
        QTreeWidgetItem *___qtreewidgetitem56 = ___qtreewidgetitem55->child(0);
        ___qtreewidgetitem56->setText(0, QApplication::translate("InspectorDock", "EndColor", 0));
        QTreeWidgetItem *___qtreewidgetitem57 = ___qtreewidgetitem55->child(1);
        ___qtreewidgetitem57->setText(0, QApplication::translate("InspectorDock", "EndColorVar", 0));
        QTreeWidgetItem *___qtreewidgetitem58 = ___qtreewidgetitem55->child(2);
        ___qtreewidgetitem58->setText(0, QApplication::translate("InspectorDock", "StartColor", 0));
        QTreeWidgetItem *___qtreewidgetitem59 = ___qtreewidgetitem55->child(3);
        ___qtreewidgetitem59->setText(0, QApplication::translate("InspectorDock", "StartColorVar", 0));
        treeWidget->setSortingEnabled(__sortingEnabled);

    } // retranslateUi

};

namespace Ui {
    class InspectorDock: public Ui_InspectorDock {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_INSPECTORDOCK_H
