#include "emotion.h"

Emotion::Emotion()
{
    _pLayerList.clear();
}
Emotion::Emotion(QString sName, QString fName, int frame, int delay)
    : _startState(sName),
      _finishState(fName),
      _totalFrame(frame),
      _frameDelay(delay)
{
    _pLayerList.clear();
}

void Emotion::setStateState(QString name)
{
    _startState = name;
}

void Emotion::setFinishState(QString name)
{
    _finishState = name;
}

void Emotion::setTotalFrame(int frame)
{
    _totalFrame = frame;
}

void Emotion::setFrameDelay(int delay)
{
    _frameDelay = delay;
}

void Emotion::setEmotionValue(QString sName, QString fName, int frame, int delay)
{
    _startState = sName;
    _finishState = fName;
    _totalFrame = frame;
    _frameDelay = delay;
}

QString Emotion::getStartState()
{
    return _startState;
}

QString Emotion::getFinishState()
{
    return _finishState;
}

int Emotion::getTotalFrame()
{
    return _totalFrame;
}

int Emotion::getFrameDelay()
{
    return _frameDelay;
}

Layer* Emotion::createLayer(QString fileName)
{
    Layer* pLayer = new Layer(fileName);
    _pLayerList.append(pLayer);
    return pLayer;
}

void Emotion::createLayer(Layer *pLayer)
{
    _pLayerList.append(pLayer);
}

Layer* Emotion::getLayerByName(QString name)
{
    if(_pLayerList.isEmpty())
        return NULL;

    QList<Layer*>::iterator iter = _pLayerList.begin();
    for(; iter != _pLayerList.end(); iter++)
    {
        Layer* pLayer = (*iter);
        if(name == pLayer->getFileName())
            return pLayer;
    }

    return NULL;
}

Layer* Emotion::getLayerByIndex(int index)
{
    if(_pLayerList.isEmpty())
        return NULL;

    return _pLayerList.at(index);
}
void Emotion::deleteLayerByName(QString name)
{
    Layer* pLayer = getLayerByName(name);

    if(NULL == pLayer)
        return;

    _pLayerList.removeOne(pLayer);
    delete pLayer;
    pLayer = NULL;
}

int Emotion::getLayerCount()
{
	return _pLayerList.count();
}

int Emotion::getLayerIndexByName(QString name)
{
	if(_pLayerList.isEmpty())
		return -1;

	int index = 0;

	QList<Layer*>::iterator iter = _pLayerList.begin();
	for(; iter != _pLayerList.end(); iter++)
	{
		Layer* pLayer = (*iter);
		if(name == pLayer->getFileName())
			return index;
		index++;
	}

	return -1;
}
