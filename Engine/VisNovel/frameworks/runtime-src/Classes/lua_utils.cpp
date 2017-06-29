#include "lua_utils.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}
#include "scripting/lua-bindings/manual/CCLuaEngine.h"
#include "scripting/lua-bindings/manual/tolua_fix.h"

#include "audio/include/AudioEngine.h"

#include "base/base64.h"

#include "ATL.h"
#include "SpriteAsync.h"

#include <cctype>
#include <locale>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <fcntl.h>
#include <unzip/unzip.h>

#include <json/rapidjson.h>
#include <json/stringbuffer.h>
#include <json/writer.h>

#include "dirent.h"

#if defined(_MSC_VER) || defined(__MINGW32__)
#include <io.h>
#include <WS2tcpip.h>
#include <Winsock2.h>
#include <iphlpapi.h>
#include "../proj.win32/SimulatorWin.h"
#define bzero(a, b) memset(a, 0, b);
#if (CC_TARGET_PLATFORM == CC_PLATFORM_WP8) || (CC_TARGET_PLATFORM == CC_PLATFORM_WINRT)
#include "inet_ntop_winrt.h"
#include "CCWinRTUtils.h"
#endif
#else
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID)
#include "ifaddrs_android/ifaddrs.h"
#include <unistd.h>
#endif
#if (CC_TARGET_PLATFORM == CC_PLATFORM_MAC) || (CC_TARGET_PLATFORM == CC_PLATFORM_IOS)
#include <sys/types.h>
#include <sys/socket.h>
#include <ifaddrs.h>
#endif
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#endif

/////////////////////////////////////////////////
class _ZIP_LOAD_ {
public:
	~_ZIP_LOAD_(){
		auto b = _cache.begin();
		auto e = _cache.end();
		for (; b != e;b++){
			unzClose(b->second);
		}
	}

	unzFile fileptr(string str){
		auto f = _cache.find(str);
		if (f == _cache.end())
			return nullptr;
		return f->second;
	}

	void add(string str, unzFile f){
		_cache[str] = f;
	}
private:
	map <string, unzFile> _cache;
};

_ZIP_LOAD_ ZIP_LOAD;
std::mutex _ZIP_LOAD_MUTEX;

using namespace cocos2d;

unsigned char* getFileDataFromZipWithPassword(const std::string& zipFilePath, const std::string& filename, const std::string& password, ssize_t *size)
{
	_ZIP_LOAD_MUTEX.lock();
	double start = utils::gettime();
	////CCLog("###getFileDataFromZipWithPassword > 1 > %f", utils::gettime() - start);

	unsigned char * buffer = nullptr;
	unzFile file = nullptr;
	*size = 0;

	const unsigned char * pBuffer = nullptr;
	do
	{
		CC_BREAK_IF(zipFilePath.empty());
		file = ZIP_LOAD.fileptr(zipFilePath);
		if (file == nullptr){
			//CCLog("###getFileDataFromZipWithPassword > 2 > %f", utils::gettime() - start);
			if (zipFilePath.at(0) == '/'){
				file = unzOpen(zipFilePath.c_str());
				//CCLog("###getFileDataFromZipWithPassword > 3-1 > %f", utils::gettime() - start);
			}
			else{
				auto files = FileUtils::getInstance();
				if (files->isFileExist(files->getWritablePath() + zipFilePath)){
					string __file = files->getWritablePath() + zipFilePath;
					file = unzOpen(__file.c_str());
					//CCLog("###getFileDataFromZipWithPassword > 3-2 > %f", utils::gettime() - start);
				}
				else{
					ssize_t __size;
					pBuffer = FileUtils::getInstance()->getFileData(zipFilePath, "rb", &__size);
					//CCLog("###getFileDataFromZipWithPassword > 3-3 > %f", utils::gettime() - start);
					file = unzOpenBuffer(pBuffer, __size);
					//CCLog("###getFileDataFromZipWithPassword > 3-31 > %f", utils::gettime() - start);
				}
			}
			ZIP_LOAD.add(zipFilePath, file);
		}

		
		CC_BREAK_IF(!file);
		//CCLog("###getFileDataFromZipWithPassword > 4 > %f", utils::gettime() - start);

		// FIXME: Other platforms should use upstream minizip like mingw-w64  
#ifdef MINIZIP_FROM_SYSTEM
		int ret = unzLocateFile(file, filename.c_str(), NULL);
#else
		int ret = unzLocateFile(file, filename.c_str(), 1);
#endif
		CC_BREAK_IF(UNZ_OK != ret);
		//CCLog("###getFileDataFromZipWithPassword > 5 > %f", utils::gettime() - start);

		char filePathA[260];
		unz_file_info fileInfo;
		ret = unzGetCurrentFileInfo(file, &fileInfo, filePathA, sizeof(filePathA), nullptr, 0, nullptr, 0);
		//CCLog("###getFileDataFromZipWithPassword > 6 > %d > %s > %s", ret, file, filename.c_str());
		CC_BREAK_IF(UNZ_OK != ret);

		//ret = unzOpenCurrentFilePassword(file, password.c_str());
		ret = unzOpenCurrentFilePassword(file, password.c_str());
		CC_BREAK_IF(UNZ_OK != ret);
		//CCLog("###getFileDataFromZipWithPassword > 7 > %f", utils::gettime() - start);

		buffer = (unsigned char*)malloc(fileInfo.uncompressed_size);
		int CC_UNUSED readedSize = unzReadCurrentFile(file, buffer, static_cast<unsigned>(fileInfo.uncompressed_size));
		CC_BREAK_IF(readedSize != 0 && readedSize != (int)fileInfo.uncompressed_size);
		//CCLog("###getFileDataFromZipWithPassword > 8 > %f", utils::gettime() - start);

		*size = fileInfo.uncompressed_size;
		unzCloseCurrentFile(file);
		//CCLog("###getFileDataFromZipWithPassword > 9 > %f", utils::gettime() - start);
	} while (0);

	if (pBuffer)
		delete []pBuffer;
	_ZIP_LOAD_MUTEX.unlock();

	return buffer;
}

