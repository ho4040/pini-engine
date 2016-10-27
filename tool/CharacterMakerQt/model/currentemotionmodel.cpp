#include "currentemotionmodel.h"

CurrentEmotionModel::CurrentEmotionModel()
{
}

void CurrentEmotionModel::setEmotion(Emotion* e)
{
    _pEmotion = e;
    notify(UPDATE_EMOTION);
	notify(UPDATE_LAYER);
}

Emotion* CurrentEmotionModel::getEmotion()
{
    return _pEmotion;
}

void CurrentEmotionModel::changeValue(Emotion* e)
{
    _pEmotion->setEmotionValue(e->getStartState(),e->getFinishState(),e->getTotalFrame(),e->getFrameDelay());
    notify(UPDATE_EMOTION);
}

Layer* CurrentEmotionModel::createLayer(QString fileName)
{
	Layer* pLayer = _pEmotion->createLayer(fileName);
	notify(UPDATE_LAYER);
	return pLayer;
}

void CurrentEmotionModel::createLayer(Layer *pLayerData)
{
	_pEmotion->createLayer(pLayerData);
	notify(UPDATE_LAYER);
}

void CurrentEmotionModel::deleteLayerByName(QString name)
{
	_pEmotion->deleteLayerByName(name);
	notify(UPDATE_LAYER);
}

int CurrentEmotionModel::getLayerIndexByName(QString name)
{
	return _pEmotion->getLayerIndexByName(name);
}
