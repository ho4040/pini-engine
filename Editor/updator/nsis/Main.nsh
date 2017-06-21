
InstallDir "$PROGRAMFILES\${GAME_TARGET_FOLDER}" ;
RequestExecutionLevel user
SetCompress off

!define MUI_ICON   "Install.ico"   ;
!define MUI_UNICON "Uninstall.ico" ;

!define MUI_WELCOMEFINISHPAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP   "Install.bmp"

!define MUI_UNWELCOMEFINISHPAGE
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "Uninstall.bmp"

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_LEFT
!define MUI_HEADERIMAGE_BITMAP "Header.bmp"

!define MUI_FINISHPAGE_NOAUTOCLOSE

!define MUI_FINISHPAGE_RUN "$INSTDIR\${GAME_EXEFILE}"
!define MUI_FINISHPAGE_RUN_TEXT "${GAME_FINISHPAGE_RUN_TEXT}"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\${GAME_HELPFILE}"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "${GAME_FINISHPAGE_SHOWREADME_TEXT}"

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${GAME_LICENSE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

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

WriteUninstaller $INSTDIR\Uninst.exe

CreateDirectory "$SMPROGRAMS\${GAME_NAME}"
CreateShortCut  "$DESKTOP\${GAME_NAME}.lnk"                      "$INSTDIR\${GAME_EXEFILE}"
CreateShortCut  "$SMPROGRAMS\${GAME_NAME}\${GAME_NAME}.lnk"      "$INSTDIR\${GAME_EXEFILE}"
CreateShortCut  "$SMPROGRAMS\${GAME_NAME}\Uninstall.lnk"  		 "$INSTDIR\Uninst.exe"

WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "DisplayName"     "$(GAME_NAME)"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "DisplayIcon"     "$INSTDIR\${GAME_EXEFILE}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "UninstallString" "$\"$INSTDIR\Uninst.exe$\""
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "QuietUninstallString" "$\"$INSTDIR\Uninst.exe$\""
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "InstallLocation" "$INSTDIR"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine" "Publisher" "Nooslab"

SectionEnd

Section "Uninstall"

Delete "$DESKTOP\${GAME_NAME}.lnk"
Delete "$SMPROGRAMS\${GAME_NAME}\${GAME_NAME}.lnk"
Delete "$SMPROGRAMS\${GAME_NAME}\Uninstall.lnk"
RMDir  "$SMPROGRAMS\${GAME_NAME}"

DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\piniengine"

; ----------------------------------------------------------------------------------------------------
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
; ----------------------------------------------------------------------------------------------------

SectionEnd