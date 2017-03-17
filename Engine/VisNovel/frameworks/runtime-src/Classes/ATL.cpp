#include "ATL.h"
#include "utils.h"
#include <cmath>
#include <stdio.h>
#include <stdlib.h>

# define M_PI           3.14159265358979323846
# define M_PI_OF_2      1.570796326794897

ATL* g_pATLInstance = nullptr;

int line_Interval_Default[] = {
	0,
	0,
	1,
	1,
	0,
	255,
	255,
	255,
	255
};

ATL::ATL()
{
	ease[0] = [](float i)->float { return i; };
    ease[1] = [](float i)->float { return -1.0f * cos(i * M_PI_OF_2) + 1.0f; };
    ease[2] = [](float i)->float { return sin(i * M_PI_OF_2); };
	ease[3] = [](float i)->float { return -0.5f * (cos(M_PI * i) - 1.0f); };
	ease[4] = [](float i)->float { if (i >= 1.0f)return 1.0f; return 0.0f; };
}

ATL::~ATL(){
	auto b = _anim.begin();
	auto e = _anim.end();
	for (; b != e; b++){
		auto _b = b->second.nodes.begin();
		auto _e = b->second.nodes.end();
		for (; _b != _e; _b++){
			auto mb = _b->frames.begin();
			auto me = _b->frames.end();
			for (; mb != me; mb++){
				delete (*mb);
			}
		}
	}

	auto cb = _frameCache.begin();
	auto ce = _frameCache.end();
	for (; cb != ce; cb++){
		delete cb->second;
	}
	_anim.clear();
}

ATL* ATL::getInstance(){
	if (g_pATLInstance == nullptr){
		g_pATLInstance = new ATL();
	}
	return g_pATLInstance;
}

void ATL::destroy(){
	if (g_pATLInstance){
		delete g_pATLInstance;
		g_pATLInstance = nullptr;
	}
}

int ATL::getJsonInt(const rapidjson::Value& root, const char* key, int def){
	int nRet = def;
	do {
		if (root.IsNull()) break;
		if (!root.HasMember(key)) break;
		if (root[key].IsNull()) break;
		nRet = root[key].GetInt();
	} while (0);
	return nRet;
}

float ATL::getJsonFloat(const rapidjson::Value& root, const char* key, float def){
	float nRet = def;
	do {
		if (root.IsNull()) break;
		if (root[key].IsNull()) break;
		nRet = root[key].GetDouble();
	} while (0);
	return nRet;
}

string ATL::getJsonStr(const rapidjson::Value& root, const char* key, string def){
	string nRet = def;
	do {
		if (root.IsNull()) break;
		if (root[key].IsNull()) break;
		nRet = root[key].GetString();
	} while (0);
	return nRet;
}

float ATL::interpolation(float time, float v1, float v2){
	return (1.0f - time)*v1 + time*v2;
}

int ATL::getMaxFrame(string id, int node){
	auto f1 = _anim.find(id);
	if (f1 == _anim.end()){
		return 0;
	}
	if (node >= f1->second.nodes.size()){
		return 0;
	}

	return f1->second.nodes[node].maxFrame + 1;
}

void ATL::registAnimation(string json){
	rapidjson::Document doc;
	doc.Parse<0>(json.c_str());

	string id = getJsonStr(doc, "name", "");
	
	ATL_Animation _animation;
	_animation.id = id;

	rapidjson::Value &nodes = doc["nodes"];
	for (int h = 0; h < nodes.Size(); h++){
		rapidjson::Value &node = nodes[h];

		int frameMax = 0;
		list<ATL_Frame> _frames;
		rapidjson::Value &frames = node["frames"];
		for (int i = 0; i < frames.Size();i++){
			rapidjson::Value &frame = frames[i];

			int frameNum = getJsonFloat(frame, "frame", 0);
			if (frameMax < frameNum){
				frameMax = frameNum;
			}

			ATL_Frame _frame;
			_frame.frame = frameNum;

			rapidjson::Value &stmts = frame["stmts"];
			for (int j = 0; j < stmts.Size(); j++){
				rapidjson::Value &stmt = stmts[j];
				ATL_Property _property;
				if (stmt["v"].IsNumber()){
					_property._val = stmt["v"].GetDouble();
				}else{
					_property._str = stmt["v"].GetString();
				}
				_property._val_type = getJsonInt(stmt, "o", 0);
				_property.ease = getJsonInt(stmt, "e", -1);
				_property.set = getJsonInt(stmt, "s", 0);
				_property.frame = frameNum;

				_frame.properties[stmt["t"].GetInt()] = _property;
			}
			_frames.push_back(_frame);
		}

		ATL_MarkNode mNode;
		mNode.maxFrame = frameMax;
		auto b = _frames.begin();
		auto e = _frames.end();
		for (; b != e; b++){
			ATL_MarkFrame* frame = createFrame(&_frames, b->frame);
			mNode.frames.push_back(frame);
		}
		_animation.nodes.push_back(mNode);
	}

	_anim[id] = _animation;

}

