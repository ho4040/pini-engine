#ifndef COMMANDLISTMODEL_H
#define COMMANDLISTMODEL_H

#include <lib/lib.h>


class CommandListModel : public Notifier
{
public:
    static CommandListModel* shared()
    {
        static CommandListModel ins;
        return &ins;
    }

    void runCommand(ICommand* cmd);
    ICommand* popCommand();

private:
    CommandListModel();

    QList<ICommand*> _pCommandList;
};

#endif // COMMANDLISTMODEL_H
