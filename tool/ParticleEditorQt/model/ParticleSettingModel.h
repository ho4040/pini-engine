#ifndef GLOBALDATAMODEL_H
#define GLOBALDATAMODEL_H

#include <iobserver.h>
#include <iostream>
#include <list>
#include "consts.h"
#include <QJsonObject>
#include "notifier.h"


class ParticleSettingModel : public Notifier
{
public:
    ParticleSettingModel();

public:
    ~ParticleSettingModel();

public:
    static ParticleSettingModel* shared();

    void setBackGroundImagePath(QString path);
    QString getBackGroundImagePath();

private:
//    ParticleData _data;
    QJsonObject particleInfo;
    QString m_BackGroundImagePath;
public:




    QJsonObject getData(); //복사본을 주는지 레퍼런스를 주는지 검토 필요, 레퍼런스를 줄 경우에는 외부에서 수정하면 통지가 발생하지 않음.


    void setData(QJsonObject data); //속성 별로 나누기.

    void setColor(float color);




};

#endif // GLOBALDATAMODEL_H
