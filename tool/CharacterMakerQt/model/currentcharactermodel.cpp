#include "currentcharactermodel.h"

CurrentCharacterModel::CurrentCharacterModel()
{
}

void CurrentCharacterModel::setCharacter(Character* c)
{
    _pCharacter = c;
    notify(UPDATE_CHARACTER);
}

Character* CurrentCharacterModel::getCharacter()
{
    return _pCharacter;
}
QString CurrentCharacterModel::getCharName()
{
    return _pCharacter->getCharName();
}

QString CurrentCharacterModel::getFontColor()
{
    return _pCharacter->getFontColor();
}

void CurrentCharacterModel::addEmotion(Emotion* e)
{
    _pCharacter->addEmotion(e);
}
void CurrentCharacterModel::setEmotionValue(Emotion* pEmotion)
{
    _pCharacter->setEmotionValue(pEmotion);
    notify(UPDATE_EMOTION);
}
