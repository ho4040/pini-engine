#ifndef CURRENTFRAMEMODEL_H
#define CURRENTFRAMEMODEL_H

#include <lib/lib.h>

class CurrentFrameModel : public Notifier
{
public:
    static CurrentFrameModel* shared()
    {
        static CurrentFrameModel ins;
        return &ins;
    }

public:
    void setKeyFrame(KeyFrame* k);
    KeyFrame* getKeyFrame();

	void setKeyFrameIndex(int index);
	int getKeyFrameIndex();

private:
    CurrentFrameModel();

	int _keyFrameIndex;
    KeyFrame* _pKeyFrame;
};

#endif // CURRENTFRAMEMODEL_H
