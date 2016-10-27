#include "VideoPlayer.h"
#include "AppDelegate.h"
#include "utils.h"

#include <stdio.h>
#include <string.h>

long GetTimeStamp() {
	struct timeval tv;
	gettimeofday(&tv, NULL);
	return tv.tv_usec;
}

LPALBUFFERSAMPLESSOFT alBufferSamplesSOFT = nullptr;
ALsizei FramesToBytes(ALsizei size, ALenum channels, ALenum type)
{
	switch (channels)
	{
	case AL_MONO_SOFT:    size *= 1; break;
	case AL_STEREO_SOFT:  size *= 2; break;
	case AL_REAR_SOFT:    size *= 2; break;
	case AL_QUAD_SOFT:    size *= 4; break;
	case AL_5POINT1_SOFT: size *= 6; break;
	case AL_6POINT1_SOFT: size *= 7; break;
	case AL_7POINT1_SOFT: size *= 8; break;
	}

	switch (type)
	{
	case AL_BYTE_SOFT:           size *= sizeof(ALbyte); break;
	case AL_UNSIGNED_BYTE_SOFT:  size *= sizeof(ALubyte); break;
	case AL_SHORT_SOFT:          size *= sizeof(ALshort); break;
	case AL_UNSIGNED_SHORT_SOFT: size *= sizeof(ALushort); break;
	case AL_INT_SOFT:            size *= sizeof(ALint); break;
	case AL_UNSIGNED_INT_SOFT:   size *= sizeof(ALuint); break;
	case AL_FLOAT_SOFT:          size *= sizeof(ALfloat); break;
	case AL_DOUBLE_SOFT:         size *= sizeof(ALdouble); break;
	}

	return size;
}

ALsizei BytesToFrames(ALsizei size, ALenum channels, ALenum type)
{
	return size / FramesToBytes(1, channels, type);
}

VideoPlayer::VideoPlayer():
	_readThread(nullptr),
	_audioThread(nullptr),
	_needThreadQuit(false),
	_needWait(true),
	_finishedReadFrame(false),
	_finishedAudio(false),
	_finishedVideo(false),
	m_pData(nullptr),
	m_pFormatCtx(NULL),
	m_fCallback(0),
	m_bRun(false),
	m_fFrame(0),
	m_fFPS(0){
	/*
	if (alBufferSamplesSOFT == nullptr){
		if (alIsExtensionPresent("AL_SOFT_buffer_samples"))
		{
			alBufferSamplesSOFT = (LPALBUFFERSAMPLESSOFT)alGetProcAddress("alBufferSamplesSOFT");
		}
	}
	*/
}

VideoPlayer::~VideoPlayer(){
	_needThreadQuit = true;
	_needWait = false;

	if (_readThread) _readThread->join();
	CC_SAFE_DELETE(_readThread);

	if (_audioThread) _audioThread->join();
	CC_SAFE_DELETE(_audioThread);

	if (_videoThread) _videoThread->join();
	CC_SAFE_DELETE(_videoThread);

	alDeleteBuffers(NUM_AL_BUFFERS, m_aALBuffers);
	alDeleteSources(1, &m_iALSource);

	av_free(m_pBuffer);
	av_free(m_pFrameRGB);
	av_free(m_pFrame);
	av_free(m_pAudioFrame);
	avcodec_close(m_pCodecCtx);
	avcodec_close(m_pAudioCodecCtx);
	avformat_close_input(&m_pFormatCtx);

	CC_SAFE_DELETE(m_pData);
}

