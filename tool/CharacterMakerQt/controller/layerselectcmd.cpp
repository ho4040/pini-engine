#include "layerselectcmd.h"

LayerSelectCmd::LayerSelectCmd(int index)
	: _bRunned(false),
	  _index(index)
{
}

void LayerSelectCmd::execute()
{
	Layer* pLayer = CurrentEmotionModel::shared()->getEmotion()->getLayerByIndex(_index);
	CurrentLayerModel::shared()->setLayer(pLayer);
}

void LayerSelectCmd::undo()
{

}
