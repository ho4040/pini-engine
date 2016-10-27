#include "characterdeletecmd.h"

CharacterDeleteCmd::CharacterDeleteCmd()
    : _bRunned(false)
{

}

void CharacterDeleteCmd::execute()
{

    _bRunned = true;
    Character* pChar = CurrentCharacterModel::shared()->getCharacter();
    _pCharacter = new Character(pChar);
    CharacterListModel::shared()->deleteCharacterData(pChar->getCharName());
}

void CharacterDeleteCmd::undo()
{
    if(_bRunned)
    {
        CharacterListModel::shared()->createCharacter(_pCharacter);
        CurrentCharacterModel::shared()->setCharacter(_pCharacter);
        CurrentEmotionModel::shared()->setEmotion(_pCharacter->getEmotionList()->at(0));
        CommandListModel::shared()->popCommand();
        _bRunned = false;
    }
}
