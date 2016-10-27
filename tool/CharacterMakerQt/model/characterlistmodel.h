#ifndef CHARACTERLISTMODEL_H
#define CHARACTERLISTMODEL_H

#include <lib/lib.h>

class CharacterListModel : public Notifier
{
public:
    static CharacterListModel* shared()
    {
        static CharacterListModel ins;
        return &ins;
    }
    ~CharacterListModel();

public:
    Character* createCharacter(QString name);
    void createCharacter(Character *pCharacter);
    Emotion* addEmotionData(QString name, QString eName);
    void deleteCharacterData(QString name);
    void deleteEmotionData(QString name, QString eName);
    QVector<Character*>* getCharacterList();
    Character* getCharacterByName(QString name);
    Character* getCharacterByIndex(int index);
	int getCharacterListCount();
	void characterListUpdate();

private:
    CharacterListModel();
    QVector<Character*> pCharacterList;

};

#endif // CHARACTERLISTMODEL_H
