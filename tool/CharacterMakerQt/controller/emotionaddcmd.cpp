#include "emotionaddcmd.h"

EmotionAddCmd::EmotionAddCmd(QString eName)
    : _bRunned(false),
      _charName(""),
      _emotionName(eName)
{

}

void EmotionAddCmd::execute()
{
    _bRunned = true;
    _charName = CurrentCharacterModel::shared()->getCharacter()->getCharName();
    Emotion* pEmotion = CharacterListModel::shared()->addEmotionData(_charName, _emotionName);
    CurrentEmotionModel::shared()->setEmotion(pEmotion);

}

void EmotionAddCmd::undo()
{
    if(_bRunned)
	{
        CharacterListModel::shared()->deleteEmotionData(_charName,_emotionName);
        CommandListModel::shared()->popCommand();
        _bRunned = false;
    }
}
