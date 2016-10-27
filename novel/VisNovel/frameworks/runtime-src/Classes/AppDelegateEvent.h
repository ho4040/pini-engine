#ifndef _APPDELEGATEEVENT_H_
#define _APPDELEGATEEVENT_H_

class AppDelegateEvent
{
public:
	AppDelegateEvent();
	virtual ~AppDelegateEvent();

	virtual void onForeground() = 0;
	virtual void onBackground() = 0;
};

#endif

