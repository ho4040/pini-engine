#include "AsyncLoaderManager.h"
#include "SpriteAsync.h"
#include "lua_utils.h"
#include "utils.h"

AsyncLoaderManager* asyncLoaderManagerInst = nullptr;
AsyncLoaderManager* AsyncLoaderManager::getInstance(){
	if (asyncLoaderManagerInst == nullptr){
		asyncLoaderManagerInst = new AsyncLoaderManager;
	}
	return asyncLoaderManagerInst;
}

void AsyncLoaderManager::purge(){
	delete asyncLoaderManagerInst;
}

AsyncLoaderManager::AsyncLoaderManager():
_closeSpriteLoadThread(false),
_spriteAsyncThread(nullptr)
{
	_closeSpriteLoadThread = false;
	_spriteAsyncThread = new std::thread(&AsyncLoaderManager::loadThread,this);
	Director::getInstance()->getScheduler()->schedule(CC_SCHEDULE_SELECTOR(AsyncLoaderManager::update), this, 0, false);
}

AsyncLoaderManager::~AsyncLoaderManager(){
	if (_spriteAsyncThread){
		_closeSpriteLoadThread = true;
		_spriteAsyncSleepCondition.notify_one();
		_spriteAsyncThread->join();
		CC_SAFE_DELETE(_spriteAsyncThread);
	}
}

void AsyncLoaderManager::registSprite(Sprite* target, const char* filename, const char* zipfile, const char* password){
	CCTexture2D* texture = TextureCache::getInstance()->getTextureForKey(filename);
	if (texture){
		target->setTexture(texture);
	}
	else if (FileUtils::getInstance()->isFileExist(filename)){
		RequestNode node = { target, SPRITE };
		_spriteAsyncQueueMutex.lock();
		_mapSpriteList.insert(std::pair<string, RequestNode>(std::string(filename), node));
		_spriteAsyncQueueMutex.unlock();

		string fn = string(filename);
		CCTextureCache::getInstance()->addImageAsync(filename, [fn, target, this](Texture2D* tex){
			if(_mapRequestTextureCache.find(target) != _mapRequestTextureCache.end()){
				SpriteLoadInfo _ = { fn, "", "", SPRITE };
				LoadedInfo i = { _, nullptr, target, SPRITE };
				_spriteAsyncQueueMutex.lock();
				ERASE_MAP(_mapLoadRequest, target);
				_mapLoadRespone[target] = i;
				_mapRequestTextureCache[target] = tex;
				_spriteAsyncQueueMutex.unlock();
			}
		});
		_mapRequestTextureCache[target] = nullptr;
		target->retain();
		
		SpriteLoadInfo spriteInfo = { filename, zipfile, password, SPRITE };
		
		_spriteAsyncQueueMutex.lock();
		_mapLoadRequest[target] = spriteInfo;
		_spriteAsyncQueueMutex.unlock();
	}
	else{
		RequestNode node = { target, SPRITE_ZIP };
		SpriteLoadInfo spriteInfo = { filename, zipfile, password, SPRITE_ZIP };

		_spriteAsyncQueueMutex.lock();
		_mapLoadRequest[target] = spriteInfo;
		_mapSpriteList.insert(std::pair<string, RequestNode>(std::string(filename), node));
		_spriteAsyncQueueMutex.unlock();

		_spriteAsyncSleepCondition.notify_one();
	}
}

void AsyncLoaderManager::registText(LabelTTF* target, const char* text, const char* fontName, int size){
}

void AsyncLoaderManager::unregist(CCNode* target){
	auto fn = _mapLoadRequest.find(target);
	int type;
	string filename;
	if (fn == _mapLoadRequest.end())
	{
		auto fn = _mapLoadRespone.find(target);
		if (fn == _mapLoadRespone.end())
			return;
		type = fn->second.info.type;
		filename = fn->second.info.filename;
	}
	else{
		type = fn->second.type;
		filename = fn->second.filename;
	}
	
	switch (type){
	case SPRITE:
		_spriteAsyncQueueMutex.lock();
		ERASE_MAP(_mapLoadRequest, target);
		ERASE_MULTIMAP(_mapSpriteList, filename, target);
		_spriteAsyncQueueMutex.unlock();

		ERASE_MAP(_mapRequestTextureCache, target);
		target->autorelease();
		break;
	case SPRITE_ZIP:
		_spriteAsyncQueueMutex.lock();
		ERASE_MAP(_mapLoadRequest, target);
		ERASE_MAP(_mapLoadRespone, target);
		ERASE_MULTIMAP(_mapSpriteList, filename, target);
		_spriteAsyncQueueMutex.unlock();
		break;
	}
}

