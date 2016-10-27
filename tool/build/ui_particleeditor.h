/********************************************************************************
** Form generated from reading UI file 'particleeditor.ui'
**
** Created by: Qt User Interface Compiler version 5.2.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PARTICLEEDITOR_H
#define UI_PARTICLEEDITOR_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_particleEditor
{
public:
    QAction *actionNew;
    QAction *actionOpen;
    QAction *actionSave;
    QAction *actionSave_as;
    QAction *action;
    QWidget *centralWidget;
    QGridLayout *gridLayout;
    QTabWidget *tabWidget;
    QMenuBar *menuBar;
    QMenu *menuFile;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *particleEditor)
    {
        if (particleEditor->objectName().isEmpty())
            particleEditor->setObjectName(QStringLiteral("particleEditor"));
        particleEditor->resize(1240, 884);
        particleEditor->setContextMenuPolicy(Qt::CustomContextMenu);
        actionNew = new QAction(particleEditor);
        actionNew->setObjectName(QStringLiteral("actionNew"));
        actionOpen = new QAction(particleEditor);
        actionOpen->setObjectName(QStringLiteral("actionOpen"));
        actionSave = new QAction(particleEditor);
        actionSave->setObjectName(QStringLiteral("actionSave"));
        actionSave_as = new QAction(particleEditor);
        actionSave_as->setObjectName(QStringLiteral("actionSave_as"));
        action = new QAction(particleEditor);
        action->setObjectName(QStringLiteral("action"));
        centralWidget = new QWidget(particleEditor);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        gridLayout = new QGridLayout(centralWidget);
        gridLayout->setSpacing(0);
        gridLayout->setContentsMargins(11, 11, 11, 11);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        gridLayout->setContentsMargins(0, 0, 0, 0);
        tabWidget = new QTabWidget(centralWidget);
        tabWidget->setObjectName(QStringLiteral("tabWidget"));

        gridLayout->addWidget(tabWidget, 0, 0, 1, 1);

        particleEditor->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(particleEditor);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 1240, 17));
        menuFile = new QMenu(menuBar);
        menuFile->setObjectName(QStringLiteral("menuFile"));
        particleEditor->setMenuBar(menuBar);
        statusBar = new QStatusBar(particleEditor);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        particleEditor->setStatusBar(statusBar);

        menuBar->addAction(menuFile->menuAction());
        menuFile->addAction(actionNew);
        menuFile->addAction(actionOpen);
        menuFile->addSeparator();
        menuFile->addAction(actionSave);
        menuFile->addAction(actionSave_as);
        menuFile->addAction(action);

        retranslateUi(particleEditor);

        QMetaObject::connectSlotsByName(particleEditor);
    } // setupUi

    void retranslateUi(QMainWindow *particleEditor)
    {
        particleEditor->setWindowTitle(QApplication::translate("particleEditor", "particleEditor", 0));
        actionNew->setText(QApplication::translate("particleEditor", "New", 0));
        actionNew->setShortcut(QApplication::translate("particleEditor", "Ctrl+N", 0));
        actionOpen->setText(QApplication::translate("particleEditor", "Open", 0));
        actionOpen->setShortcut(QApplication::translate("particleEditor", "Ctrl+O", 0));
        actionSave->setText(QApplication::translate("particleEditor", "Save", 0));
        actionSave->setShortcut(QApplication::translate("particleEditor", "Ctrl+S", 0));
        actionSave_as->setText(QApplication::translate("particleEditor", "Save as", 0));
        action->setText(QApplication::translate("particleEditor", "\353\260\260\352\262\275\355\231\224\353\251\264\353\266\210\353\237\254\354\230\244\352\270\260", 0));
        menuFile->setTitle(QApplication::translate("particleEditor", "File", 0));
    } // retranslateUi

};

namespace Ui {
    class particleEditor: public Ui_particleEditor {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PARTICLEEDITOR_H