ATL_MarkFrame* ATL::createFrame(list<ATL_Frame> *flist, int frame){
	if (frame < 0)
		frame = 0;

	ATL_Frame before;
	ATL_Frame after;
	ATL_MarkFrame* ret = new ATL_MarkFrame();
	ret->frame = frame;

	list<ATL_Frame>::iterator b = flist->begin();
	list<ATL_Frame>::iterator e = flist->end();
	for (; b != e; b++){
		int curFrame = b->frame;
		ATL_Frame* target = nullptr;
		if (curFrame < frame)
			target = &before;
		else
			target = &after;

		map<int, ATL_Property>::iterator _b = b->properties.begin();
		map<int, ATL_Property>::iterator _e = b->properties.end();
		for (; _b != _e; ++_b){
			ATL_Property prop = _b->second;
			prop.frame = b->frame;

			map<int, ATL_Property>::iterator f = target->properties.find(_b->first);
			if (f != target->properties.end()){
				if (abs(f->second.frame - frame) < abs(prop.frame - frame)){
					continue;
				}
			}
			target->properties[_b->first] = prop;
		}
	}

	for (int i = 0; i < PROPTYPE::END; i++){
		map<int, ATL_Property>::iterator t1 = before.properties.find(i);
		map<int, ATL_Property>::iterator t2 = after.properties.find(i);
		ATL_MarkProp prop;
		prop.type = i;
		prop.isInit = false;
		prop.left_val_type = 1;
		if (t2 != after.properties.end()){
			prop.isInit = true;
			if (i >= PROPTYPE::MACRO){
				if (frame == t2->second.frame){
					prop.right_frame = t2->second.frame;
					prop.right_str = t2->second._str;
					prop.right_val_type = t2->second._val_type;
				}
			}else{
				prop.left_num =  line_Interval_Default[i];
				prop.left_frame = 0;
				prop.left_val_type = 1;
				if (t1 != before.properties.end()){
					prop.left_frame = t1->second.frame;
					if (t1->second.set > 0.5f)
					{
						prop.left_num = 0.0f;
						prop.left_setNum = t1->second._val;
						prop.isLeftSet = true;
					}
					else
					{
						prop.left_num = t1->second._val;
						prop.left_setNum = 0.0f;
						prop.isLeftSet = false;
					}
					prop.left_str = t1->second._str;
					prop.left_val_type = t1->second._val_type;
				}

				prop.right_frame = t2->second.frame;
				if (t2->second.set > 0.5f)
				{
					prop.right_num = 0.0f;
					prop.right_setNum = t2->second._val;
					prop.isRightSet = true;
				}
				else
				{
					prop.right_num = t2->second._val;
					prop.right_setNum = 0.0f;
					prop.isRightSet = false;
				}
				prop.right_str = t2->second._str;
				prop.right_val_type = t2->second._val_type;

				prop.ease = t2->second.ease;
			}
		}
		ret->props.push_back(prop);
	}
	return ret;
}

