#ifndef LAYERSELECTCMD_H
#define LAYERSELECTCMD_H

#include <lib/lib.h>

class LayerSelectCmd : public ICommand
{

private:
	bool _bRunned;
	int _index;

public:
	LayerSelectCmd(int index);

	void execute();
	void undo();
};

#endif // LAYERSELECTCMD_H
