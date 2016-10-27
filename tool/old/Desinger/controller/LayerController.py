# -*- coding: utf-8 -*-


import copy
import json

from PySide import QtCore, QtGui

from utility.QtUtils import QtUtils

# from controller.SceneController import SceneController

class LayerController(QtCore.QObject):
	#Modles
	class LayerModel(QtCore.QObject):
		exceptedSerializationList = ["_filePath"]

		def __init__(self, parent=None, name=None, isVisible=True, isLock=False, drawOrder=1, filePath=None,
					 component=None):
			from controller.ComponentController import ComponentController

			super(LayerController.LayerModel, self).__init__(parent)

			self._filePath = filePath
			self._name = name
			self._isVisible = isVisible
			self._isLock = isLock
			self._drawOrder = drawOrder
			self._component = component if component and len(component) > 0 else [
				ComponentController.getDefaultComponent()]

		#name
		@property
		def name(self):
			return self._name

		@name.setter
		def name(self, value):
			self._name = value

		#isVisible
		@property
		def isVisible(self):
			return self._isVisible

		@isVisible.setter
		def isVisible(self, value):
			self._isVisible = value

		#isLock
		@property
		def isLock(self):
			return self._isLock

		@isLock.setter
		def isLock(self, value):
			self._isLock = value

		#drawOrder
		@property
		def drawOrder(self):
			return self._drawOrder

		@drawOrder.setter
		def drawOrder(self, value):
			self._drawOrder = value

		#component
		@property
		def component(self):
			return self._component

		@component.setter
		def component(self, value):
			self._component = value

		#component list
		@property
		def componentIds(self):
			comIds = []
			for v in self._component:
				_id = v.get('id', None);
				if _id: comIds.append(_id)
			return comIds

		def saveLayer(self, filePath=None):
			filePath = filePath or self._filePath
			writeStr = QtUtils.objToJsonStr(self, True, LayerController.LayerModel.exceptedSerializationList)
			if len(filePath) > 0:
				with open(filePath, "w") as fileObj:
					fileObj.write(writeStr)
				self._filePath = filePath

		@staticmethod
		def objectFromJsonObj(jsonObj):
			obj = LayerController.LayerModel()
			obj.loadFromJsonObj(jsonObj)
			return obj

		@staticmethod
		def objectFromJsonStr(jsonStr):
			return LayerController.LayerModel.objectFromJsonObj(json.loads(jsonStr))

		def loadFromJsonObj(self, jsonObj):
			self.__dict__ = dict(self.__dict__.items() + jsonObj.items())

			if "_name" in jsonObj:
				self._name = jsonObj["_name"]
			if "_isVisible" in jsonObj:
				self._isVisible = jsonObj["_isVisible"]
			if "_isLock" in jsonObj:
				self._isLock = jsonObj["_isLock"]
			if "_drawOrder" in jsonObj:
				self._drawOrder = jsonObj["_isLock"]

		def loadFromJsonStr(self, jsonStr):
			self.loadFromJsonObj(json.loads(jsonStr))

	class LayerListModel(QtCore.QObject):
		exceptedSerializationList = ["_filePath"]

		def __init__(self, parent=None, layerList=None, sceneName="", filePath=None):
			super(LayerController.LayerListModel, self).__init__(parent)

			self._filePath = None
			self._layerList = layerList or []
			self._sceneName = sceneName

		def __getitem__(self, key):
			return self._layerList[key]

		def __setitem__(self, key, value):
			self._layerList[key] = value

		def __iter__(self):
			return self._layerList.__iter__()

		def __len__(self):
			return len(self._layerList)

		def addLayer(self, name=None, isVisible=True, isLock=False, drawOrder=1, component={}):
			layerModel = LayerController.LayerModel(name=name, isVisible=isVisible, isLock=isLock, drawOrder=drawOrder,
													component=component)
			self._layerList.append(layerModel)

			return layerModel

		def deleteLayer(self, layer):
			self._layerList.remove(layer)
			return layer

		def isContain(self, name):
			return name in self._layerList

		def saveLayerList(self, filePath=None):
			filePath = filePath or self._filePath
			writeStr = QtUtils.objToJsonStr(self, True, LayerController.LayerListModel.exceptedSerializationList)

			if len(filePath) > 0:
				with open(filePath, "w") as fileObj:
					fileObj.write(writeStr)
				self._filePath = filePath

		@staticmethod
		def objectFromJsonObj(jsonObj):
			obj = LayerController.LayerListModel()
			obj.loadFromJsonObj(jsonObj)
			return obj

		@staticmethod
		def objectFromJsonStr(jsonStr):
			obj = LayerController.LayerListModel.objectFromJsonObj(json.loads(jsonStr))
			return obj

		def loadFromJsonObj(self, jsonObj):
			if "_sceneName" in jsonObj:
				self._sceneName = jsonObj["_sceneName"]
			if "_layerList" in jsonObj:
				self._layerList = jsonObj["_layerList"]

		@property
		def layerList(self):
			return self._layerList

		@layerList.setter
		def layerList(self, value):
			self._layerList = value

		@property
		def sceneName(self):
			return self._sceneName

		@sceneName.setter
		def sceneName(self, value):
			self._sceneName = value

	#Signals
	focusChanged = QtCore.Signal(list)
	propertyChanged = QtCore.Signal(LayerModel, dict)

	itemAdded = QtCore.Signal(LayerListModel, LayerModel)
	itemDeleted = QtCore.Signal(LayerListModel, LayerModel)

	#Singleton
	_instance = None

	@staticmethod
	def getInstance():
		def store():
			if not LayerController._instance:
				LayerController._instance = LayerController()
			return LayerController._instance

		return store()

	def __init__(self, parent=None):
		from controller.SceneController import SceneController

		self.sc = SceneController.SceneListModel.getInstance()

		super(LayerController, self).__init__(parent)

		self._currentSceneName = None
		self._focusLayers = []

	@property
	def currentSceneName(self):
		return self._currentSceneName

	@currentSceneName.setter
	def currentSceneName(self, value):
		self._currentSceneName = value

	@property
	def currentScene(self):
		return self.sc.getSceneByName(self._currentSceneName)

	@property
	def currentLayerList(self):
		return self.currentScene.layerListModel

	@property
	def focusLayer(self):
		return self._focusLayers

	def renameCurrentSceneName(self,oldPath,newPath):
		oldFileInfo = QtCore.QFileInfo(oldPath)
		newFileInfo = QtCore.QFileInfo(newPath)

		if self._currentSceneName == oldFileInfo.completeBaseName():
			self._currentSceneName = newFileInfo.completeBaseName()

	def clearFocusLayer(self, isNotify=True):
		if len(self._focusLayers) > 0:
			self._focusLayers = []
			if isNotify:
				self.focusChanged.emit(self._focusLayers)

	def includeFocusLayer(self, layerModel):
		if layerModel in self._focusLayers:
			return

		self._focusLayers.append(layerModel)
		self.focusChanged.emit(self._focusLayers)

	def excludeFocusLayer(self, layerModel):
		if layerModel in self._focusLayers:
			self._focusLayers.remove(layerModel)
			self.focusChanged.emit(self._focusLayers)
			return True
		return False

	def containFocusLayer(self, layerModel):
		return layerModel in self._focusLayers

	def setFocusLayer(self, layerModels):
		isChanged = self._focusLayers != layerModels

		if isChanged:
			self.focusChanged.emit(layerModels)

		self._focusLayers = layerModels

	def addLayer(self, name, isVisible=True, isLock=False, drawOrder=1):
		if self.currentScene:
			if not self.currentLayerList.isContain(name):
				layer = self.currentLayerList.addLayer(name, isVisible, isLock, drawOrder)
				self.itemAdded.emit(self.currentLayerList, layer)

	def deleteLayer(self, layerModel):
		layer = self.currentLayerList.deleteLayer(layerModel)
		self.itemDeleted.emit(self.currentLayerList, layer)

	def deleteLayers(self, layerModels):
		for m in layerModels:
			self.deleteLayer(m)

	def deleteFocusLayers(self):
		self.deleteLayers(self._focusLayers)
		self._focusLayers = []

	@staticmethod
	def modifyModelProperty(layerModel, key, value):
		if hasattr(layerModel, key):
			setattr(layerModel, key, value)
			LayerController.getInstance().propertyChanged.emit(layerModel, {key: value})
