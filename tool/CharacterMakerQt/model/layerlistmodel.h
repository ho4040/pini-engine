#ifndef LAYERLISTMODEL_H
#define LAYERLISTMODEL_H

#include <lib/lib.h>

class LayerListModel : public Notifier
{
public:
    static LayerListModel* shared()
    {
        static LayerListModel ins;
        return &ins;
    }

public:



private:
    LayerListModel();
    QList<Layer*> _pLayerList;
};

#endif // LAYERLISTMODEL_H
