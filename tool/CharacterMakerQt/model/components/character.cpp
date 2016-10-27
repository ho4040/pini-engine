#include "character.h"

Character::Character()
{
}
Character::Character(Character* pCharacter)
{
	this->_charName = pCharacter->getCharName();
	this->_fontColor = pCharacter->getFontColor();

    QVector<Emotion*> *pEmotionList = pCharacter->getEmotionList();
    QVector<Emotion*>::iterator iter = pEmotionList->begin();

    for(; iter != pEmotionList->end(); iter++)
    {
		Emotion* pEmotion = (*iter);
		Emotion* eData = new Emotion(pEmotion->getStartState(), pEmotion->getFinishState(), pEmotion->getTotalFrame(), pEmotion->getFrameDelay());
        this->addEmotion( eData);
    }

}
Character::Character(QString name)
	:_charName(name),
	 _fontColor("FFFFFF")
{
    Emotion* e = new Emotion("보통","보통",100,30);
	this->addEmotion(e);
}

Character::Character(QString name, QString fontColor)
	:_charName(name),
	 _fontColor(fontColor)
{

}

Character::~Character()
{
    if(emotionList.isEmpty()) return;

    QVector<Emotion*>::iterator iter = emotionList.begin();
    for(; iter != emotionList.end(); iter++)
    {
        Emotion *p = (*iter);
        delete p;
        p = NULL;
        emotionList.erase(iter);
        iter--;
    }
    emotionList.clear();
}

void Character::addEmotion(Emotion* e)
{
    if(e == NULL) return;

    emotionList.append(e);
}

QString Character::getCharName()
{
	return _charName;
}

QString Character::getFontColor()
{
	return _fontColor;
}

QVector<Emotion*>* Character::getEmotionList()
{
    return &emotionList;
}

void Character::deleteEmotionItem(QString state)
{
    QVector<Emotion*>::iterator iter = emotionList.begin();
    for(; iter != emotionList.end(); iter++)
    {
        Emotion* e = (*iter);
        if(e->getStartState() == state)
        {
            delete e;
            e = NULL;
            emotionList.erase(iter);
            break;
        }
    }
}

Emotion* Character::getEmotionByName(QString name)
{
    QVector<Emotion*>::iterator iter = emotionList.begin();
    for(; iter != emotionList.end(); iter++)
    {
        Emotion* e = (*iter);
        if(e->getStartState() == name)
        {
            return e;
        }
    }
    return NULL;
}

Emotion* Character::getEmotionByIndex(int index)
{
    if(!emotionList.isEmpty())
    {
        return emotionList.at(index);
    }
    else
    {
        return NULL;
    }
}

int Character::getEmotionCount()
{
    return emotionList.count();
}

QString Character::getEmotionNameByindex(int index)
{
    return getEmotionByIndex(index)->getStartState();
}

void Character::setEmotionValue(Emotion* pEmotion)
{
    Emotion* e = getEmotionByName(pEmotion->getStartState());

    e->setEmotionValue(pEmotion->getStartState(), pEmotion->getFinishState(), pEmotion->getTotalFrame(), pEmotion->getFrameDelay());
//    e->startState = pEmotion->startState;
//    e->finishState = pEmotion->finishState;
//    e->totalFrame = pEmotion->totalFrame;
//    e->frameDelay = pEmotion->frameDelay;
}







