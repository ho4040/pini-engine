# -*- coding: utf-8 -*-
from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

class BrowserWindow(Window):
	def __init__(self,parent=None):
		super(BrowserWindow,self).__init__(parent)
		self.setWindowTitle("browser")

		self.model = QtGui.QFileSystemModel()

		self.explorer.setModel(self.model)

		self.explorer.setColumnHidden(1, True)
		self.explorer.setColumnHidden(2, True)
		self.explorer.setColumnHidden(3, True)
		self.explorer.doubleClicked.connect(self.doubleClicked)

		ProjectController.getInstance().changed.connect(self.loadScene)

	@LayoutGUI
	def GUI(self):
		#s = self.Layout.splitter(True)
		#with s.split():
		#	self.explorer = self.Layout.addWidget(QtGui.QTreeView(self))
		#with s.split():
		#	self.folder	  = self.Layout.listbox(self.layerFactory,[])
		self.explorer = self.Layout.addWidget(QtGui.QTreeView(self))
		
	def layerFactory(self,data):
		self.Layout.label(data)
		return 30

	def OnFileRenamed(self,rem):
		pass

	def doubleClicked(self,modelIndex):
		fi = QFileInfo(self.model.filePath(modelIndex))
		if not fi.isDir() : 
			if fi.suffix() == "scene" : 
				SceneListController.getInstance().Open(fi.filePath())

	def loadScene(self,path):
		self.explorer.setRootIndex(self.model.setRootPath(ProjectController.getInstance().path))

def start():
	m = NoriterMain()
	m.Dock(NoriterMain.DOCK_BOTTOM,BrowserWindow(m))