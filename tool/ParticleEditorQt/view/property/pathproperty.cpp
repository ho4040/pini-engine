#include "pathproperty.h"
#include "ui_pathproperty.h"
#include <QLineEdit>
#include <QFileDialog>

PathProperty::PathProperty(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::PathProperty)
{
    ui->setupUi(this);
}

PathProperty::~PathProperty()
{
    delete ui;
}

QString PathProperty::text()
{
    return ui->lineEdit->text();
}

void PathProperty::setText(QString text)
{
    ui->lineEdit->setText(text);
}



QLineEdit* PathProperty::getLineEdit()
{
    return ui->lineEdit;
}

void PathProperty::on_pushButton_clicked()
{
    QFileDialog* pDialog = new QFileDialog(this);
    QString path = pDialog->getOpenFileName(this,"load");
    delete pDialog;


    ui->lineEdit->setText(path);
}
