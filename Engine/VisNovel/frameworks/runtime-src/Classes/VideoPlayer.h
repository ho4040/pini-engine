#ifndef __VIDEO_PLAYER_H__
#define __VIDEO_PLAYER_H__

#include "cocos2d.h"
#include "CCLuaEngine.h"

#include "AL/al.h"
#include "AL/alc.h"
#include "AL/alext.h"

#include "AppDelegateEvent.h"

#include <mutex>
#include <thread>
#include <condition_variable>
#include <list>

extern "C" {
	#include "libavcodec/avcodec.h"
	#include "libavformat/avformat.h"
	#include "libavutil/mathematics.h"
	#include "libswscale/swscale.h"
	#include "libavutil/avutil.h"
	#include "libswresample/swresample.h"
}

using namespace std;
using namespace cocos2d;

#define NUM_AL_BUFFERS 6
#define MAX_AUDIO_FRAME_SIZE 12000/2

class VideoPlayer : public Sprite, public AppDelegateEvent {
public:
	struct AudioChunk{
		unsigned char data[MAX_AUDIO_FRAME_SIZE];
		int size;
		int sample_rate;
	};
private:
	AVFormatContext *m_pFormatCtx;
	AVCodecContext  *m_pCodecCtx;
	AVCodecContext  *m_pAudioCodecCtx;
	AVFrame         *m_pFrame;
	AVFrame         *m_pAudioFrame;
	AVFrame         *m_pFrameRGB;
	uint8_t         *m_pBuffer;

	int             m_iVideoStream;
	int             m_iAudioStream;
	float			m_fFrame;
	float			m_fFPS;
	bool			m_bRun;
	string			m_sPath;
	unsigned char*  m_pData;

	int				m_iWidth;
	int				m_iHeight;

	int				m_iInitBuffer;

	ALuint m_iALSource;
	ALuint m_aALBuffers[NUM_AL_BUFFERS];

	std::thread* _readThread;
	std::thread* _videoThread;
	std::thread* _audioThread;
	bool		 _needThreadQuit;
	bool		 _needWait;
	bool		 _finishedReadFrame;
	bool		 _finishedAudio;
	bool		 _finishedVideo;

	std::mutex			_vPacketQueueMutex;
	list<AVPacket>		_vPacketQueue;

	std::mutex			_aPacketQueueMutex;
	list<AVPacket>		_aPacketQueue;

	std::mutex			_videoQueueMutex;
	list<Image*>		_videoQueue;

	LUA_FUNCTION	m_fCallback;
public:
	VideoPlayer();
	virtual ~VideoPlayer();

	void play();
	void stop();

	void setCallback(LUA_FUNCTION func);

	void ticker(float dt);

	void onEnter();
	void onExit();

	void readFrame();
	void playVideo();
	void playAudio();

	int prepareAudio(list<AudioChunk> *aqueue); //called in thread

	int getWidth() { return m_iWidth; }
	int getHeight(){ return m_iHeight; }
public:
	virtual void onForeground();
	virtual void onBackground();

public:
	bool isRun(){
		return m_bRun;
	}

protected:
	bool init(string path);
	void readNextFrame();
	Image* avToTexture(AVFrame *pFrame, int width, int height);
	list<AudioChunk> audio_decode_frame(AVCodecContext *ctx, AVFrame* frame, AVPacket* packet);

public:
	static VideoPlayer* create(string path);
};

#ifdef __cplusplus
extern "C" {
#endif    
	int luaopen_VideoPlayer_core(struct lua_State *L);
#ifdef __cplusplus
}
#endif

/*
#if (CC_TARGET_PLATFORM == CC_PLATFORM_ANDROID || CC_TARGET_PLATFORM == CC_PLATFORM_IOS)
#else
#endif
*/

#endif