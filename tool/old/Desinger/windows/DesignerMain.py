import os
import sys

from PySide.QtGui import *
from PySide.QtCore import *

from ModuleRefresher import ModuleRefresher

from controller.SceneController import *

from graphics.graphicsView import *

from uic.Ui_DesignerMain import Ui_DesignerMain

class DesignerMain(QMainWindow,Ui_DesignerMain):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not DesignerMain._instance:
			DesignerMain._instance = super(DesignerMain,cls).__new__(cls,*args,**kwargs)

		return DesignerMain._instance

	def __init__(self,path=None,parent=None):
		if DesignerMain._isInit:
			return
		super(DesignerMain,self).__init__(parent)
		DesignerMain._isInit = True
		self.setupUi(self)

		self.pc = ProjectController.getInstance()
		self.sc = SceneController.getInstance()
		self.sl = SceneController.SceneListModel.getInstance()
		self.lc = LayerController.getInstance()

		self.projectPath = path
		self.moduleRefresher = ModuleRefresher(os.path.join(os.curdir,"docks"))

		self.compositionDocks()

		#connect
		self.browser.openScene.connect(self.OnOpenScene)
		self.sc.focusChanged.connect(self.OnSceneFocusChanged)
		self.sc.sceneClosed.connect(self.OnTabClosed)
		self.ui_TabWidget.currentChanged.connect(self.uicall_TabChanged)


		self.newMenuBtn.triggered.connect(self.uicall_newMenuBtnTriggered)
		self.openMenuBtn.triggered.connect(self.uicall_openMenuBtnTriggered)
		self.saveMenuBtn.triggered.connect(self.uicall_saveMenuBtnTriggered)
		self.saveAsMenuBtn.triggered.connect(self.uicall_saveAsMenuBtnTriggered)
		self.exitMenuBtn.triggered.connect(self.uicall_exitMenuBtnTriggered)

		self.ui_TabWidget.tabCloseRequested.connect(self.uicall_tabCloseRequested)
		self.sl.sceneRenamed.connect(self.OnSceneRenamed)

		self.sc.sceneWatcher.fileChanged.connect(self.OnExternalFileRenamed)

	def compositionDocks(self):
		# self.addDockWidget(Qt.LeftDockWidgetArea,self.layerList);
		# self.addDockWidget(Qt.LeftDockWidgetArea,self.browser);

		# self.tabifyDockWidget(self.browser,self.layerList);

		# self.addDockWidget(Qt.RightDockWidgetArea,self.property);
		pass

	def uicall_tabCloseRequested(self,index):
		view = self.ui_TabWidget.widget(index)
		self.sc.closeScene(view.sceneModel,index)

	def OnTabClosed(self,sceneModel,tabIndex):
		self.ui_TabWidget.removeTab(tabIndex)

	def uicall_TabChanged(self,index):	
		self.sc.focusScene(self.ui_TabWidget.tabText(index))

	def OnOpenScene(self,filePath):
		self.sc.openScene(filePath)

	def OnSceneFocusChanged(self,sceneList,scene):
		view = scene.property("tabView")
		if not view:
			view = DesignerView(self.ui_TabWidget,scene)
			scene.setProperty("tabView",view)
			self.ui_TabWidget.addTab(view,scene.name)

		self.ui_TabWidget.setCurrentWidget(view)

	def uicall_newMenuBtnTriggered(self):
		print "call OnNewMenuBtnTriggered(self)!!"

		scenePath = os.path.join(self.projectPath,"scene")
		if not os.path.isdir(scenePath):
			os.mkdir(scenePath)

		filePath,_ = QFileDialog.getSaveFileName(parent=self,dir=scenePath,filter='scenes (*.scene)')
		if len(filePath) > 0:
			sceneName = QtCore.QFileInfo(filePath).completeBaseName()

			newScene = SceneController.SceneModel(name=sceneName,filePath=filePath)
			newScene.saveScene(filePath)

			self.sc.openScene(filePath)

	def uicall_openMenuBtnTriggered(self):
		print "call OnOpenMenuBtnTriggered(self)!!"

		fileNames,_ = QFileDialog.getOpenFileNames(parent = self,dir = self.projectPath,filter='scenes (*.scene)')

		for fileName in fileNames:
			self.sc.openScene(fileName)

	def uicall_saveMenuBtnTriggered(self):
		print "call OnSaveMenuBtnTriggered(self)!!"
		currentScene = LayerController.getInstance().currentScene
		if currentScene:
			scenePath = currentScene.filePath
			if len(scenePath) > 0 and os.path.isfile(scenePath):
				currentScene.saveScene(scenePath)
			else:
				self.uicall_saveAsMenuBtnTriggered()

	def uicall_saveAsMenuBtnTriggered(self):
		print "call OnSaveAsMenuBtnTriggered(self)!!"
		currentScene = LayerController.getInstance().currentScene
		scenePath    = os.path.join(self.projectPath,"scene")

		if not os.path.isdir(scenePath):
			os.mkdir(scenePath)
		if currentScene:
			openDir = currentScene.filePath if currentScene.filePath else scenePath
			filePath,_ = QFileDialog.getSaveFileName(parent=self,dir=openDir,filter='scenes (*.scene)')
			currentScene.saveScene(filePath)

	def uicall_exitMenuBtnTriggered(self):
		print "call OnExitMenuBtnTriggered(self)!!"
		QApplication.instance().exit()

	def OnSceneRenamed(self,oldBaseName,newBaseName):
		for index in range(self.ui_TabWidget.count()):
			if self.ui_TabWidget.tabText(index) == oldBaseName:
				self.ui_TabWidget.setTabText(index,newBaseName)

	def OnExternalFileRenamed(self,path):
		print path