#include "particlelistmodel.h"
#include "particlesystem.h"


ParticleListModel g_ParticleListModel;


ParticleListModel* ParticleListModel::shared(){
    return &g_ParticleListModel;
}

ParticleListModel::ParticleListModel()
{
}

ParticleListModel::~ParticleListModel()
{
    delete pParticleSystem;
}


void ParticleListModel::updateParticleSystemInfo(QJsonObject info)
{
    if (pParticleSystem == NULL)
    {
        pParticleSystem = new ParticleSystem(info);
    }
    else
    {
        pParticleSystem->updateParticleSystemInfo(info);
    }

}

int ParticleListModel::getTotalPaticle()
{
    return pParticleSystem->getTotalPaticle();
}

Particle * ParticleListModel::getParticleAt(int index)
{
    return pParticleSystem->getParticleAt(index);
}
ParticleSystem* ParticleListModel::getParticleSystem()
{
    return pParticleSystem;
}

QString ParticleListModel::getParticleTexturePath()
{
    return pParticleSystem->getTexturePath();
}

QString ParticleListModel::getParticleDestBlendFunc()
{
    return pParticleSystem->getDestBlendFunc();
}

QString ParticleListModel::getParticleSrcBlendFunc()
{
    return pParticleSystem->getSrcBlendFunc();
}


