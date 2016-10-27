#ifndef KEYFRAMESELECTCMD_H
#define KEYFRAMESELECTCMD_H

#include <lib/lib.h>

class KeyFrameSelectCmd : public ICommand
{
private:
	bool	_bRunned;
	int		_index;

public:
	KeyFrameSelectCmd(int index);

	void execute();
	void undo();
};

#endif // KEYFRAMESELECTCMD_H
