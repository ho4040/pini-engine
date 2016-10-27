#ifndef CHARACTERDELETECMD_H
#define CHARACTERDELETECMD_H

#include <lib/lib.h>

class Character;

class CharacterDeleteCmd : public ICommand
{
private:
    bool    _bRunned;
    Character* _pCharacter;

public:
    CharacterDeleteCmd();
    void execute();
    void undo();
};

#endif // CHARACTERDELETECMD_H
