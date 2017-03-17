
!include "MUI2.nsh"

Name    "피니엔진" ; 게임 이름
OutFile "installer.exe" ; 설치 파일 이름

!define	GAME_NAME     "피니엔진" ; 게임 이름
!define GAME_EXEFILE  "피니엔진.exe" ; 게임 실행 파일 이름
!define GAME_TARGET_FOLDER "nooslab\piniengine" ; 게임 폴더 이름
!define GAME_SOURCE_FOLDER "Master" ; 게임 폴더 이름
!define	GAME_HELPFILE "Help.txt" ; 게임 도움말 파일 이름
!define GAME_LICENSE  "EULA.txt" ; 라이센스 파일
!define GAME_FINISHPAGE_RUN_TEXT "${GAME_NAME}를 실행합니다."
!define GAME_FINISHPAGE_SHOWREADME_TEXT "도움말을 확인합니다."

!include "Main.nsh"
