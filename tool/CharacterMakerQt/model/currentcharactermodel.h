#ifndef CURRENTCHARACTERMODEL_H
#define CURRENTCHARACTERMODEL_H

#include <lib/lib.h>

class CurrentCharacterModel : public Notifier
{
public:
    static CurrentCharacterModel* shared()
    {
        static CurrentCharacterModel ins;
        return &ins;
    }

public:
    void setCharacter(Character* c);
    Character* getCharacter();

    void addEmotion(Emotion* e);
    void setEmotionValue(Emotion* pEmotion);

    QString getCharName();
    QString getFontColor();

    QVector<Emotion*>* getEmotionList();
    Emotion* getEmotionByName(QString name);
    Emotion* getEmotionByIndex(int index);

private:
    CurrentCharacterModel();

private:
    Character* _pCharacter;
};

#endif // CURRENTCHARACTERMODEL_H
