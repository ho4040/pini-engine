# -*- coding: utf-8 -*-
import sys
import os
import json

from PySide.QtCore import *
from PySide.QtGui import *

from .LayerController import LayerController

class SceneController(QObject):
	def __init__(self):
		super(SceneController,self).__init__()
		self.layerController = LayerController();
		self.path = ""
		
	def Load(self,path):
		return
		''' 
		fp = QFile(path)
		fp.open(QIODevice.ReadOnly)
		data = str(fp.readAll())
		fp.close()

		self.path = path

		jsonData = json.loads(data)
		layer = jsonData["layer"]

		self.LoadLayer(layer)
		'''
		
	@property
	def layerCtrl(self):
		return self.layerController

	def LoadLayer(self,layer,parent=None):
		for o in layer:
			objModel = self.layerController.New(parent);
			if "components" in o and len(o["components"]) > 0 :
				pass
			if "children" in o and len(o["children"]) > 0 :
				self.LoadLayer(o["children"],objModel)


