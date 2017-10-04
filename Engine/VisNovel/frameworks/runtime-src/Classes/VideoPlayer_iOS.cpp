#include "VideoPlayer_iOS.h"
#include "AppDelegate.h"
#include "utils.h"

#include <stdio.h>
#include <string.h>

VideoPlayer::VideoPlayer(){
}

VideoPlayer::~VideoPlayer(){
}

bool VideoPlayer::init(string path){
    return -1;
}

void VideoPlayer::play(){
}

void VideoPlayer::onEnter(){
	CCSprite::onEnter();
}

void VideoPlayer::onExit(){
	CCSprite::onExit();
	stop();
}

void VideoPlayer::onForeground(){
}

void VideoPlayer::onBackground(){
}

void VideoPlayer::stop(){
}

void VideoPlayer::setCallback(LUA_FUNCTION func){
	m_fCallback = func;
}

VideoPlayer* VideoPlayer::create(string path){
	VideoPlayer* self = new VideoPlayer();
	if (self->init(path)){
		self->autorelease();
		return self;
	}
	return nullptr;
}


#include <lua.h>
#include <lauxlib.h>
#include "scripting/lua-bindings/manual/tolua_fix.h"
static int lua_videoplayer_create(lua_State *L) {
	const char *message = luaL_checklstring(L, 2, NULL);
	VideoPlayer* tolua_ret = VideoPlayer::create(message);

	int nID = (tolua_ret) ? (int)tolua_ret->_ID : -1;
	int* pLuaID = (tolua_ret) ? &tolua_ret->_luaID : NULL;
	toluafix_pushusertype_ccobject(L, nID, pLuaID, (void*)tolua_ret, "npini.VideoPlayer");
	
	return 1;
}

static int lua_videoplayer_play(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	cobj->play();
	return 0;
}

static int lua_videoplayer_stop(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	cobj->stop();
	return 0;
}

static int lua_videoplayer_setCallback(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	LUA_FUNCTION handler = toluafix_ref_function(L, 2, 0);

	cobj->setCallback(handler);

	return 0;
}
static int lua_videoplayer_getWidth(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	tolua_pushnumber(L, cobj->getWidth() );
	return 1;
}
static int lua_videoplayer_getHeight(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	tolua_pushnumber(L, cobj->getHeight());
	return 1;
}

int luaopen_VideoPlayer_core(struct lua_State *L){
	tolua_usertype(L, "npini.VideoPlayer");
	tolua_cclass(L, "VideoPlayer", "npini.VideoPlayer", "cc.Sprite", nullptr);

	tolua_beginmodule(L, "VideoPlayer");
	tolua_function(L, "create", lua_videoplayer_create);
	tolua_function(L, "play", lua_videoplayer_play);
	tolua_function(L, "stop", lua_videoplayer_stop);
	tolua_function(L, "setCallback", lua_videoplayer_setCallback);
	tolua_function(L, "getWidth", lua_videoplayer_getWidth);
	tolua_function(L, "getHeight", lua_videoplayer_getHeight);
	tolua_endmodule(L);
	return 1;
}
