#ifndef _ATL_H_
#define _ATL_H_

#include "json/rapidjson.h"
#include "json/document.h"

#define _HAS_ITERATOR_DEBUGGING 0 

#include <map>
#include <list>
#include <vector>
#include <unordered_map>
#include <functional>
#include <queue>
#include <string>

using namespace std;

struct ATL_MarkProp{
	int left_frame;
	int left_val_type;
	float left_num;
	float left_setNum;
	bool isLeftSet;
	string left_str;

	int right_frame;
	int right_val_type;
	float right_num;
	float right_setNum;
	bool isRightSet;
	string right_str;

	int ease;
	int type;

	bool isInit;
};

struct ATL_MarkFrame{
	vector<ATL_MarkProp> props;
	int frame;
};

struct ATL_MarkNode{
	vector<ATL_MarkFrame*> frames;
	int maxFrame;
};

struct ATL_Animation{
	vector<ATL_MarkNode> nodes;
	string id;
};

struct ATL_Property{
	int _val_type;
	float _val;
	float _setval;
	string _str;

	int ease;
	float set;
	int frame;
	ATL_Property(){
		set = 0.0f;
		ease = -1;
		_val = 0;
		_setval = 0.0f;
		_str = "";
		frame = 0;
		_val_type = 1;
	}
};

struct ATL_Frame{
	map<int,ATL_Property> properties;
	int frame;
};

struct ATL_Thread_Queue{
	string id;
	string hash;
	string nodeName;
	int node;
};

struct ATL_Frame_Cache{
	string id;
	int node;
	int fn;
	string hash;

	int idx;
};

class ATL{
	enum PROPTYPE{
		POS_X,
		POS_Y,
		SCALE_X,
		SCALE_Y,
		ROT,
		COLOR_R,
		COLOR_G,
		COLOR_B,
		COLOR_A, 
		MACRO, // INTERVAL
		LUA,
		IMAGE,
		END
	};
private:
	ATL();
	~ATL();

public:
	static ATL* getInstance();
	static void destroy();

	void registAnimation(string json);
	ATL_MarkFrame* createFrame(list<ATL_Frame> *flist, int frame);
	int getMaxFrame(string id, int node);

	list<int> getMarkedFrames(string idx, int node);
	int getFrame(string id, int node, int frame, string nodeName,string hash="");
	
	ATL_Frame* getFrame(int idx);
	void deleteFrame(int idx);

	int numNode(string idx);
	bool isExists(string idx);

	float getNumberValue(string nodeName, string name);
	string getStringValue(string nodeName, string name);

	bool registNumberValue(string nodeName, string name, float value);
	bool registStringValue(string nodeName, string name, string value);
	void clearValue();

	void deleteNodeValue(string nodeName);

	void frameReadThread();
	void clearFrame();

private:
	int getJsonInt(const rapidjson::Value& root, const char* key, int def);
	float getJsonFloat(const rapidjson::Value& root, const char* key, float def);
	string getJsonStr(const rapidjson::Value& root, const char* key, string def);

	float interpolation(float time, float v1, float v2);

private:
	unordered_map<string, ATL_Animation> _anim;
	unordered_map<string, ATL_Frame_Cache> _framePreCache;
	map<int, ATL_Frame*> _frameCache;
	map<string, map<string, float>> _numberValues;
	map<string, map<string, string>> _stringValues;
	function<float(float)> ease[5];
};

#endif