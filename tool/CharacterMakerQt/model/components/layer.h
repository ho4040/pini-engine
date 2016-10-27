#ifndef LAYER_H
#define LAYER_H

#include <lib/lib.h>

class Layer
{
public:
    Layer(QString fileName);
	Layer(Layer* pLayerData);
	~Layer();

	void setLayerNum(int num);
	int getLayerNum();

    void setFileName(QString fileName);
    QString getFileName();

    KeyFrame* getKeyFrameByindex(int index);
	KeyFrame* getKeyFrameByFrameIndex(int index);
	int	getkeyFrameCount();
    void addKeyFrame(KeyFrame* pkeyFrame);
	KeyFrame* createKeyFrame(int index);
    void deleteKeyFrame(int index);

	QLinkedList<KeyFrame*> *getKeyFrameList();

private:
	int _layerNum;
    QString _fileName;
    QString _emotionName;

    QLinkedList<KeyFrame*> _keyFrameList;
};

#endif // LAYER_H