static int messagebox(lua_State *L) {
	const char *message = luaL_checklstring(L, 1, NULL);
	const char *title = luaL_checklstring(L, 2, NULL);
	
	cocos2d::MessageBox(message, title);

	return 0;
}

int getBroadcastAddress(lua_State *L)
{
	struct ifaddrs *ifaddr, *ifa;
	int family, s, n;
	char host[NI_MAXHOST];
	char boardcast[NI_MAXHOST];
	bool isGet = false;

#if (CC_TARGET_PLATFORM == CC_PLATFORM_WIN32)
#define MALLOC(x) HeapAlloc(GetProcessHeap(), 0, (x))
#define FREE(x) HeapFree(GetProcessHeap(), 0, (x))

	PMIB_IPADDRTABLE pIPAddrTable;
	DWORD dwSize = 0;
	DWORD dwRetVal = 0;
	IN_ADDR IPAddr;

	pIPAddrTable = (MIB_IPADDRTABLE *) MALLOC(sizeof (MIB_IPADDRTABLE));

	if (pIPAddrTable) {
		if (GetIpAddrTable(pIPAddrTable, &dwSize, 0) ==
			ERROR_INSUFFICIENT_BUFFER) {
			FREE(pIPAddrTable);
			pIPAddrTable = (MIB_IPADDRTABLE *) MALLOC(dwSize);

		}
		if (pIPAddrTable == NULL) {
			return 0;
		}
	}

	if ( (dwRetVal = GetIpAddrTable( pIPAddrTable, &dwSize, 0 )) != NO_ERROR ) { 
		if (FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS, NULL, dwRetVal, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),       // Default language
			NULL, 0, NULL)) {
		}
	}

	for (int i=0; i < (int) pIPAddrTable->dwNumEntries; i++) {
		IPAddr.S_un.S_addr = (u_long) pIPAddrTable->table[i].dwAddr;
		strcpy(host, inet_ntoa(IPAddr));

		IPAddr.S_un.S_addr = (u_long)(pIPAddrTable->table[i].dwAddr | (~pIPAddrTable->table[i].dwMask));
		strcpy(boardcast, inet_ntoa(IPAddr));
		
		if (strcmp("127.0.0.1", host) != 0){
			isGet = true;
			break;
		}
	}

	if (pIPAddrTable) {
		FREE(pIPAddrTable);
		pIPAddrTable = NULL;
	}
