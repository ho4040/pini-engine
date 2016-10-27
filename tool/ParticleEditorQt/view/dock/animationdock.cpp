#include "animationdock.h"
#include "ui_animationdock.h"

animationdock::animationdock(QWidget *parent) :
    QDockWidget(parent),
    ui(new Ui::animationdock)
{
    ui->setupUi(this);
}

animationdock::~animationdock()
{
    delete ui;
}
