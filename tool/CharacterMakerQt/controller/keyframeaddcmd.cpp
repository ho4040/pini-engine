#include "keyframeaddcmd.h"

KeyFrameAddCmd::KeyFrameAddCmd()
{
}

KeyFrameAddCmd::KeyFrameAddCmd(int layerIndex, int frameIndex)
	: _bRunned(false), _layerIndex(layerIndex), _frameIndex(frameIndex)
{
	_charName = CurrentCharacterModel::shared()->getCharName();
	_emotionName = CurrentEmotionModel::shared()->getEmotion()->getStartState();
}

void KeyFrameAddCmd::execute()
{
	_bRunned = true;
	Layer* pLayer = CurrentEmotionModel::shared()->getEmotion()->getLayerByIndex(_layerIndex);
	CurrentLayerModel::shared()->setLayer(pLayer);
	KeyFrame* pFrame = CurrentLayerModel::shared()->createKeyFrame(_frameIndex);
	CurrentFrameModel::shared()->setKeyFrame(pFrame);
}

void KeyFrameAddCmd::undo()
{
	if(_bRunned)
	{
		CurrentLayerModel::shared()->deleteKeyFrame(_frameIndex);
		CurrentFrameModel::shared()->setKeyFrame(NULL);
		_bRunned = false;
	}
}
