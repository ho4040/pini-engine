# -*- coding: utf-8 -*-

import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *

from graphics.components import *
from controller.LayerController import LayerController

class ComponentController(QObject):
	COMPONENTSDATA = {
	    'Transform' : UCTransform,
	    'Rectangle' : UCRectangle,
	    'Sprite'    : UCSprite
	}

	COMPONENTSUI = {
		'Transform' : UCTransform.UI,
	    'Rectangle' : UCRectangle.UI,
	    'Sprite'    : UCSprite.UI
	}

	class ComponentModel(QObject):pass

	#signal
	componentAdded = Signal(LayerController.LayerModel,dict,int)
	componentDeleted = Signal(LayerController.LayerModel,int) # int idx
	componentModify = Signal(LayerController.LayerModel,int,dict)

	#instance
	_instance = None
	
	@staticmethod
	def getDefaultComponent():
		dest = {"id":'Transform'};
		dest.update(ComponentController.COMPONENTSDATA['Transform'].default())
		return dest

	@staticmethod
	def getInstance():
		if ComponentController._instance == None:
			ComponentController._instance = ComponentController()

		return ComponentController._instance

	def __init__(self):
		super(ComponentController,self).__init__()

		from controller.UndoController import UndoController
		self.uc = UndoController.getInstance()

	def ComponentInstance(self,com):
		return ComponentController.COMPONENTSDATA.get(com['id'],None)

	def Init(self,uiobj):
		for com in uiobj.model.component:
			uiobj.addComponent(self.ComponentInstance(com))
		return uiobj

	def HasComponent(self,layerModel,c):
		for rc in layerModel.component:
			_rc = ComponentController.COMPONENTSDATA.get(rc['id'],None)
			if _rc and _rc == c : 
				return True
		return False

	def Add(self,layerModel,compIdx):
		_refCom = ComponentController.COMPONENTSDATA.get(compIdx,None)
		if _refCom :
			_def = _refCom.default()
			_def["id"] = compIdx

			if _refCom(None,-1).requireTest(layerModel) : 
				self.uc.addComponent(layerModel,_def)
			else:
				print "component failed!!!!"
	
	def Remove(self,layerModel,number):
		if len(layerModel.component) > number : 
			self.uc.deleteComponent(layerModel,number)
		else:
			print "component failed!!!!"

	def Swap(self,layerModel,idx1,idx2):
		pass

	def Modify(self,layerModel,idx,dat):
		old = {}
		new = {}
		comp = layerModel.component[idx]
		for key,value in dat.iteritems():
			v = comp.get(key,None)
			if v != None and v != value : 
				old[key] = v
				new[key] = value

		if len(old)>0 :
			self.uc.modifyComponent(layerModel,idx,new,old)

	#===============================================
	#for undo command!
	#===============================================
	def _Command_Modify_(self,layerModel,idx,dat):
		comp = layerModel.component[idx]

		old = dict(comp)
		comp.update(dat);

		self.componentModify.emit(layerModel,idx,old)

	def _Command_Add_(self,layerModel,_def,number):
		layerModel.component.insert(number,_def)
		self.componentAdded.emit(layerModel,_def,number)

	def _Command_Deleted_(self,layerModel,number):
		del layerModel.component[number]
		self.componentDeleted.emit(layerModel,number)






