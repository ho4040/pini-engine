#include "gldrawer.h"
#include "qmath.h"
#include "math.h"
#include <QFile.h>
#include "particlelistmodel.h"
#include "ParticleSettingModel.h"
#include<QDebug>


GLDrawer::GLDrawer(QWidget *parent) :
    QGLWidget(parent)
{
    connect(&_timer,SIGNAL(timeout()),this,SLOT(updateGL()));
    _timer.start(16);
    _timer.setInterval(16);
    pixmap = QPixmap("fire.png");
//    m_BackImage = QPixmap("sell_pet_bg.png");


    ParticleSettingModel::shared()->addListener(this);
}

GLDrawer::~GLDrawer()
{

}

void GLDrawer::onNotice(NOTIS e){
    if(e == ALL_UPDATE)
    {
        chageTexture(ParticleListModel::shared()->getParticleTexturePath());
    }
    else if(e == BACKGROUNDIMAGE_UPDATE)
    {
        QString path = ParticleSettingModel::shared()->getBackGroundImagePath();
        qDebug()<<path<<endl;
        m_BackImage = QPixmap(path);


    }

}

int angle = 0;
GLfloat transX = 0;
GLfloat transY = 0;
float num = 50;
float radius = 0;
float maxValue = 0;
bool isbool = true;


void GLDrawer::chageTexture(QString path)
{
    pixmap = QPixmap(path);
}

int GLDrawer::getGlBlendFuncOption(QString option)
{
    if(option == "GL_ZERO" )
    {
        return 0;
    }
    else if(option == "GL_ONE")
    {
        return 1;
    }
    else if(option == "GL_SRC_COLOR")
    {
        return 0x0300;
    }
    else if(option == "GL_ONE_MINUS_SRC_COLOR")
    {
        return 0x0301;
    }
    else if(option == "GL_DST_COLOR")
    {
        return 0x0306;
    }
    else if(option == "GL_ONE_MINUS_DST_COLOR")
    {
        return 0x0307;
    }
    else if(option == "GL_SRC_ALPHA")
    {
        return 0x0302;
    }
    else if(option == "GL_ONE_MINUS_SRC_ALPHA")
    {
        return 0x0303;
    }
    else if(option == "GL_DST_ALPHA")
    {
        return 0x0304;
    }
    else if(option == "GL_ONE_MINUS_DST_ALPHA")
    {
        return 0x0305;
    }
    else if(option == "GL_SRC_ALPHA_SATURATE")
    {
        return 0x0308;
    }
}


void GLDrawer::initializeGL()
{
    glClearColor(0,0,0,1);
}


void GLDrawer::drawRect(float x, float y, float w, float h)
{
    glPushMatrix();
    glLoadIdentity();
    glTranslatef(-w/2,-h/2,0);
    glScalef(w, h, 1);
    glBegin(GL_QUADS);


        glColor3f(0.0f,0.0f,0.0f);


        glVertex3f(0.0, 1,0.0);

        glVertex3f(1, 1,0.0);

        glVertex3f(1, 0,0.0);

        glVertex3f(0, 0,0.0);
    glEnd();
    glPopMatrix();
}

void GLDrawer::drawImage(QPixmap img,float x, float y, float w, float h)
{
    glEnable(GL_TEXTURE_2D);
    bindTexture ( img, GL_TEXTURE_2D, GL_RGBA );

    glPushMatrix();

    glLoadIdentity();

    glTranslatef(x,y,0);
    glScalef(w/2, h/2, 1);


    glBegin(GL_QUADS);
        glColor3f(1.0f,1.0f,1.0f);

        glTexCoord2f(0.0, 1.0);
        glVertex3f(-1.0, 1,0.0);

        glTexCoord2f(1.0, 1.0);
        glVertex3f(1.0, 1.0,0.0);

        glTexCoord2f(1.0, 0.0);
        glVertex3f(1.0, -1.0,0.0);

        glTexCoord2f(0.0, 0.0);
        glVertex3f(-1.0, -1.0,0.0);
    glEnd();
    glPopMatrix();
    glDisable(GL_TEXTURE_2D);
}

