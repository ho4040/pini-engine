#include "SpriteAsync.h"
#include "utils.h"
#include "AsyncLoaderManager.h"

SpriteAsync::SpriteAsync():
	Sprite()
{
}

SpriteAsync::~SpriteAsync(){
}

SpriteAsync* SpriteAsync::create(const char* filename, const char* zipfile, const char* password){
	SpriteAsync* sprite = new SpriteAsync();
	if (sprite && sprite->initWithFile(filename, zipfile, password)){
		sprite->autorelease();
		return sprite;
	}
	delete sprite;
	return nullptr;
}

bool SpriteAsync::initWithFile(const char* filename, const char* zipfile, const char* password){
	Sprite::init();
	AsyncLoaderManager::getInstance()->registSprite(this, filename, zipfile, password);
	return true;
}

void SpriteAsync::setTexture(Texture2D* tex){
	Sprite::setTexture(tex);

	Rect rect = Rect::ZERO;
	if (tex)
		rect.size = tex->getContentSize();
	setTextureRect(rect);
}

void SpriteAsync::onEnter(){
	Sprite::onEnter();
}

void SpriteAsync::onExit(){
	Sprite::onExit();
	AsyncLoaderManager::getInstance()->unregist(this);
}
