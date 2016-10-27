/********************************************************************************
** Form generated from reading UI file 'gldrawer.ui'
**
** Created by: Qt User Interface Compiler version 5.2.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_GLDRAWER_H
#define UI_GLDRAWER_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_GLDrawer
{
public:

    void setupUi(QWidget *GLDrawer)
    {
        if (GLDrawer->objectName().isEmpty())
            GLDrawer->setObjectName(QStringLiteral("GLDrawer"));
        GLDrawer->resize(400, 300);

        retranslateUi(GLDrawer);

        QMetaObject::connectSlotsByName(GLDrawer);
    } // setupUi

    void retranslateUi(QWidget *GLDrawer)
    {
        GLDrawer->setWindowTitle(QApplication::translate("GLDrawer", "Form", 0));
    } // retranslateUi

};

namespace Ui {
    class GLDrawer: public Ui_GLDrawer {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_GLDRAWER_H
