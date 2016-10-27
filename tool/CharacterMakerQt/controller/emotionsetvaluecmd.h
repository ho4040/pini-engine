#ifndef EMOTIONSETVALUECMD_H
#define EMOTIONSETVALUECMD_H

#include <lib/lib.h>

class EmotionSetValueCmd : public ICommand
{
private:
    bool _bRunned;
    QString _charName;
    Emotion* _pNewEmotion;
    Emotion* _pOldEmotion;

public:
    EmotionSetValueCmd(Emotion* pEmotion);

    void execute();
    void undo();
};

#endif // EMOTIONSETVALUECMD_H
