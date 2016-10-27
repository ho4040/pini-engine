#ifndef _ASYNC_LOADER_MANAGER_H_
#define _ASYNC_LOADER_MANAGER_H_

#include "cocos2d.h"

using namespace std;
using namespace cocos2d;

enum{
	SPRITE = 1,
	SPRITE_ZIP = 2
};

typedef struct SpriteLoadInfo_{
	std::string filename;
	std::string zipname;
	std::string password;
	int type;
} SpriteLoadInfo;

typedef struct LoadedInfo_{
	SpriteLoadInfo info;
	Image* image;
	Node* node;
	int type;
} LoadedInfo;

typedef struct RequestNode_{
	Node* node;
	int type;
}RequestNode;

#define ERASE_MAP(map,key) \
{\
	if (map.find(key) != map.end()){ \
		map.erase(map.find(key)); \
	}\
}

#define ERASE_MULTIMAP(multimap,key1,key2) \
{\
	auto range = multimap.equal_range(key1);\
	for (auto b = range.first; b != range.second; b++){\
		if (b->second.node == key2){\
			multimap.erase(b);\
			break;\
				}\
		}\
}

class AsyncLoaderManager : public Ref{
private:
	bool _closeSpriteLoadThread;
	std::thread* _spriteAsyncThread;
	
	std::map<CCNode*, SpriteLoadInfo> _mapLoadRequest;
	std::map<CCNode*, LoadedInfo> _mapLoadRespone;
	std::map<CCNode*, Texture2D*> _mapRequestTextureCache;
	std::multimap<string, RequestNode > _mapSpriteList;

	std::mutex _spriteAsyncQueueMutex;
	std::mutex _spriteAsyncSleepMutex;
	std::condition_variable _spriteAsyncSleepCondition;

public:
	AsyncLoaderManager();
	virtual ~AsyncLoaderManager();

	void registSprite(Sprite*, const char* path, const char* zip, const char* password);
	void registText(LabelTTF*, const char* text, const char* fontName, int size);
	void unregist(CCNode*);

	void loadThread();
	virtual void update(float dt);

public:
	static AsyncLoaderManager* getInstance();
	static void purge();

};

#endif