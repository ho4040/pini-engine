# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.phonon import *

from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

from command.ScriptCommands import GraphicsProtocolObject
from command.ScriptCommands import ScriptGraphicsProtocol
from command.FontManager import FontManager

import shutil
import os
from PIL import Image
import locale

class FileListView(QTreeView):
	def sizeHint(self):
		return QSize(0,0)

	def __init__(self,parent):
		super(FileListView,self).__init__(parent)
		self.setDragDropMode(QAbstractItemView.InternalMove)
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.viewport().setAcceptDrops(True)
		self.setDropIndicatorShown(True)

	def dragEnterEvent(self, e):
		e.accept()
	
	def dragMoveEvent(self,e):
		e.acceptProposedAction();

	def dropEvent(self, e):
		count = 0
		if e.dropAction() == Qt.MoveAction : 
			distIdx = self.indexAt(e.pos())
			distDir = self.model().filePath(distIdx)
			if os.path.isfile(distDir) : 
				distDir = os.path.dirname(distDir)
			for url in e.mimeData().urls():
				srcpath = url.toLocalFile()
				filename = os.path.basename(srcpath)

				if len(distDir) == 0 : 
					return 

				fullpath = os.path.join(distDir,filename)
				print srcpath,fullpath
				if os.path.isfile(fullpath) : 
					QMessageBox.warning(self,u"피니엔진",u"옮길 폴더에 같은 파일명을 가진 파일이 있습니다.")
					return
				
				print srcpath,fullpath
				os.rename(srcpath,fullpath)
		else:
			for url in e.mimeData().urls():
				path = url.toLocalFile()
				self.moveFile(path)
				count += 1
			QMessageBox.information(self,u"Noriter",unicode(count)+u"개 파일을 프로젝트 폴더로 복사하였습니다.")

	def moveFile(self,path) : 
		proj = ProjectController().path
		fname, ext = os.path.splitext(path)
		ext = ext.lower()
		
		if ext == ".png" or ext == ".jpg" : 
			if ext == ".jpg" : 
				fname = os.path.basename(path)
				fname, ext = os.path.splitext(fname)
				
				im = Image.open(path)
				im.save(os.path.join(proj,"image",fname+".png"))
			else:
				self.copyFile(path,os.path.join(proj,"image",""),0)
		elif ext == ".lnx" :
			self.copyFile(path,os.path.join(proj,"scene",""),0)
		elif ext == ".ttf" :
			self.copyFile(path,os.path.join(proj,"font",""),0)
		elif ext == ".mp3" or ext == ".ogg" :
			self.copyFile(path,os.path.join(proj,"sound",""),0)
		elif ext == ".lua" :
			self.copyFile(path,os.path.join(proj,"module",""),0)
		else:
			self.copyFile(path,os.path.join(proj,"etc",""),0)
		return ext[1:]

	def copyFile(self,source,distDir,count):
		filename = os.path.basename(source)
		
		suffix = ""
		if count > 0 : 
			suffix = "_"+str(count)

		fname, ext = os.path.splitext(filename)
		dist = distDir + fname + suffix + ext

		if os.path.exists(dist) : 
			self.copyFile(source,distDir,count+1)
			return None

		shutil.copyfile(source, dist)

		return dist

class SoundPlayer(QObject):
	finished = Signal()
	    
	def __init__(self, parent = None):
		super(SoundPlayer, self).__init__(parent)
		self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
		self.mediaObject = Phonon.MediaObject(self)
		self.mediaObject.finished.connect(self.finished)
 
		Phonon.createPath(self.mediaObject, self.audioOutput)
 
	@Slot()
	def play(self):
		self.mediaObject.play()
 
	def playFile(self, file):
		self.mediaObject.stop()
		self.mediaObject.clearQueue()
		self.mediaObject.setCurrentSource(file)
		self.mediaObject.play()
 
	def stop(self):
		if self.isPlaying():
			self.mediaObject.stop()
			self.mediaObject.clearQueue()

	@Slot()
	def pause(self):
		self.mediaObject.pause()
 
	def isPlaying(self):
		return self.mediaObject.state() == Phonon.PlayingState

class AssetImage(QLabel):
	def __init__(self,src,parent=None):
		super(AssetImage,self).__init__(parent)

		self.setPixmap(QPixmap(src))

	def mouseReleaseEvent (self,event):
		AssetViewer().close()

