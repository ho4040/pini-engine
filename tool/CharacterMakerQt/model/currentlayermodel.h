#ifndef CURRENTLAYERMODEL_H
#define CURRENTLAYERMODEL_H

#include <lib/lib.h>

class CurrentLayerModel : public Notifier
{
public:
    static CurrentLayerModel* shared()
    {
        static CurrentLayerModel ins;
        return &ins;
    }

public:
    void setLayer(Layer* pLayer);
    Layer* getLayer();
	KeyFrame* createKeyFrame(int index);
    void addKeyFrame(KeyFrame* pkeyFrame);
    void deleteKeyFrame(int index);

private:
    CurrentLayerModel();

    Layer* _pLayer;
};

#endif // CURRENTLAYERMODEL_H
