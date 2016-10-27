#ifndef LAYERADDCMD_H
#define LAYERADDCMD_H

#include <lib/lib.h>

class LayerAddCmd : public ICommand
{
private:
    bool _bRunned;
    QString _charName;
    QString _emotionName;
    QString _layerName;

public:
    LayerAddCmd(QString name);

    void execute();
    void undo();
};

#endif // LAYERADDCMD_H
