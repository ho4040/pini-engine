#include "particlesystem.h"
#include <QJsonObject>
#include <QStringList>
#include <math.h>
#include <time.h>
#include <QColor>
#include <QDebug>

#define PI 3.1415926535

ParticleSystem::ParticleSystem()
{
//    connect(&_timer,SIGNAL(timeout()),this,SLOT(updateParticleSystem()));
//    timer.start(0.1);
}

ParticleSystem::ParticleSystem(QJsonObject data)
{


    updateParticleSystemInfo(data);

}

ParticleSystem::~ParticleSystem()
{
    deleteParticle();
}
void ParticleSystem::updateParticleSystemInfo(QJsonObject data)
{
    QStringList keys = data.keys();

    foreach (QString key, keys)
    {
        QJsonObject child =  data.value(key).toObject();

        QStringList childKeys = child.keys();
        foreach ( QString childKey,childKeys)
        {
            if(childKey == "TotalParticles")
            {
                m_TotalParticle  = child.value(childKey).toInt();
            }
            else if(childKey == "PosVarX")
            {
                m_PosVarX  = child.value(childKey).toInt(1);
            }
            else if(childKey == "PosVarY")
            {
                m_PosVarY  = child.value(childKey).toInt(1);
            }
            else if(childKey == "SourcePositionX")
            {
                m_SourcePositionX  = child.value(childKey).toInt(1);
            }
            else if(childKey == "SourcePositionY")
            {
                m_SourcePositionY  = child.value(childKey).toInt(1);
            }
            else if(childKey == "Speed")
            {
                m_Speed  = child.value(childKey).toInt(1);
            }
            else if(childKey == "SpeedVar")
            {
                m_SpeedVar = child.value(childKey).toInt(1);
            }
            else if(childKey == "Angle")
            {
                m_Angle = child.value(childKey).toInt(1);
            }
            else if(childKey == "AngleVar")
            {
                m_AngleVar = child.value(childKey).toInt(1);
            }
            else if(childKey == "Life")
            {
                m_Life = child.value(childKey).toInt(1);
            }
            else if(childKey == "LifeVar")
            {
                m_LifeVar = child.value(childKey).toInt(1);
            }
            else if(childKey == "EmissionRate")
            {
                m_EmissionRate = child.value(childKey).toInt(1);
                m_EmissionRateTime=0;
                m_EmissionRateTimeDt =0;
                if (m_EmissionRate != 0 )
                    m_EmissionRateTime = 1/m_EmissionRate;
            }
            else if(childKey == "StartSize")
            {
                m_StartSize = child.value(childKey).toInt(1);
            }
            else if(childKey == "StartSizeVar")
            {
                m_StartSizeVar = child.value(childKey).toInt(1);
            }
            else if(childKey == "EndSize")
            {
                m_EndSize = child.value(childKey).toInt(1);
            }
            else if(childKey == "EndSizeVar")
            {
                m_EndSizeVar = child.value(childKey).toInt(1);
            }
            else if(childKey == "GravityAngle")
            {
                m_GravityAngle = child.value(childKey).toInt(1);
                m_GravityAngle = (PI/180)*m_GravityAngle;
            }
            else if(childKey == "GravitySpeed")
            {
                m_GravitySpeed = child.value(childKey).toInt(1);
            }
            else if(childKey == "EndColor")
            {
                m_EndColor = child.value(childKey).toString();
            }
            else if(childKey == "EndColorVar")
            {
                m_EndColorVar = child.value(childKey).toString();
            }
            else if(childKey == "StartColor")
            {
                m_StartColor = child.value(childKey).toString();
            }
            else if(childKey == "StartColorVar")
            {
                m_StartColorVar = child.value(childKey).toString();
            }
            else if(childKey == "TexturePath")
            {
                m_TexturePath = child.value(childKey).toString();
            }
            else if(childKey == "DestBlendFunc")
            {
                m_DestBlendFunc = child.value(childKey).toString();
            }
            else if(childKey == "SrcBlendFunc")
            {
                m_SrcBlendFunc = child.value(childKey).toString();
            }
            else if(childKey == "IsFixedRotation")
            {
                QString t = child.value(childKey).toString();
                if (t == "False")
                    m_IsFixedRotation= false;
                else
                    m_IsFixedRotation= true;

            }
            else if(childKey == "StartSpin")
            {
                m_StartSpin = child.value(childKey).toInt(0);
            }
            else if(childKey == "StartSpinVar")
            {
                m_StartSpinVar = child.value(childKey).toInt(0);
            }
            else if(childKey == "EndSpin")
            {
                m_EndSpin = child.value(childKey).toInt(0);
            }
            else if(childKey == "EndSpinVar")
            {
                m_EndSpinVar = child.value(childKey).toInt(0);
            }
            else if(childKey == "TagentialAccel")
            {
                m_TangentialAccel = child.value(childKey).toInt(0);
            }
            else if(childKey == "TagentialAccelVar")
            {
                m_TangentialAccelVar = child.value(childKey).toInt(0);
            }


        }
    }

    deleteParticle();

    for(int i=0; i<m_TotalParticle;i++)
    {
        Particle * p = new Particle;

        p->isFixedRotation = m_IsFixedRotation;
        p->x = m_SourcePositionX;
        if (m_PosVarX != 0)
        {
            p->x +=(rand()%m_PosVarX)-(m_PosVarX/2);
        }
        p->y = m_SourcePositionY;
        if (m_PosVarY != 0)
        {
            p->y +=(rand()%m_PosVarY)-(m_PosVarY/2);
        }

        int angle = m_Angle;
        if (m_AngleVar != 0)
        {
            angle += (rand()%m_AngleVar)-(m_AngleVar/2);
        }
        p->degree= (PI/180)*angle;
        p->startDegree =p->degree;

        int speed =m_Speed;
        if (m_SpeedVar != 0)
        {
            speed += (rand()%m_SpeedVar)-(m_SpeedVar/2);
        }
        int life =m_Life;
        if (m_LifeVar != 0)
        {
            life += (rand()%m_LifeVar)-(m_LifeVar/2);
        }

        p->life = life;



        int spin = m_StartSpin;
        if (m_StartSpinVar != 0)
        {
            spin +=(rand()%m_StartSpinVar)-(m_StartSpinVar/2);
        }

        int endSpin = m_EndSpin;
        if (m_EndSpinVar != 0)
        {
            endSpin +=(rand()%m_EndSpinVar)-(m_EndSpinVar/2);
        }

        float spinDt = m_EndSpin;
        if(life != 0)
            spinDt = (endSpin - spin);

        p->startRotate = spin;
        p->currentRotate = spin;
        p->deltaRotate = spinDt;

        int size = m_StartSize;
        if (m_StartSizeVar != 0)
            size += (rand()%m_StartSizeVar)-(m_StartSizeVar/2);
        p->currentSize = size;
        p->startSize = size;


        float sizeDt = m_EndSize;


        if (m_EndSizeVar != 0)
            sizeDt += (rand()%m_EndSizeVar)-(m_EndSizeVar/2);

        sizeDt = (sizeDt - size)/life*0.016;

        p->sizeDt = sizeDt;


        QColor start(m_StartColor);

        if (m_StartColorVar != "#000000")
        {
            QColor sv(m_StartColorVar);
            Color3d startColor = Color3d(start.red(),start.green(),start.blue());
            Color3d startColorVar = Color3d(sv.red(),sv.green(),sv.blue());
            int r = rand();
            int rr ,rg,rb;
            if (startColorVar.red != 0)
            {
                rr = r%(int)startColorVar.red;
            }
            if (startColorVar.green != 0)
            {
                rg = r%(int)startColorVar.green;
            }
            if (startColorVar.blue != 0)
            {
                rb = r%(int)startColorVar.blue;
            }

            startColor += Color3d(rr,rg,rb)-(startColorVar/2);
            p->startColor = startColor;
        }
        else
        {
            p->startColor = Color3d(start.red(),start.green(),start.blue());
            p->currentColor = Color3d(start.red(),start.green(),start.blue());
        }

        QColor end(m_EndColor);

        if (m_StartColorVar != "#000000")
        {
            QColor ev(m_StartColorVar);
            Color3d endColor = Color3d(end.red(),end.green(),end.blue());
            Color3d endColorVar = Color3d(ev.red(),ev.green(),ev.blue());

            int r = rand();
            int rr ,rg,rb;
            if (endColorVar.red != 0)
            {
                rr = r%(int)endColorVar.red;
            }
            if (endColorVar.green != 0)
            {
                rg = r%(int)endColorVar.green;
            }
            if (endColorVar.blue != 0)
            {
                rb = r%(int)endColorVar.blue;
            }

            endColor += Color3d(rr,rg,rb)-(endColorVar/2);
            p->endColor = endColor;
        }
        else
            p->endColor = Color3d(end.red(),end.green(),end.blue());


        if(m_StartColor != m_EndColor)
        {
            p->ColorDt = p->endColor-p->startColor;
        }




        p->speed = speed;
        p->tangentialAcc = m_TangentialAccel;

        p->visible = false;
        p->lifeTime = 0;
        m_particleList.append(p);

        p->pos = Vector2d(p->x, p->y);


        p->velocity = Vector2d(cos(p->degree), sin(p->degree));
        p->velocity *= p->speed;

        p->accVec = Vector2d(cos(m_GravityAngle), sin(m_GravityAngle));
        p->accVec *= m_GravitySpeed;

        p->tangentialAccVec =Vector2d(cos(p->degree), sin(p->degree));
        p->tangentialAccVec *= p->tangentialAcc;

        if (p->isFixedRotation)
            p->currentRotate += atan2(p->y,p->x)*  PI;

    }

}

