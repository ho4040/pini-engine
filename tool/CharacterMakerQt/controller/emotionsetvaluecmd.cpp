#include "emotionsetvaluecmd.h"

EmotionSetValueCmd::EmotionSetValueCmd(Emotion* pEmotion)
    : _bRunned(false),
      _pNewEmotion(pEmotion)
{
    _charName = CurrentCharacterModel::shared()->getCharacter()->getCharName();
}

void EmotionSetValueCmd::execute()
{
    _bRunned = true;
    Emotion* pCurrentEmotion = CurrentEmotionModel::shared()->getEmotion();

    _pOldEmotion = new Emotion(pCurrentEmotion->getStartState(), pCurrentEmotion->getFinishState(), pCurrentEmotion->getTotalFrame(), pCurrentEmotion->getFrameDelay());
//    _pOldEmotion->startState = pCurrentEmotion->startState;
//    _pOldEmotion->finishState = pCurrentEmotion->finishState;
//    _pOldEmotion->totalFrame = pCurrentEmotion->totalFrame;
//    _pOldEmotion->frameDelay = pCurrentEmotion->frameDelay;

    CurrentCharacterModel::shared()->setEmotionValue(_pNewEmotion);
}

void EmotionSetValueCmd::undo()
{
    if (_bRunned) {
        Character* pCharacter = CharacterListModel::shared()->getCharacterByName(_charName);
        CurrentCharacterModel::shared()->setCharacter(pCharacter);
        CurrentCharacterModel::shared()->setEmotionValue(_pOldEmotion);

        Emotion* pE =  pCharacter->getEmotionByName(_pOldEmotion->getStartState());
        CurrentEmotionModel::shared()->setEmotion(pE);
        delete _pOldEmotion;
        _bRunned = false;
    }
}
