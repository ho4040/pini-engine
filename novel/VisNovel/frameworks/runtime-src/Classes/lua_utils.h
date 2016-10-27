#ifndef _LUA_UTILES_FUNCTIONS_
#define _LUA_UTILES_FUNCTIONS_

#include "cocos2d.h"
using namespace std;
using namespace cocos2d;


extern "C" {
#include <lua.h>
	extern int luaopen_luautils_core(struct lua_State *L);
}

extern unsigned char* getFileDataFromZipWithPassword(const std::string& zipFilePath, const std::string& filename, const std::string& password, ssize_t *size);

#endif