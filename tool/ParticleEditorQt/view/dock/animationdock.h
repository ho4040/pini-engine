#ifndef ANIMATIONDOCK_H
#define ANIMATIONDOCK_H

#include <QDockWidget>

namespace Ui {
class animationdock;
}

class animationdock : public QDockWidget
{
    Q_OBJECT

public:
    explicit animationdock(QWidget *parent = 0);
    ~animationdock();

private:
    Ui::animationdock *ui;
};

#endif // ANIMATIONDOCK_H
