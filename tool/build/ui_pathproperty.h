/********************************************************************************
** Form generated from reading UI file 'pathproperty.ui'
**
** Created by: Qt User Interface Compiler version 5.2.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PATHPROPERTY_H
#define UI_PATHPROPERTY_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_PathProperty
{
public:
    QHBoxLayout *horizontalLayout;
    QLineEdit *lineEdit;
    QPushButton *pushButton;

    void setupUi(QWidget *PathProperty)
    {
        if (PathProperty->objectName().isEmpty())
            PathProperty->setObjectName(QStringLiteral("PathProperty"));
        PathProperty->resize(169, 23);
        horizontalLayout = new QHBoxLayout(PathProperty);
        horizontalLayout->setSpacing(0);
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        lineEdit = new QLineEdit(PathProperty);
        lineEdit->setObjectName(QStringLiteral("lineEdit"));

        horizontalLayout->addWidget(lineEdit);

        pushButton = new QPushButton(PathProperty);
        pushButton->setObjectName(QStringLiteral("pushButton"));

        horizontalLayout->addWidget(pushButton);


        retranslateUi(PathProperty);

        QMetaObject::connectSlotsByName(PathProperty);
    } // setupUi

    void retranslateUi(QWidget *PathProperty)
    {
        PathProperty->setWindowTitle(QApplication::translate("PathProperty", "Form", 0));
        pushButton->setText(QApplication::translate("PathProperty", "...", 0));
    } // retranslateUi

};

namespace Ui {
    class PathProperty: public Ui_PathProperty {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PATHPROPERTY_H