void AsyncLoaderManager::update(float dt){
	if (_mapLoadRespone.size() > 0){
		_spriteAsyncQueueMutex.lock();
		auto fn = _mapLoadRespone.begin();
		LoadedInfo info = fn->second;
		_mapLoadRespone.erase(fn);
		_spriteAsyncQueueMutex.unlock();

		switch (info.type){
			case SPRITE:{
				auto fn = _mapRequestTextureCache.find(info.node);
				if (fn != _mapRequestTextureCache.end()){
					if (fn->second){
						CCTexture2D* texture = fn->second;
						((SpriteAsync*)fn->first)->setTexture(texture);
						fn->first->autorelease();
						_mapRequestTextureCache.erase(fn);

						_spriteAsyncQueueMutex.lock();
						auto range = _mapSpriteList.equal_range(info.info.filename);
						for (auto b = range.first; b != range.second; b++){
							((SpriteAsync*)b->second.node)->setTexture(texture);
							ERASE_MAP(_mapLoadRespone, b->second.node);
						}
						_mapSpriteList.erase(info.info.filename);
						_spriteAsyncQueueMutex.unlock();
					}
				}
			}break;
			case SPRITE_ZIP:{
				Texture2D* texture = nullptr;
				if (info.image){
					TextureCache::getInstance()->addImage(info.image, info.info.filename);

					texture = new Texture2D;
					texture->initWithImage(info.image);
					texture->autorelease();
					delete info.image;
				}
				else{
					texture = TextureCache::getInstance()->textureForKey(info.info.filename);
				}
				if (texture){
					((SpriteAsync*)info.node)->setTexture(texture);
				}

				_spriteAsyncQueueMutex.lock();
				auto range = _mapSpriteList.equal_range(info.info.filename);
				for (auto b = range.first; b != range.second; b++){
					((SpriteAsync*)b->second.node)->setTexture(texture);
					ERASE_MAP(_mapLoadRespone, b->second.node);
				}
				_mapSpriteList.erase(info.info.filename);
				_spriteAsyncQueueMutex.unlock();
			}break;
		}
	}
}

void AsyncLoaderManager::loadThread(){
	while (1){
		Sleep(1);
		if (_closeSpriteLoadThread){
			break;
		}
		if (_mapLoadRequest.size() == 0){
			std::unique_lock<std::mutex> lk(_spriteAsyncSleepMutex);
			_spriteAsyncSleepCondition.wait(lk);
			continue;
		}

		_spriteAsyncQueueMutex.lock();
		auto fn = _mapLoadRequest.begin();
		if (fn->second.type != SPRITE_ZIP){
			_spriteAsyncQueueMutex.unlock();
			continue;
		}

		CCTexture2D* texture = TextureCache::getInstance()->getTextureForKey(fn->second.filename);
		if (texture){
			LoadedInfo i = { fn->second, NULL };
			_mapLoadRespone[fn->first] = i;
			_mapLoadRequest.erase(fn);
			_spriteAsyncQueueMutex.unlock();
			continue;
		}
		
		SpriteLoadInfo info = fn->second;
		CCNode* node = fn->first;

		_spriteAsyncQueueMutex.unlock();

		ssize_t pSize = 0;
		const unsigned char * tdata = nullptr;
		if (info.password.length() > 0){
			tdata = getFileDataFromZipWithPassword(info.zipname, info.filename, info.password, &pSize);
		}
		else{
			tdata = FileUtils::getInstance()->getFileDataFromZip(info.zipname, info.filename, &pSize);
		}

		if (tdata){
			Image* image = new (std::nothrow) Image();
			if (image->initWithImageData(tdata, pSize)){
				_spriteAsyncQueueMutex.lock();
				if (_mapLoadRequest.find(node) != _mapLoadRequest.end()){
					LoadedInfo i = { info, image, node, fn->second.type };
					_mapLoadRespone[node] = i;
				}
				_spriteAsyncQueueMutex.unlock();
			}
			free((void*)tdata);
		}

		_spriteAsyncQueueMutex.lock();
		if (_mapLoadRequest.find(node) != _mapLoadRequest.end()){
			_mapLoadRequest.erase(fn);
		}
		_spriteAsyncQueueMutex.unlock();
	}
}
