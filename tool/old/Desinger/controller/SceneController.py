# -*- coding: utf-8 -*-

import os
import copy
import json

from PySide import QtGui, QtCore
from controller.LayerController import LayerController
from utility.QtUtils import QtUtils


class SceneController(QtCore.QObject):
	# Singleton
	_instance = None

	@staticmethod
	def getInstance():
		def store():
			if not SceneController._instance:
				SceneController._instance = SceneController()
			return SceneController._instance

		return store()

	#Modles
	class SceneListModel(QtCore.QObject):
		#Singleton
		_instance = None

		sceneRenamed = QtCore.Signal(unicode,unicode)

		@staticmethod
		def getInstance():
			def store():
				if not SceneController.SceneListModel._instance:
					SceneController.SceneListModel._instance = SceneController.SceneListModel()
				return SceneController.SceneListModel._instance

			return store()

		#Variable
		exceptedSerializationList = ["_filePath"]
		#Signals

		#Functions
		def __init__(self, parent=None, filePath=None, sceneList=None):
			super(SceneController.SceneListModel, self).__init__(parent)

			self._sceneList = sceneList or {}
			self._filePath = filePath
			self._name = None

		@property
		def name(self):
			return self._name

		@name.setter
		def name(self, value):
			self._name = value

		def addScene(self, filePath, name=None):
			obj = None
			if os.path.isfile(filePath):
				if not name:
					name = QtCore.QFileInfo(filePath).completeBaseName()

				#if file loaded, just return scene model not addictory loading
				if self._sceneList.get(name, None):
					return self._sceneList[name]

				obj = SceneController.SceneModel(filePath=filePath)
				if obj.name:
					name = obj.name
				self._sceneList[name] = obj
			return obj

		def addSceneByObj(self, obj, name=None):
			if not name:
				name = obj.name
			self._sceneList[name] = obj

		def closeSceneByName(self, name):
			closedSceneModel = None
			if name in self._sceneList:
				closedSceneModel = self._sceneList[name]
				del self._sceneList[name]

			return closedSceneModel

		def closeSceneByObj(self,sceneModel):
			result = False
			sceneModels = self._sceneList.values()

			if sceneModel in sceneModels:
				index = sceneModels.index(sceneModel)
				key   = self._sceneList.keys()[index]
				del self._sceneList[key]
				result = True

			return result

		def getSceneByName(self, name):
			if name in self._sceneList:
				return self._sceneList[name]
			else:
				return None

		def renameScene(self,oldPath,newPath):
			oldFileInfo = QtCore.QFileInfo(oldPath)
			newFileInfo = QtCore.QFileInfo(newPath)

			oldBaseName = oldFileInfo.completeBaseName()
			newBaseName = newFileInfo.completeBaseName()

			scene = self.getSceneByName(oldBaseName)
			if scene:
				scene.name     = newBaseName
				scene.filePath = newPath

				self._sceneList[newBaseName] = scene
				del self._sceneList[oldBaseName]

				self.sceneRenamed.emit(oldBaseName,newBaseName)

			return scene

		def openSceneList(self, filePath):
			if os.path.isfile(filePath) == False:
				return

			self._filePath = filePath
			if not self._name:
				self._name = QtCore.QFileInfo(filePath).completeBaseName()
			self._sceneList = {}

			data = ""
			fp = QtCore.QFile(filePath)
			fp.open(QtCore.QIODevice.ReadOnly)
			data = unicode(fp.readAll())
			fp.close()

			if len(data) > 0:
				self.loadFromJsonStr(data)

		def saveSceneList(self, filePath=None):
			filePath = filePath or self._filePath
			writeStr = QtUtils.objToJsonStr(self, True, SceneController.SceneListModel.exceptedSerializationList)
			if len(filePath) > 0:
				with open(filePath, "w") as fileObj:
					fileObj.write(writeStr)

			self._filePath = filePath

		@staticmethod
		def objectFromJsonObj(jsonObj):
			obj = SceneController.SceneListModel()
			obj.loadFromJsonObj(jsonObj)
			return obj

		@staticmethod
		def objectFromJsonStr(jsonStr):
			return SceneController.SceneListModel.objectFromJsonObj(json.loads(jsonStr))

		def loadFromJsonObj(self, jsonObj):
			if "_sceneList" in jsonObj:
				if jsonObj["_sceneList"]:
					for key, value in jsonObj["_sceneList"].items():
						sceneModel = SceneController.SceneModel()
						sceneModel.loadFromJsonObj(value)
						self._sceneList[key] = sceneModel

		def loadFromJsonStr(self, jsonStr):
			self.loadFromJsonObj(json.loads(jsonStr))

	class SceneModel(QtCore.QObject):
		#Variable
		exceptedSerializationList = ["_filePath"]

		#Functions
		def __init__(self, parent=None, filePath="", name=""):
			super(SceneController.SceneModel, self).__init__(parent)
			self._filePath = filePath
			self._name = name
			self._layerListModel = LayerController.LayerListModel(sceneName=name)

			if len(filePath) > 0:
				self.openScene(filePath=filePath)

		@property
		def filePath(self):
			return self._filePath
		@filePath.setter
		def filePath(self,value):
			self._filePath = value

		@property
		def name(self):
			return self._name

		@name.setter
		def name(self, value):
			self._name = value

		@property
		def layerListModel(self):
			return self._layerListModel

		@layerListModel.setter
		def layerListModel(self, value):
			self._layerListModel = value

		def openScene(self, filePath):
			if os.path.isfile(filePath) == False:
				return

			self._filePath = filePath
			if not self._name:
				self._name = QtCore.QFileInfo(filePath).completeBaseName()

			data = ""
			fp = QtCore.QFile(filePath)
			fp.open(QtCore.QIODevice.ReadOnly)
			data = unicode(fp.readAll())
			fp.close()

			if len(data) > 0:
				self.loadFromJsonStr(data)

			return self._name

		def saveScene(self, filePath=None):
			filePath = filePath or self._filePath
			writeStr = QtUtils.objToJsonStr(self, True, SceneController.SceneModel.exceptedSerializationList)
			with open(filePath, "w") as fileObj:
				fileObj.write(writeStr)

		@staticmethod
		def objectFromJsonObj(jsonObj):
			obj = SceneController.SceneModel()
			obj.loadFromJsonObj(jsonObj)
			return obj

		@staticmethod
		def objectFromJsonStr(jsonStr):
			return SceneController.SceneModel.objectFromJsonObj(json.loads(jsonStr))

		def loadFromJsonObj(self, jsonObj):
			self._layerListModel = LayerController.LayerListModel()

			# if "_name" in jsonObj:
			# 	self._name = jsonObj["_name"]
			self._layerListModel.sceneName = self._name

			if "_layerListModel" in jsonObj:
				if "_layerList" in jsonObj["_layerListModel"]:
					for value in jsonObj["_layerListModel"]["_layerList"]:
						self._layerListModel.addLayer(name=value["_name"],
													  isVisible=value["_isVisible"],
													  isLock=value["_isLock"],
													  drawOrder=value["_drawOrder"],
													  component=value["_component"])

		def loadFromJsonStr(self, jsonStr):
			self.loadFromJsonObj(json.loads(jsonStr))

	#Signals
	focusChanged    = QtCore.Signal(SceneListModel, SceneModel)
	propertyChanged = QtCore.Signal(dict)
	sceneClosed     = QtCore.Signal(SceneModel,int)

	sceneWatcher    = QtCore.QFileSystemWatcher()

	#Functions
	def __init__(self, parent=None):
		super(SceneController, self).__init__(parent)
		self._openSceneName = None

		self.sl = SceneController.SceneListModel.getInstance()

	def openSceneList(self, filePath):
		if os.path.isfile(filePath) == False:
			return

		self.sl.openSceneList(filePath)

	def openScene(self, filePath):
		if os.path.isfile(filePath) == False:
			return

		scene = self.sl.addScene(filePath)
		if scene:
			self.sceneWatcher.addPath(filePath)
			self.focusScene(scene.name)

	def focusScene(self, name):
		scene = self.sl.getSceneByName(name)

		if scene:
			self.focusChanged.emit(self.sl, scene)
			return scene
		else:
			return None
	def renameScene(self,oldPath,newPath):
		oldFileInfo = QtCore.QFileInfo(oldPath)
		newFileInfo = QtCore.QFileInfo(newPath)

		isScene = oldFileInfo.suffix() == "scene" and newFileInfo.suffix() == "scene"

		if not isScene:
			return

		scene = self.sl.renameScene(oldPath,newPath)

		if not scene:
			print "renameScene({0},{1}) not found scene!".format(oldPath,newPath)

	def closeScene(self, sceneModel,tabIndex):
		result = self.sl.closeSceneByObj(sceneModel)
		if result:
			self.sceneWatcher.removePath(sceneModel.filePath)
			self.sceneClosed.emit(sceneModel,tabIndex)

	@staticmethod
	def createTestSceneFile(filePath=None):
		sceneListModel = SceneController.SceneListModel.getInstance()
		sceneListModel.name = "testSceneList"

		testSceneModel1 = SceneController.SceneModel(name="testScene1")
		testSceneModel1.layerListModel.addLayer(name="apple", drawOrder=1)
		testSceneModel1.layerListModel.addLayer(name="orange", drawOrder=2)
		testSceneModel1.layerListModel.addLayer(name="strawberry", drawOrder=3)
		testSceneModel1.layerListModel.addLayer(name="grapes", drawOrder=3)
		testSceneModel1.layerListModel.addLayer(name="watermelon", drawOrder=4)
		testSceneModel1.layerListModel.addLayer(name="tangerine", drawOrder=8)
		testSceneModel1.layerListModel.addLayer(name="cherry", drawOrder=9)

		testSceneModel2 = SceneController.SceneModel(name="testScene2")
		testSceneModel2.layerListModel.addLayer(name="Lorem ipsum", drawOrder=1)
		testSceneModel2.layerListModel.addLayer(name="dolor sit amet", drawOrder=2)
		testSceneModel2.layerListModel.addLayer(name="consectetur adipiscing", drawOrder=3)
		testSceneModel2.layerListModel.addLayer(name="elit. Nulla", drawOrder=3)
		testSceneModel2.layerListModel.addLayer(name="egestas", drawOrder=4)
		testSceneModel2.layerListModel.addLayer(name="libero non", drawOrder=8)
		testSceneModel2.layerListModel.addLayer(name="risus mollis", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="ut sodales", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="purus et libero", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="venenatis", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="rutrum", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="ullamcorper neque,", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="varius commodo", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="Proin vitae", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="feugiat turpis", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="id adipiscing", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="ullamcorper bibendum.", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="erat et massa", drawOrder=9)
		testSceneModel2.layerListModel.addLayer(name="dignissim odio.", drawOrder=9)

		sceneListModel.addSceneByObj(testSceneModel1)
		sceneListModel.addSceneByObj(testSceneModel2)

		testSceneListPath = filePath or os.path.join(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation), "testSceneList.sceneList")
		testScene1Path = filePath or os.path.join(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation), "testScene1.scene")
		testScene2Path = filePath or os.path.join(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation), "testScene2.scene")

		sceneListModel.saveSceneList(testSceneListPath)
		testSceneModel1.saveScene(testScene1Path)
		testSceneModel2.saveScene(testScene2Path)