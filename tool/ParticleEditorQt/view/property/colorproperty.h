#ifndef COLORPROPERTY_H
#define COLORPROPERTY_H

#include <QWidget>
#include <QLineEdit>

namespace Ui {
class ColorProperty;
}

class ColorProperty : public QWidget
{
    Q_OBJECT

public:
    explicit ColorProperty(QWidget *parent = 0);
    ~ColorProperty();

    QString text();
    void setText(QString text);

    void changedText();
    QLineEdit* getLineEdit();
private slots:
    void on_pushButton_clicked();

private:
    Ui::ColorProperty *ui;


    QColor m_color;
};

#endif // COLORPROPERTY_H
