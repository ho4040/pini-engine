#ifndef _PINI_TEXTINPUT_
#define _PINI_TEXTINPUT_

#include "cocos2d.h"
#include "CCLuaEngine.h"
using namespace cocos2d;
using namespace std;

class TextInput : public TextFieldTTF, public TextFieldDelegate
{
private:
	TextInput();
	virtual ~TextInput();

public:
	static TextInput* create(string placeholder,string fontName,int size);

	bool init(string placeholder, string fontName, int size);

	void setEnableIME(bool enable);
	void setMaxLength(int max);

	void setPasswordMode(bool enable);

	// TextFieldDelegate
	virtual bool onTextFieldAttachWithIME(TextFieldTTF * sender);
	virtual bool onTextFieldDetachWithIME(TextFieldTTF * sender);
	virtual bool onTextFieldInsertText(TextFieldTTF * sender, const char * text, size_t nLen) override;
	virtual bool onTextFieldDeleteBackward(TextFieldTTF * sender, const char * delText, size_t nLen) override;
	virtual bool onDraw(TextFieldTTF * sender);

	virtual void visit(Renderer *renderer, const Mat4 &parentTransform, uint32_t parentFlags) override;

private:
	int _maxLength;
	string _text;
	bool _password;
};


#ifdef __cplusplus
extern "C" {
#endif    
	int luaopen_TextInput_core(struct lua_State *L);
#ifdef __cplusplus
}
#endif

#endif