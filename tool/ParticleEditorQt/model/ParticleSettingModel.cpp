#include "ParticleSettingModel.h"
#include "particlelistmodel.h"


ParticleSettingModel g_ParticleSettingModel;


ParticleSettingModel* ParticleSettingModel::shared(){
    return &g_ParticleSettingModel;
}

ParticleSettingModel::ParticleSettingModel()
{

}

ParticleSettingModel::~ParticleSettingModel()
{
}


QJsonObject ParticleSettingModel::getData()
{
    return particleInfo;
}

QString ParticleSettingModel::getBackGroundImagePath()
{
    return m_BackGroundImagePath;
}

void ParticleSettingModel::setData(QJsonObject data)
{
    particleInfo = data;

    ParticleListModel::shared()->updateParticleSystemInfo(particleInfo);

    notify(ALL_UPDATE);
}

void ParticleSettingModel::setColor(float color)
{
   // _data.EndColor = color;
    notify(ALL_UPDATE);
}

void ParticleSettingModel::setBackGroundImagePath(QString path)
{
    m_BackGroundImagePath = path;
    notify(BACKGROUNDIMAGE_UPDATE);
}
