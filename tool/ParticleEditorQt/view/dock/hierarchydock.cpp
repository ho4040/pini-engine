#include "hierarchydock.h"
#include "ui_hierarchydock.h"
#include "hierarchylistitem.h"

hierarchydock::hierarchydock(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::hierarchydock)
{
    ui->setupUi(this);
}

hierarchydock::~hierarchydock()
{
    delete ui;
}

void hierarchydock::on_pushButton_clicked()
{


}
