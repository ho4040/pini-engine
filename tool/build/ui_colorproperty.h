/********************************************************************************
** Form generated from reading UI file 'colorproperty.ui'
**
** Created by: Qt User Interface Compiler version 5.2.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_COLORPROPERTY_H
#define UI_COLORPROPERTY_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QGraphicsView>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_ColorProperty
{
public:
    QGridLayout *gridLayout;
    QLineEdit *lineEdit;
    QPushButton *pushButton;
    QGraphicsView *graphicsView;

    void setupUi(QWidget *ColorProperty)
    {
        if (ColorProperty->objectName().isEmpty())
            ColorProperty->setObjectName(QStringLiteral("ColorProperty"));
        ColorProperty->resize(142, 23);
        gridLayout = new QGridLayout(ColorProperty);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        gridLayout->setContentsMargins(0, 0, 0, 0);
        lineEdit = new QLineEdit(ColorProperty);
        lineEdit->setObjectName(QStringLiteral("lineEdit"));

        gridLayout->addWidget(lineEdit, 0, 1, 1, 1);

        pushButton = new QPushButton(ColorProperty);
        pushButton->setObjectName(QStringLiteral("pushButton"));

        gridLayout->addWidget(pushButton, 0, 2, 1, 1);

        graphicsView = new QGraphicsView(ColorProperty);
        graphicsView->setObjectName(QStringLiteral("graphicsView"));
        graphicsView->setMaximumSize(QSize(30, 30));
        QBrush brush(QColor(0, 0, 0, 255));
        brush.setStyle(Qt::SolidPattern);
        graphicsView->setBackgroundBrush(brush);

        gridLayout->addWidget(graphicsView, 0, 0, 1, 1);


        retranslateUi(ColorProperty);

        QMetaObject::connectSlotsByName(ColorProperty);
    } // setupUi

    void retranslateUi(QWidget *ColorProperty)
    {
        ColorProperty->setWindowTitle(QApplication::translate("ColorProperty", "Form", 0));
        lineEdit->setText(QApplication::translate("ColorProperty", "0", 0));
        pushButton->setText(QApplication::translate("ColorProperty", "...", 0));
    } // retranslateUi

};

namespace Ui {
    class ColorProperty: public Ui_ColorProperty {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_COLORPROPERTY_H