#else

	if (getifaddrs(&ifaddr) == -1) {
		perror("getifaddrs");
		exit(EXIT_FAILURE);
	}


	for (ifa = ifaddr, n = 0; ifa != NULL; ifa = ifa->ifa_next, n++) {
		if (ifa->ifa_addr == NULL)
			continue;

		family = ifa->ifa_addr->sa_family;

		if (family == AF_INET /*|| family == AF_INET6*/ ) {
			s = getnameinfo(ifa->ifa_broadaddr,
				(family == AF_INET) ? sizeof(struct sockaddr_in) :
				sizeof(struct sockaddr_in6),
				host, NI_MAXHOST,
				NULL, 0, NI_NUMERICHOST);
			if (s != 0) {
				//CCLog("getnameinfo() failed: %s\n", gai_strerror(s));
				continue;
			}

			////CCLog("\t\taddress: <%s>", host);

			if (strcmp(host,"127.0.0.1") != 0){
				strcpy(boardcast, host);
				isGet = true;
			}
		}
	}

	freeifaddrs(ifaddr);
#endif
	if (isGet){
		lua_pushfstring(L, boardcast);
		return 1;
	}else{
		return 0;
	}
}

int forceRender(lua_State *L)
{
	Director::getInstance()->getRenderer()->render();
	return 0;
}

#define CHUNK 16384

int achiveDirectory(lua_State *L)
{
	return 0;
}

int autorelease(lua_State *L){
	Ref* cobj = static_cast<Ref*>(tolua_tousertype(L, 1, 0));
	if (cobj){
		cobj->autorelease();
	}
	return 0;
}

int updateBlend(lua_State *L){
	Sprite* cobj = static_cast<Sprite*>(tolua_tousertype(L, 1, 0));

	// it is possible to have an untextured sprite
	if (!cobj->getTexture() || !cobj->getTexture()->hasPremultipliedAlpha())
	{
		cobj->setBlendFunc( BlendFunc::ALPHA_NON_PREMULTIPLIED );
		cobj->setOpacityModifyRGB(false);
	}
	else
	{
		cobj->setBlendFunc(BlendFunc::ALPHA_PREMULTIPLIED);
		cobj->setOpacityModifyRGB(true);
	}
	return 0;
}

int CreateSpriteAsync(lua_State *L){
	int argc = lua_gettop(L) - 1;

	const char *filename = "";
	const char *ZIP = "";
	const char *password = "";

	if (argc >= 0){
		filename = luaL_checklstring(L, 1, NULL);
		if (argc >= 1){
			ZIP = luaL_checklstring(L, 2, NULL);
			if (argc >= 2){
				password = luaL_checklstring(L, 3, NULL);
			}
		}
	}

	SpriteAsync* tolua_ret = SpriteAsync::create(filename, ZIP, password);

	int nID = (tolua_ret) ? (int)tolua_ret->_ID : -1;
	int* pLuaID = (tolua_ret) ? &tolua_ret->_luaID : NULL;
	toluafix_pushusertype_ccobject(L, nID, pLuaID, (void*)tolua_ret, "cc.Sprite");
	return 1;
}
int loadSpriteFromZip(lua_State *L){
	double start = utils::gettime();

	const char *ZIP = luaL_checklstring(L, 1, NULL);
	const char *filename = luaL_checklstring(L, 2, NULL);
	
	string password = tolua_tocppstring(L, 3, "");
	//const char *message = luaL_checklstring(L, 1, NULL);

	//CCLog(">>>%s >>> %s >%s<", ZIP,filename,password.c_str());
	//CCLog("LOAD SPRITE FROM ZIP > 1 > %f", utils::gettime() - start);

	CCTexture2D* texture = TextureCache::getInstance()->getTextureForKey(filename);
	//CCLog("LOAD SPRITE FROM ZIP > 2 > %f", utils::gettime() - start);
	if (texture == nullptr){
		ssize_t pSize = 0;
		const unsigned char * tdata = nullptr;
		//CCLog("LOAD SPRITE FROM ZIP > 3 > %f", utils::gettime() - start);
		if (password.length() > 0){
			tdata = getFileDataFromZipWithPassword(ZIP, filename, password, &pSize);
			//CCLog("LOAD SPRITE FROM ZIP > 3-1 > %f", utils::gettime() - start);
		}
		else{
			tdata = FileUtils::getInstance()->getFileDataFromZip(ZIP, filename, &pSize);
			//CCLog("LOAD SPRITE FROM ZIP > 3-2 > %f", utils::gettime() - start);
		}
		if (tdata == nullptr){
			return 0;
		}
		if (pSize == 0){
			free((void*)tdata);
			return 0;
		}

		Image* image = new Image();
		bool t = image->initWithImageData(tdata, pSize);
		if (t){
			//CCLog("LOAD SPRITE FROM ZIP > 4 > %f", utils::gettime() - start);
			texture = TextureCache::getInstance()->addImage(image, filename);
			texture->retain();
		}
		//CCLog("LOAD SPRITE FROM ZIP > 5 > %f", utils::gettime() - start);
		free((void*)tdata);
		delete image;
		//CCLog("LOAD SPRITE FROM ZIP > 6 > %f", utils::gettime() - start);
	}

	CCSprite * tolua_ret = Sprite::createWithTexture(texture);
	//CCLog("LOAD SPRITE FROM ZIP > 7 > %f", utils::gettime() - start);

	int nID = (tolua_ret) ? (int)tolua_ret->_ID : -1;
	int* pLuaID = (tolua_ret) ? &tolua_ret->_luaID : NULL;
	toluafix_pushusertype_ccobject(L, nID, pLuaID, (void*)tolua_ret, "cc.Sprite");
	//CCLog("LOAD SPRITE FROM ZIP > 8 > %f", utils::gettime() - start);

	return 1;
}

