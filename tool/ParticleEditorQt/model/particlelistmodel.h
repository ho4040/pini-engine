#ifndef PARTICLELISTMODEL_H
#define PARTICLELISTMODEL_H

#include "notifier.h"
#include <QJsonObject>
#include "particlesystem.h"
#include <qtimer.h>

class ParticleListModel: public Notifier
{
public:
    static ParticleListModel* shared();
    void addParticle();
    void updateParticleSystemInfo(QJsonObject info);
    void frameMove(float dt);
    void stop();
    void play();


    ParticleListModel();
    ~ParticleListModel();

    ParticleSystem* getParticleSystem();

    int getTotalPaticle();
    Particle * getParticleAt(int index);

    QString getParticleTexturePath();
    QString getParticleDestBlendFunc();
    QString getParticleSrcBlendFunc();

private:
    ParticleSystem* pParticleSystem;
    QTimer timer;
};

#endif // PARTICLELISTMODEL_H
