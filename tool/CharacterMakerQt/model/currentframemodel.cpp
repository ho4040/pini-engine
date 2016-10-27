#include "currentframemodel.h"

CurrentFrameModel::CurrentFrameModel()
{
}

void CurrentFrameModel::setKeyFrame(KeyFrame* k)
{
    _pKeyFrame = k;
	notify(UPDATE_FRAME);
}

KeyFrame* CurrentFrameModel::getKeyFrame()
{
	return _pKeyFrame;
}

void CurrentFrameModel::setKeyFrameIndex(int index)
{
	_pKeyFrame = NULL;
	_keyFrameIndex = index;
	notify(UPDATE_FRAME);
}

int CurrentFrameModel::getKeyFrameIndex()
{
	return _keyFrameIndex;
}