int ExtractZipTempFile(lua_State *L){
	const char *ZIP = luaL_checklstring(L, 1, NULL);
	const char *filename = luaL_checklstring(L, 2, NULL);
	string password = tolua_tocppstring(L, 3, "");

	string ROOT_PATH = FileUtils::getInstance()->getWritablePath()+"tmp/";
	string FILEPATH = filename;

	if (!FileUtils::getInstance()->isDirectoryExist(ROOT_PATH)){
		FileUtils::getInstance()->createDirectory(ROOT_PATH);
	} else if (FileUtils::getInstance()->isFileExist(ROOT_PATH + FILEPATH)){
		string DIST = ROOT_PATH + FILEPATH;
		lua_pushfstring(L, DIST.c_str());
		return 1;
	}

	ssize_t pSize = 0;
	const unsigned char * tdata;

	if (password.length() > 0){
		tdata = getFileDataFromZipWithPassword(ZIP, filename, password, &pSize);
	}
	else{
		tdata = FileUtils::getInstance()->getFileDataFromZip(ZIP, filename, &pSize);
	}
	if (tdata == nullptr){
		return 0;
	}

	string DIST = ROOT_PATH + FILEPATH;
	std::string PATH = DIST.substr(0, DIST.find_last_of('/'));

	if (!FileUtils::getInstance()->isDirectoryExist(PATH))
		FileUtils::getInstance()->createDirectory(PATH);

	FILE* fp = fopen(DIST.c_str(),"wb");
	if (fp){
		fwrite(tdata,pSize,1,fp);
		lua_pushfstring(L, DIST.c_str());

		free((void*)tdata);
		fclose(fp);
		return 1;
	}
	free((void*)tdata);
	fclose(fp);
	return 0;
}

////////////////////////////////////////
/////////////ATL FOR LUA!!//////////////
int FAL_registAnimation(lua_State *L){
	const char *JSON = luaL_checklstring(L, 1, NULL);
	ATL::getInstance()->registAnimation(JSON);
	return 0;
}

int FAL_getFrame(lua_State *L){
	const char *id = luaL_checklstring(L, 1, NULL);
	int node = luaL_checkint(L, 2);
	int frame = luaL_checkint(L, 3);
	const char *nodeName = luaL_checklstring(L, 4, NULL);
	const char *hash = luaL_checklstring(L, 5, NULL);

	int ret = ATL::getInstance()->getFrame(id, node, frame, nodeName, hash);
	lua_pushinteger(L, ret);
	return 1;
}

