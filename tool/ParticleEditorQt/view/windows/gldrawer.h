#ifndef GLDRAWER_H
#define GLDRAWER_H

#include <QWidget>
#include <QGLWidget>
#include <QTimer>
#include "iobserver.h"


class GLDrawer : public QGLWidget , IObserver
{
    Q_OBJECT

public:
    explicit GLDrawer(QWidget *parent = 0);
    ~GLDrawer();

    void drawRect(float x, float y, float w, float h);
    void drawRect(QPixmap img, int angle, float x, float y, float w, float h);
    void drawImage(QPixmap img,float x, float y, float w, float h);

    void chageTexture(QString path);
    void onNotice(NOTIS e);
    int getGlBlendFuncOption(QString option);

private:
    QTimer _timer;
    QPixmap pixmap;
    QPixmap m_BackImage;
protected:
    void initializeGL();
//    void initializeOverlayGL();
//    void glDraw();
//    void glInit();
    void paintGL();
//    void paintOverlayGL();
    void resizeGL(int w, int h);
//    void resizeOverlayGL();



};

#endif // GLDRAWER_H
