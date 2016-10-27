#include "layeraddcmd.h"

LayerAddCmd::LayerAddCmd(QString name)
    : _bRunned(false),
    _layerName(name)
{
    _charName = CurrentCharacterModel::shared()->getCharName();
    _emotionName = CurrentEmotionModel::shared()->getEmotion()->getStartState();
}

void LayerAddCmd::execute()
{
    _bRunned = true;
    Layer* pLayer = CurrentEmotionModel::shared()->createLayer(_layerName);
    CurrentLayerModel::shared()->setLayer(pLayer);
	CurrentFrameModel::shared()->setKeyFrame(pLayer->getKeyFrameByindex(0));
}

void LayerAddCmd::undo()
{
    if(_bRunned)
    {
        _bRunned = false;
        Character* pChar = CharacterListModel::shared()->getCharacterByName(_charName);
        Emotion* pEmotion = pChar->getEmotionByName(_emotionName);

        CurrentCharacterModel::shared()->setCharacter(pChar);
        CurrentEmotionModel::shared()->setEmotion(pEmotion);
        pEmotion->deleteLayerByName(_layerName);
        CurrentLayerModel::shared()->setLayer(pEmotion->getLayerByIndex(0));
    }
}
