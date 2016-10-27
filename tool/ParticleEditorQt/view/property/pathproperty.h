#ifndef PATHPROPERTY_H
#define PATHPROPERTY_H

#include <QWidget>
#include <qlineedit.h>

namespace Ui {
class PathProperty;
}

class PathProperty : public QWidget
{
    Q_OBJECT

public:
    explicit PathProperty(QWidget *parent = 0);
    ~PathProperty();

    QString text();
    void setText(QString text);

    void changedText();
    QLineEdit* getLineEdit();

private slots:
    void on_pushButton_clicked();

private:
    Ui::PathProperty *ui;
};

#endif // PATHPROPERTY_H
