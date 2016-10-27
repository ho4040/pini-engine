#include "colorproperty.h"
#include "ui_colorproperty.h"
#include <QColorDialog>

ColorProperty::ColorProperty(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::ColorProperty)
{
    ui->setupUi(this);

    ui->graphicsView->setScene(new QGraphicsScene);
}

ColorProperty::~ColorProperty()
{
    delete ui;
}


QString ColorProperty::text()
{
    return ui->lineEdit->text();
}


void ColorProperty::setText(QString text)
{
//    QString str = QString::number(text);
    ui->lineEdit->setText(text);
    m_color = QColor(text);
    ui->graphicsView->setBackgroundBrush(QBrush(m_color));
}

QLineEdit* ColorProperty::getLineEdit()
{
    return ui->lineEdit;
}

void ColorProperty::on_pushButton_clicked()
{
    QColorDialog* pDialog = new QColorDialog(this);
    m_color = pDialog->getColor();
    delete pDialog;

    ui->lineEdit->setText(m_color.name());

    QPalette pal = ui->lineEdit->palette();
    pal.setColor(QPalette::Base,m_color);
    ui->lineEdit->setPalette(pal);
    ui->graphicsView->setBackgroundBrush(QBrush(m_color));

}
