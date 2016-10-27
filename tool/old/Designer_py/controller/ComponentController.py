# -*- coding: utf-8 -*-
import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *

from controller.LayerController import LayerController

class ComponentController(QObject):
	class ComponentModel(object):pass

	componentAdded = Signal(LayerController.ObjectModel,object)
	componentDeleted = Signal(LayerController.ObjectModel,int)
	componentModify = Signal(LayerController.ObjectModel,int,dict,dict)

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if ComponentController._instance == None:
			ComponentController._instance = ComponentController()
		return ComponentController._instance

	@staticmethod
	def default():
		return {}

	def __init__(self):
		super(ComponentController,self).__init__()
		self.registedComponent = {}

	def ComponentIds(self):
		return list(self.registedComponent.keys())

	def Add(self,objModel,strId):
		if strId in self.registedComponent:
			m = self.registedComponent[strId](objModel)
			return self.AddInstance(objModel,m,None)
		return -1

	def AddInstance(self,objModel,inst,number):
		objModel.AddComponent(inst,number)
		objModel.sortNumber()
		self.componentAdded.emit(objModel,inst)
		return inst.number

	def Remove(self,objModel,idx):
		if len( objModel.components ) > idx:
			model = objModel.components[idx]
			del objModel.components[idx]

			objModel.sortNumber()

			self.componentDeleted.emit(model,idx)

	def Modify(self,objModel,idx,dat):
		old = {}
		new = {}
		comp = objModel.components[idx]
		for key,value in dat.iteritems():
			v = comp.data.get(key,None)
			if v != None and v != value : 
				old[key] = v
				new[key] = value
		if len(old)>0 :
			self.componentModify.emit(objModel,idx,new,old)

	def Regist(self,strId,comp):
		if not (strId in self.registedComponent) :
			self.registedComponent[strId] = comp;




