# -*- coding: utf-8 -*-
import sys
import os
import json

from PySide.QtCore import *
from PySide.QtGui import *

from .SceneController import SceneController
from Noriter.utils.Json import Json

class SceneListController(QObject):

	SceneLoaded = Signal( SceneController )
	SceneOpen = Signal( SceneController )

	def __init__(self):
		super(SceneListController,self).__init__()
		self.sceneList = {}

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if SceneListController._instance == None:
			SceneListController._instance = SceneListController()
		return SceneListController._instance

	def Load(self,path):
		if QFile(path).exists() :
			sc = SceneController()
			sc.Load(path)

			self.sceneList[path] = sc
			self.currentScene = None
			self.SceneLoaded.emit(self.sceneList[path])

			return True
		return False

	def Open(self,path):
		if not path in self.sceneList:
			if not self.Load(path) :
				return 

		self.currentScene = self.sceneList[path]
		self.SceneOpen.emit(self.sceneList[path])

	def Save(self,path):
		pass

	def New(self,path):
		fp = QFile(path)
		fp.open(QIODevice.WriteOnly)
		fp.write(json.dumps(SceneController.default()))
		fp.close()

	def Now(self):
		return self.currentScene
