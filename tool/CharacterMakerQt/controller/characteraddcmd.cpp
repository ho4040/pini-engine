#include "characteraddcmd.h"

CharacterAddCmd::CharacterAddCmd(QString name)
    : _bRunned(false),
      _charName(name)
{

}

void CharacterAddCmd::execute()
{
    _bRunned = true;
    Character* pCharacter = CharacterListModel::shared()->createCharacter(_charName);
    CurrentCharacterModel::shared()->setCharacter(pCharacter);
    CurrentEmotionModel::shared()->setEmotion(pCharacter->getEmotionList()->at(0));
}

void CharacterAddCmd::undo()
{
    if(_bRunned){
        CharacterListModel::shared()->deleteCharacterData(_charName);
        CommandListModel::shared()->popCommand();
        _bRunned = false;
    }
}