int FAL_getMaxFrame(lua_State *L){
	const char *id = luaL_checklstring(L, 1, NULL);
	int node = luaL_checkint(L, 2);
	int ret = ATL::getInstance()->getMaxFrame(id, node);
	
	lua_pushinteger(L, ret);
	return 1;
}

int FAL_deleteFrame(lua_State *L){
	int frame = luaL_checkint(L, 1);
	ATL::getInstance()->deleteFrame(frame);
	return 0;
}

int FAL_getNumberVal(lua_State *L){
	int idx = luaL_checkint(L, 1);
	int key = luaL_checkint(L, 2);

	ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
	if (frame == nullptr){
		return 0;
	}
	if (frame->properties.find(key) == frame->properties.end()){
		return 0;
	}
	float ret = frame->properties[key]._val;
	float ret2 = frame->properties[key]._setval;
	float ret3 = frame->properties[key].set;
	lua_pushnumber(L, ret);
	lua_pushnumber(L, ret2);
	lua_pushnumber(L, ret3);
	return 3;
}

int FAL_getStringVal(lua_State *L){
	int idx = luaL_checkint(L, 1);
	int key = luaL_checkint(L, 2);

	ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
	if (frame == nullptr){
		return 0;
	}
	if (frame->properties.find(key) == frame->properties.end()){
		return 0;
	}
	string ret = frame->properties[key]._str;
	lua_pushfstring(L, ret.c_str());
	return 1;
}

int FAL_isValue(lua_State* L){
	int idx = luaL_checkint(L, 1);
	int key = luaL_checkint(L, 2);

	ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
	if (frame == nullptr){
		lua_pushboolean(L, false);
	}else{
		if (frame->properties.find(key) == frame->properties.end()){
			lua_pushboolean(L, false);
		}else{
			lua_pushboolean(L, true);
		}
	}
	return 1;
}

int FAL_numNode(lua_State *L){
	const char *id = luaL_checklstring(L, 1, NULL);
	int ret = ATL::getInstance()->numNode(id);
	lua_pushnumber(L, ret);
	return 1;
}

int FAL_isExists(lua_State *L){
	const char *id = luaL_checklstring(L, 1, NULL);
	bool ret = ATL::getInstance()->isExists(id);
	lua_pushboolean(L, ret);
	return 1;
}


int FAL_registStringValue(lua_State *L){
	const char *node = luaL_checklstring(L, 1, NULL);
	const char *idx = luaL_checklstring(L, 2, NULL);
	const char *value = luaL_checklstring(L, 3, NULL);
	bool ret = ATL::getInstance()->registStringValue(node, idx, value);
	lua_pushboolean(L, ret);
	return 1;
}

int FAL_registNumberValue(lua_State *L){
	const char *node = luaL_checklstring(L, 1, NULL);
	const char *idx = luaL_checklstring(L, 2, NULL);
	float value = luaL_checknumber(L, 3);
	bool ret = ATL::getInstance()->registNumberValue(node, idx, value);
	lua_pushboolean(L, ret);
	return 1;
}

int FAL_deleteNodeValue(lua_State *L){
	const char *node = luaL_checklstring(L, 1, NULL);
	ATL::getInstance()->deleteNodeValue(node);
	return 0;
}

int FAL_clearFrame(lua_State *L){
	ATL::getInstance()->clearFrame();
	return 0;
}

rapidjson::Document savevar_document;
int SAVEVAR_SET_STRING(lua_State* L){
	const char *idx = luaL_checklstring(L, 1, NULL);
	const char *var = luaL_checklstring(L, 2, NULL);
	if (savevar_document.IsObject() == false){
		savevar_document.SetObject();
	}

	rapidjson::Value IDX(rapidjson::kStringType);
	IDX.SetString(idx, savevar_document.GetAllocator());
	
	rapidjson::Value VAR(rapidjson::kStringType);
	VAR.SetString(var, savevar_document.GetAllocator());

	if (savevar_document.HasMember(idx) == false)
		savevar_document.AddMember(IDX, VAR, savevar_document.GetAllocator());
	else
		savevar_document[IDX] = VAR;
	return 0;
}

