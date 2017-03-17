!include "MUI2.nsh"

Name    "동방 브레이크" ; 게임 이름
OutFile "TouhouBreak.exe" ; 설치 파일 이름

!define	GAME_NAME     "동방 브레이크" ; 게임 이름
!define GAME_EXEFILE  "TouhouBreak.exe" ; 게임 실행 파일 이름
!define GAME_TARGET_FOLDER "TouhouBreak" ; 게임 폴더 이름
!define GAME_SOURCE_FOLDER "Master" ; 게임 폴더 이름
!define	GAME_HELPFILE "Help.txt" ; 게임 도움말 파일 이름
!define GAME_LICENSE  "EULA.txt" ; 라이센스 파일

!include "Main.nsh"