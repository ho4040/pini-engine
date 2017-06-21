
!include "MUI2.nsh"

Name    "piniengine" ;
OutFile "installer.exe" ;

!define	GAME_NAME     "piniengine" ; 
!define GAME_EXEFILE  "piniengine.exe" ;
!define GAME_TARGET_FOLDER "nooslab\piniengine" ;
!define GAME_SOURCE_FOLDER "Master" ;
!define	GAME_HELPFILE "Help.txt" ; 
!define GAME_LICENSE  "EULA.txt" ; 
!define GAME_FINISHPAGE_RUN_TEXT "${GAME_NAME}"
!define GAME_FINISHPAGE_SHOWREADME_TEXT ""

!include "Main.nsh"
