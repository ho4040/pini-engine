# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Noriter.UI.Layout import *
from Noriter.views.NoriterMainWindow import *
from Noriter.utils.Settings import Settings

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController

from PySide.QtCore import * 
from PySide.QtGui import *
from PySide.QtNetwork import *

from view.ScreenInfoWindow import ScreenInfoWindow
from view.RemotePlayWindow import RemotePlayWindow
from view.SceneMapWindow import SceneMapWindow
from view.ATLEditor import ATLEditor
from view.VariableViewWindow import VariableViewWindow
from view.DefineSettingWindow import DefineSettingWindow
from view.BookmarkListWindow import BookmarkListWindow
from view.Launcher import LauncherView
from view.Export_Android import ExportAndroidWindow
from view.Export_Windows import ExportWindowsWindow
from view.SceneScriptWindow import SceneScriptWindowManager
from view.AboutPiniWindow import AboutPiniWindow
from view.CompileProgressWindow import CompileProgressWindow
from view.FundingListWindow import FundingListWindow

from command.FontManager import FontManager

from Noriter.utils.Utils import Utils
from view.AssetLibraryWindow import AssetLibraryWindow

from slpp import slpp
import subprocess
import shutil
import os
import locale

from config import *
from appdirs import *

from view.OutputWindow import OutputWindow 

import socket
import thread, time

from command.RemoteClient import RemoteClient

@MenuBar("파일(&F)/스크립트 생성(&N)...",QKeySequence.New)
def NewScene():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
	path,ext = QFileDialog.getSaveFileName(parent=NoriterMain(),caption="New Scene",dir=inst.sceneDirectory )
	if len(path) > 0:
		fi = QFileInfo(path) 
		if len(fi.suffix()) == 0 :
			path = path+".lnx"
		elif fi.suffix() != "lnx" :
			path = fi.path() + QDir.separator() + fi.baseName() + ".lnx"

		SceneListController.getInstance().New(path)
		SceneListController.getInstance().Open(path)

@MenuBar("파일(&F)/스크립트 열기(&O)...",QKeySequence.Open)
def OpenScene():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
	
	path,ext = QFileDialog.getOpenFileName(parent=NoriterMain(),caption="Open Scene",dir=inst.sceneDirectory )
	if path.startswith( inst.sceneDirectory ) :
		fi = QFileInfo(path)
		if fi.suffix() == "lnx" :
			SceneListController.getInstance().Open(path)
		else:
			print "can not open scene"
	else:
		print "can not open scene"

@MenuBar("파일(&F)/스크립트 저장(&S)",QKeySequence.Save)
def Save(showAleart=False,discard=None):
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	if showAleart : 
		flag = QMessageBox.Save
		if discard : 
			flag = flag | QMessageBox.Discard
		flag = flag | QMessageBox.Cancel

		sceneScriptWindowManager = SceneScriptWindowManager.getInstance()
		currentFileName = sceneScriptWindowManager.getActiveFilename()

		if currentFileName == None:
			return -1

		msgBox = QMessageBox()
		msgBox.setText(u"저장")
		msgBox.setInformativeText(currentFileName + u"을(를) 저장하시겠습니까?")
		msgBox.setStandardButtons(flag)
		msgBox.setDefaultButton(QMessageBox.Cancel)
		msgBox.setIcon(QMessageBox.Warning)
		ret = msgBox.exec_()

		if ret == QMessageBox.Save:
			sceneScriptWindowManager.saveActiveScene()
		elif ret == QMessageBox.Discard:
			return -1
		elif ret == QMessageBox.Cancel:
			return 0
	else:
		sceneScriptWindowManager = SceneScriptWindowManager.getInstance()
		sceneScriptWindowManager.saveActiveScene()

	OutputWindow().notice(u"파일이 저장되었습니다.")
	return 1

@MenuBar("파일(&F)/스크립트 모두 저장(&A)",[QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_S)])
def SaveAll(showAleart=False,discard=None):
	SceneScriptWindowManager.getInstance().saveAll()

@MenuBar("파일(&F)/0")
def FileSeparator0(showAlert=False,discard=None):
	pass

@MenuBar("파일(&F)/프로젝트 선택(&P)...")
def OpenLaucher(showAleart=False,discard=None):
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	result = SceneScriptWindowManager.getInstance().reset()

	if not result:
		return

	BookmarkListWindow().hide()
	SceneMapWindow(NoriterMain()).hide()
	DefineSettingWindow().hide()
	ATLEditor().hide()
	FontManager().reset()

	m = NoriterMain()
	ret = m.close()

	if ret:
		def close():
			pass
		launcher = LauncherView(m)
		launcher.onClose = close

