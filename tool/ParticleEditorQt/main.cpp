#include "view/windows/particleeditor.h"
#include <QApplication>
#include <qfile>


int main(int argc, char *argv[])
{

    QApplication a(argc, argv);

    QFile file(":/QMain.css");
    file.open(QIODevice::ReadOnly);
    QString bytes = file.readAll();
    file.close();

    a.setStyleSheet(bytes);

    particleEditor w;
    w.show();

    return a.exec();
}
