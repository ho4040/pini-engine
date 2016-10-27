#ifndef HIERARCHYDOCK_H
#define HIERARCHYDOCK_H

#include <QDockWidget>

namespace Ui {
class hierarchydock;
}

class hierarchydock : public QDockWidget
{
    Q_OBJECT

public:
    explicit hierarchydock(QWidget *parent = 0);
    ~hierarchydock();

private slots:
    void on_pushButton_clicked();

private:
    Ui::hierarchydock *ui;
};

#endif // HIERARCHYDOCK_H
