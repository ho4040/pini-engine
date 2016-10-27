# -*- coding: utf-8 -*-
import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *

class UndoController(QObject):
	class UndoModel:pass

	class ModifyComponentCommand(QUndoCommand):
		def __init__(self, layerModel, number, new, old):
			super(UndoController.ModifyComponentCommand, self).__init__()
			self.layerModel = layerModel
			self.number = number
			self.new = new
			self.old = old

			from controller.ComponentController import ComponentController
			self.controller = ComponentController.getInstance()

			self.setText(layerModel.name+":[ mod ("+layerModel.component[number]['id']+") ]")

		def undo(self):
			self.controller._Command_Modify_(self.layerModel,self.number,self.old)

		def redo(self):
			self.controller._Command_Modify_(self.layerModel,self.number,self.new)

	class AddComponentCommand(QUndoCommand):
		def __init__(self, layerModel, _def, number):
			super(UndoController.AddComponentCommand, self).__init__()
			self.layerModel = layerModel
			self.number = number
			self._def = _def

			from controller.ComponentController import ComponentController
			self.controller = ComponentController.getInstance()

			self.setText(layerModel.name+":[ add ("+_def['id']+") ]")

		def undo(self):
			self.controller._Command_Deleted_(self.layerModel,self.number)

		def redo(self):
			self.controller._Command_Add_(self.layerModel,self._def,self.number)

	class RemoveComponentCommand(QUndoCommand):
		def __init__(self, layerModel, number):
			super(UndoController.RemoveComponentCommand, self).__init__()
			self.layerModel = layerModel
			self.number = number
			self._def = self.layerModel.component[self.number]

			from controller.ComponentController import ComponentController
			self.controller = ComponentController.getInstance()

			self.setText(layerModel.name+":[ rem ("+self._def['id']+") ]")

		def undo(self):
			self.controller._Command_Add_(self.layerModel,self._def,self.number)

		def redo(self):
			self._def = self.layerModel.component[self.number]
			self.controller._Command_Deleted_(self.layerModel,self.number)

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if UndoController._instance == None:
			UndoController._instance = UndoController()
		return UndoController._instance

	def __init__(self):
		super(UndoController,self).__init__()
		self.stacks = {}
		self.currentScene = ''

		from controller.SceneController import SceneController
		SceneController.getInstance().focusChanged.connect(self.OnSceneFocusChanged)

	def OnSceneFocusChanged(self,sceneList,scene):
		self.openUndoStack(scene.name)

	def openUndoStack(self,sceneName):
		if sceneName not in self.stacks:
			self.stacks[sceneName] = QUndoStack(self)
			#for test
		self.currentScene = sceneName
		self.v = QUndoView(self.stacks[sceneName])
		self.v.show()

	def undo(self):
		self.stacks[self.currentScene].undo()

	def push(self,undo):
		self.stacks[self.currentScene].push(undo) 

	def newLayer(self,layer):
		pass
	def deleteLayer(self,layer):
		pass
	def modifyLayer(self,layer,new,old):
		pass
	def addComponent(self,layer,_def):
		self.push(UndoController.AddComponentCommand(layer,_def,len(layer.component)))
	def deleteComponent(self,layer,number):
		self.push(UndoController.RemoveComponentCommand(layer,number))
	def sortComponent(self,layer,newNumber,oldNumber):
		pass
	def modifyComponent(self,layer,number,new,old):
		self.push(UndoController.ModifyComponentCommand(layer,number,new,old))

UndoController.getInstance()