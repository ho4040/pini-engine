# -*- coding: utf-8 -*-
import sys
import os
import json

from PySide.QtCore import *
from PySide.QtGui import *

class LayerController(QObject):
	class ObjectModel(object):
		def __init__(self,parent=None):
			self.components = []
			self.children = []
			self.parent = parent

		def serialize(self):
			pass

		def AddComponent(self,comp,number=None):
			if number is None:
				number = len(self.components)

			self.components.insert(number,comp)

		def sortNumber(self):
			i = 0
			for c in self.components : 
				c.number = i
				i += 1

	objectAdded = Signal( ObjectModel )
	objectRemoved = Signal( ObjectModel )
	objectSelected = Signal( list )

	def __init__(self):
		super(LayerController,self).__init__()
		self.layer = LayerController.ObjectModel()

	def SetSelectObjects(self,objects):
		self.objectSelected.emit(objects)

	def New(self,parent=None):
		if parent is None:
			parent = self.layer

		if self.Exists(parent):
			objModel = LayerController.ObjectModel( parent )
			if parent : 
				parent.children.append( objModel )
			
			self.objectAdded.emit( objModel )
			return objModel
		else:
			return None

	def Remove(self,objModel):
		if self.Exists(objModel) : 
			objModel.parent.children.remove( objModel )
			objModel.parent = None

			self.objectRemoved.emit( objModel )

	def Exists(self,obj,parent=None):
		if obj is self.layer :
			return True 

		if parent is None:
			parent = self.layer

		for v in parent.children :
			if v == obj :
				return True
			elif len(v.children) > 0 :
				if self.Find(obj,v.children) : 
					return True
		return False