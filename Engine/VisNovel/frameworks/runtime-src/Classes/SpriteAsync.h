#ifndef _SPRITE_ASYNC_H_
#define _SPRITE_ASYNC_H_

#include "cocos2d.h"

using namespace cocos2d;

class SpriteAsync : public Sprite{
private:

public:
	SpriteAsync();
	virtual ~SpriteAsync();

	static SpriteAsync* create(const char* filename, const char* zipfile = "", const char* password = "");
	virtual bool initWithFile(const char* filename, const char* zipfile = "", const char* password = "");

	virtual void onEnter();
	virtual void onExit();

	void setTexture(Texture2D* tex);
};

#endif