@MenuBar("파일(&F)/0")
def FileSeparator1(showAlert=False,discard=None):
	pass

@MenuBar("파일(&F)/익스포트(&E)/윈도우(&W)...")
def OpenExportWindows(showAleart=False,discard=None):
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	ExportWindowsWindow(NoriterMain()).exec_()

@MenuBar("파일(&F)/익스포트(&E)/안드로이드(&A)...")
def OpenExportAndroid(showAleart=False,discard=None):
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	ExportAndroidWindow(NoriterMain()).exec_()

@MenuBar("파일(&F)/0")
def FileSeparator2(showAlert=False,discard=None):
	pass

@MenuBar("파일(&F)/끌내기(&X)")
def CloseEditor(showAlert=False,discard=None):
	closeEvent = QCloseEvent()
	NoriterMain().closeSignal.emit(NoriterMain(),closeEvent)

	if closeEvent.isAccepted():
		QApplication.quit()

@MenuBar("편집(&E)/실행 취소(&U)",QKeySequence.Undo)
def EditUndo(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.undo()

@MenuBar("편집(&E)/반복(&R)",QKeySequence.Redo)
def EditRedo(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.redo()

@MenuBar("편집(&E)/0")
def EditSeparator0(showAlert=False,discard=None):
	pass

@MenuBar("편집(&E)/잘라내기(&T)",QKeySequence.Cut)
def EditCut(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.cut()

@MenuBar("편집(&E)/복사(&C)",QKeySequence.Copy)
def EditCopy(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.copy()

@MenuBar("편집(&E)/붙여넣기(&P)",QKeySequence.Paste)
def EditPaste(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.paste()

@MenuBar("편집(&E)/삭제(&L)",QKeySequence.Delete)
def EditDelete(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.removeSelectedText()

@MenuBar("편집(&E)/0")
def EditSeparator1(showAlert=False,discard=None):
	pass

@MenuBar("편집(&E)/찾기(&F)...",QKeySequence.Find)
def EditFind(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.showFind()

@MenuBar("편집(&E)/바꾸기(&R)...",QKeySequence.Replace)
def EditReplace(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.showReplace()

@MenuBar("편집(&E)/0")
def EditSeparator2(showAlert=False,discard=None):
	pass

@MenuBar("편집(&E)/대사줄 토글(&S)",[QKeySequence(Qt.CTRL+Qt.Key_Semicolon)])
def EditToggleSemicolon(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.toggleSemicolon()

@MenuBar("편집(&E)/주석 토글(&M)",[QKeySequence(Qt.CTRL+Qt.Key_Slash)])
def EditToggleComment(showAlert=False,disacrd=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.toggleComment()

@MenuBar("편집(&E)/0")
def EditSeparator3(showAlert=False,discard=None):
	pass

@MenuBar("편집(&E)/모두 선택(&A)",QKeySequence.SelectAll)
def EditSelectAll(showAlert=False,discard=None):
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.selectAll()




@MenuBar("루아(&L)/새로운 루아 모듈(&N)...")
def OpenExportAndroid(showAleart=False,discard=None):
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	m = NoriterMain()
	text,ok = QInputDialog.getText(m, u"새로운 루아 모듈",u"모듈이름을 적어주세요.")
	if ok and text:
		fullpath = os.path.join(inst.path,"module",text+u".lua")
		if os.path.exists(fullpath) :
			QMessageBox.warning(m,u"피니엔진",u"모듈명이 중복되었습니다. 다른 이름으로 해주세요.")
			return

		fp = QFile(fullpath)
		fp.open(QIODevice.WriteOnly | QIODevice.Text)
		
		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out <<u"--함수 정의 코드는 여기에 적어주세요.\n\n"
		out <<u"local function m(fileName)\n"
		out <<u"	--[스크립트] 매크로가 불리는 시점에 실행 될 루아 코드를 적어주세요.\n\n\n"
		out <<u"end\n"
	

		out <<u"return m\n"
		out = None
		fp.close()

		QMessageBox.information(m,u"피니엔진",u"성공적으로 생성하였습니다.")
		filePath = fullpath.encode(locale.getpreferredencoding())
		os.system('start "" "'+filePath+'"')

	#ExportAndroidWindow(NoriterMain()).exec_()

@MenuBar("프로젝트(&P)/화면 설정(&S)...")
def OpenScreen():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
		
	ScreenInfoWindow(NoriterMain()).exec_()

@MenuBar("프로젝트(&P)/선실행 스크립트 편집(&P)")
def PreMainScript():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
	
	targetPath = inst.path + u"/scene/프리메인.lnx"

	if not os.path.isfile(targetPath) :
		SceneListController.getInstance().New(targetPath)

	SceneListController.getInstance().Open(targetPath)

@MenuBar("도구(&T)/스크립트 표(&T)")
def Actors():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
		
	SceneMapWindow(NoriterMain()).show()
	SceneMapWindow(NoriterMain()).refreshMap()

@MenuBar("도구(&T)/치환설정(&D)")
def DefineSetting():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	DefineSettingWindow().updateList()
	DefineSettingWindow().show()

@MenuBar("도구(&T)/변수 뷰어(&V)")
def VariableViewer():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
	
	VariableViewWindow().show()

@MenuBar("도구(&T)/북마크 목록(&B)")
def OpenBookmarkListWindow():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	BookmarkListWindow().show()
	BookmarkListWindow().refreshData()

# @MenuBar("도구(&T)/0")
# def ToolsSeparator0(showAlert=False,discard=None):
# 	pass

# @MenuBar("도구(&T)/애니메이션 편집기(&A)")
# def OpenATLEditor():
# 	inst = ProjectController()
# 	if len(inst.path) == 0 : 
# 		return

# 	ATLEditor().show()
# 	ATLEditor().refreshData()

@MenuBar("테스트(&S)/기기 테스트(&R)...")
def OpenScreen():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
		
	RemotePlayWindow(NoriterMain()).exec_()

@MenuBar("윈도우(&W)/로그(&L)")
def OpenLogWindow():
	from view.OutputWindow import OutputWindow
	OutputWindow().show()

@MenuBar("윈도우(&W)/0")
def WindowSeparator3(showAlert=False,discard=None):
	pass

@MenuBar("윈도우(&W)/다음 창(&N)",QKeySequence.NextChild)
def NextWindow():
	manager = SceneScriptWindowManager.getInstance()
	currentActive = manager.getActive()

	isNext = False

	if currentActive != None:
		if len(manager.windows) > 1:
			for v in manager.activateQueue:
				if v == currentActive:
					isNext = True
					continue
				if isNext:
					v.raise_()
					v.editor.setFocus()
					isNext = False
					break
			if isNext:
				manager.activateQueue[0].raise_()
				manager.activateQueue[0].editor.setFocus()

@MenuBar("윈도우(&W)/현재 창 닫기(&C)",QKeySequence.Close)
def CloseCurrentWindow():
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow:
		activeSceneScriptWindow.close()

def __run__(clean,isCurrentScene,startLine=None):
	from command.ScriptCommands import ScriptCommand

	SceneScriptWindowManager.getInstance().saveAll()
	
	APPPATH = ""
	if sys.platform == "darwin" : 
		if config.__RELEASE__ == False : 
			APPPATH = "../../Engine/OSX.app"
		else : 
			APPPATH = "OSX.app"
	else :
		if config.__RELEASE__ == False : 
			APPPATH = "../../Engine/window64"
			try:
				shutil.rmtree(APPPATH + "/src")
			except Exception, e:
				pass
			try:
				shutil.rmtree(APPPATH + "/res")
			except Exception, e:
				pass
			try:
				shutil.copytree(APPPATH + "/../VisNovel/src",APPPATH + "/src")
			except Exception, e:
				pass
			try:
				shutil.copytree(APPPATH + "/../VisNovel/res",APPPATH + "/res")
			except Exception, e:
				pass

		else : 
			APPPATH = "window"

	print APPPATH
	####### run !!!!!
	OutputWindow().notice("RUN : "+APPPATH)
	OutputWindow().notice(u"테스트 플레이를 위한 컴파일 시작")

	msgBox = CompileProgressWindow(NoriterMain())
	msgBox.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
	msgBox.show()
	msgBox.setText(u"초기화 중...")
	
	def afterCompileProj(failFiles,inst):
		OutputWindow().notice(u"테스트 플레이를 위한 컴파일 끝.")
		OutputWindow().notice(u"파일 복사 중.")
		msgBox.setText(u"파일 복사중...")

		dispath = user_data_dir("pini_remote","")+"/"
		BUILDPATH = ProjectController().path + "/build/"
		BUILDPATH = BUILDPATH.replace("\\","/")
		
		if clean : 
			try:
				shutil.rmtree(dispath)
			except Exception, e:
				pass
		try:
			for root, dirs, files in os.walk(BUILDPATH, topdown=False):
				for name in files:
					path = os.path.join(root, name).replace("\\","/")
					dist = dispath+path.replace(BUILDPATH,"")

					if os.path.isdir(os.path.dirname(dist)) == False :
						os.makedirs(os.path.dirname(dist))

					shutil.copyfile(path,dist)

				for name in dirs:
					path = os.path.join(root, name).replace("\\","/")
					dist = dispath+path.replace(BUILDPATH,"")
					if os.path.isdir(dist) == False :
						os.makedirs(dist)
		except Exception, e:
			msgBox.hide()
			QMessageBox.warning(NoriterMain(),"pini",u"파일 복사에 실패하였습니다. 관리자모드로 실행하시거나 컴퓨터를 재부팅 후 다시 시도해주세요.")
			return

		if type(failFiles) == types.StringType:
			msgBox.hide()
			QMessageBox.warning(NoriterMain(),"pini",u"다음의 이유로 실패하였습니다.\n" + failFiles)
			return

		if failFiles == None:
			msgBox.hide()
			QMessageBox.warning(NoriterMain(),"pini",u"비정상적인 이유로 컴파일에 실패하였습니다.")
			return

		if len(failFiles) > 0 :
			failFile = u""

			for fileName in failFiles:
				if len(failFile) != 0:
					failFile = failFile + ","
				failFile = failFile + "\"" + fileName[0] + u".lnx\" 파일의 "
				failFile = failFile + unicode(str(fileName[1]+1)) + u"번째 줄"
			msgBox.hide()
			QMessageBox.warning(NoriterMain(),"pini",failFile+u"에 스크립트 파일에 에러가 있습니다. 수정 후 실행해주세요!")
			return

		HOST,PORT = "127.0.0.1",45674
		def newproc():
			if sys.platform == "darwin" : 
				proc = subprocess.Popen(["open", APPPATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			else:
				if ProjectController().fullscreen : 
					proc = subprocess.Popen([APPPATH+"/pini_remote.exe","--fullscreen"], cwd=APPPATH)
				else:
					proc = subprocess.Popen([APPPATH+"/pini_remote.exe","--nonfullscreen"], cwd=APPPATH)
		def remoting():
			remote = RemoteClient(NoriterMain())
			if inst:
				activeScript = SceneScriptWindowManager.getInstance().getActive()
				if activeScript:
					remote.playScene = activeScript.fileName
			remote.startLine = startLine
			remote._connect(HOST,PORT,False)

		ping = QTcpSocket() 
		ping.connectToHost(HOST,PORT)
		ping.waitForConnected(500)
		msgBox.hide()
		
		if ping.state() != QAbstractSocket.ConnectedState : 
			ping.close()
			newproc()
		remoting()

	ProjectController().compileProj(False,afterCompileProj,isCurrentScene)

@MenuBar("테스트(&S)/클린 테스트(&C)",QKeySequence.Print)
def CleanTestRun():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	inst = ProjectController()
	BUILDPATH  = inst.path + "/build/"

	AssetLibraryWindow().watcherOn = False
	AssetLibraryWindow().watcher = None

	try:
		shutil.rmtree(BUILDPATH)
	except Exception, e:
		pass

	try:
		os.makedirs(BUILDPATH)
	except Exception, e:
		pass

	__run__(True,False)

	AssetLibraryWindow().watcherOn = True
	AssetLibraryWindow().updateWatcher()

@MenuBar("테스트(&S)/바로 테스트(&T)",QKeySequence.Refresh)
def TestRun():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	__run__(False,False)

@MenuBar("테스트(&S)/현재 장면 테스트(&U)",[QKeySequence(Qt.Key_F6)])
def CurrentScriptRun():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	__run__(False,True)

@MenuBar("테스트(&S)/현재 커서부터 실행(&R)",[QKeySequence(Qt.CTRL+Qt.Key_F6)])
def CurrentScriptCursorRun():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return

	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		__run__(False,True,activeSceneScriptWindow.editor.textCursor().blockNumber())
	else:
		TestRun()

@MenuBar("도움말(&H)/오픈 소스 프로젝트(&H)")
def OpenOfficialSite():
	QDesktopServices.openUrl(QUrl("https://github.com/ho4040/pini-engine"))

@MenuBar("도움말(&H)/공식 가이드 문서(&G)",QKeySequence.HelpContents)
def OpenOfficialGuide():
	activeSceneScriptWindow = SceneScriptWindowManager.getInstance().getActive()
	if activeSceneScriptWindow != None:
		activeSceneScriptWindow.editor.showReference()
	else:
		QDesktopServices.openUrl(QUrl("http://nooslab.com/piniengine/wiki"))

@MenuBar("도움말(&H)/오픈소스 후원자 리스트")
def FundingListScreen():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
		
	FundingListWindow(NoriterMain()).exec_()

@MenuBar("도움말(&H)/피니엔진에 대하여(&P)...")
def OpenAboutScreen():
	inst = ProjectController()
	if len(inst.path) == 0 : 
		return
		
	AboutPiniWindow(NoriterMain()).exec_()
