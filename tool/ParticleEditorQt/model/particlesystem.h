#ifndef PARTICLESYSTEM_H
#define PARTICLESYSTEM_H

#include "QPoint"
#include "geoLib.h"
#include "QList"
#include <QJsonObject>

struct Particle
{
    float x;
    float y;

    Vector2d pos;
    Vector2d velocity; //속도
    Vector2d accVec;    //가속도아님-> gravity //밖으로빼기
    Vector2d tangentialAccVec; //매순간 다시 계산하도록 함수로 수정.

    float startSize;
    float currentSize;
    float deltaSize;

    float rotation;
    float deltaRotation;

    float timeToLive;
    float speed;
    float degree;
    float startDegree;
    float life;
    float lifeTime;
    float sizeDt;
    float tangentialAcc;


    bool visible;

    Color3d startColor;
    Color3d endColor;
    Color3d currentColor;
    Color3d ColorDt;

    float currentRotate;
    float startRotate;
    float deltaRotate;

    bool isFixedRotation;

    unsigned int atlasIndex;




};

class ParticleSystem
{
public:
    ParticleSystem();
    ParticleSystem(QJsonObject data);
    ~ParticleSystem();

    int getTotalPaticle();

    Particle * getParticleAt(int index);
    QString getTexturePath();
    QString getDestBlendFunc();
    QString getSrcBlendFunc();

//private slots:
    void updateParticleSystem(float dt);
    void updateParticleSystemInfo(QJsonObject data);
    void deleteParticle();
protected:

private:
    int m_TotalParticle;
    bool m_IsLoop;
    float m_Suration;
    float m_Speed;
    int m_PosVarX;
    int m_PosVarY;
    int m_SourcePositionX;
    int m_SourcePositionY;
    float m_GravityAngle;
    int m_GravitySpeed;
    int m_SpeedVar;
    int m_Angle;
    int m_AngleVar;
    int m_Life;
    int m_LifeVar;
    float m_EmissionRate;
    float m_EmissionRateTime;
    float m_EmissionRateTimeDt;
    int m_StartSize;
    int m_StartSizeVar;
    int m_EndSize;
    int m_EndSizeVar;
    QString m_EndColor;
    QString m_EndColorVar;
    QString m_StartColor;
    QString m_StartColorVar;

    QString m_TexturePath;
    QString m_DestBlendFunc;
    QString m_SrcBlendFunc;

    bool m_IsFixedRotation;

    int m_EndSpin;
    int m_EndSpinVar;
    int m_StartSpin;
    int m_StartSpinVar;

    int m_TangentialAccel;
    int m_TangentialAccelVar;



    float m_LastDt;

//    QTimer _timer;

    QList<Particle *> m_particleList;
};

#endif // PARTICLESYSTEM_H