int SAVEVAR_SET_NUMBER(lua_State* L){
	const char *idx = luaL_checklstring(L, 1, NULL);
	float var = luaL_checknumber(L, 2);
	if (savevar_document.IsObject() == false){
		savevar_document.SetObject();
	}

	rapidjson::Value IDX(rapidjson::kStringType);
	IDX.SetString(idx, savevar_document.GetAllocator());

	rapidjson::Value VAR(rapidjson::kNumberType);
	VAR.SetDouble(var);

	if (savevar_document.HasMember(idx) == false){
		savevar_document.AddMember(IDX, VAR, savevar_document.GetAllocator());
	}
	else{
		savevar_document[IDX] = VAR;
	}
	return 0;
}

int SAVEVAR_FLUSH(lua_State* L){
	double start = utils::gettime();

	static const string filename = FileUtils::getInstance()->getWritablePath()+"UserDefault.data";
	rapidjson::StringBuffer buffer;
	rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);

	savevar_document.Accept(writer);

	string str = buffer.GetString();
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID)
	int fd = open(filename.c_str(), O_WRONLY | O_CREAT | O_SYNC, 0644);
	if (fd){
		write(fd, str.c_str(), str.length());
		fsync(fd);
		close(fd);
	}
#else
	FILE* f = fopen(filename.c_str(), "wb");
	if (f){
		fwrite(str.c_str(), str.length(), 1, f);
		fflush(f);
		fclose(f);
	}
#endif
	return 0;
}

int FILE_SaveString(lua_State* L){
	const char *filename = luaL_checklstring(L, 1, NULL);
	string str = tolua_tocppstring(L, 2, NULL);
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID)
	int fd = open(filename,O_WRONLY | O_CREAT | O_SYNC, 0644);
	if (fd){
		write(fd, str.c_str(), str.length());
		fsync(fd);
		close(fd);
	}
#else
	FILE* f = fopen(filename,"wb");
	if (f){
		fwrite(str.c_str(), str.length(), 1, f);
		fflush(f);
		fclose(f);
	}
#endif
	return 0;
}

int FILE_LoadString(lua_State* L){
	const char *filename = luaL_checklstring(L, 1, NULL);

	ssize_t __size;
	const char * pBuffer = (const char *)FileUtils::getInstance()->getFileData(filename, "rb", &__size);
	if (pBuffer){
		string ret(pBuffer, __size);

		delete[] pBuffer;

		lua_pushfstring(L,ret.c_str());
		return 1;
	}
	return 0;
}

struct PROFILE_AREA{
	long start;
	long end;
	string name;
};

vector<pair<long, string>> map_sort(map<string, long> &target)
{
	vector<pair<long, string> > vt;
	vector<pair<long, string> >::iterator it_vt;
	map<string, long>::iterator it_map;
	for (it_map = target.begin(); it_map != target.end(); it_map++)
	{
		vt.push_back(make_pair(it_map->second, it_map->first));
	}
	sort(vt.rbegin(), vt.rend());

	return vt;
}
//
//class PROPILER{
//public:
//	std::list<PROFILE_AREA> stack;
//	std::map<std::string, long> total;
//	std::map<std::string, long> average;
//	std::map<std::string, int>  count;
//
//	long __programs;
//	long __real;
//	PROPILER(){
//		__programs = 0;
//		__real = getTime();
//	}
//
//	~PROPILER(){
//		FILE* f = fopen("profile.txt", "a");
//		long programDt = getTime() - __real;
//		fprintf(f, "::::%ld:%ld(%f%%)\n", __programs, programDt, (((float)__programs) / ((float)programDt)) * 100.0f);
//
//		vector<pair<long, string>> v = map_sort(average);
//		auto b = v.begin();
//		auto e = v.end();
//		for (; b != e; b++){
//			fprintf(f, ">>>%s(%f%%)\n", b->second.c_str(), (((float)total[b->second]) / ((float)__programs))*100.0f);
//			fprintf(f, "total:%ld\n", total[b->second]);
//			fprintf(f, "count:%ld\n", count[b->second]);
//			fprintf(f, "aver:%d\n", average[b->second]);
//		}
//		fclose(f);
//	}
//
//	long getTime() {
//		struct timeval tv;
//		gettimeofday(&tv, NULL);
//		
//		return tv.tv_usec + tv.tv_sec*1000000;
//	}
//
//	void push(string area){
//		PROFILE_AREA _area;
//		_area.start = getTime();
//		_area.name = area;
//		stack.push_back(_area);
//	}
//
//	void pop(){
//		PROFILE_AREA _area = stack.back();
//		_area.end = getTime();
//
//		long dt = _area.end - _area.start;
//		stack.pop_back();
//
//		__programs += dt;
//
//		auto f = total.find(_area.name);
//		if (f == total.end()){
//			total[_area.name] = dt;
//			average[_area.name] = dt;
//			count[_area.name] = 1;
//		}
//		else{
//			average[_area.name] = (average[_area.name] + dt) / 2.0f;
//			total[_area.name] = total[_area.name] + dt;
//			count[_area.name] = count[_area.name] + 1;
//		}
//	}
//};

