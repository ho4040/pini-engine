#ifndef EMOTION_H
#define EMOTION_H

#include <lib/lib.h>

class Layer;
class Emotion
{
public:
    Emotion();
    Emotion(QString sName, QString fName, int frame, int delay);

    void setStateState(QString name);
    void setFinishState(QString name);
    void setTotalFrame(int frame);
    void setFrameDelay(int delay);
    void setEmotionValue(QString sName, QString fName, int frame, int delay);

    QString getStartState();
    QString getFinishState();
    int getTotalFrame();
    int getFrameDelay();

    Layer* createLayer(QString fileName);
    void createLayer(Layer *pLayer);
    Layer* getLayerByName(QString name);
    Layer* getLayerByIndex(int index);
    int getLayerCount();
	int getLayerIndexByName(QString name);

    void deleteLayerByName(QString name);

private:
    QString _startState;
    QString _finishState;
    int _totalFrame;
    int _frameDelay;

    QList<Layer*> _pLayerList;

};

#endif // EMOTION_H
