#ifndef KEYFRAMEDELETECMD_H
#define KEYFRAMEDELETECMD_H

#include <lib/lib.h>

class KeyFrameDeleteCmd : public ICommand
{
private:
	bool		_bRunned;
	KeyFrame*	_pKeyFrame;
	QString		_layerName;

public:
	KeyFrameDeleteCmd(QString layerName, KeyFrame* pKeyFrame);

	void execute();
	void undo();
};

#endif // KEYFRAMEDELETECMD_H
