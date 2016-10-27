#include "filemanager.h"
#include <QFile>
#include <Qdir>
#include <QDir>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>
#include <QTreeWidget>
#include <QComboBox>
#include <QSpinBox>

#include <QString>
#include "ParticleSettingModel.h"

FileManager g_fileManager;
FileManager* FileManager::shared(){
    return &g_fileManager;
}

FileManager::FileManager()
{
}

FileManager::~FileManager()
{

}


bool FileManager::save(QString path )
{


    QJsonObject root =  ParticleSettingModel::shared()->getData();

    QFile file(path);
    file.open(QIODevice::WriteOnly);
    file.write(QJsonDocument(root).toJson());
    file.close();

    return true;
}

bool FileManager::open(QString path)
{

    QFile file(path);

    file.open(QIODevice::ReadOnly);
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll());

    file.close();

    QJsonObject root = doc.object();

    ParticleSettingModel::shared()->setData(root);


    return true;
}