bool VideoPlayer::init(string path){
	m_sPath = path;

	AVCodec         *pCodec;
	AVCodec         *pAudioCodec;
	// Register all formats and codecs
	av_register_all();

	//cocos2d::log("VideoPlayer::init() called");
	
	// Open video file
	string _path = CCFileUtils::getInstance()->getWritablePath() + path;
	//cocos2d::log("VideoPlayer::init() called, path = %s", _path.c_str());
	if (FileUtils::getInstance()->isFileExist(_path)){
		//cocos2d::log("file exist.");
		path = _path;
	}
	else
	{
		//cocos2d::log("file does not exist.");
		ssize_t _size;
		unsigned char* data = FileUtils::getInstance()->getFileData(path, "rb", &_size);

		if (_size > 0)
		{
			string targetFolder = CCFileUtils::getInstance()->getWritablePath() + "etc";
			if (!FileUtils::getInstance()->isDirectoryExist(targetFolder))
			{
				//cocos2d::log("target folder does not exist.");
				FileUtils::getInstance()->createDirectory(targetFolder);
				//cocos2d::log("target folder make success.");
			}
			//cocos2d::log("file size = %d", (int)_size);

			FILE *fp = fopen(_path.c_str(), "wb");
			if (fp != nullptr)
			{
				//cocos2d::log("file open success.");
				ssize_t write_size = fwrite(data, _size, 1, fp);
				//cocos2d::log("file write success.");
				fclose(fp);
				//cocos2d::log("file close success.");

				delete[] data;
				//cocos2d::log("buffer clear.");
			}
			else
			{
				//cocos2d::log("file open failed.");
			}

			path = _path;
		}
		else
		{
			//cocos2d::log("data read failed.");
		}
	}

	if (avformat_open_input(&m_pFormatCtx, path.c_str(), NULL, NULL) != 0){
		CCLOG("avformat_open_input 1 Failed");
		return -1; // Couldn't open file
	}


	// Retrieve stream information
	if (avformat_find_stream_info(m_pFormatCtx, NULL) < 0){
		CCLOG("avformat_find_stream_info Failed");
		return -1; // Couldn't find stream information
	}

	// Dump information about file onto standard error
	av_dump_format(m_pFormatCtx, 0, path.c_str(), 0);

	// Find the first video stream
	m_iVideoStream = -1;
	m_iAudioStream = -1;
	for (int i = 0; i < m_pFormatCtx->nb_streams; i++){
		if (m_pFormatCtx->streams[i]->codec->codec_type == AVMEDIA_TYPE_VIDEO && m_iVideoStream < 0) {
			m_iVideoStream = i;
		}
		if (m_pFormatCtx->streams[i]->codec->codec_type == AVMEDIA_TYPE_AUDIO && m_iAudioStream < 0) {
			m_iAudioStream = i;
		}
	}
	if (m_iVideoStream == -1){
		CCLOG("connot find video stream ");
		return -1;
	}
	if (m_iAudioStream == -1){
		CCLOG("connot find audio stream ");
		return -1;
	}

	// Get a pointer to the codec context for the video stream
	m_pCodecCtx = m_pFormatCtx->streams[m_iVideoStream]->codec;
	m_pAudioCodecCtx = m_pFormatCtx->streams[m_iAudioStream]->codec;
	
	m_fFPS = av_q2d(m_pFormatCtx->streams[m_iVideoStream]->time_base);

	////////////////////////////
	pAudioCodec = avcodec_find_decoder(m_pAudioCodecCtx->codec_id);
	if (!pAudioCodec) {
		CCLOG("Unsupported codec!\n");
		return -1;
	}
	
	if (avcodec_open2(m_pAudioCodecCtx, pAudioCodec, NULL) < 0){
		CCLOG("audio open failed!\n");
		return -1; // audio open failed
	}

	alGenBuffers(NUM_AL_BUFFERS, m_aALBuffers);
	alGenSources(1, &m_iALSource);

	alSourcef(m_iALSource, AL_PITCH, 1);
	alSourcef(m_iALSource, AL_GAIN, 1);
	alSourcei(m_iALSource, AL_LOOPING, AL_FALSE);
	alSource3f(m_iALSource, AL_POSITION, 0, 0, 0);
	alSource3f(m_iALSource, AL_VELOCITY, 0, 0, 0);
	m_iInitBuffer = 1;
	////////////////////////////

	// Find the decoder for the video stream
	pCodec = avcodec_find_decoder(m_pCodecCtx->codec_id);
	if (pCodec == NULL) {
		CCLOG("Unsupported codec!\n");
		return -1; // Codec not found
	}
	// Open codec
	if (avcodec_open2(m_pCodecCtx, pCodec, NULL) < 0){
		CCLOG("avcodec_open2 codec!\n");
		return -1; // Could not open codec
	}

	// Allocate video frame
	m_pFrame = avcodec_alloc_frame();
	m_pAudioFrame = avcodec_alloc_frame();

	// Allocate an AVFrame structure
	m_pFrameRGB = avcodec_alloc_frame();
	if (m_pFrameRGB == NULL){
		CCLOG("m_pFrameRGB alloc failed!");
		return -1;
	}

	m_iWidth = m_pCodecCtx->width;
	m_iHeight = m_pCodecCtx->height;

	int numBytes = avpicture_get_size(PIX_FMT_RGBA, m_pCodecCtx->width, m_pCodecCtx->height);
	m_pBuffer = (uint8_t *)av_malloc(numBytes*sizeof(uint8_t));

	avpicture_fill((AVPicture *)m_pFrameRGB, m_pBuffer, PIX_FMT_RGBA, m_pCodecCtx->width, m_pCodecCtx->height);

	_readThread	 = new std::thread(&VideoPlayer::readFrame, this);
	_videoThread = new std::thread(&VideoPlayer::playVideo, this);
	_audioThread = new std::thread(&VideoPlayer::playAudio, this);

	setContentSize(Size(m_iWidth, m_iHeight));
	//CCLOG("%f %f", getContentSize().width, getContentSize().height);

	//CCTextureCache::getInstance()->addImageAsync();
	return Sprite::init();
}