int ATL::getFrame(string id, int node, int fn, string nodeName, string arg){
	char _buf[2048];
	memset(_buf, 2048, 0);
	sprintf(_buf, "i%s-n%d-fn%d-s%s", id.c_str(), node, fn, arg.c_str());

	auto t = _framePreCache.find(_buf);

	if (t != _framePreCache.end()){
		return t->second.idx;
	}
	auto f1 = _anim.find(id);
	if (f1 == _anim.end()){
		return 0;
	}
	if (node >= f1->second.nodes.size()){
		return 0;
	}

	ATL_Frame* frame = new ATL_Frame();
	frame->frame = fn;
	int idx = 0;
	do{
		idx = (rand() % 99999) + 1;
	} while (_frameCache.find(idx) != _frameCache.end());
	_frameCache[idx] = frame;

	auto b = f1->second.nodes[node].frames.begin();
	auto e = f1->second.nodes[node].frames.end();
	for (; b != e; b++){
		if ((*b)->frame >= fn){
			auto _b = (*b)->props.begin();
			auto _e = (*b)->props.end();
			for (; _b != _e; _b++){
				if (_b->isInit){
					ATL_Property prop;
					prop.frame = fn;
					if (_b->type >= PROPTYPE::MACRO){
						if (_b->right_frame == fn){
							if (_b->right_val_type == 0){
								prop._str = getStringValue(nodeName, _b->right_str);
							}else{
								prop._str = _b->right_str;
							}
						}
					}
					else{
						float time = fn - _b->left_frame;
						float length = _b->right_frame - _b->left_frame;
						if (length == 0){
							time = 1;
						}
						else{
							time = time / length;
						}
						float s1 = 0;
						float s1s = 0;
						float s1l = 0;
						float s2 = 0;
						float s2s = 0;
						float s2l = 0;

						if (_b->left_val_type == 0){
							s1 = getNumberValue(nodeName, _b->left_str);
						}
						else{
							s1 = _b->left_num;
							s1s = _b->left_setNum;
							s1l = _b->isLeftSet ? 0.0f : 1.0f;
						}

						if (_b->right_val_type == 0){
							s2 = getNumberValue(nodeName, _b->right_str);
						}
						else{
							s2 = _b->right_num;
							s2s = _b->right_setNum;
							s2l = _b->isRightSet ? 0.0f : 1.0f;
						}

						if (_b->ease > -1){
							time = ease[_b->ease](time);
						}

						float v = interpolation(time, s1, s2);
						float vs = interpolation(time, s1s, s2s);
						float vl = interpolation(time, s1l, s2l);
						prop._val = v;
						prop._setval = vs;
						prop.set = vl;
					}
					frame->properties[_b->type] = prop;
				}
			}
			break;
		}
	}

	ATL_Frame_Cache cache;
	cache.id = id;
	cache.node = node;
	cache.fn = fn;
	cache.hash = arg;
	cache.idx = idx;

	_framePreCache.insert(std::pair<string, ATL_Frame_Cache>(_buf, cache));
	return idx;
}

ATL_Frame* ATL::getFrame(int idx){
	auto f = _frameCache.find(idx);
	if (f == _frameCache.end()){
		return nullptr;
	}
	return f->second;
}

void ATL::deleteFrame(int idx){
	auto f = _frameCache.find(idx);
	if (f == _frameCache.end()){
		return ;
	}

	delete f->second;
	_frameCache.erase(f);
}

list<int> ATL::getMarkedFrames(string idx, int node){
	list<int> ret;

	auto f1 = _anim.find(idx);
	if (f1 == _anim.end()){
		printf("CAN NOT FIND ANIMATION!");
		return ret;
	}
	if (node >= f1->second.nodes.size()){
		return ret;
	}

	vector<ATL_MarkFrame*>::iterator b = f1->second.nodes[node].frames.begin();
	vector<ATL_MarkFrame*>::iterator e = f1->second.nodes[node].frames.end();
	for (; b != e;b++){
		ret.push_back((*b)->frame);
	}
	return ret;
}

int ATL::numNode(string idx){
	auto f1 = _anim.find(idx);
	if (f1 == _anim.end()){
		return 0;
	}
	return f1->second.nodes.size();
}

bool ATL::isExists(string idx){
	auto f1 = _anim.find(idx);
	if (f1 == _anim.end()){
		return false;
	}
	return true;
}

float ATL::getNumberValue(string nodeName, string name){
	map<string, map<string, float>>::iterator f = _numberValues.find(nodeName);
	if (f == _numberValues.end()){
		return 0;
	}
	map<string, float>::iterator f2 = f->second.find(name);
	if (f2 == f->second.end()){
		return 0;
	}
	return f2->second;
}

string ATL::getStringValue(string nodeName, string name){
	map<string, map<string, string>>::iterator f = _stringValues.find(nodeName);
	if (f == _stringValues.end()){
		return string();
	}
	map<string, string>::iterator f2 = f->second.find(name);
	if (f2 == f->second.end()){
		return string();
	}
	return f2->second;
	
}

