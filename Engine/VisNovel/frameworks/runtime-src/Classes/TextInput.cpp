#include "TextInput.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static int _calcCharCount_(const char * text)
{
	int n = 0;
	char ch = 0;
	while ((ch = *text))
	{
		CC_BREAK_IF(!ch);

		if (0x80 != (0xC0 & ch))
		{
			++n;
		}
		++text;
	}
	return n;
}


TextInput::TextInput() : 
	TextFieldTTF(),
	_maxLength(-1),
	_password(false)
{
}

TextInput::~TextInput()
{
}

TextInput* TextInput::create(string placeholder, string fontName, int fontSize){
	TextInput *ret = new (std::nothrow) TextInput();
	if (ret && ret->init("", fontName, fontSize))
	{
		ret->autorelease();
		if (placeholder.size()>0)
		{
			ret->setPlaceHolder(placeholder);
		}
		return ret;
	}
	CC_SAFE_DELETE(ret);
	return nullptr;
}

bool TextInput::init(std::string placeholder, std::string fontName, int fontSize){
	
	if (FileUtils::getInstance()->isFileExist(fontName))
	{
		TTFConfig ttfConfig(fontName.c_str(), fontSize, GlyphCollection::DYNAMIC);
		if (this->setTTFConfig(ttfConfig) == false)
			return false;

		_placeHolder = std::string(placeholder);
		Label::setTextColor(_colorSpaceHolder);
		Label::setString(_placeHolder);

		this->setDelegate(this);
		return true;
	}
	return false;
}

void TextInput::setEnableIME(bool enable){
	if (enable){
		this->attachWithIME();
	}
	else{
		this->detachWithIME();
	}
}

void TextInput::setPasswordMode(bool enable){
	_password = enable;
}

void TextInput::visit(Renderer *renderer, const Mat4 &parentTransform, uint32_t parentFlags){
	string _tmp;
	if (_password){
		_tmp = this->getString();
		int count = _calcCharCount_(_tmp.c_str());
		string pass = "";
		for (int i = 0; i < count; i++){
			pass += "*";
		}
		TextFieldTTF::setString(pass);
	}

	TextFieldTTF::visit(renderer, parentTransform, parentFlags);

	if (_password){
		TextFieldTTF::setString(_tmp);
	}
}
void TextInput::setMaxLength(int max){
	_maxLength = max;
}

bool TextInput::onTextFieldAttachWithIME(TextFieldTTF * sender){
	return false;
}
bool TextInput::onTextFieldDetachWithIME(TextFieldTTF * sender){
	return false;
}
bool TextInput::onTextFieldInsertText(TextFieldTTF * sender, const char * text, size_t nLen){
	if (_maxLength > 0) {
		if (sender->getCharCount() >= _maxLength)
			return true;
	}
	return false;
}
bool TextInput::onTextFieldDeleteBackward(TextFieldTTF * sender, const char * delText, size_t nLen){
	return false;
}
bool TextInput::onDraw(TextFieldTTF * sender){
	return false;
}

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////
#include <lua.h>
#include <lauxlib.h>
#include "scripting/lua-bindings/manual/tolua_fix.h"

static int lua_TextInput_create(lua_State *L) {
	const char *placeholder = luaL_checklstring(L, 2, NULL);
	const char *fontName = luaL_checklstring(L, 3, NULL);
	const int size = luaL_checknumber(L, 4);
	TextInput* tolua_ret = TextInput::create(placeholder,fontName,size);

	int nID = (tolua_ret) ? (int)tolua_ret->_ID : -1;
	int* pLuaID = (tolua_ret) ? &tolua_ret->_luaID : NULL;
	toluafix_pushusertype_ccobject(L, nID, pLuaID, (void*)tolua_ret, "npini.TextInput");

	return 1;
}
static int lua_TextInput_setEnableIME(lua_State *L) {
	TextInput* cobj = static_cast<TextInput*>(tolua_tousertype(L, 1, 0));
	bool value = ((bool)tolua_toboolean(L, 2, 0));

	cobj->setEnableIME(value);
	return 0;
}
static int lua_TextInput_setMaxLegnth(lua_State *L) {
	TextInput* cobj = static_cast<TextInput*>(tolua_tousertype(L, 1, 0));
	int value = ((int)tolua_tonumber(L, 2, 0));

	cobj->setMaxLength(value);
	return 0;
}
static int lua_TextInput_setPasswordMode(lua_State *L) {
	TextInput* cobj = static_cast<TextInput*>(tolua_tousertype(L, 1, 0));
	bool value = ((bool)tolua_toboolean(L, 2, 0));

	cobj->setPasswordMode(value);
	return 0;
}

int luaopen_TextInput_core(struct lua_State *L){
	tolua_usertype(L, "npini.TextInput");
	tolua_cclass(L, "TextInput", "npini.TextInput", "cc.Label", nullptr);

	tolua_beginmodule(L, "TextInput");
	tolua_function(L, "create", lua_TextInput_create);
	tolua_function(L, "setEnableIME", lua_TextInput_setEnableIME);
	tolua_function(L, "setMaxLength", lua_TextInput_setMaxLegnth); 
	tolua_function(L, "setPasswordMode", lua_TextInput_setPasswordMode);
	tolua_endmodule(L);
	return 1;
}