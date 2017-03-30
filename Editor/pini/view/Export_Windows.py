# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import *
from PySide.QtCore import *
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from view.ProgressIndicator import QProgressIndicator

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

import xml.etree.ElementTree as ET
import subprocess
import os
import urllib2
import shutil
import zipfile
import locale
import random
import time
import base64
import hashlib
import os_encoding
from PIL import Image

from view.AssetLibraryWindow import AssetLibraryWindow

from pepy.ico_plugin import *

if sys.platform == "win32" : 
	from pepy import pe


from config import *

def PJOIN(*paths):
	path = []
	for v in paths:
		v = v.replace("/","\\")
		path.append(v.encode(locale.getpreferredencoding()))
	ret = os.path.join(*path).replace("/","\\")
	return ret

LUAJIT_PATH = "resource\\tools\\lua\\luajit.exe"

class Thread_Command(QThread):
	def __init__(self, command, parent = None ):
		super(Thread_Command,self).__init__(parent)
		self.command = command

	def run(self):
		os.system(self.command)

class EditWindow(ModalWindow):
	def __init__(self,title="",source="",parent=None):
		self.title = title
		self.source = source
		super(EditWindow,self).__init__(parent)

		self.saveData = source

	@LayoutGUI
	def GUI(self):
		self.Layout.label(self.title)
		self.Layout.hline();
		self.Layout.gap(3)

		self.textedit = self.Layout.textedit(self.source,None)

		self.Layout.gap(2)
		self.Layout.hline()
		self.Layout.gap(2)

		self.Layout.button(u"저장하기",self.save)
		self.resize(400,400)

	def save(self):
		self.saveData = self.textedit.toPlainText()
		self.close()

	def exec_(self):
		super(EditWindow,self).exec_()
		return self.saveData