void ParticleSystem::deleteParticle()
{

    for(int i=0; i<m_TotalParticle;i++)
    {
        Particle * p = m_particleList.value(i);
        delete p;
    }

    m_particleList.clear();
}

int ParticleSystem::getTotalPaticle()
{
    return m_TotalParticle;
}

Particle * ParticleSystem::getParticleAt(int index)
{
    return m_particleList.value(index);
}

QString ParticleSystem::getTexturePath()
{
    return m_TexturePath;
}

QString ParticleSystem::getDestBlendFunc()
{
    return m_DestBlendFunc;
}

QString ParticleSystem::getSrcBlendFunc()
{
    return m_SrcBlendFunc;
}

void ParticleSystem::updateParticleSystem(float dt)
{

    m_EmissionRateTimeDt += dt;

    for(int i=0; i<m_TotalParticle;i++)
    {
        Particle* p = m_particleList.value(i);
        if (p->visible == false && m_EmissionRateTime < m_EmissionRateTimeDt)
        {
            p->visible = true;

            m_EmissionRateTimeDt=0;
            p->currentSize = p->startSize;

            p->pos = Vector2d(p->x, p->y);
            p->velocity = Vector2d(cos(p->startDegree), sin(p->startDegree));
            p->velocity *= p->speed;
            p->pos +=p->velocity;


            p->accVec = Vector2d(cos(m_GravityAngle), sin(m_GravityAngle));
            p->accVec *= m_GravitySpeed;

            p->tangentialAccVec =Vector2d(cos(p->startDegree), sin(p->startDegree));
            p->tangentialAccVec *= p->tangentialAcc;

            p->currentColor = p->startColor;
            p->currentRotate = p->startRotate;
        }

        if (p->visible)
        {
//            p->degree = p->degree*180/PI;

//            p->degree +=1;

//            p->degree = p->degree*(PI/180);

//            p->velocity = Vector2d(cos(p->degree), sin(p->degree));
//            p->velocity *= p->speed;

            float degree = atan2((p->pos).y,(p->pos).x)*180/PI;
            qDebug()<< degree<<endl;
            degree+=90;

            degree= degree*(PI/180);
            qDebug()<< degree<<endl;
            qDebug()<< "----------"<<endl;

//            p->velocity = Vector2d(cos(degree), sin(degree));
//            p->velocity *= p->speed;

            p->tangentialAccVec =Vector2d(cos(degree), sin(degree));
            p->tangentialAccVec *= p->tangentialAcc;



            p->velocity += p->tangentialAccVec*dt;
            p->velocity += p->accVec*dt;






            p->pos += p->velocity*dt;







//            p->pos += Vector2d(-1,0);
//            p->pos += Vector2d(cos(180*(PI/180)),sin(180*(PI/180)));


            p->currentSize += p->sizeDt;

            p->lifeTime +=dt;//dt로 변경해주세요.


            float ratio = p->lifeTime / p->life;

            p->currentColor = p->startColor + (p->ColorDt*ratio);

            p->currentRotate=0;
            if(p->isFixedRotation)
            {
                p->currentRotate = atan2((p->velocity*dt).y,(p->velocity*dt).x)*180/PI;
//                p->currentAngle+=90;
            }
            p->currentRotate += p->startRotate + (p->deltaRotate*ratio);



//            qDebug()<< p->currentAngle<<endl;

            if (p->life < p->lifeTime)
            {
                p->visible = false;
                p->lifeTime = 0;
                p->x = m_SourcePositionX;
                if (m_PosVarX != 0)
                {
                    p->x +=(rand()%m_PosVarX)-(m_PosVarX/2);
                }
                p->y = m_SourcePositionY;
                if (m_PosVarY != 0)
                {
                    p->y +=(rand()%m_PosVarY)-(m_PosVarY/2);
                }
            }
        }
    }


}


