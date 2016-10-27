#include "emotiondeletecmd.h"

EmotionDeleteCmd::EmotionDeleteCmd(QString name, Emotion* pEmotion)
    : _bRunned(false),
      _charName(name)
{

    this->_pEmotion = new Emotion(pEmotion->getStartState(), pEmotion->getFinishState(), pEmotion->getTotalFrame(), pEmotion->getFrameDelay());
}

void EmotionDeleteCmd::execute()
{
    _bRunned = true;
    Character* pCurrentChar = CurrentCharacterModel::shared()->getCharacter();
    pCurrentChar->deleteEmotionItem(this->_pEmotion->getStartState());
    CurrentEmotionModel::shared()->setEmotion(pCurrentChar->getEmotionByIndex(0));
}

void EmotionDeleteCmd::undo()
{
    if(_bRunned)
    {
        Character* pCurrentChar = CurrentCharacterModel::shared()->getCharacter();
        pCurrentChar->addEmotion(_pEmotion);
        CurrentEmotionModel::shared()->setEmotion(_pEmotion);
        CommandListModel::shared()->popCommand();
        _bRunned = false;
    }
}
