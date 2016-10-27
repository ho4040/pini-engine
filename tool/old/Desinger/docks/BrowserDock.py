# -*- coding: utf-8 -*-

import os
import shutil
from windows.DesignerMain import DesignerMain

from PySide.QtGui import *
from PySide.QtCore import *

from uic.Ui_BrowserDock import Ui_BrowserDock
from controller.ProjectController import *
from controller.SceneController import *

from utility.QtUtils import *

class BrowserDock(QDockWidget,Ui_BrowserDock):
	contextMenu = ["Menu","Open",0,["Create","Script","Scene",0,"Folder"],"Remove","Rename",0,"Show in Explorer"]

	#signal
	selectedContextMenu = Signal(unicode,unicode)
	openScene = Signal(unicode)

	def __init__(self,parent=None):
		super(BrowserDock,self).__init__(parent)
		self.setupUi(self)

		self.model = QFileSystemModel()
		self.model.fileRenamed.connect(self.OnFileRenamed)

		self.ui_Explorer.setModel(self.model)
		self.ui_Explorer.setRootIndex(self.model.setRootPath(ProjectController.getInstance().path))

		self.ui_Explorer.setColumnHidden(1, True)
		self.ui_Explorer.setColumnHidden(2, True)
		self.ui_Explorer.setColumnHidden(3, True)

		self.ui_Explorer.customContextMenuRequested.connect(self.OnExplorerContextMenu)
		self.ui_Explorer.doubleClicked.connect(self.OnOpenFile)
		self.selectedContextMenu.connect(self.OnSelectExplorerMenu)

	def createNewScriptFile(self,path):
		fileName,ok = QInputDialog.getText(self,self.trUtf8("새로운 스크립"),self.trUtf8("새로운 스크립트의 파일이름을 입력해주세요."),QLineEdit.Normal,"")
		if ok :
			if ('.lua' in fileName) == False :
				fileName += ".lua"

			filePath = os.path.join(path,fileName)
			if QFile.exists(filePath) :
				QMessageBox.warning(self,"Designer",self.trUtf8("파일이 존재합니다."))
				return

			fp = open(filePath,"w")
			fp.write("")
			fp.close()

	def createNewScene(self,path):
		fileName,ok = QInputDialog.getText(self,self.trUtf8("새로운 화면"),self.trUtf8("새로운 화면의 파일이름을 입력해주세요."),QLineEdit.Normal,"")
		if ok :
			if ('.scene' in fileName) == False :
				fileName += ".scene"

			filePath = os.path.join(path,fileName)
			if QFile.exists(filePath) :
				QMessageBox.warning(self,"Designer",self.trUtf8("파일이 존재합니다."))
				return

			fp = open(filePath,"w")
			fp.write("default scene data")
			fp.close()

	def createFolder(self,path):
		fileName,ok = QInputDialog.getText(self,self.trUtf8("새로운 폴더"),self.trUtf8("새로운 화면의 폴더이름을 입력해주세요."),QLineEdit.Normal,"")
		if ok :
			filePath = os.path.join(path,fileName)
			if QFile.exists(filePath) :
				QMessageBox.warning(self,"Designer",self.trUtf8("폴더가 존재합니다."))
				return

			os.makedirs(filePath)

	def RemoveFile(self,path):
		q = QMessageBox.question(self,self.trUtf8("파일 삭제"),self.trUtf8("해당 파일을 정말로 삭제하시겠습니까?"),QMessageBox.Cancel,QMessageBox.Yes)
		if q == QMessageBox.Yes:
			for modelIndex in self.ui_Explorer.selectedIndexes():
				self.ui_Explorer.model().remove(modelIndex)

	def Rename(self,path):
		fileInfo = QFileInfo(path)
		if fileInfo.isDir() or fileInfo.isFile() :
			fileName,ok = QInputDialog.getText(self,self.trUtf8("새로운 이름"),self.trUtf8("파일의 새로운 이름을 입력해주세요."),QLineEdit.Normal,fileInfo.fileName())
			if ok :
				filePath = os.path.join(fileInfo.path(),fileName)
				if QFile.exists(filePath) :
					QMessageBox.warning(self,"Designer",self.trUtf8("파일이 존재합니다."))
					return
				os.rename(path,filePath)

				LayerController.getInstance().renameCurrentSceneName(path,filePath)
				SceneController.getInstance().renameScene(path,filePath)

	def ShowInExplorer(self,path):
		fileInfo = QFileInfo(path)
		QDesktopServices.openUrl(QUrl.fromLocalFile(fileInfo.path()))

	def FileOpen(self,path):
		fileInfo = QFileInfo(path)
		if ".lua" in path :
			QDesktopServices.openUrl(QUrl.fromLocalFile(path))
		elif ".scene" in path :
			self.openScene.emit(path)
		else:
			self.ShowInExplorer(path)

	def OnSelectExplorerMenu(self,selected,path):
		if selected == "Script" : 
			self.createNewScriptFile(path)
		elif selected == "Scene" : 
			self.createNewScene(path)
		elif selected == "Folder" : 
			self.createFolder(path)
		elif selected == "Remove" : 
			self.RemoveFile(path)
		elif selected == "Rename" : 
			self.Rename(path)
		elif selected == "Show in Explorer" : 
			self.ShowInExplorer(path)		
		elif selected == "Open" : 
			self.FileOpen(path)			

	def OnExplorerContextMenu(self,pos):
		menu = QtUtils.ContextMenu(BrowserDock.contextMenu,self)
		action = menu.exec_(self.ui_Explorer.mapToGlobal(pos+QPoint(0,20)))		

		if action :
			self.selectedContextMenu.emit(action.text(),self.model.filePath(self.ui_Explorer.currentIndex()))

	def OnOpenFile(self,index):
		filePath = self.model.filePath(index)
		if QFileInfo(filePath).isDir() == False :
			self.FileOpen(filePath)

	def OnFileRenamed(self,path,oldName,newName):
		print path
		print oldName
		print newName

def start():
	dMain = DesignerMain()
	browser = BrowserDock(dMain)
	if hasattr(dMain,"browser") and dMain.browser:
		dMain.removeDockWidget(dMain.browser)
	dMain.browser = browser
	dMain.addDockWidget(QtCore.Qt.LeftDockWidgetArea,browser)

	existBrowser   = hasattr(dMain,"browser") and dMain.browser
	existLayerList = hasattr(dMain,"layerList") and dMain.layerList
	if existBrowser and existLayerList:
		dMain.tabifyDockWidget(dMain.browser,dMain.layerList)

