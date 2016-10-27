#ifndef CURRENTEMOTIONMODEL_H
#define CURRENTEMOTIONMODEL_H

#include <lib/lib.h>

class CurrentEmotionModel : public Notifier
{
public:
    static CurrentEmotionModel* shared()
    {
        static CurrentEmotionModel ins;
        return &ins;
    }

public:
    void setEmotion(Emotion* e);
    Emotion* getEmotion();

    void changeValue(Emotion* e);
	Layer* createLayer(QString fileName);
	void createLayer(Layer* pLayerData);
	void deleteLayerByName(QString name);
	int	getLayerIndexByName(QString name);

private:
    CurrentEmotionModel();

private:
    Emotion* _pEmotion;
};

#endif // CURRENTEMOTIONMODEL_H
