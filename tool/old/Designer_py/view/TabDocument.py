from Noriter.UI.Layout import *
from Noriter.UI.TabWidget import TabWidget
from Noriter.views.NoriterMainWindow import * 

from controller.SceneListController import SceneListController
from graphics.GraphicsView import *

class TabDocument(TabWidget):
	def __init__(self,parent=None):
		super(TabDocument,self).__init__(parent)

		self.slc = SceneListController.getInstance();
		self.slc.SceneOpen.connect(self.openScene)
		self.slc.SceneLoaded.connect(self.loadScene)

	def loadScene(self,scene):
		with self.tab(QtCore.QFileInfo(scene.path).baseName()) as tab :
			tab.path = scene.path
			self.Layout.addWidget( DesignerView(self,scene) )

	def openScene(self,scene):
		for i in range(0,self.count()):
			self.widget(i)

	def GUI(self):
		pass

def start():
	m = NoriterMain()
	m.SetMain(TabDocument(m))