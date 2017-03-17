#ifndef _PINI_C_UTILS_
#define _PINI_C_UTILS_

#ifndef GPP_FOR_PYTHON
#include "cocos2d.h"
#endif

#include <stdlib.h>

#if (CC_TARGET_PLATFORM == CC_PLATFORM_WIN32)
#include <windows.h>
#else
#include "unistd.h"
extern void Sleep(float t);
#endif

#endif