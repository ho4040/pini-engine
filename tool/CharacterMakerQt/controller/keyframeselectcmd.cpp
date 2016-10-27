#include "keyframeselectcmd.h"

KeyFrameSelectCmd::KeyFrameSelectCmd(int index)
	: _bRunned(false),
	  _index(index)
{
}

void KeyFrameSelectCmd::execute()
{
	KeyFrame* pkeyFrame = CurrentLayerModel::shared()->getLayer()->getKeyFrameByFrameIndex(_index);
	if(NULL != pkeyFrame)
		CurrentFrameModel::shared()->setKeyFrame(pkeyFrame);
	else
		CurrentFrameModel::shared()->setKeyFrameIndex(_index);
}

void KeyFrameSelectCmd::undo()
{

}
