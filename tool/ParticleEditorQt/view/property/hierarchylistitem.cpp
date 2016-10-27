#include "hierarchylistitem.h"
#include "ui_hierarchylistitem.h"

hierarchylistitem::hierarchylistitem(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::hierarchylistitem)
{
    ui->setupUi(this);
}

hierarchylistitem::~hierarchylistitem()
{
    delete ui;
}
