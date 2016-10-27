#ifndef LAYERDELETECMD_H
#define LAYERDELETECMD_H

#include <lib/lib.h>

class LayerDeleteCmd : public ICommand
{

private:
	bool _bRunned;
	QString _charName;
	QString _emotionName;
	QString _layerName;
	Layer*	_pLayer;

public:
	LayerDeleteCmd(QString lName, QString eName);

	void execute();
	void undo();
};

#endif // LAYERDELETECMD_H
