# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.UI.Widget import Widget 

from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import *

from controller.ProjectController import ProjectController
from command.ScriptCommands import ScriptGraphicsProtocol

import shutil
import glob
from config import *
import locale

class LauncherView(Widget):
	def __init__(self,parent=None):
		super(LauncherView,self).__init__(parent)
		self.GUI()
		
		self.setWindowTitle(u"프로젝트 선택")
		self.resize(400,350)

		self.onClose = None
		self.sampleDir = None

		#
		self.close()
		self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint )
		self.show()

		self.projects = []
		self.list.data = self.projects

		self._layout.setContentsMargins(5, 5, 5, 5)

		try:
			if config.__RELEASE__ == False : 
				self.sampleDir = os.path.join("..","sample_proj","sample")
			else:
				self.sampleDir = os.path.join(".","sample")
			self.sampleDir = unicode(self.sampleDir)
			self.find_all_proj(self.sampleDir,self.samplelist)
		except Exception, e:
			print e
		self.samplelist.doubleClicked.connect(self.selectExample)

		if Settings()["workspace"] is None : 
			document = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DocumentsLocation)

			workspace = os.path.join(document,"pini_project")
			self.setWorkspace(workspace)

		self.setWorkspace(Settings()["workspace"])

		self.list.doubleClicked.connect(self.selectProject)
		self.list.changed.connect(self.changedSelected)

		self.selectedIndices = []

	@LayoutGUI
	def GUI(self):
		self.tab = self.Layout.tab()
		print self.tab
		with self.tab.tab(u"내 프로젝트") : 
			with Layout.HBox(5):
				self.Layout.label(u"작업폴더")
				self.workspace = self.Layout.input(Settings()["workspace"],None)
				self.Layout.button("...",self.findWorkspace).setFixedHeight(20)

			self.Layout.gap(10)

			with Layout.HBox():
				self.list = self.Layout.listbox(self.projectFactory,[])

				self.Layout.gap(5)

				with Layout.VBox():
					self.Layout.button(u"프로젝트 실행",self.onClickedSelectProject)
					self.Layout.gap(2)
					self.Layout.button(u"프로젝트 생성",self.newProject)
					self.Layout.gap(2)
					self.Layout.button(u"프로젝트 삭제",self.removeProject)
					
					self.Layout.spacer()

					self.Layout.button(u"공식사이트 가기",self.gotoSite)
					self.Layout.gap(2)
					self.Layout.button(u"닫기",self.close)

		with self.tab.tab(u"예제") : 
			self.samplelist = self.Layout.listbox(self.projectFactory,[])

	def findWorkspace(self):
		path = QtGui.QFileDialog.getExistingDirectory(parent=self,caption="Workspace",dir=Settings()["workspace"])
		if path : self.setWorkspace(path)

	def setWorkspace(self,path):
		absPath = QDir(path).absolutePath()
		absSampleDir = QDir(self.sampleDir).absolutePath()

		if absPath == absSampleDir:
			QtGui.QMessageBox.warning(self,u"피니엔진",u"샘플 폴더는 작업폴더로 지정할 수 없습니다.")
			self.findWorkspace()
			return

		QtCore.QDir().mkpath(path)
		Settings()["workspace"] = path

		self.workspace.setText( path )
		self.loadingWorkspace( path )

	def loadingWorkspace(self,path):
		self.find_all_proj(path,self.list)

	def find_all_proj(self,path,_list):
		print "find_all_proj",path
		projs = []
		for dirname in os.listdir(path):
			fullpath = os.path.join(path,dirname,"PROJ")
			if os.path.exists(fullpath):
				projs.append(dirname)
		if len(projs) == 0 : 
			projs = [u"생성된 프로젝트가 없습니다."]
		_list.data = projs

	def projectFactory(self,data):
		self.Layout.label(data)
		return 20

	def onClickedSelectProject(self):
		if len(self.selectedIndices) > 0:
			idx = self.selectedIndices[0].data
			if not idx in self.list.data:
				return
			idx = self.list.data.index(idx)
			self.selectProject(idx)

	def selectProject(self,idx):
		if u"생성된 프로젝트가 없습니다." == self.list.data[idx] :
			return;
			
		ProjectController().path = os.path.join(Settings()["workspace"],self.list.data[idx])
		ScriptGraphicsProtocol().luaInit()
		NoriterMain().show()
		self.close()

	def selectExample(self,idx):
		try:
			example_name = self.samplelist.data[idx]

			os.path.join(self.sampleDir,example_name)
			text = u'"'+example_name+u'"예제를 작업폴더에 복사하시겠습니까?'
			btn = QtGui.QMessageBox.question(self, u"피니엔진",text, QtGui.QMessageBox.Yes , QtGui.QMessageBox.No )
			
			if btn == QtGui.QMessageBox.Yes : 
				ret = exampleCopyer(self.sampleDir,example_name,self).exec_()
				if ret : 
					self.loadingWorkspace(Settings()["workspace"])
					self.tab.focus(0)
		except Exception, e:
			print e

	def changedSelected(self,indices):
		if len(indices) <= 0:
			self.selectedIndices = []
			return
		self.selectedIndices = indices

	def newProject(self):
		name = newProject(self).exec_()
		if len(name) > 0 :
			self.loadingWorkspace(Settings()["workspace"])

	def removeProject(self):
		if len(self.selectedIndices) > 0:
			idx = self.selectedIndices[0].data
			if not idx in self.list.data:
				return
			btn = QtGui.QMessageBox.question(self, u"피니엔진", 
											 idx+u"(을/를) 정말로 삭제하시겠습니까?\n프로젝트 삭제는 복원이 안됩니다.",
									   		 QtGui.QMessageBox.Yes , QtGui.QMessageBox.No )
			if btn == QtGui.QMessageBox.Yes : 
				idx = self.list.data.index(idx)
				fullpath = os.path.join(Settings()["workspace"],self.list.data[idx])
				if ProjectController().path == fullpath : 
					QtGui.QMessageBox.warning(self,u"피니엔진",u"현재 실행 중인 프로젝트는 삭제가 불가능합니다. 엔진을 완전 종료 한 뒤 삭제해주시기바랍니다.")
					return 
				try:
					shutil.rmtree(fullpath)
					QtGui.QMessageBox.information(self,u"피니엔진",u"성공적으로 삭제했습니다.")
				except Exception, e:
					QtGui.QMessageBox.warning(self,u"피니엔진",u"프로젝트를 완전히 삭제하지 못했습니다. 프로젝트를 엑세스하고 있는 모든 프로그램을 종료 한 뒤 삭제해주세요.")
				self.loadingWorkspace(Settings()["workspace"])

	def gotoSite(self):
		QtGui.QDesktopServices.openUrl("http://piniengine.com");

	def closeEvent(self,e):
		super(LauncherView,self).closeEvent(e)
		if self.onClose : 
			self.onClose()