void VideoPlayer::readFrame(){
	while (1){
		while (1){
			if (_needThreadQuit)
				return;
			if (_needWait == false){
				_vPacketQueueMutex.lock();
				if (_vPacketQueue.size() < 60){
					_vPacketQueueMutex.unlock();
					break;
				}
				_vPacketQueueMutex.unlock();

				_aPacketQueueMutex.lock();
				if (_aPacketQueue.size() < 60){
					_aPacketQueueMutex.unlock();
					break;
				}
				_aPacketQueueMutex.unlock();
			}
			Sleep(1);
		}
		list<AVPacket> videos;
		list<AVPacket> audios;
		AVPacket packet;
		int ret = 0;
		while (ret >= 0) {
			ret = av_read_frame(m_pFormatCtx, &packet);
			if (packet.stream_index == m_iVideoStream) {
				videos.push_back(packet);
			}
			else if (packet.stream_index == m_iAudioStream) {
				audios.push_back(packet);
			}
			else{
				av_free_packet(&packet);
			}
			if (videos.size() > 10 && audios.size() > 10)
				break;
		}

		if (videos.size() > 0){
			_vPacketQueueMutex.lock();
			_vPacketQueue.insert(_vPacketQueue.end(), videos.begin(), videos.end());
			_vPacketQueueMutex.unlock();
		}

		if (audios.size() > 0){
			_aPacketQueueMutex.lock();
			_aPacketQueue.insert(_aPacketQueue.end(), audios.begin(), audios.end());
			_aPacketQueueMutex.unlock();
		}

		if (ret < 0){
			_finishedReadFrame = true;
			while(_needThreadQuit == false)Sleep(1);
			break;
		}
	}
}

void VideoPlayer::playVideo(){
	while (1){
		WAITING_VIDEO_QUEUE:
		while (1){
			if (_needThreadQuit)
				return;

			if (_needWait == false){
				_videoQueueMutex.lock();
				if (_videoQueue.size() < 30){
					_videoQueueMutex.unlock();
					break;
				}
				_videoQueueMutex.unlock();
			}

			Sleep(1);
		}
		int frameFinished;

		_vPacketQueueMutex.lock();
		if (_vPacketQueue.size() == 0){
			_vPacketQueueMutex.unlock();
			if (_finishedReadFrame){
				_finishedVideo = true;
				while (_needThreadQuit == false)Sleep(10);
				break;
			}
			goto WAITING_VIDEO_QUEUE;
		}
		AVPacket packet = _vPacketQueue.front();
		_vPacketQueue.pop_front();
		_vPacketQueueMutex.unlock();

		avcodec_decode_video2(m_pCodecCtx, m_pFrame, &frameFinished, &packet);
		if (frameFinished) {
			static int sws_flags = SWS_BICUBIC;
			struct SwsContext *img_convert_ctx;
			int target_width = m_pCodecCtx->width;
			int target_height = m_pCodecCtx->height;
			img_convert_ctx = sws_getContext(
				m_pCodecCtx->width,
				m_pCodecCtx->height,
				m_pCodecCtx->pix_fmt,
				target_width,
				target_height,
				PIX_FMT_RGBA,
				sws_flags, NULL, NULL, NULL);

			sws_scale(img_convert_ctx, m_pFrame->data, m_pFrame->linesize, 0, m_pCodecCtx->height, m_pFrameRGB->data, m_pFrameRGB->linesize);
			sws_freeContext(img_convert_ctx);

			Image* texture = avToTexture(m_pFrameRGB, target_width, target_height);

			_videoQueueMutex.lock();
			_videoQueue.push_back(texture);
			_videoQueueMutex.unlock();

			av_free_packet(&packet);
		}
	}
}

