#ifndef CHARACTERADDCMD_H
#define CHARACTERADDCMD_H

#include <lib/lib.h>

class CharacterAddCmd : public ICommand
{
private:
    bool _bRunned;
    QString _charName;

public:
    CharacterAddCmd(QString name);

    void execute();
    void undo();
};

#endif // CHARACTERADDCMD_H
