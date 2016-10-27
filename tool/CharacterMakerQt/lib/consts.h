#ifndef CONSTS_H
#define CONSTS_H
#include <QtCore>
#include <lib/geoLib.h>

#define KEYFRAMESTARTX	80
#define KEYFRAMESTARTY	30
#define KEYFRAMESIZEX	15
#define KEYFRAMESIZEY	30

enum NOTIS{
    UPDATE_CHARACTER,
    UPDATE_EMOTION,
    UPDATE_LAYER,
    UPDATE_FRAME,
    ALL_UPDATE
};

class Layer;

struct KeyFrame
{
	KeyFrame(int findex) : frameIndex(findex), rotation(0.0f), position(0,0), scale(0, 0) {}
	KeyFrame(int findex, float rot, Vector2d pos, Vector2d s)
		: frameIndex(findex), rotation(rot), position(pos.x,pos.y), scale(s.x, s.y) {}
	KeyFrame(Layer* pPart, float rot, Vector2d pos, Vector2d s)
		: pParent(pPart), rotation(rot), position(pos.x,pos.y), scale(s.x, s.y) {}

	Layer		*pParent;
	int         frameIndex;
	float       rotation;
	Vector2d    position;
	Vector2d    scale;
};

#endif // CONSTS_H