int VideoPlayer::prepareAudio(list<AudioChunk> *aqueue){
WAITING_AUDIO_QUEUE:
	aqueue->clear();
	while (1){
		if (_needThreadQuit)
			return -1;
		if (_needWait == false){
			_aPacketQueueMutex.lock();
			if (_aPacketQueue.size() > 0){
				_aPacketQueueMutex.unlock();
				break;
			}
			else{
				if (_finishedReadFrame){
					_aPacketQueueMutex.unlock();
					_finishedAudio = true;
					while (_needThreadQuit == false)Sleep(10);
					return -1;
				}
			}
			_aPacketQueueMutex.unlock();
		}
		Sleep(1);
	}
	if (aqueue->size() <= 0){
		_aPacketQueueMutex.lock();
		if (_aPacketQueue.size() == 0){
			_aPacketQueueMutex.unlock();
			if (_finishedReadFrame){
				_finishedAudio = true;
				return -1;
			}
			goto WAITING_AUDIO_QUEUE;
		}
		AVPacket packet = _aPacketQueue.front();
		_aPacketQueue.pop_front();
		_aPacketQueueMutex.unlock();

		list<AudioChunk> q = audio_decode_frame(m_pAudioCodecCtx, m_pAudioFrame, &packet);
		aqueue->insert(aqueue->end(), q.begin(), q.end());
	}
	return 1;
}

void VideoPlayer::playAudio(){
	list<AudioChunk> aqueue;
	while (1){
		int ret = prepareAudio(&aqueue);
		if (ret == -1)
			return;
		
		list<AudioChunk>::iterator b = aqueue.begin();
		list<AudioChunk>::iterator e = aqueue.end();

		int n = 0;
		for (; b != e;){
			AudioChunk chunk = *b;
			if (m_iInitBuffer) {
				size_t i, got;

				/* Rewind the source position and clear the buffer queue */
				alSourceRewind(m_iALSource);
				alSourcei(m_iALSource, AL_BUFFER, 0);

				/* Fill the buffer queue */
				for (i = 0; i < NUM_AL_BUFFERS; i++){
					if (alBufferSamplesSOFT){
						alBufferSamplesSOFT(m_aALBuffers[i], chunk.sample_rate, AL_FORMAT_STEREO16,
							BytesToFrames(chunk.size, 2, AL_SHORT_SOFT),
							2, AL_SHORT_SOFT, chunk.data);
					} else{
						alBufferData(m_aALBuffers[i], AL_FORMAT_STEREO16, chunk.data, chunk.size, chunk.sample_rate);
					}
					b++;
					if (b == e){
						int ret = prepareAudio(&aqueue);
						if (ret == -1)
							return;

						b = aqueue.begin();
						e = aqueue.end();
					}
					chunk = *b;
				}
				int error = alGetError();
				if (error != AL_NO_ERROR)
				{
					fprintf(stderr, "Error buffering for playback : %d\n", error);
					continue;
				}

				/* Now queue and start playback! */
				alSourceQueueBuffers(m_iALSource, i, m_aALBuffers);
				alSourcePlay(m_iALSource);
				error = alGetError();
				if (error != AL_NO_ERROR)
				{
					fprintf(stderr, "Error starting playback : %d\n", error);
					continue;
				}
				m_iInitBuffer = 0;
			}
			else {
				int n = 0;
				////////////////////////////////////////////////////////////////////////////////////////////////
				ALint process, state;

				/* Get relevant source info */
				alGetSourcei(m_iALSource, AL_BUFFERS_PROCESSED, &process);
				if (alGetError() != AL_NO_ERROR)
				{
					fprintf(stderr, "Error checking source state\n");
					return ;
				}

				/* Unqueue and handle each processed buffer */
				while (process > 0)
				{
					ALuint bufid;
					alSourceUnqueueBuffers(m_iALSource, 1, &bufid);
					
					if (alBufferSamplesSOFT){
						alBufferSamplesSOFT(bufid, chunk.sample_rate, AL_FORMAT_STEREO16,
							BytesToFrames(chunk.size, 2, AL_SHORT_SOFT),
							2, AL_SHORT_SOFT, chunk.data);
					}
					else{
						alBufferData(bufid, AL_FORMAT_STEREO16, chunk.data, chunk.size, chunk.sample_rate);
					}

					alSourceQueueBuffers(m_iALSource, 1, &bufid);

					b++;
					process--;
					if (process <= 0)
						break;
					if (b == e){
						int ret = prepareAudio(&aqueue);
						if (ret == -1)
							return;

						b = aqueue.begin();
						e = aqueue.end();
					}
					chunk = *b;
				}

				/* Make sure the source hasn't underrun */
				alGetSourcei(m_iALSource, AL_SOURCE_STATE, &state);
				if (state != AL_PLAYING && state != AL_PAUSED)
				{
					ALint queue;

					/* If no buffers are queued, playback is finished */
					alGetSourcei(m_iALSource, AL_BUFFERS_QUEUED, &queue);
					if (queue == 0)
						return ;

					alSourcePlay(m_iALSource);
					if (alGetError() != AL_NO_ERROR)
					{
						fprintf(stderr, "Error restarting playback\n");
						return ;
					}
				}
				////////////////////////////////////////////////////////////////////////////////////////////////
			}
		}
	}

}