//PROPILER profiler;
int PROP_PUSH(lua_State* L){
	//const char *name = luaL_checklstring(L, 1, NULL);
	//profiler.push(name);
	return 0;
}

int PROP_POP(lua_State* L){
	//profiler.pop();
	return 0;
}

int COPY_PRZ(lua_State* L){
	ssize_t _size;
	const unsigned char* dat = CCFileUtils::getInstance()->getFileData("res.prz", "rb", &_size);

	string dest = CCFileUtils::getInstance()->getWritablePath();
	dest = dest + "res.prz";

	FILE *fp = fopen(dest.c_str(), "wb");
	ssize_t write_size = fwrite(dat, _size, 1, fp);
	fclose(fp);

	delete[] dat;

	return 0;
}

void SAVE_FILE(const char* var, const char* filename, char type, void* data, int size){
	int var_size = strlen(var);
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID)
	int fd = open(filename, O_WRONLY | O_CREAT | O_SYNC, 0644);
	if (fd){
		write(fd, &type, 1);
		write(fd, &size, 4);
		write(fd, data, size);
		write(fd, &var_size, 4);
		write(fd, var, var_size);
		fsync(fd);
		close(fd);
	}
#else
	FILE* f = fopen(filename, "wb");
	if (f){
		fwrite(&type, 1, 1, f);
		fwrite(&size, 4, 1, f);
		fwrite(data, size, 1, f);
		fwrite(&var_size, 4, 1, f);
		fwrite(var, var_size, 1, f);
		fflush(f);
		fclose(f);
	}
#endif
}

int Save_SaveVar_Number(lua_State* L){
	const char *var = luaL_checklstring(L, 1, NULL);
	const char *filename = luaL_checklstring(L, 2, NULL);
	float value = luaL_checknumber(L, 3);

	SAVE_FILE(var, filename, 0, &value, sizeof(value));
	return 0;
}

int Save_SaveVar_String(lua_State* L){
	const char *var = luaL_checklstring(L, 1, NULL);
	const char *filename = luaL_checklstring(L, 2, NULL);
	const char *value = luaL_checklstring(L, 3, NULL);
	string str = value;

	SAVE_FILE(var, filename, 1, (void*)str.c_str(), str.size());
	return 0;
}

int Save_SaveVar_Boolean(lua_State* L){
	const char *var = luaL_checklstring(L, 1, NULL);
	const char *filename = luaL_checklstring(L, 2, NULL);
	bool value = lua_toboolean(L, 3);

	int c = value;
	SAVE_FILE(var,filename, 0, &c, sizeof(c));
	return 0;
}

int Load_SaveVar(lua_State* L){
	const char *filename = luaL_checklstring(L, 1, NULL);
	if (FileUtils::getInstance()->getFileSize(filename) <= 0)
		return 0;

	FILE* fp = fopen(filename,"rb");
	if (fp == NULL){
		fclose(fp);
		return 0;
	}
	char type;
	int size;
	
	fread(&type, 1, 1, fp);
	if (type < 0) return 0;
	fread(&size, 4, 1, fp);
	if (size < 0) return 0;

	if (type == 0){
		float value = 0;
		fread(&value, 4, 1, fp);
		lua_pushnumber(L, value);
	}
	else if(type == 1){
		const char* tmp = new char[size + 1];
		memset((void*)tmp, 0, size + 1);
		fread( (void*) tmp, size, 1, fp );
		string str = tmp;
		lua_pushfstring(L, str.c_str());
		delete[] tmp;
	}

	fread(&size, 4, 1, fp);
	if (size < 0) return 0;
	const char* tmp = new char[size + 1];
	memset((void*) tmp, 0, size + 1);
	fread((void*)tmp, size, 1, fp);
	string str = tmp;
	lua_pushfstring(L, str.c_str());
	delete[] tmp;
	fclose(fp);
	return 2;
}

