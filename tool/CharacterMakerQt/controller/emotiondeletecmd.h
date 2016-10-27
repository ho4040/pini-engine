#ifndef EMOTIONDELETECMD_H
#define EMOTIONDELETECMD_H
#include <lib/lib.h>

class EmotionDeleteCmd : public ICommand
{
private:
    bool _bRunned;
    QString _charName;
    Emotion *_pEmotion;

public:
    EmotionDeleteCmd(QString name, Emotion* pEmotion);

    void execute();
    void undo();
};

#endif // EMOTIONDELETECMD_H