bool ATL::registNumberValue(string nodeName, string name, float value){
	map<string, map<string, float>>::iterator f = _numberValues.find(nodeName);
	if (f == _numberValues.end()){
		_numberValues[nodeName] = map<string, float>();
	}
	if (_numberValues[nodeName][name] == value){
		return false;
	}
	_numberValues[nodeName][name] = value;
	return true;
}

bool ATL::registStringValue(string nodeName, string name, string value){
	map<string, map<string, string>>::iterator f = _stringValues.find(nodeName);
	if (f == _stringValues.end()){
		_stringValues[nodeName] = map<string, string>();
	}
	if (_stringValues[nodeName][name] == value){
		return false;
	}
	_stringValues[nodeName][name] = value;
	return true;
}
void ATL::clearValue(){
	_numberValues.clear();
	_stringValues.clear();
}

void ATL::deleteNodeValue(string nodeName){
	map<string, map<string, string>>::iterator f = _stringValues.find(nodeName);
	if (f != _stringValues.end()){
		_stringValues.erase(f);
	}
	map<string, map<string, float>>::iterator f2 = _numberValues.find(nodeName);
	if (f2 != _numberValues.end()){
		_numberValues.erase(f2);
	}
}

void ATL::clearFrame(){
	
	auto b = _frameCache.begin();
	auto e = _frameCache.end();
	for (; b != e; b++ ){
		delete b->second;
	}
	_frameCache.clear();
	_framePreCache.clear();
}


extern "C"{
#ifndef GPP_FOR_PYTHON
	////////////
	// FOR LUA
	
	// lua_utils.cpp¿¡ ÀÖÀ½.
#else
	////////////
	// FOR PYTHON
	void registAnimation(char* json){
		ATL::getInstance()->registAnimation(json);
	}

	int getFrame(char* id, int node, int frame,char* nodeName,char* hash){
		return ATL::getInstance()->getFrame(id, node, frame, nodeName, hash);
	}

	void deleteFrame(int idx){
		return ATL::getInstance()->deleteFrame(idx);

	}
	
	int getMaxFrame(char* id, int node){
		return ATL::getInstance()->getMaxFrame(id,node);
	}

	float getNumberVal(int idx,int key){
		ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
		if(frame == nullptr){
			return 0;
		}
		if(frame->properties.find(key) == frame->properties.end()){
			return 0;
		}
		return frame->properties[key]._val;
	}

	float getNumberSetVal(int idx,int key){
		ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
		if(frame == nullptr){
			return 0;
		}
		if(frame->properties.find(key) == frame->properties.end()){
			return 0;
		}
		return frame->properties[key]._setval;
	}

	float getNumberSet(int idx,int key){
		ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
		if(frame == nullptr){
			return 0;
		}
		if(frame->properties.find(key) == frame->properties.end()){
			return 0;
		}
		return frame->properties[key].set;
	}

	bool isValue(int idx,int key){
		ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
		if(frame == nullptr){
			return 0;
		}
		if(frame->properties.find(key) == frame->properties.end()){
			return false;
		}
		return true;
	}

	char* getStringVal(int idx,int key){
		ATL_Frame* frame = ATL::getInstance()->getFrame(idx);
		if(frame == nullptr){
			return (char*)string("").c_str();
		}
		if(frame->properties.find(key) == frame->properties.end()){
			return (char*)string("").c_str();
		}
		return (char*)frame->properties[key]._str.c_str();
	}

	char* getMarkedFrames(char* idx,int key){
		list<int> ret = ATL::getInstance()->getMarkedFrames(idx,key);
		
		string stm;
		list<int>::iterator b = ret.begin();
		list<int>::iterator e = ret.end();
		for(;b!=e;b++){
			int c = *b;
			char a[40] = {0,};
			sprintf(a, "%d", c);
			stm += a + string(",");
		}
		return (char*)stm.c_str();
	}

	int numNode(char* id){
		return ATL::getInstance()->numNode(id);
	}

	bool isExists(char* id){
		return ATL::getInstance()->isExists(id);
	}

	bool registStringValue(char* node,char* idx,char* value){
		return ATL::getInstance()->registStringValue(node,idx,value);
	}

	bool registNumberValue(char* node, char* idx, float value){
		return ATL::getInstance()->registNumberValue(node, idx, value);
	}

	void deleteNodeValue(char* node){
		ATL::getInstance()->deleteNodeValue(node);
	}

	void clearFrame(){
		ATL::getInstance()->clearFrame();
	}
#endif
}