from Noriter.UI.Layout import *
from Noriter.UI.Widget import Widget
from Noriter.views.NoriterMainWindow import * 

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController
from graphics.GraphicsView import *

from view.OutputWindow import OutputWindow

class SceneDocument(Widget):
	def __init__(self,parent=None):
		self.view = None
		super(SceneDocument,self).__init__(parent)

		self.sceneListCtrl = SceneListController.getInstance();
		self.sceneListCtrl.SceneOpen.connect(self.openScene)
		self.sceneListCtrl.SceneLoaded.connect(self.loadScene)

		self.sceneCtrl = None

		OutputWindow().noticed.connect(self.noticeLog)
		
	def noticeLog(self,text,color):
		if self.sceneCtrl : 
			self.sceneCtrl.view.log(text,color)

	def loadScene(self,scene):
		pass 

	def openScene(self,scene):
		if self.view == None:
			self.GUI()
		
		if self.sceneCtrl != scene : 
			self.sceneCtrl = scene
			scene.view = self.view
		
	@LayoutGUI
	def GUI(self):
		if self.view == None:
			self.view = self.Layout.addWidget(DesignerView(self))
