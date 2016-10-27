#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <lib/lib.h>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow , IObserver
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

    void onNotice(NOTIS e);
	void ListElements(QDomElement root, QString tagName, QString attribute);

private slots:

	void on_actionOpen_triggered();
	void on_actionSave_triggered();

private:
    Ui::MainWindow *ui;

    Characterlistwidget*    charListWidget;
    TimelineWidget*           timeLineWidget;
    FrameInfoWidget*        frameInfoWidget;
};

#endif // MAINWINDOW_H
