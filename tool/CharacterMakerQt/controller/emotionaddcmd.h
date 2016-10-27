#ifndef EMOTIONADDCMD_H
#define EMOTIONADDCMD_H

#include <lib/lib.h>

class EmotionAddCmd : public ICommand
{
private:
    bool    _bRunned;
    QString _charName;
    QString _emotionName;

public:
    EmotionAddCmd(QString eName);

    void execute();
    void undo();
};

#endif // EMOTIONADDCMD_H
