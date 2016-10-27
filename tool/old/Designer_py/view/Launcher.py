# -*- coding: utf-8 -*-
from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import *

from controller.ProjectController import ProjectController


class LauncherView(Window):
	def __init__(self):
		super(LauncherView,self).__init__()
		self.resize(400,350)

		self.projects = []
		self.list.data = self.projects

		self._layout.setContentsMargins(5, 5, 5, 5)

		if Settings()["workspace"] is None :
			document = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DocumentsLocation)

			workspace = str(os.path.join(document,"noriter"))
			self.setWorkspace(workspace)

		self.setWorkspace(Settings()["workspace"])

		self.list.doubleClicked.connect(self.selectProject)
		self.list.changed.connect(self.changedSelected)

		self.selectedIndices = []

	@LayoutGUI
	def GUI(self):
		with Layout.HBox(5):
			self.Layout.label("workspace")
			self.workspace = self.Layout.input(Settings()["workspace"],None)
			self.Layout.button("...",self.findWorkspace)

		with Layout.HBox():
			self.list = self.Layout.listbox(self.projectFactory,[])

			with Layout.VBox():
				self.Layout.button("Select",self.onClickedSelectProject)
				self.Layout.button("New Project",self.newProject)
				self.Layout.spacer()
				self.Layout.button("close",self.newProject)

	def findWorkspace(self):
		path = QtGui.QFileDialog.getExistingDirectory(parent=self,caption="Workspace",dir=Settings()["workspace"])
		if path : self.setWorkspace(path)

	def setWorkspace(self,path):
		QtCore.QDir().mkpath(path)
		Settings()["workspace"] = path

		self.workspace.setText( path )
		self.loadingWorkspace( path )

	def loadingWorkspace(self,path):
		projs = []
		for dirname in os.listdir(path):
			if os.path.exists(os.path.join(path,dirname,"PROJ")):
				projs.append(dirname)
		self.list.data = projs

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
		ProjectController.getInstance().path = os.path.join(Settings()["workspace"],self.list.data[idx])
		NoriterMain().show()
		self.close()

	def changedSelected(self,indices):
		if len(indices) <= 0:
			self.selectedIndices = []
			return
		self.selectedIndices = indices

	def newProject(self):
		name = newProject(self).exec_()
		if len(name) > 0 :
			self.loadingWorkspace()

class newProject(ModalWindow):
	_Project_Default_Dir_ = ("build","resource","script","scene","symbol")
	def __init__(self,parent):
		super(newProject,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.project = ""

	@LayoutGUI
	def GUI(self):
		with Layout.HBox():
			self.Layout.label(self.trUtf8("작업폴더 : ")+Settings()["workspace"])

		with Layout.HBox(5):
			self.Layout.label("Name")
			self.Layout.input("",self.projectName)

		with Layout.HBox():
			self.Layout.button("cancel",self.close)
			self.Layout.spacer()
			self.Layout.button("make",self.makeProject)

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
			os.makedirs(fullpath)

			for dir in newProject._Project_Default_Dir_:
				os.makedirs(os.path.join(fullpath,dir))

			proj = open(os.path.join(fullpath,"PROJ"),"w")
			proj.write("")
			proj.close()

			QtGui.QMessageBox.information(self,"Noriter",self.trUtf8("정상적으로 프로젝트가 생성되었습니다."))

			self.close()
		else:
			QtGui.QMessageBox.warning(self,"Noriter",self.trUtf8("작업폴더에 동일한 프로젝트명의 폴더가 이미 있습니다.\n프로젝트명을 변경해주세요."))


def start():
	LauncherView()