void VideoPlayer::readNextFrame(){
	Image* img= nullptr;

	_videoQueueMutex.lock();
	if (_videoQueue.size() > 0) {
		img = _videoQueue.front();
		_videoQueue.pop_front();
	}
	_videoQueueMutex.unlock();

	if (img){
		Texture2D* tex = new Texture2D();
		tex->initWithImage(img);
		tex->autorelease();

		setTexture(tex);
		setTextureRect(Rect(0, 0, m_iWidth, m_iHeight));

		delete img;
	}

}

list<VideoPlayer::AudioChunk> VideoPlayer::audio_decode_frame(AVCodecContext *ctx, AVFrame* frame, AVPacket* packet) {
	AVCodecContext *aCodecCtx = ctx;
	list<AudioChunk> bufferQueue;

	while (packet->size > 0) {
		int len, data_size = 0;
		int got_frame = 0;
		len = avcodec_decode_audio4(aCodecCtx, frame, &got_frame, packet);
		if (len < 0) {
			// if error, skip frame 
			CCLOG("audio_decode_frame error");
			break;
		}
		if (got_frame)
		{
			AudioChunk chunk;
			memset(chunk.data, 0, MAX_AUDIO_FRAME_SIZE);
			if (aCodecCtx->sample_fmt != AV_SAMPLE_FMT_S16){
				SwrContext * pAudioCvtContext = NULL;
				pAudioCvtContext = swr_alloc_set_opts(pAudioCvtContext, aCodecCtx->channel_layout, AV_SAMPLE_FMT_S16, aCodecCtx->sample_rate, aCodecCtx->channel_layout, aCodecCtx->sample_fmt, aCodecCtx->sample_rate, 0, 0); //SwrContext를 생성한다. 여기서는 singed 16bits로 변환하고자 한다.
				int err;
				if ((err = swr_init(pAudioCvtContext)) < 0) { //초기화
					if (err == AVERROR(EINVAL)){
						CCLOG("Failed to initialize the resampling context\n");
						break;
					}
				}

				static uint8_t AudioCvtBuffer[MAX_AUDIO_FRAME_SIZE]; //변환결과 저장되는 버퍼
				uint8_t *out[] = { AudioCvtBuffer };
				const uint8_t *in[] = { frame->data[0] };

				uint8_t *ain[32];
				if (!av_sample_fmt_is_planar(aCodecCtx->sample_fmt))
				{
					ain[0] = frame->data[0];
				}
				else
				{
					ain[0] = frame->data[0]; //8.1ch대비 9개를 만들었다
					ain[1] = frame->data[0];
					ain[2] = frame->data[0];
					ain[3] = frame->data[0];
					ain[4] = frame->data[0];
					ain[5] = frame->data[0];
					ain[6] = frame->data[0];
					ain[7] = frame->data[0];
					ain[8] = frame->data[0];
				}
				swr_convert(pAudioCvtContext, out, frame->nb_samples, (const uint8_t **)ain, frame->nb_samples);  //변환수행!

				data_size = av_samples_get_buffer_size(NULL, aCodecCtx->channels, frame->nb_samples, AV_SAMPLE_FMT_S16, 1); //결과 데이터 길이 구하기
				memcpy(chunk.data, AudioCvtBuffer, data_size);

			}
			else{
				data_size = av_samples_get_buffer_size(NULL, aCodecCtx->channels, frame->nb_samples, aCodecCtx->sample_fmt, 1);
				memcpy(chunk.data, frame->data[0], data_size);
			}
			chunk.size = data_size;
			chunk.sample_rate = aCodecCtx->sample_rate;
			bufferQueue.push_back(chunk);
		}
		packet->size -= len;
		packet->data += len;
	}
	av_free_packet(packet);
	return bufferQueue;
}

