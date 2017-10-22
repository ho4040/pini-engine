PiniEngine
=============
피니엔진은 비주얼 노벨 게임 제작도구입니다. 

[![IMAGE ALT TEXT](http://img.youtube.com/vi/5FD2cSPqFLE/0.jpg)](http://www.youtube.com/watch?v=5FD2cSPqFLE "피니엔진 프리뷰 트레일러")

LNX 스크립트를 이용하여 게임을 개발하며 개발 및 빌드를 도와주는 에디터가 동봉되어있습니다.

피니에디터를 이용하여 개발 스크립트를 작성하고 작성된 스크립트는 PLY를 통해 컴파일 되며 만들어진 실행파일은 cocos2d-x엔진을 통해 실행됩니다.


LNX
-------------
LNX는 피니엔진용 스크립트언어입니다. 한글로 스크립팅할 수 있다는 특징이있습니다.

LNX의 형태는 아래와 같습니다.
<pre><code>#파라미터 알려줌
:야근시작
[대화 이름="김똘똘"]
;으윽! 야근인건가요?

직원수 = $프로그래머 + $그래픽 + $사운드 + $기획자 + $QA + $운영자
@조건 직원수 == 0:
	[대화 이름="김똘똘"]
	;하지만 야근을 할 직원이 없군요...
	>>주메뉴시작

[독백]
;야근을 하게되면 시간을 추가로 얻을 수 있습니다 하지만 사원들은 애사심이 떨어지고 애사심이 너무 떨어지면..
;퇴사를 하기도 합니다. 보너스로 달랠 수 있기는 합니다만.
;
;<연결 "야근10">10시간 야근</연결>
;<연결 "야근20">20시간 야근</연결>
;<연결 "야근40">40시간 야근</연결>
;
;<연결 "야근포기">그만두자</연결>
;
</code></pre>

설치
-------------
실행 파일은 [여기](http://piniengine.com/)에서 다운 받으실 수 있습니다.

빌드 - 에디터
-------------
#### 필요 
1. python 2.7 (32-bit)
2. pip
  * [PIL](http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe)
  * pillow
3. [MinGW](https://sourceforge.net/projects/mingw/files/Installer/) (window only)
  * [g++](http://studymake.tistory.com/385) 
4. (Lua for window)[https://github.com/rjpcomputing/luaforwindows/releases]
  * 설치 후 c:\Program Files (x86)\lua\5.1\lib\ 폴더 내용물 복사 후 C:\python27\libs\에 붙혀넣기
  * 설치 후 c:\Program Files (x86)\lua\5.1\include\ 폴더 내용물 복사 후 C:\python27\include\에 붙혀넣기
5. [vcpython27](http://aka.ms/vcpython27)

```bash
git clone https://github.com/ho4040/pini-engine

cd pini-engine/Engine
python android_compile.py

cd ../dependency/lupa-1.0b1.tar/
python setup.py install --no-luajit

cd ../Editor/pini/
pip install PySide
pip install openpyxl
pip install pillow
pip install appdirs

python main.py
```

빌드 - 피니리모트
-------------
#### 필요 
1. [visual studio 2013 community](http://go.microsoft.com/?linkid=9863609)

#### 빌드
1. "/Engine/VisNovel/frameworks/runtime-src/proj.win32/pini_remote.sln"파일을 엽니다.
2. Visual studio의 빌드버튼을 눌러 빌드를 시작함.
3. 빌드가 완료되면 "/Engine/VisNovel/frameworks/runtime-src/classes/ffmpeg/lib/window/*.dll" 파일들을 "/Engine/VisNovel/frameworks/runtime-src/proj.win32/Debug.win32/"로 복사. 
4. visual studio에서 프로젝트 실행

#### 피니엔진 에디터에 적용하여 테스트하기
1. "/Engine/VisNovel/frameworks/runtime-src/proj.win32/Debug.win32/"폴더 내의 dll파일과 exe파일을 "/Engine/window64/"으로 복사
2. "/Editor/pini/run.cmd" 파일 실행

빌드 - APK
--------------
#### 필요
1. [android-sdk-tool](https://dl.google.com/android/repository/sdk-tools-windows-3859397.zip)
2. [ant](http://theeye.pe.kr/archives/1334)
3. android-ndk-r10d
  * [Windows 32-bit](http://dl.google.com/android/ndk/android-ndk-r10d-windows-x86.exe)
  * [Windows 64-bit](http://dl.google.com/android/ndk/android-ndk-r10d-windows-x86_64.exe)
4. [cocos2d-x-3.9](http://www.cocos2d-x.org/filedown/cocos2d-x-3.9.zip)

#### 빌드
```bash
cd cocos2d-x

python setup.py

# android sdk, ant, ndk 경로 설정.

cd pini-engine/Engine/
python android_compile.py
```

피니엔진 배포 빌드
-------------
```bash
cd Editor

python dist_pini.py
```

iOS용 게임 빌드하기
-------------
1. iOS용 빌드를 위해서는 OSX운영체제의 PC와 XCode가 필요합니다.
2. 엔진 전체 코드를 pull 받습니다.
3. 피니엔진을 이용하여 window 버전을 export합니다.
4. export된 폴더에 res, src 폴더를 각각 "pini-engine/Engine/VisNovel/src","pini-engine/Engine/VisNovel/res"에 복사합니다.
5. pini-engine/Engine/VisNovel/frameworks/runtime-src/proj.ios_mac/pini_remote.xcodeproj 을 열고 빌드를 시작합니다.


작업 된 내용
1. 인앱결제 안되던 문제 수정
2. android api 버전 14로 수정
3. 윈도우 익스포트 후 한글명일 때 저장이 제대로 안되던 문제 수정
4. 기기테스트가 되지 않던 문제 수정
5. 로컬푸시로 앱 진입 시 튕기는 문제 수정
6. 깃헙 연결 메뉴 추가
7. 후원자 리스트 메뉴 추가
8. iOS빌드 지원
9. 소프트키 자동 숨김 기능 추가

해야하는 작업
3. 피니엔진 에디터 사용중 작업중인 내용이 자동저장될때 에디터가 넘춰버림, 메모리사용량이 급증하는 현상이 발견됨
4. 업데이트하여 변화된 내용 위키에 표시

메모 
py2exe 탓인지 다른 모듈 버전업되서인지 
inspect.py 에서 could not get source code 에러가 남.
임시로 아래 코드 추가함.
```
        if not lines:
            fname = file.split("\\")[-1]
            with open(fname) as f:
                lines = f.readlines()
```

```
def findsource(object):
    """Return the entire source file and starting line number for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a list of all the lines
    in the file and the line number indexes a line in that list.  An IOError
    is raised if the source code cannot be retrieved."""

    file = getfile(object)
    sourcefile = getsourcefile(object)
    if not sourcefile and file[:1] + file[-1:] != '<>':
        raise IOError('source code not available')
    file = sourcefile if sourcefile else file

    module = getmodule(object, file)
    if module:
        lines = linecache.getlines(file, module.__dict__)
        if not lines:
            fname = file.split("\\")[-1]
            with open(fname) as f:
                lines = f.readlines()
    else:
        lines = linecache.getlines(file)
    if not lines:
        raise IOError('could not get source code')

```