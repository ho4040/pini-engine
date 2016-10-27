#include "mygraphicsview.h"

MyGraphicsView::MyGraphicsView(QWidget *parent) :
    QGraphicsView(parent)

{
    scene = new QGraphicsScene;
    this->setSceneRect(50,50,350,350);
    this->setScene(scene);

}
void MyGraphicsView::mousePressEvent(QMouseEvent * e)
  {

  }
void MyGraphicsView::mouseMoveEvent (QMouseEvent *move)
{

}
