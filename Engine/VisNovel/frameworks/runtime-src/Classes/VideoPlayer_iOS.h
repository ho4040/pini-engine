#ifndef __VIDEO_PLAYER_H__
#define __VIDEO_PLAYER_H__

#include "cocos2d.h"
#include "scripting/lua-bindings/manual/CCLuaEngine.h"

#include "AppDelegateEvent.h"

#if (CC_TARGET_PLATFORM == CC_PLATFORM_WIN32 )
#include <Windows.h>
#endif

#include <mutex>
#include <thread>
#include <condition_variable>
#include <list>

using namespace std;
using namespace cocos2d;

class VideoPlayer : public Sprite, public AppDelegateEvent {
public:
	LUA_FUNCTION	m_fCallback;
public:
	VideoPlayer();
	virtual ~VideoPlayer();

	void play();
	void stop();

	void setCallback(LUA_FUNCTION func);

	void onEnter();
	void onExit();

	int getWidth() { return 0; }
	int getHeight(){ return 0; }
public:
	virtual void onForeground();
	virtual void onBackground();

public:
	bool isRun(){
		return false;
	}

protected:
	bool init(string path);
public:
	static VideoPlayer* create(string path);
};

#ifdef __cplusplus
extern "C" {
#endif    
	int luaopen_VideoPlayer_core(struct lua_State *L);
#ifdef __cplusplus
}
#endif

/*
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID || CC_TARGET_PLATFORM == CC_PLATFORM_IOS)
#else
#endif
*/

#endif
