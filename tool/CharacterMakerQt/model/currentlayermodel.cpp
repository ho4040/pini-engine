#include "currentlayermodel.h"

CurrentLayerModel::CurrentLayerModel()
{
}
void CurrentLayerModel::setLayer(Layer* pLayer)
{
    if(pLayer)
    {
        _pLayer = pLayer;
		notify(UPDATE_LAYER);
    }
}

Layer* CurrentLayerModel::getLayer()
{
    return _pLayer;
}

KeyFrame* CurrentLayerModel::createKeyFrame(int index)
{
	KeyFrame* pkF = _pLayer->createKeyFrame(index);
	notify(UPDATE_FRAME);
	return pkF;
}

void CurrentLayerModel::addKeyFrame(KeyFrame* pkeyFrame)
{
    _pLayer->addKeyFrame(pkeyFrame);
	notify(UPDATE_FRAME);
}


void CurrentLayerModel::deleteKeyFrame(int index)
{
    _pLayer->deleteKeyFrame(index);
	notify(UPDATE_FRAME);
}
