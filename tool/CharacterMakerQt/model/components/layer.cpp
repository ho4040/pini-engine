#include "layer.h"

Layer::Layer(QString fileName)
    : _fileName(fileName)
{
    _keyFrameList.clear();

	createKeyFrame(0);
}

Layer::Layer(Layer* pLayerData)
{
	_keyFrameList.clear();

	_fileName = pLayerData->getFileName();

	QLinkedList<KeyFrame*> *pKeyFrameList = pLayerData->getKeyFrameList();
	QLinkedList<KeyFrame*>::iterator iter = pKeyFrameList->begin();

	for(; iter != pKeyFrameList->end(); iter++)
	{
		KeyFrame *temp = (*iter);
		KeyFrame *pKeyFrame = new KeyFrame(temp->frameIndex, temp->rotation, temp->position, temp->scale);
		this->addKeyFrame(pKeyFrame);
	}
}

Layer::~Layer()
{
	if(!_keyFrameList.empty())
	{
		QLinkedList<KeyFrame*>::iterator iter = _keyFrameList.begin();
		for(; iter != _keyFrameList.end(); iter++)
		{
			KeyFrame* pKeyFrame = (*iter);
			if(pKeyFrame != NULL)
			{
				delete pKeyFrame;
				pKeyFrame = NULL;
				_keyFrameList.erase(iter);
			}
			else
			{
				_keyFrameList.erase(iter);
			}

			iter--;
		}
	}
}

void Layer::setLayerNum(int num)
{
	_layerNum = num;
}

int Layer::getLayerNum()
{
	return _layerNum;
}

void Layer::setFileName(QString fileName)
{
    _fileName = fileName;  
}

QString Layer::getFileName()
{
    return _fileName;
}

KeyFrame* Layer::getKeyFrameByindex(int index)
{
    if(_keyFrameList.isEmpty())
        return NULL;

    int i = 0;
    QLinkedList<KeyFrame*>::iterator iter = _keyFrameList.begin();

    for(; iter != _keyFrameList.end(); iter++)
    {
        KeyFrame* pKeyFrame = (*iter);

        if(i == index)
            return pKeyFrame;

        i++;
    }
    return NULL;
}

KeyFrame* Layer::getKeyFrameByFrameIndex(int index)
{
	if(_keyFrameList.isEmpty())
		return NULL;

	QLinkedList<KeyFrame*>::iterator iter = _keyFrameList.begin();

	for(; iter != _keyFrameList.end(); iter++)
	{
		KeyFrame* pKeyFrame = (*iter);

		if(pKeyFrame->frameIndex == index)
			return pKeyFrame;
	}
	return NULL;
}

int Layer::getkeyFrameCount()
{
	return _keyFrameList.count();
}

KeyFrame* Layer::createKeyFrame(int index)
{
	KeyFrame* pKeyFrame = new KeyFrame(index);
	_keyFrameList.append(pKeyFrame);
	return pKeyFrame;
}

void Layer::addKeyFrame(KeyFrame* pkeyFrame)
{
    _keyFrameList.append( pkeyFrame);
}

void Layer::deleteKeyFrame(int index)
{
    KeyFrame* pKeyFrame = getKeyFrameByFrameIndex(index);

    if(pKeyFrame)
    {
        _keyFrameList.removeOne(pKeyFrame);
        delete pKeyFrame;
        pKeyFrame = NULL;
	}
}

QLinkedList<KeyFrame *> *Layer::getKeyFrameList()
{
	return &_keyFrameList;
}