class ExportWindowsWindow(ModalWindow):
	def sizeHint(self):
		return QSize(300,0)

	def __init__(self,src=None,parent=None):
		self.work_step = 0

		super(ExportWindowsWindow,self).__init__(parent)
		self.setWindowTitle(u"윈도우 익스포트")

	def closeEvent(self,e):
		super(ExportWindowsWindow,self).closeEvent(e)

	def btn_find_dist_path(self):
		path = QFileDialog.getExistingDirectory(parent=self,caption=u"저장할 위치" )
		if path : 
			self.savePath.setText(path)

	def DEFAULT_EULA(self):
		return u'''최종 사용자 사용권 계약을 적는 공간입니다.

타 소프트웨어의 계약서를 비교하여 작성할 수 있습니다.
*타 소프트웨어 EUAL 문서
 > http://mediago.sony.com/kor/legal/eula
 > http://www.adobe.com/kr/products/eulas/players/shockwave/
 > http://www.steampowered.com/eula_testapp17460/korean.html

모든 해당 문서 작성의 요령은 피니엔진 사이트내에 강의를 올릴 예정입니다.
'''

	def DEFAULT_README(self):
		return u'설치 후 나오는 게임 소개 내용입니다.'

	@LayoutGUI
	def GUI(self):
		savepath = u""
		gamename = u"테스트게임"
		version  = u"0.1"
		distname = u""
		iconpath = u"resource/export_default_icon.png"
		encryptionEnable = False
		inst = ProjectController()
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				savepath = Settings()["path"] if Settings()["path"] else savepath
				gamename = Settings()["game"] if Settings()["game"] else gamename
				version  = Settings()["version"] if Settings()["version"] else version
				distname = Settings()["distname"] if Settings()["distname"] else distname
				iconpath = Settings()["iconpath"] if Settings()["iconpath"] else iconpath
				encryptionEnable = Settings()["encryto"] == 1
				if Settings()["iconpath"] == None :
					Settings()["iconpath"] = iconpath
		self.Layout.clear()
		
		self.Layout.label(u"<b>1. 게임 정보 설정</b>")
		self.Layout.hline();
		self.Layout.gap(3)
		
		with Layout.HBox():
			with Layout.VBox():
				with Layout.HBox():
					self.Layout.label(u"저장위치").setFixedWidth(80)
					self.savePath = self.Layout.input(savepath,None)
					self.Layout.button(u"...",self.btn_find_dist_path).setFixedHeight(20);
				with Layout.HBox():
					self.Layout.label(u"게임명").setFixedWidth(80)
					self.saveGameName = self.Layout.input(gamename,None)
				with Layout.HBox():
					self.Layout.label(u"버전정보").setFixedWidth(80)
					self.saveVersion = self.Layout.input(version,None)
				with Layout.HBox():
					self.Layout.label(u"배포자명").setFixedWidth(80)
					self.saveDistname = self.Layout.input(distname,None)
				with Layout.HBox():
					self.Layout.label(u"리소스암호화").setFixedWidth(80)
					self.encryto = self.Layout.checkbox(u"사용", encryptionEnable, None)

				self.Layout.spacer()

			self.Layout.gap(5)
			
			with Layout.VBox():
				self.appIcon = self.Layout.img(iconpath)#.setFixedSize(50,50)
				self.appIcon.setFixedSize(60,60)
				self.Layout.button(u"...",self.find_icon).setFixedHeight(20)

		self.Layout.gap(2)
		self.Layout.hline()
		self.Layout.gap(2)

		#with Layout.HBox():
		self.Layout.button(u"익스포트",self.export)
		#self.Layout.button(u"인스톨러",self.installer)

		self.resize(350,0)

	@LayoutGUI
	def GUI_FIN_EXPORT(self):
		self.Layout.clear()

		self.Layout.label(u"<b>2. 익스포팅 완료</b>")
		self.Layout.hline();
		self.Layout.gap(3)

		self.Layout.label(u"익스포팅 폴더")

		with Layout.HBox():
			self.Layout.label(self.exported_path)
			self.Layout.button(u"열기",self.open_export_dir).setFixedSize(50,20)

		self.Layout.spacer()

		self.Layout.hline()
		with Layout.HBox():
			self.Layout.button(u"인스톨러 생성",self.installer)
			self.Layout.button(u"익스포트 종료",self.close)

	@LayoutGUI
	def GUI_NSIS_SETUP(self):
		LINE_CSS = "*{color:#515151}"

		header = "resource/tools/win32/NSIS/script/header.png"
		install_icon   = "resource/export_default_icon.png"
		uninstall_icon = "resource/export_default_icon.png"
		install_side   = "resource/tools/win32/NSIS/script/Install.png"
		uninstall_side = "resource/tools/win32/NSIS/script/Install.png"

		inst = ProjectController()
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				header = Settings()["header"] if Settings()["header"] else header
				install_icon   = Settings()["install_icon"]   if Settings()["install_icon"] else install_icon
				uninstall_icon = Settings()["uninstall_icon"] if Settings()["uninstall_icon"] else uninstall_icon
				install_side   = Settings()["install_side"]   if Settings()["install_side"] else install_side
				uninstall_side = Settings()["uninstall_side"] if Settings()["uninstall_side"] else uninstall_side

		self.Layout.clear()
		
		self.Layout.label(u"<b>3. 인스톨러 정보 셋팅</b>")
		self.Layout.hline();
		self.Layout.gap(3)
		
		with Layout.HBox():
			self.Layout.label(u"사용권 계약").setFixedWidth(75)
			self.Layout.button(u"수정하기",self.open_EUAL_editor)

			self.Layout.gap(25)

			self.Layout.label(u"설치 후 문서").setFixedWidth(75)
			self.Layout.button(u"수정하기",self.open_README_editor)

		self.Layout.gap(2)
		self.Layout.hline()
		self.Layout.gap(2)

		with Layout.HBox():
			with Layout.VBox():
				self.Layout.label(u"<b>인스톨러 아이콘")
				self.installIcon = self.Layout.img(install_icon)
				self.installIcon.setFixedSize(80,80)
				self.Layout.button(u"64x64",self.find_install_icon).setFixedSize(80,20)
				self.Layout.spacer()
			
			self.Layout.gap(3)
			self.Layout.vline().setStyleSheet(LINE_CSS)
			self.Layout.gap(3)

			with Layout.VBox():
				self.Layout.label(u"<b>언인스톨러 아이콘")
				self.uninstallIcon = self.Layout.img(uninstall_icon)
				self.uninstallIcon.setFixedSize(80,80)
				self.Layout.button(u"64x64",self.find_uninstall_icon).setFixedSize(80,20)
				self.Layout.spacer()

			self.Layout.gap(3)
			self.Layout.vline().setStyleSheet(LINE_CSS)
			self.Layout.gap(3)

			with Layout.VBox():
				self.Layout.label(u"<b>인스톨 상단")
				self.headerImg = self.Layout.img(header)
				self.headerImg.setFixedSize(175,53)
				self.Layout.button(u"175x53",self.find_header).setFixedHeight(20)
				self.Layout.spacer()

			self.Layout.gap(3)
			self.Layout.vline().setStyleSheet(LINE_CSS)
			self.Layout.gap(3)

			with Layout.VBox():
				self.Layout.label(u"<b>인스톨 좌측")
				self.installSideImg = self.Layout.img(install_side)
				self.installSideImg.setFixedSize(191/2,290/2)
				self.Layout.button(u"191x290",self.find_install_side).setFixedSize(82,20)
			
			self.Layout.gap(3)
			self.Layout.vline().setStyleSheet(LINE_CSS)
			self.Layout.gap(3)

			with Layout.VBox():
				self.Layout.label(u"<b>언인스톨 좌측")
				self.uninstallSideImg = self.Layout.img(uninstall_side)
				self.uninstallSideImg.setFixedSize(191/2,290/2)
				self.Layout.button(u"191x290",self.find_uninstall_side).setFixedSize(82,20)

			self.Layout.spacer()
		
		self.Layout.gap(3)
		self.Layout.hline()
		self.Layout.gap(3)

		#with Layout.HBox():
		self.Layout.button(u"인스톨러 생성",self.generate_installer)
		#	self.Layout.button(u"CD 굽기",self.installer)

	def find_install_icon(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"인스톨 아이콘으로 사용할 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["install_icon"] = path
					self.installIcon.setPixmap(path)

	def find_uninstall_icon(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"언인스톨 아이콘으로 사용할 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["uninstall_icon"] = path
					self.uninstallIcon.setPixmap(path)

	def find_header(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"인스톨러 상단 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["header"] = path
					self.headerImg.setPixmap(path)

	def find_install_side(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"인스톨러 좌측 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["install_side"] = path
					self.installSideImg.setPixmap(path)

	def find_uninstall_side(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"언인스톨러 좌측 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["uninstall_side"] = path
					self.uninstallSideImg.setPixmap(path)

	def find_icon(self):
		path,ext = QFileDialog.getOpenFileName(parent=self,caption=u"아이콘으로 사용할 이미지를 선택해주세요.",filter="JPEG (*.jpg *.jpeg);;PNG (*.png);;" )
		if path : 
			self.appIcon.setPixmap(QPixmap(path))

			t = str(time.time()).replace(".","")
			distDir = "tmp_storage/icons/"
			
			
			if os.path.isdir( os.path.dirname(distDir) ) == False :
				os.makedirs( os.path.dirname(distDir) )
			
			distPNG = ""
			while 1: 		
				t = (str(time.time())+str(random.random()*100)).replace(".","")
				distPNG = distDir + t + ".png"
				if not os.path.isfile(distPNG) : 
					break

			bpng = Image.open(path)
			png5 = bpng.resize((128, 128), Image.ANTIALIAS) 

			png5.save(distPNG)

			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					Settings()["iconpath"] = distPNG

	def open_EUAL_editor(self):
		EUAL = self.DEFAULT_EULA()
		inst = ProjectController()
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				if Settings()["EUAL"] : 
					EUAL = Settings()["EUAL"]
		text = EditWindow(u"최종 사용자 사용권 계약(EUAL)",EUAL,self).exec_()
		
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				Settings()["EUAL"] = text
						
	def open_README_editor(self):
		README = self.DEFAULT_README()
		inst = ProjectController()
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				if Settings()["README"] : 
					README = Settings()["README"]
		text = EditWindow(u"리드미 텍스트(README)",README,self).exec_()

		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				Settings()["README"] = text

	def installer(self):
		self.GUI_NSIS_SETUP()

	def generate_installer(self):
		if not os.path.isdir("nsis") :
			proc = subprocess.Popen(["start","/w","resource\\tools\\win32\\NSIS\\installer.exe","/S","/D="+os.getcwd()+"\\nsis"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,shell=True )
			try:
				out, err = proc.communicate()
				print ">>>",out,err
			except Exception, e:
				pass

		if os.path.isfile("nsis/makensis.exe") : 
			distDir = "tmp_storage/installer/"
			if os.path.isdir( os.path.dirname(distDir) ) :
				shutil.rmtree('tmp_storage/installer/')
			os.makedirs( os.path.dirname(distDir) )
			#os.makedirs( os.path.dirname(distDir+"Master/") )

			header = "resource/tools/win32/NSIS/script/header.png"
			install_icon   = "resource/export_default_icon.png"
			uninstall_icon = "resource/export_default_icon.png"
			install_side   = "resource/tools/win32/NSIS/script/Install.png"
			uninstall_side = "resource/tools/win32/NSIS/script/Install.png"
			readme = self.DEFAULT_README()
			eual = self.DEFAULT_EULA()
			gamename = u"테스트게임"
			version  = u"0.1"
			distname = u""
		
			inst = ProjectController()
			with Settings("WINDOW_EXPORT") :
				with Settings(inst.path) :
					header = Settings()["header"] if Settings()["header"] else header
					install_icon   = Settings()["install_icon"]   if Settings()["install_icon"] else install_icon
					uninstall_icon = Settings()["uninstall_icon"] if Settings()["uninstall_icon"] else uninstall_icon
					install_side   = Settings()["install_side"]   if Settings()["install_side"] else install_side
					uninstall_side = Settings()["uninstall_side"] if Settings()["uninstall_side"] else uninstall_side
					readme = Settings()["README"] if Settings()["README"] else readme
					eual   = Settings()["EUAL"] if Settings()["EUAL"] else eual
					gamename = Settings()["game"] if Settings()["game"] else gamename
					version  = Settings()["version"] if Settings()["version"] else version
					distname = Settings()["distname"] if Settings()["distname"] else distname
	
			master = u'''
!include "MUI2.nsh"

Name    "[gamename]" ; 게임 이름
OutFile "installer.exe" ; 설치 파일 이름

!define	GAME_NAME     "[gamename]" ; 게임 이름
!define GAME_EXEFILE  "[gamename].exe" ; 게임 실행 파일 이름
!define GAME_TARGET_FOLDER "[distname]\[gamename]" ; 게임 폴더 이름
!define GAME_SOURCE_FOLDER "Master" ; 게임 폴더 이름
!define GAME_DISTRIBUTOR "[distname]"; 배포자명
!define	GAME_HELPFILE "Help.txt" ; 게임 도움말 파일 이름
!define GAME_LICENSE  "EULA.txt" ; 라이센스 파일
!define GAME_FINISHPAGE_RUN_TEXT "${GAME_NAME}를 실행합니다."
!define GAME_FINISHPAGE_SHOWREADME_TEXT "도움말을 확인합니다."

!include "Main.nsh"
'''

			master = master.replace(u"[gamename]", gamename)
			master = master.replace(u"[distname]", distname)
			
			def png2ico(src,dst,size):
				image = Image.open(src)
				back = Image.new("RGBA", size, (0,0,0,0))
				image = image.resize(size, Image.ANTIALIAS)
				offset = [0,0]
				if image.size[0] >= image.size[1]:
					offset[1] = back.size[1]/2-image.size[1]/2
				else:
					offset[0] = back.size[0]/2-image.size[0]/2
				back.paste(image, tuple(offset))
				back.save(dst, "ICO")

			def png2bmp(src,dst,size):
				image = QImage(src)
				image.scaled(size[0],size[1])
				image.save(dst,"BMP")

			def textsave(txt,dst):
				fp = QFile(dst)
				fp.open(QIODevice.WriteOnly | QIODevice.Text)
				
				out = QTextStream(fp)
				out.setCodec("EUC-KR")
				out.setGenerateByteOrderMark(False)
				out << txt

				out = None
				fp.close()

			png2ico(install_icon  ,distDir+"Install.ico",(64,64))
			png2ico(uninstall_icon,distDir+"Uninstall.ico",(64,64))

			png2bmp(header,distDir+"Header.bmp",(175,53))
			png2bmp(install_side,distDir+"Install.bmp",(191,290))
			png2bmp(uninstall_side,distDir+"Uninstall.bmp",(191,290))

			textsave(readme,distDir+"Help.txt")
			textsave(eual,distDir+"EULA.txt")
			textsave(master,distDir+"Master.nsi")

			shutil.copyfile("resource/tools/win32/NSIS/script/Main.nsh", distDir+"Main.nsh")

			binpath = self.exported_path + "/export_window/"

			shutil.copytree( binpath, distDir + "Master/" )
			proc = subprocess.Popen(["nsis\\makensis.exe",distDir+"Master.nsi"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,shell=True )
			try:
				out, err = proc.communicate()
				print "makensis",out, err
			except Exception, e:
				pass

			shutil.copyfile(distDir+"installer.exe",self.exported_path+"/installer.exe")

			print os.path.dirname(distDir)
			QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.exported_path))

			QMessageBox.information(self,"Pini",u"인스톨러가 생성되었습니다!")
			self.close()
		else:
			QMessageBox.warning(self,"Pini",u"NSIS 설치에 실패하였습니다.\n관리자 모드를 승인해주세요. 해당 오류가 해결이 안되면 관리자에게 문의해주세요.")

	def open_export_dir(self):
		QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.exported_path+"/export_window"))		

	def compile_cocos_lua(self,path,dist):
		luaf = path.replace("/","\\").encode(os_encoding.cp())
		luacf= (dist+"c").replace("/","\\").encode(os_encoding.cp())

		ARGU = [LUAJIT_PATH,"-b",luaf,luacf]
		proc = subprocess.Popen(ARGU, stdout=subprocess.PIPE, stdin=subprocess.PIPE,shell=True )
		try:
			out, err = proc.communicate()
			print ">>>",out,err
		except Exception, e:
			print e

	def export(self):
		version = self.saveVersion.text()
		savepath = self.savePath.text()
		gamename = self.saveGameName.text()
		distname = self.saveDistname.text()
		encryto = self.encryto.isChecked()
		if len(savepath) == 0 :
			QMessageBox.warning(self,"Pini",u"저장 위치를 지정해주세요!")
			return 

		if len(gamename) == 0 :
			QMessageBox.warning(self,"Pini",u"게임명을 정해주세요!")
			return 

		if len(distname) == 0 :
			QMessageBox.warning(self,"Pini",u"배포자명을 정해주세요!")
			return 

		ICO_path = None
		inst = ProjectController()
		with Settings("WINDOW_EXPORT") :
			with Settings(inst.path) :
				Settings()["path"] = savepath
				Settings()["game"] = gamename
				Settings()["version"]  = version
				Settings()["distname"] = distname
				Settings()["encryto"] = 1 if encryto else 2

				if Settings()["iconpath"] : 
					ICO_path = Settings()["iconpath"]

		BUILDPATH  = inst.path + "/build/"
		binpath    = savepath  + "/export_window/"
		srcpath    = savepath  + "/export_window/src"  
		respath    = savepath  + "/export_window/res"  

		BUILDPATH = BUILDPATH.replace("\\","/")
		srcpath   = srcpath.replace("\\","/")
		respath   = respath.replace("\\","/")
		binpath   = binpath.replace("\\","/")

		AssetLibraryWindow().watcherOn = False
		AssetLibraryWindow().watcher = None

		shutil.rmtree(BUILDPATH)
		os.makedirs(BUILDPATH)

		def windowExport(arg1,arg2):
			print "====================================================="
			for root, dirs, files in os.walk(BUILDPATH, topdown=False):
				for name in files:
					path = os.path.join(root, name).replace("\\","/")
					ext  = os.path.splitext(path)[1]	
					dist = srcpath+path.replace(BUILDPATH,"/")

					#print "=",root.replace("\\","/").replace(BUILDPATH,""),path,ext,dist

					if ext==".obj" : 
						continue

					if os.path.isdir(os.path.dirname(dist)) == False :
						os.makedirs(os.path.dirname(dist))

					if ext==".lua" : 
						self.compile_cocos_lua(path,dist)
					else:
						fr = open(path, 'rb')
						fs = open(dist, 'wb')

						fs.write(fr.read())

						fr.close()
						fs.close()

			if encryto : 
				SEVENZIPPATH = "resource\\tools\\win32\\7z\\7z.exe"
				DISTPATH = srcpath+"/"
				base_password = str(time.time())
				print "base_password=",base_password
				base_password = base64.b64encode(hashlib.md5(base_password).digest())
				print "after md5:",base_password

				f = open(DISTPATH+'pp.lua', 'w')
				f.write("return function() return \"" + base_password + "\" end" )
				f.close();

				base_password = base_password[0:11]
				
				isImageExist = os.path.exists(DISTPATH+"image")
				isSoundExist = os.path.exists(DISTPATH+"sound")

				targetFolders = []

				if isImageExist:
					targetFolders.append(PJOIN(DISTPATH,'image'))
				if isSoundExist:
					targetFolders.append(PJOIN(DISTPATH,'sound'))

				DISTPRZPATH = PJOIN(DISTPATH,"..","res.prz")
				rc = subprocess.call([SEVENZIPPATH,'a','-tzip','-p'+base_password,'-r','-y',DISTPRZPATH] + targetFolders)

				if isImageExist:
					shutil.rmtree(DISTPATH+"image")
				if isSoundExist:
					shutil.rmtree(DISTPATH+"sound")

			APPPATH = ""
			if sys.platform == "darwin" : 
				if config.__RELEASE__ == False : 
					APPPATH = "../../Engine/OSX.app"
				else : 
					APPPATH = "OSX.app"
			else :
				if config.__RELEASE__ == False : 
					APPPATH = "../../Engine/window64/"
				else : 
					APPPATH = "window/"

			DEFAULT_SRC = APPPATH + "src/"
			DEFAULT_RES = APPPATH + "res/"
			def copyAll(SOURCE,DIST):
				for root, dirs, files in os.walk(SOURCE, topdown=False):
					for name in files:
						path = os.path.join(root, name).replace("\\","/")
						dist = DIST+path.replace(SOURCE,"/")

						if os.path.isdir(os.path.dirname(dist)) == False :
							os.makedirs(os.path.dirname(dist))

						fr = open(path, 'rb')
						fs = open(dist, 'wb')

						fs.write(fr.read())

						fr.close()
						fs.close()

			copyAll(DEFAULT_SRC,srcpath)
			copyAll(DEFAULT_RES,respath)

			if os.path.isdir(srcpath+"/etc") : 
				if os.path.isdir(srcpath+"/../etc") : 
					shutil.rmtree(srcpath+"/../etc")
				shutil.move(srcpath+"/etc", srcpath+"/../etc")

			gamename.encode("UTF-8")

			EEP = srcpath+"/_export_execute_.lua"
			fp = QFile(EEP)
			fp.open(QIODevice.WriteOnly | QIODevice.Text)
			
			out = QTextStream(fp)
			out.setCodec("UTF-8")
			out.setGenerateByteOrderMark(False)
			out << "return \""
			out << gamename
			out << "\""

			out = None
			fp.close()

			self.compile_cocos_lua(EEP,EEP)
			
			os.remove(EEP)

			files = [ f for f in os.listdir(APPPATH) if os.path.isfile(os.path.join(APPPATH,f)) ]
			for v in files:
				path = os.path.join(APPPATH, v).replace("\\","/")
				dist = os.path.join(binpath, v).replace("\\","/")

				if os.path.isdir(os.path.dirname(dist) ) == False :
					os.makedirs(os.path.dirname(dist) )

				fr = open(path, 'rb')
				fs = open(dist, 'wb')

				fs.write(fr.read())

				fr.close()
				fs.close()

			distapp = binpath+gamename+u".exe"
			if os.path.isfile(distapp) : 
				os.remove(distapp)
			
			if ICO_path : 
				execute = pe.PEFile(binpath+"pini_remote.exe")
				execute.replace_icon(ICO_path)
				execute.write(binpath+"_pini_remote.exe")
				
				os.rename(binpath+"_pini_remote.exe", distapp)
				os.remove(binpath+"pini_remote.exe")
			else :
				os.rename(binpath+"pini_remote.exe", distapp)
			
			def refresh_icon_window():
				import ctypes
				from ctypes import wintypes

				# http://msdn.microsoft.com/en-us/library/ms644950
				SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutA
				SendMessageTimeout.restype = wintypes.LPARAM  # aka LRESULT
				SendMessageTimeout.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
				                               wintypes.UINT, wintypes.UINT, ctypes.c_void_p]

				# http://msdn.microsoft.com/en-us/library/bb762118
				SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
				SHChangeNotify.restype = None
				SHChangeNotify.argtypes = [wintypes.LONG, wintypes.UINT, wintypes.LPCVOID, wintypes.LPCVOID]

				HWND_BROADCAST     = 0xFFFF
				WM_SETTINGCHANGE   = 0x001A
				SMTO_ABORTIFHUNG   = 0x0002
				SHCNE_ASSOCCHANGED = 0x08000000

				SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0, SMTO_ABORTIFHUNG, 5000, None)
				SHChangeNotify(SHCNE_ASSOCCHANGED, 0, None, None)

			refresh_icon_window()
			self.exported_path = savepath
			self.GUI_FIN_EXPORT()

			AssetLibraryWindow().watcherOn = True
			AssetLibraryWindow().updateWatcher()
			print "all fin!"
		inst.compileProj(False,windowExport)