int SetWindowTitle(lua_State* L){
#if defined(_MSC_VER) || defined(__MINGW32__)
	const char *filename = luaL_checklstring(L, 1, NULL);
	//SimulatorWin::getInstance()->setTitle((char*)filename);
#endif
	return 0;
}


/////////////////////////////////////////////////
/////////////////////////////////////////////////
/////////////////////////////////////////////////
extern "C" {

	static void set_info_luautil(lua_State *L) {
		lua_pushliteral(L, "_COPYRIGHT");
		lua_pushliteral(L, "Copyright (C) 2015 nooslab");
		lua_settable(L, -3);
		lua_pushliteral(L, "_DESCRIPTION");
		lua_pushliteral(L, "cocos2d-x lua utils");
		lua_settable(L, -3);
		lua_pushliteral(L, "_VERSION");
		lua_pushliteral(L, "plu 0.1");
		lua_settable(L, -3);
	}

	static struct luaL_Reg luautillib[] = {
		{ "MessageBox", messagebox },
		{ "GetBroadcastAddr", getBroadcastAddress },
		{ "forceRender", forceRender },
		{ "loadSpriteFromZip", loadSpriteFromZip },
		{ "extractZipTempFile", ExtractZipTempFile },
		{ "updateBlend", updateBlend },
		{ "CreateSpriteAsync", CreateSpriteAsync },
		
		//ATL FOR LUA
		{ "FAL_registAnimation", FAL_registAnimation },
		{ "FAL_getFrame", FAL_getFrame },
		{ "FAL_getMaxFrame", FAL_getMaxFrame },
		{ "FAL_deleteFrame", FAL_deleteFrame },
		{ "FAL_getNumberVal", FAL_getNumberVal },
		{ "FAL_getStringVal", FAL_getStringVal },
		{ "FAL_isValue", FAL_isValue },
		{ "FAL_numNode", FAL_numNode },
		{ "FAL_isExists", FAL_isExists },
		{ "FAL_registStringValue", FAL_registStringValue },
		{ "FAL_registNumberValue", FAL_registNumberValue },
		{ "FAL_deleteNodeValue", FAL_deleteNodeValue },
		{ "FAL_clearFrame", FAL_clearFrame },
		
		//FILE
		{ "FILE_SaveString", FILE_SaveString },
		{ "FILE_LoadString", FILE_LoadString },

		//SAVE_VAR
		{ "SAVEVAR_SET_STRING", SAVEVAR_SET_STRING },
		{ "SAVEVAR_SET_NUMBER", SAVEVAR_SET_NUMBER },
		{ "SAVEVAR_FLUSH", SAVEVAR_FLUSH },

		//COPYPRZ
		{ "COPYPRZ", COPY_PRZ },

		//accurate gettime
		{ "PROP_PUSH", PROP_PUSH },
		{ "PROP_POP", PROP_POP },
		{ "AUTORELEASE", autorelease },

		//
		{ "SET_WINDOW_TITLE", SetWindowTitle },
		{ NULL, NULL }
	};

	int luaopen_luautils_core(struct lua_State *L){
		lua_newtable(L);
		int nup = 0;
		luaL_Reg *l = luautillib;

		luaL_checkstack(L, nup + 1, "too many upvalues");
		for (; l->name != NULL; l++) {  /* fill the table with given functions */
			int i;
			lua_pushstring(L, l->name);
			for (i = 0; i < nup; i++)  /* copy upvalues to the top */
				lua_pushvalue(L, -(nup + 1));
			lua_pushcclosure(L, l->func, nup);  /* closure with those upvalues */
			lua_settable(L, -(nup + 3)); /* table must be below the upvalues, the name and the closure */
		}
		lua_pop(L, nup);  /* remove upvalues */

		set_info_luautil(L);
		return 1;
	}
}