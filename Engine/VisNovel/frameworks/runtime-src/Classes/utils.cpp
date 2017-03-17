#include "utils.h"

#if (CC_TARGET_PLATFORM == CC_PLATFORM_WIN32)

#else
void Sleep(float t){
	usleep(t * 1000);
}
#endif
