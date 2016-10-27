# -*- coding: utf-8 -*-
from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import *

from controller.ComponentController import ComponentController
from controller.SceneListController import SceneListController

class LayerWindow(Window):
	def __init__(self,parent=None):
		super(LayerWindow,self).__init__(parent)
		self.setWindowTitle("layers")

		self.sceneCtrl = None
		self.objList = []

		self.sceneListCtrl = SceneListController.getInstance();
		self.sceneListCtrl.SceneOpen.connect(self.loadScene)

		self.list.changed.connect(self.changedSelected)
		ComponentController.getInstance().componentModify.connect(self.componentModify)

	@LayoutGUI
	def GUI(self):
		self.list = self.Layout.listbox(self.layerFactory,[])
		self.Layout.button("Add Object",self.AddObject)
		self.Layout.button("Remove Object",self.RemoveObject)
	
	def componentModify(self,objModel,idx,new,old):
		if objModel in self.objList:
			if "name" in new :
				objModel.components[idx].data["name"] = new["name"]
				self.updateList()

	def changedSelected(self,indices):
		s = []
		for v in indices:
			s.append( v.model )
		self.sceneCtrl.layerCtrl.SetSelectObjects( s )

	def layerFactory(self,model):
		transform = model.components[0].data
		self.Layout.label(transform['name'])
		self.Layout.widget.model = model
		return 30

	def updateList(self):
		self.list.data = self.objList

	def AddObject(self):
		self.sceneCtrl.layerCtrl.New()

	def RemoveObject(self):
		pass

	def OnAddObject(self,objModel):
		self.objList.append(objModel);
		self.updateList()

	def OnRemoveObject(self,objModel):
		self.updateList()

	def OnSelectObject(self,objModels):
		arr = []
		for v in objModels:
			arr.append( self.objList.index(v) )

		self.list.changed.disconnect(self.changedSelected)
		self.list.selectIndices(arr)
		self.list.changed.connect(self.changedSelected)

	def loadScene(self,path):
		if self.sceneCtrl : 
			self.sceneCtrl.layerCtrl.objectAdded.disconnect(self.OnAddObject)
			self.sceneCtrl.layerCtrl.objectRemoved.disconnect(self.OnRemoveObject)
			self.sceneCtrl.layerCtrl.objectSelected.disconnect(self.OnSelectObject)

		self.sceneCtrl = self.sceneListCtrl.Now()
		self.sceneCtrl.layerCtrl.objectAdded.connect(self.OnAddObject)
		self.sceneCtrl.layerCtrl.objectRemoved.connect(self.OnRemoveObject)
		self.sceneCtrl.layerCtrl.objectSelected.connect(self.OnSelectObject)

		self.objList = self.sceneCtrl.layerCtrl.layer.children[:]
		self.updateList()

def start():
	m = NoriterMain()
	m.Dock(NoriterMain.DOCK_LEFT,LayerWindow(m))


