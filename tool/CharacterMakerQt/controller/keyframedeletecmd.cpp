#include "keyframedeletecmd.h"

KeyFrameDeleteCmd::KeyFrameDeleteCmd(QString layerName, KeyFrame *pKeyFrame)
	: _bRunned(false)
{

	_pKeyFrame = new KeyFrame(pKeyFrame->frameIndex, pKeyFrame->rotation, pKeyFrame->position, pKeyFrame->scale);
	_layerName = layerName;
}

void KeyFrameDeleteCmd::execute()
{
	_bRunned = true;
	KeyFrame* pKeyFrame = CurrentLayerModel::shared()->getLayer()->getKeyFrameByFrameIndex(_pKeyFrame->frameIndex);
	CurrentLayerModel::shared()->deleteKeyFrame(pKeyFrame->frameIndex);
	CurrentFrameModel::shared()->setKeyFrame(NULL);
}

void KeyFrameDeleteCmd::undo()
{
	if(_bRunned)
	{
		Layer* pLayer = CurrentEmotionModel::shared()->getEmotion()->getLayerByName(_layerName);
		pLayer->addKeyFrame(_pKeyFrame);
		CurrentFrameModel::shared()->setKeyFrame(_pKeyFrame);
		_bRunned = false;
	}

}