class AssetViewer(Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not AssetViewer._instance:
			AssetViewer._instance = super(AssetViewer,cls).__new__(cls,*args,**kwargs)

		return AssetViewer._instance

	def __init__(self,src=None,parent=None):
		self.AssetMode = None
		if AssetViewer._isInit == False:
			super(AssetViewer,self).__init__(parent)
			self.setWindowTitle(unicode("리소스 뷰어","utf-8"))
		if src == None : 
			return 
		AssetViewer._isInit = True

		self.move(100,100)
		if hasattr(self,"sp") and self.sp :
			self.stopSound()
		self.sp = None

		self.AssetMode = 0
		fname, ext = os.path.splitext(src)
		if ext == ".png" or ext == ".jpg" : 
			self.AssetMode = 1
			self.path = src
		elif ext == ".mp3" or ext == ".ogg" : 
			self.AssetMode = 2
			self.path = src
		
		self.GUI()

	@LayoutGUI
	def GUI(self):
		if self.AssetMode == None : 
			return 

		self.Layout.clear()
		self.resize(QSize(0,0))

		if self.AssetMode == 1 : 
			img = self.Layout.addWidget(AssetImage(self.path,self))#self.Layout.img(self.path)
		elif self.AssetMode == 2 : 
			with self.Layout.VBox(5):
				self.Layout.label(os.path.basename(self.path))
				with self.Layout.HBox():
					self.Layout.button("Play",self.playSound)
					self.Layout.button("Stop",self.stopSound)
					self.Layout.button("Close",self.close)

		elif self.AssetMode == 0 :
			self.Layout.label(unicode("미리보기가 지원되지 않는 리소스입니다.","utf-8"))

	def playSound(self):
		self.stopSound()

		self.sp = SoundPlayer(self)
		self.sp.playFile(self.path)

	def stopSound(self):
		if self.sp : 
			self.sp.stop()
			self.sp = None

	def closeEvent(self,e):
		super(AssetViewer,self).closeEvent(e)
		self.stopSound()

		AssetViewer._instance = None
		AssetViewer._isInit   = False

class AssetLibraryWindow(Window):
	def sizeHint(self):
		return QSize(600, 0)

	#instance
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not AssetLibraryWindow._instance:
			AssetLibraryWindow._instance = super(AssetLibraryWindow,cls).__new__(cls,*args,**kwargs)

		return AssetLibraryWindow._instance

	def __init__(self,src=None,parent=None):
		if AssetLibraryWindow._isInit:
			return 
		AssetLibraryWindow._isInit = True
		
		super(AssetLibraryWindow,self).__init__(parent)
		self.setWindowTitle(unicode("프로젝트 파일","utf-8"))

		self.model = QFileSystemModel()

		self.explorer.setModel(self.model)
		self.explorer.doubleClicked.connect(self.doubleClicked)
		self.explorer.setColumnHidden(1, True)
		self.explorer.setColumnHidden(2, True)
		self.explorer.setColumnHidden(3, True)
		self.explorer.setContextMenuPolicy(Qt.CustomContextMenu);
		self.explorer.customContextMenuRequested.connect(self.contextMenu);
		self.watcher = None

		self.watcherOn = True

		self.images  = []
		self.scenes  = []
		self.audio   = []
		self.movie   = []
		self.fonts   = []
		self.modules = []

		self.resDirty = False

		self.updateTimer = QTimer(self)
		self.updateTimer.timeout.connect(self.updateCompileProj)

		self.close()
		self.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
		self.show()

		ProjectController().changed.connect(self.loadProject)

		#self.setMinimumWidth(600)
		#self.setMaximumWidth(600)

	def contextMenu(self,pos):
		index = self.explorer.indexAt(pos);
		path = self.model.filePath(index)
		menu = QMenu(self)
		cwd = self.model.rootPath()
		if len(path) > 0 : 
			menu.addAction(u"미리보기")
			menu.addSeparator()
			menu.addAction(u"이름 바꾸기")
			menu.addAction(u"삭제")
			menu.addSeparator()
		
		menu.addAction(u"폴더로 가기")
		menu.addAction(u"파일 가져오기")
		menu.addAction(u"폴더 생성")

		#pos.setY(pos.y()+20)
		a = menu.exec_(self.mapToGlobal(pos+QPoint(30,30)))
		if a:
			if a.text() == u"미리보기" : 
				self.openFile(path)
			elif a.text() == u"폴더로 가기" :
				targetUrl = QUrl.fromLocalFile(os.path.dirname(path))
				if targetUrl.path() != "":
					QDesktopServices.openUrl(targetUrl)
				else:
					QDesktopServices.openUrl("file:///"+cwd)
			elif a.text() == u"이름 바꾸기" :
				currentName = os.path.basename(path)
				
				if currentName == u"메인.lnx":
					QMessageBox.warning(self,u"피니엔진",u"메인.lnx 는 이름을 바꾸거나 삭제할 수 없습니다.")
					return

				currentPath = os.path.dirname(path)
				text,ok = QInputDialog.getText(self, u"파일명 > "+currentName,u"변경할 파일이름 : ")
				if text : 
					ext = os.path.splitext(text)[1]
					if len(ext) == 0 : 
						ext = os.path.splitext(path)[1]
						text += ext
					distName = os.path.join(currentPath,text)
					if os.path.exists(distName) : 
						QMessageBox.warning(self,u"피니엔진",u"이미 존재하는 파일명입니다.")
						return 

					os.rename(path,distName)
					QMessageBox.warning(self,u"피니엔진",u"파일명을 변경하였습니다.")

			elif a.text() == u"삭제" :
				currentName = os.path.basename(path)

				if currentName == u"메인.lnx":
					QMessageBox.warning(self,u"피니엔진",u"메인.lnx 는 이름을 바꾸거나 삭제할 수 없습니다.")
					return

				btn = QMessageBox.question(self, u"피니엔진", 
												 currentName+u"(을/를) 정말로 삭제하시겠습니까?\n삭제된 파일은 복원이 안됩니다.",
										   		 QMessageBox.Yes , QMessageBox.No )
				if btn == QMessageBox.Yes : 
					self.watcherOn = False
					self.watcher = None
					try:
						if os.path.isdir(path) : 
							shutil.rmtree(path)
						else : 
							os.remove(path)

						try:
							objPath = path
							objPath = objPath.replace(u"/scene/",u"/build/obj/scene/").replace(".lnx",".obj")
							os.remove(objPath)
						except Exception, e:
							print e
							pass
						QMessageBox.information(self,u"피니엔진",u"성공적으로 삭제했습니다.")
					except Exception, e:
						QMessageBox.warning(self,u"피니엔진",u"파일을 삭제하지 못했습니다.\n파일을 엑세스하고 있는 모든 프로그램을 종료 한 뒤 삭제해주세요.")
					self.watcherOn = True
					self.updateWatcher()

			elif a.text() == u"파일 가져오기" :
				srcpath,ext = QFileDialog.getOpenFileName(parent=self,caption="Select File")
				if srcpath : 
					self.open_dirs(self.explorer.moveFile(srcpath))
					QMessageBox.information(self,u"피니엔진",u"새로운 파일을 추가했습니다.")
			elif a.text() == u"폴더 생성" :
				text,ok = QInputDialog.getText(self, u"새로운 폴더 만들기",u"폴더이름을 정해주세요.")
				if ok and text:
					p = os.path.join(cwd,text)
					os.makedirs(p)
					QMessageBox.information(self,u"피니엔진",u"새로운 폴더를 만들었습니다.")

	@LayoutGUI
	def GUI(self):
		with self.Layout.HBox(1):
			with self.Layout.VBox(1) : 
				self.toggle_scene  = self.Layout.button(unicode("장면","utf-8"),self.Menu_Scene)#.setFixedSize(50,50)
				self.toggle_image  = self.Layout.button(unicode("이미지","utf-8"),self.Menu_Image)#.setFixedSize(50,50)
				self.toggle_sound  = self.Layout.button(unicode("사운드","utf-8"),self.Menu_Audio)#.setFixedSize(50,50)
				self.toggle_fonts  = self.Layout.button(unicode("폰트","utf-8"),self.Menu_Fonts)#.setFixedSize(50,50)
				self.toggle_module = self.Layout.button(unicode("모듈","utf-8"),self.Menu_Module)#.setFixedSize(50,50)
				self.toggle_etc    = self.Layout.button(unicode("기타","utf-8"),self.Menu_ETC)#.setFixedSize(50,50)
				self.Layout.spacer()
			self.explorer = self.Layout.addWidget(FileListView(self))

	def open_dirs(self,ext):
		if ext == "png" or ext == "jpg" : 
			self.Menu_Image()
		elif ext == "lnx" :
			self.Menu_Scene()
		elif ext == "ttf" :
			self.Menu_Fonts()
		elif ext == "mp3" or ext == "ogg" :
			self.Menu_Audio()
		elif ext == "lua" :
			self.Menu_Module()
		else:
			self.Menu_ETC()

	def toogle_all_enable(self):
		self.toggle_scene.setEnabled(True)
		self.toggle_image.setEnabled(True)
		self.toggle_sound.setEnabled(True)
		self.toggle_fonts.setEnabled(True)
		self.toggle_module.setEnabled(True)
		self.toggle_etc.setEnabled(True)
	def Menu_Image(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"image")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/image"))
		self.toggle_image.setEnabled(False)
	def Menu_Scene(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"scene")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/scene"))
		self.toggle_scene.setEnabled(False)
	def Menu_Audio(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"sound")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/sound"))
		self.toggle_sound.setEnabled(False)
	def Menu_Fonts(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"font")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/font"))
		self.toggle_fonts.setEnabled(False)
	def Menu_Module(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"module")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/module"))
		self.toggle_module.setEnabled(False)
	def Menu_ETC(self):
		self.toogle_all_enable()
		self.model.mkdir(self.model.setRootPath(ProjectController().path),"etc")
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path+"/etc"))
		self.toggle_etc.setEnabled(False)

	def openFile(self,path):
		print path
		fi = QFileInfo(path)
		if not fi.isDir() : 
			ext = fi.suffix()
			filePath = fi.filePath()
			if ext == "lnx" :
				SceneListController.getInstance().Open(filePath)
			elif ext == "png" or ext == "jpg":
				AssetViewer(filePath)
			elif ext == "mp3" or ext == "ogg" :
				AssetViewer(filePath)
			elif ext == "lua":
				filePath = filePath.encode(locale.getpreferredencoding())
				os.system('start "" "'+filePath+'"')
				#QDesktopServices.openUrl(QUrl(filePath))
			else :  
				QDesktopServices.openUrl(QUrl(filePath))

	def doubleClicked(self,modelIndex):
		self.openFile(self.model.filePath(modelIndex))

	def layerFactory(self,data):
		self.Layout.label(data)
		return 30

	def loadProject(self,path):
		self.Menu_Scene()
		#self.explorer.setRootIndex(self.model.setRootPath(ProjectController().path))
		
		mainScene = ProjectController().path+unicode("/scene/메인.lnx","utf-8")
		inst = ProjectController()

		with Settings("PROJECT_USER_SETTING") :
			with Settings(inst.path) :
				lastScene = Settings()["lastSceneLoaded"] if Settings()["lastSceneLoaded"] else mainScene
				mainScene = ProjectController().path+"/"+lastScene
		
		if not os.path.exists(mainScene) : 
			mainScene = ProjectController().path+unicode("/scene/메인.lnx","utf-8")

			if not os.path.exists(mainScene) :
				try:
					os.makedirs(os.path.dirname(mainScene))
				except Exception, e:
					pass
				f = open(mainScene,"w")
				f.close()

		SceneListController.getInstance().Open(mainScene)

		self.updateWatcher()

	def updateWatcher(self,path=""):
		print self.watcherOn,path
		if self.watcherOn == False :
			return

		self.images = []
		self.scenes = []
		self.audio  = []
		self.movie  = []
		self.fonts  = []
		self.modules= []

		GraphicsProtocolObject().ImgClear()
		ScriptGraphicsProtocol().XLSXClear()
	
		self.watcher = None
		self.watcher = QFileSystemWatcher()
		for base, dirs, names in os.walk(ProjectController().path):
			for _dir in dirs:
				self.watcher.addPath(os.path.join(base, _dir))
			for name in names:
				path = os.path.join(base, name)
				ext = os.path.splitext(path)[1]
				ext = ext.lower()
				
				if ext == ".png" or ext == ".jpg":
					if path.startswith(ProjectController().path + QDir.separator() + "image") :
						self.images.append(path)
				elif ext == ".lnx":
					if path.startswith(ProjectController().path + QDir.separator() + "scene") :
						self.scenes.append(path)
				elif ext == ".lua":
					if path.startswith(ProjectController().path + QDir.separator() + "module") :
						self.modules.append(path)
				elif ext == ".mp3" or ext == ".ogg":
					if path.startswith(ProjectController().path + QDir.separator() + "sound") :
						self.audio.append(path)
				elif ext == ".avi" : 
					if path.startswith(ProjectController().path + QDir.separator() + "etc") :
						self.movie.append(path)
				elif ext == ".ttf" : 
					if path.startswith(ProjectController().path + QDir.separator() + "font") :
						FontManager().AddFont(os.path.splitext(name)[0],path)

		self.watcher.directoryChanged.connect(self.directoryChanged)
		self.watcher.fileChanged.connect(self.fileChanged)

		self.resDirty = True

		self.updateTimer.stop()
		self.updateTimer.start(1000)

	def updateCompileProj(self):
		if self.resDirty : 
			ProjectController().compileProj()
			self.resDirty = False
		self.updateTimer.stop()

	def directoryChanged(self,path):
		if self.watcherOn == False :
			return ;
		if path.startswith(ProjectController().path+"\\build") : 
			return ;
		print "directoryChanged",path
		self.updateWatcher(path)

	def fileChanged(self,path):
		#print path
		pass#print "fileChanged",path