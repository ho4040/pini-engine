# -*- coding: utf-8 -*-
from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.SceneListController import SceneListController
from controller.ComponentController import *
from view.NewComponentWindow import NewComponentWindow
from command.commands import *

class InspectorWindow(Window):
	def __init__(self,parent=None):
		super(InspectorWindow,self).__init__(parent)
		self.setWindowTitle("inspector")

		self.nowScene = None
		self.objects = []

		self.componentCtrl = ComponentController.getInstance()
		self.componentCtrl.componentAdded.connect(self.OnAddComponent)
		self.componentCtrl.componentDeleted.connect(self.OnDeleteComponent)
		SceneListController.getInstance().SceneOpen.connect(self.OnSceneOpen)

	@LayoutGUI
	def GUI(self):
		self.Layout.clear()
		if hasattr(self,'objects') and len(self.objects) > 0 :
			objModel = self.objects[0]
			for comp in objModel.components:
				self.Layout.addWidget(comp.UI(objModel,comp.number))

		self.Layout.spacer()
		self.Layout.button( "Add Component",self.addComponent )

#	def OnAddComponent(self,model,comp):
#		if model in self.objects :
#			self.GUI()

	def OnAddComponent(self,objModel,compModel):
		if objModel in self.objects :
			self.GUI()

	def OnDeleteComponent(self,model,idx):
		if model.objectModel in self.objects :
			self.GUI()

	def addComponent(self):
		comp = NewComponentWindow(self)
		idx = comp.exec_()
		if len(idx) is not 0:
			for objModel in self.objects:
				Command.Component.Add(objModel,idx)
			self.GUI()

	def OnObjectSelected(self,objects):
		self.objects = objects
		self.GUI()

	def OnSceneOpen(self,sceneCtrl):
		if self.nowScene : 
			self.nowScene.layerCtrl.objectSelected.disconnect( self.OnObjectSelected )

		self.nowScene = sceneCtrl
		self.nowScene.layerCtrl.objectSelected.connect( self.OnObjectSelected )

def start():
	m = NoriterMain()
	m.Dock(NoriterMain.DOCK_RIGHT,InspectorWindow(m))

