#ifndef ICOMMAND_H
#define ICOMMAND_H

class ICommand
{
public:
    ICommand();
    virtual void execute(){}
    virtual void undo(){}
};

#endif // ICOMMAND_H