void GLDrawer::drawRect(QPixmap img,int a, float x, float y, float w, float h)
{

    glEnable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    int src = getGlBlendFuncOption(ParticleListModel::shared()->getParticleSystem()->getSrcBlendFunc());
    int dest = getGlBlendFuncOption(ParticleListModel::shared()->getParticleSystem()->getDestBlendFunc());
//    glBlendFunc(GL_SRC_ALPHA, GL_ONE);
    glBlendFunc(src, dest);
    bindTexture ( img, GL_TEXTURE_2D, GL_RGBA );

    glPushMatrix();
//    glLoadIdentity();


    glTranslatef(x,y,0);
    glScalef(w, h, 1);

    glRotatef(a,0,0,1);


//    glRotatef();
    glBegin(GL_QUADS);


//        glColor3f(rand()%100/100.0f,rand()%100/100.0f,rand()%100/100.0f);
//        glColor3f(1.0f,1.0f,1.0f);

        glTexCoord2f(0.0, 1.0);
        glVertex3f(-1.0, 1,0.0);

        glTexCoord2f(1.0, 1.0);
        glVertex3f(1.0, 1.0,0.0);

        glTexCoord2f(1.0, 0.0);
        glVertex3f(1.0, -1.0,0.0);

        glTexCoord2f(0.0, 0.0);
        glVertex3f(-1.0, -1.0,0.0);
    glEnd();


    glPopMatrix();

    glDisable(GL_TEXTURE_2D);
    glDisable(GL_BLEND);
}


void GLDrawer::paintGL()
{

    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT);

    glMatrixMode(GL_MODELVIEW);
    angle+=1;

    if (m_BackImage.isNull() == false)
        drawImage(m_BackImage,0,0,800,600);
    else
        drawRect(0,0,800,600);

    glLoadIdentity();
    float dt = (float)_timer.interval()/1000;
    ParticleListModel::shared()->getParticleSystem()->updateParticleSystem(dt);

    int num = ParticleListModel::shared()->getTotalPaticle();
    for(int i =0; i<num;i++)
    {
        Particle* p = ParticleListModel::shared()->getParticleAt(i);
        if (p->visible)
        {

            glPushMatrix();

            float a = (1.0/255.0);
            glColor3f(a*(float)p->currentColor.red,a*(float)p->currentColor.green,a*(float)p->currentColor.blue);



            drawRect(pixmap,p->currentRotate,p->pos.x,p->pos.y,p->currentSize,p->currentSize);
            glPopMatrix();
        }
    }


    setAutoBufferSwap(true);
}

//void GLDrawer::paintGL()
//{

//    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT);

//    glMatrixMode(GL_MODELVIEW);


//    drawRect(0,0,800,600);

//    glLoadIdentity();


//    angle=angle+1;

//    if (radius >250 && isbool == true)
//        isbool = false;
//    else if(radius <0 && isbool == false)
//        isbool = true;


//    if (isbool)
//    {
//        maxValue=maxValue+0.3;
//        radius++;
//    }
//    else
//    {
//        maxValue=maxValue-0.3;
//        radius--;
//    }

//    glTranslatef(400,300,0);

//    for(int j =0; j<5;j++)
//    {
//        glPushMatrix();
//        glTranslatef(rand()%50,rand()%50,0);
//        for(int i =0; i<num;i++)
//        {
//            glPushMatrix();

//            float r = sin(((i/num)+angle )*10*3.14*2)*maxValue;
//            transX = sin(((i/num)+angle ) * (3.14*2))*(r+radius);
//            transY = cos(((i/num)+angle )* (3.14*2))*(r+radius);

//            drawRect(pixmap,transX,transY,25,25);
//            glPopMatrix();

//        }
//        glPopMatrix();
//    }

//    setAutoBufferSwap(true);
//}


void GLDrawer::resizeGL(int w, int h)
{


    GLint width = (GLint)w;
    GLint height = (GLint)h;

    GLint x=0,y=0;


    x = (width-800)/2;
    y = (height-600)/2;



    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    glOrtho(-400.0, 400.0, -300.0,300.0 , 1.0, -1.0);


    glViewport(x,y,800,600);


}


