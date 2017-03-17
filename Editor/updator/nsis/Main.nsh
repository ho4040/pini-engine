
InstallDir "$PROGRAMFILES\${GAME_TARGET_FOLDER}" ; 기본 설치 폴더
RequestExecutionLevel user
SetCompress off

!define MUI_ICON   "Install.ico"   ; 설치 파일 아이콘
!define MUI_UNICON "Uninstall.ico" ; 삭제 파일 아이콘

; # 처음이나 마지막 설치 화면 왼쪽에 나오는 그림 설정 (가로: 164, 세로: 314)
!define MUI_WELCOMEFINISHPAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP   "Install.bmp"

; # 처음이나 마지막 삭제 화면 왼쪽에 나오는 그림 설정 (가로: 164, 세로: 314)
!define MUI_UNWELCOMEFINISHPAGE
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "Uninstall.bmp"

; # 라이센스, 경로, 설치 화면 오른쪽 위에 나오는 그림 설정 (가로: 150, 세로: 57)
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_LEFT
!define MUI_HEADERIMAGE_BITMAP "Header.bmp"

!define MUI_FINISHPAGE_NOAUTOCLOSE

; # 설치를 끝낸 후 할 일 설정 (도움말이 없을 경우 MUI_FINISHPAGE_SHOWREADME와 MUI_FINISHPAGE_SHOWREADME_TEXT 부분 삭제)
!define MUI_FINISHPAGE_RUN "$INSTDIR\${GAME_EXEFILE}"
!define MUI_FINISHPAGE_RUN_TEXT "${GAME_FINISHPAGE_RUN_TEXT}"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\${GAME_HELPFILE}"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "${GAME_FINISHPAGE_SHOWREADME_TEXT}"

!define MUI_ABORTWARNING

; # 설치 화면 순서 설정
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${GAME_LICENSE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; # NSIS 폴더 Contrib\Language files\Korean.nlf 파일에서 글꼴과 글씨 크기를 굴림으로 하지 말고 `-` 로 해야한다.
; # 그렇지 않으면 헤더, 사이드 이미지들이 이상하게 늘어남.
!insertmacro MUI_LANGUAGE "Korean"

Function .onInit
    StrCpy $0   "$LOCALAPPDATA"
    StrLen $1 $0
    IntCmp $1 0 lbl_done

    StrCpy $INSTDIR "$LOCALAPPDATA\${GAME_TARGET_FOLDER}"
lbl_done:
FunctionEnd

Section "Install"

; ----------------------------------------------------------------------------------------------------
    SetOutPath "$INSTDIR"
    File /r "${GAME_SOURCE_FOLDER}\*.*"
    File "${GAME_HELPFILE}"
; ----------------------------------------------------------------------------------------------------

; # 삭제 파일 만들기
WriteUninstaller $INSTDIR\Uninst.exe

; # 바탕화면, 시작메뉴에 바로가기 만들기
CreateDirectory "$SMPROGRAMS\${GAME_NAME}"
CreateShortCut  "$DESKTOP\${GAME_NAME}.lnk"                      "$INSTDIR\${GAME_EXEFILE}"
CreateShortCut  "$SMPROGRAMS\${GAME_NAME}\${GAME_NAME}.lnk"      "$INSTDIR\${GAME_EXEFILE}"
CreateShortCut  "$SMPROGRAMS\${GAME_NAME}\Uninstall.lnk"  		 "$INSTDIR\Uninst.exe"

; # 프로그램 추가/제거에 등록
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "DisplayName"     "$(GAME_NAME)"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "DisplayIcon"     "$INSTDIR\${GAME_EXEFILE}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "UninstallString" "$\"$INSTDIR\Uninst.exe$\""
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "QuietUninstallString" "$\"$INSTDIR\Uninst.exe$\""
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "InstallLocation" "$INSTDIR"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "Publisher" "Nooslab"

SectionEnd

Section "Uninstall"

; # 바탕화면, 시작메뉴에 있는 바로가기 삭제
Delete "$DESKTOP\${GAME_NAME}.lnk"
Delete "$SMPROGRAMS\${GAME_NAME}\${GAME_NAME}.lnk"
Delete "$SMPROGRAMS\${GAME_NAME}\Uninstall.lnk"
RMDir  "$SMPROGRAMS\${GAME_NAME}"

; # 프로그램 추가/제거 등록 해제
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine"

; ----------------------------------------------------------------------------------------------------
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
; ----------------------------------------------------------------------------------------------------

SectionEnd