class exampleCopyer(ModalWindow):
	def __init__(self,_dir,name,parent):
		self.origin = name
		self.name = name
		self.dir = _dir

		super(exampleCopyer,self).__init__(parent)

		self.ret = False

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

	@LayoutGUI
	def GUI(self):
		with Layout.HBox():
			self.Layout.label(u"작업폴더 : "+Settings()["workspace"])

		with Layout.HBox(5):
			self.Layout.label(u"프로젝트 이름")
			self.Layout.input(self.name,self.projectName)

		with Layout.HBox():
			self.Layout.spacer()
			self.Layout.button(u"복사",self.useExample)
			self.Layout.button(u"취소",self.close)
	
	def projectName(self,text):
		self.name = text

	def useExample(self):
		dist = os.path.join(Settings()["workspace"],self.name)
		source = os.path.join(self.dir,self.origin)
		
		if not os.path.isdir(dist) :
			print source,dist
			shutil.copytree(source,dist)
			QtGui.QMessageBox.information(self,"Noriter",u"정상적으로 프로젝트가 생성되었습니다.")
			self.ret = True
			self.close()
		else:
			QtGui.QMessageBox.warning(self,"Noriter",u"작업폴더에 동일한 프로젝트명의 폴더가 이미 있습니다.\n프로젝트명을 변경해주세요.")

	def exec_(self):
		super(exampleCopyer,self).exec_()
		return self.ret

class newProject(ModalWindow):
	def __init__(self,parent):
		super(newProject,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.project = ""

	@LayoutGUI
	def GUI(self):
		with Layout.HBox():
			self.Layout.label(u"작업폴더 : "+Settings()["workspace"])

		with Layout.HBox(5):
			self.Layout.label(u"프로젝트 이름")
			self.Layout.input("",self.projectName)

		with Layout.HBox():
			self.Layout.spacer()
			self.Layout.button(u"생성",self.makeProject)
			self.Layout.button(u"취소",self.close)

	def exec_(self):
		super(newProject,self).exec_()
		return self.project

	def projectName(self,text):
		self.project = text

	def makeProject(self):
		if len(self.project) == 0 :
			return

		fullpath = os.path.join(Settings()["workspace"],self.project)
		if not os.path.exists(fullpath):
			
			DEFAULT_FILES = u"resource/proj_default"
			shutil.copytree(DEFAULT_FILES,fullpath)
			'''
			for root, dirs, files in os.walk(DEFAULT_FILES, topdown=False):
				for name in files:
					path = os.path.join(root, name).replace("\\","/")
					dist = fullpath+path.replace(DEFAULT_FILES,"")

					if os.path.isdir(os.path.dirname(dist)) == False :
						os.makedirs(os.path.dirname(dist))

					fr = open(path, 'rb')
					fs = open(dist, 'wb')

					fs.write(fr.read())

					fr.close()
					fs.close()

				for name in dirs:
					path = os.path.join(root, name).replace("\\","/")
					dist = fullpath+path.replace(DEFAULT_FILES,"")
					if os.path.isdir(dist) == False :
						os.makedirs(dist)
			'''
			for root, dirs, files in os.walk(fullpath, topdown=False):
				for name in files:
					path = os.path.join(root, name).replace("\\","/")
					if name == "TMP" : 
						os.remove(path)

			QtGui.QMessageBox.information(self,"Noriter",u"정상적으로 프로젝트가 생성되었습니다.")

			self.close()
		else:
			QtGui.QMessageBox.warning(self,"Noriter",u"작업폴더에 동일한 프로젝트명의 폴더가 이미 있습니다.\n프로젝트명을 변경해주세요.")
