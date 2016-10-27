#ifndef KEYFRAMEADDCMD_H
#define KEYFRAMEADDCMD_H

#include <lib/lib.h>

class KeyFrameAddCmd : public ICommand
{
private:
	bool		_bRunned;
	QString		_charName;
	QString		_emotionName;
	int			_layerIndex;
	int			_frameIndex;

public:
    KeyFrameAddCmd();
	KeyFrameAddCmd(int layerIndex, int frameIndex);

	void execute();
	void undo();
};

#endif // KEYFRAMEADDCMD_H
