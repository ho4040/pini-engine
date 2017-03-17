#include "AppDelegateEvent.h"
#include "AppDelegate.h"
#include "cocos2d.h"

using namespace cocos2d;

AppDelegateEvent::AppDelegateEvent()
{
	AppDelegate* app = (AppDelegate*)CCApplication::getInstance();
	app->registEventNode(this);
}


AppDelegateEvent::~AppDelegateEvent()
{
	AppDelegate* app = (AppDelegate*)CCApplication::getInstance();
	app->unregistEventNode(this);
}
