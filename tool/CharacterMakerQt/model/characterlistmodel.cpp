#include "characterlistmodel.h"

CharacterListModel::CharacterListModel()
{
}

CharacterListModel::~CharacterListModel()
{
    if(!pCharacterList.isEmpty())
    {
        QVector<Character*>::iterator iter = pCharacterList.begin();
        for(; iter!=pCharacterList.end(); iter++)
        {
            Character* pChar = (*iter);
            if(pChar != NULL)
            {
                delete pChar;
                pChar = NULL;
                pCharacterList.erase(iter);
            }
            else
            {
                pCharacterList.erase(iter);
            }
            iter--;
        }
    }
}

Character* CharacterListModel::createCharacter(QString name)
{
    Character* pCharacter = new Character(name);
    pCharacterList.append(pCharacter);
	notify(ALL_UPDATE);
    return pCharacter;
}

void CharacterListModel::createCharacter(Character *pCharacter)
{
    pCharacterList.append(pCharacter);
	//notify(ALL_UPDATE);
}

Emotion* CharacterListModel::addEmotionData(QString name, QString eName)
{
    Character* c = getCharacterByName(name);

    // 감정을 추가하면 기본적으로 추가되는 값
    Emotion *e = new Emotion(eName, eName, 100, 30);
    c->addEmotion(e);

	notify(ALL_UPDATE);

    return e;
}

QVector<Character*>* CharacterListModel::getCharacterList()
{
    return &pCharacterList;
}

Character* CharacterListModel::getCharacterByName(QString name)
{
    QVector<Character*>::iterator iter = pCharacterList.begin();
    for(; iter != pCharacterList.end(); iter++)
    {
        Character *p = (*iter);
        if(p->getCharName() == name)
        {
            return p;
        }
    }

    return NULL;
}
Character* CharacterListModel::getCharacterByIndex(int index)
{
    if(!pCharacterList.isEmpty())
    {
        return pCharacterList.at(index);
    }
    else
    {
        return NULL;
    }

}

int CharacterListModel::getCharacterListCount()
{
	return pCharacterList.count();
}

void CharacterListModel::characterListUpdate()
{
	notify(ALL_UPDATE);
}

void CharacterListModel::deleteCharacterData(QString name)
{
    QVector<Character*>::iterator iter = pCharacterList.begin();
    for(; iter != pCharacterList.end(); iter++)
    {
        Character *p = (*iter);
        if(p->getCharName() == name)
        {
            delete p;
            p = NULL;
            pCharacterList.erase(iter);
            iter--;
        }
    }

    notify(ALL_UPDATE);
}

void CharacterListModel::deleteEmotionData(QString name, QString eName)
{
    Character* c = getCharacterByName(name);

    if(c == NULL) return;

    c->deleteEmotionItem(eName);
    notify(ALL_UPDATE);
}