Image* VideoPlayer::avToTexture(AVFrame *pFrame, int width, int height){
	if (m_pData == nullptr)
		m_pData = new unsigned char[width*height * 4];
	memcpy(m_pData, pFrame->data[0] , width *height*4);
	
	Image* img = new (std::nothrow) Image();
	img->initWithRawData((unsigned char const*)m_pData, 0, width, height, 0);

	return img;
}

void VideoPlayer::play(){
	_needWait = false;
	m_bRun = true;
	schedule(schedule_selector(VideoPlayer::ticker), 0);
}

void VideoPlayer::ticker(float dt){
	//CCLOG("ticker %f", dt);
	if (_finishedVideo && _finishedAudio){

		_videoQueueMutex.lock();
		int vqs = _videoQueue.size();
		_videoQueueMutex.unlock();
		if (vqs > 0) {
			stop();
			if (m_fCallback){
				LuaEngine* engine = (LuaEngine*)ScriptEngineManager::getInstance()->getScriptEngine();

				int ret = engine->getLuaStack()->executeFunctionByHandler(m_fCallback, 0);
				engine->getLuaStack()->clean();
			}
		}
	} else{

		m_fFrame += dt;
		while (m_fFrame > m_fFPS){
			readNextFrame();
			m_fFrame -= m_fFPS;
		}
	}
}

void VideoPlayer::onEnter(){
	CCSprite::onEnter();
}

void VideoPlayer::onExit(){
	CCSprite::onExit();
	stop();
}

void VideoPlayer::onForeground(){
	_needWait = false;
}

void VideoPlayer::onBackground(){
	_needWait = true;
}

void VideoPlayer::stop(){
	_needWait = true;
	m_bRun = false;
	unschedule(schedule_selector(VideoPlayer::ticker));
}

void VideoPlayer::setCallback(LUA_FUNCTION func){
	m_fCallback = func;
}

VideoPlayer* VideoPlayer::create(string path){
	VideoPlayer* self = new VideoPlayer();
	if (self->init(path)){
		self->autorelease();
		return self;
	}
	return nullptr;
}


#include <lua.h>
#include <lauxlib.h>
#include <tolua_fix.h>
static int lua_videoplayer_create(lua_State *L) {
	const char *message = luaL_checklstring(L, 2, NULL);
	VideoPlayer* tolua_ret = VideoPlayer::create(message);

	int nID = (tolua_ret) ? (int)tolua_ret->_ID : -1;
	int* pLuaID = (tolua_ret) ? &tolua_ret->_luaID : NULL;
	toluafix_pushusertype_ccobject(L, nID, pLuaID, (void*)tolua_ret, "npini.VideoPlayer");
	
	return 1;
}

static int lua_videoplayer_play(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	cobj->play();
	return 0;
}

static int lua_videoplayer_stop(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	cobj->stop();
	return 0;
}

static int lua_videoplayer_setCallback(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	LUA_FUNCTION handler = toluafix_ref_function(L, 2, 0);

	cobj->setCallback(handler);

	return 0;
}
static int lua_videoplayer_getWidth(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	tolua_pushnumber(L, cobj->getWidth() );
	return 1;
}
static int lua_videoplayer_getHeight(lua_State *L) {
	VideoPlayer* cobj = static_cast<VideoPlayer*>(tolua_tousertype(L, 1, 0));
	tolua_pushnumber(L, cobj->getHeight());
	return 1;
}

int luaopen_VideoPlayer_core(struct lua_State *L){
	tolua_usertype(L, "npini.VideoPlayer");
	tolua_cclass(L, "VideoPlayer", "npini.VideoPlayer", "cc.Sprite", nullptr);

	tolua_beginmodule(L, "VideoPlayer");
	tolua_function(L, "create", lua_videoplayer_create);
	tolua_function(L, "play", lua_videoplayer_play);
	tolua_function(L, "stop", lua_videoplayer_stop);
	tolua_function(L, "setCallback", lua_videoplayer_setCallback);
	tolua_function(L, "getWidth", lua_videoplayer_getWidth);
	tolua_function(L, "getHeight", lua_videoplayer_getHeight);
	tolua_endmodule(L);
	return 1;
}