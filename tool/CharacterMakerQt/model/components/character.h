#ifndef CHARACTER_H
#define CHARACTER_H

#include <lib/lib.h>

class Emotion;

class Character
{
private:
	QString _charName;
	QString _fontColor;

    QVector<Emotion*> emotionList;

public:
    Character();
    Character(Character* pCharacter);
    Character(QString name);
	Character(QString name, QString fontColor);
    ~Character();

    //아래 함수들을 currentCharacterModel 쪽으로 이동하는 것이 좋을 듯.
    void addEmotion(Emotion* e);

    QString getCharName();
    QString getFontColor();

    QVector<Emotion*>* getEmotionList();
    Emotion* getEmotionByName(QString name);
    Emotion* getEmotionByIndex(int index);
//    emotion* swapEmotionOrder(int index1, index2);
    int getEmotionCount();
    QString getEmotionNameByindex(int index);
    void deleteEmotionItem(QString state);
    void setEmotionValue(Emotion* pEmotion);
};

#endif // CHARACTER_H
