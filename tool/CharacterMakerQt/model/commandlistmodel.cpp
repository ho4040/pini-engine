#include "commandlistmodel.h"

CommandListModel::CommandListModel()
{
	_pCommandList.clear();
}

void CommandListModel::runCommand(ICommand* cmd)
{
    cmd->execute();
    _pCommandList.push_back(cmd);
}

ICommand* CommandListModel::popCommand()
{
    if(!_pCommandList.isEmpty())
    {
        ICommand* pCmd = _pCommandList.back();
        _pCommandList.pop_back();

        return pCmd;
    }

    return NULL;
}
