LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := cocos2dlua_shared

LOCAL_CFLAGS := -D__STDC_CONSTANT_MACROS=1
APP_OPTIM := release

LOCAL_MODULE_FILENAME := libcocos2dlua

LOCAL_SRC_FILES := \
../../Classes/AppDelegate.cpp \
../../Classes/ide-support/SimpleConfigParser.cpp \
../../Classes/ide-support/RuntimeLuaImpl.cpp \
../../Classes/ide-support/lua_debugger.c \
hellolua/main.cpp \
../../Classes/AppDelegateEvent.cpp \
../../Classes/VideoPlayer.cpp \
../../Classes/ATL.cpp \
../../Classes/TextInput.cpp \
../../Classes/md5/md5lib.c \
../../Classes/md5/ldes56.c \
../../Classes/md5/des56.c \
../../Classes/md5/compat-5.2.c \
../../Classes/md5/md5.c \
../../Classes/lua_utils.cpp \
../../Classes/utils.cpp \
../../Classes/SpriteAsync.cpp \
../../Classes/AsyncLoaderManager.cpp \
../../Classes/ifaddrs_android/ifaddrs.c

LOCAL_C_INCLUDES := \
$(LOCAL_PATH)/../../Classes \
$(LOCAL_PATH)/../../../cocos2d-x/external \
$(LOCAL_PATH)/../../../cocos2d-x/tools/simulator/libsimulator/lib \
$(LOCAL_PATH)/../../../cocos2d-x/tools/simulator/libsimulator/lib/protobuf-lite \
$(LOCAL_PATH)/../../Classes/md5 \
$(LOCAL_PATH)/../../Classes/ffmpeg/android/include \
$(LOCAL_PATH)/../../Classes/openal/include \
$(LOCAL_PATH)/../../Classes/ifaddrs_android

# _COCOS_HEADER_ANDROID_BEGIN
# _COCOS_HEADER_ANDROID_END

LOCAL_STATIC_LIBRARIES := cocos2d_lua_static
LOCAL_STATIC_LIBRARIES += cocos2d_simulator_static

LOCAL_SHARED_LIBRARIES := libavcodec libavformat libswscale libavutil libswresample libopenal

# _COCOS_LIB_ANDROID_BEGIN
# _COCOS_LIB_ANDROID_END

include $(BUILD_SHARED_LIBRARY)

$(call import-module,scripting/lua-bindings/proj.android)
$(call import-module,tools/simulator/libsimulator/proj.android)
$(call import-module,../../runtime-src/Classes/ffmpeg)
$(call import-module,../../runtime-src/Classes/openal)

# _COCOS_LIB_IMPORT_ANDROID_BEGIN
# _COCOS_LIB_IMPORT_ANDROID_END
