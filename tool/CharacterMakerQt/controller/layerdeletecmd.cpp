#include "layerdeletecmd.h"

LayerDeleteCmd::LayerDeleteCmd(QString lName, QString eName)
	: _bRunned(false),
	  _emotionName(eName),
	  _layerName(lName)
{

}

void LayerDeleteCmd::execute()
{
	_bRunned = true;
	Layer* pLayer = CurrentLayerModel::shared()->getLayer();
	_pLayer = new Layer(pLayer);
	CurrentEmotionModel::shared()->deleteLayerByName(_layerName);
	CurrentLayerModel::shared()->setLayer(NULL);
}

void LayerDeleteCmd::undo()
{
	if(_bRunned)
	{
		Emotion* pEmotion = CurrentCharacterModel::shared()->getCharacter()->getEmotionByName(_emotionName);
		CurrentEmotionModel::shared()->setEmotion(pEmotion);
		CurrentEmotionModel::shared()->createLayer(_pLayer);
		CurrentLayerModel::shared()->setLayer(_pLayer);
		CommandListModel::shared()->popCommand();

		_bRunned = false;
	}

}
