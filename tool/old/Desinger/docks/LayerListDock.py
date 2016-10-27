# -*- coding: utf-8 -*-
from PySide import QtGui, QtCore

from windows.DesignerMain import DesignerMain
from uic.Ui_LayerListDock import Ui_LayerList
from widget.LayerFrame import LayerFrame

from controller.SceneController import *


class LayerListDock(QtGui.QDockWidget, Ui_LayerList):
	def __init__(self, parent=None):
		super(LayerListDock, self).__init__(parent)
		self.setupUi(self)

		self.ui_layerAdd.clicked.connect(self.layerAdd_clicked)
		self.ui_layerDelete.clicked.connect(self.layerDelete_clicked)

		self.lc = LayerController.getInstance()
		self.lc.itemAdded.connect(self.layerAdded)
		self.lc.itemDeleted.connect(self.layerDeleted)

		self.sc = SceneController.getInstance()
		self.sc.focusChanged.connect(self.focusedSceneChanged)

		# for test ---------------------------------------------------------------------
		self.ui_openTestScene.hide()
		self.ui_testScene1Select.hide()
		self.ui_testScene2Select.hide()
		self.ui_openTestScene.clicked.connect(self.openTestSceneList_clicked)
		self.ui_testScene1Select.clicked.connect(self.testScene1Select_clicked)
		self.ui_testScene2Select.clicked.connect(self.testScene2Select_clicked)
		# ------------------------------------------------------------------------------

		self.checkLayerBtn()

	def checkLayerBtn(self):
		currentScene    = LayerController.getInstance().currentScene
		layerBtnEnabled = True if currentScene else False
		self.ui_layerAdd.setEnabled(layerBtnEnabled)
		self.ui_layerDelete.setEnabled(layerBtnEnabled)

	#'''
	def openTestSceneList_clicked(self):
		SceneController.createTestSceneFile()
		self.sc.openSceneList(os.path.join(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation),
										   "testSceneList.sceneList"))

	def testScene1Select_clicked(self):
		scene = self.sc.focusScene("testScene1")

	def testScene2Select_clicked(self):
		scene = self.sc.focusScene("testScene2")
	#'''

	def layerAdd_clicked(self):
		name, ok = QtGui.QInputDialog.getText(self, self.trUtf8("레이어 추가"), self.trUtf8("레이어 이름을 입력하세요"),
											  QtGui.QLineEdit.Normal, "layer")
		if ok: self.lc.addLayer(name)

	def layerDelete_clicked(self):
		self.lc.deleteFocusLayers()

	def layerFrameAdd(self, layerModel):
		frame = LayerFrame(layerModel, self.ui_ListVBox)
		self.ui_ListVBox.addWidget(frame)

		self.frameSize = frame.rect()
		self.measureScrollArea()

	def measureScrollArea(self):
		self.ui_ListContents.setFixedSize(self.ui_ListContents.width(),
										  self.frameSize.height() * self.ui_ListVBox.count())

	def layerFrameRemoveByIndex(self, index):
		child = self.ui_ListVBox.takeAt(index)
		return child == None

	def layerFrameRemoveByName(self, name):
		layerListBox = self.ui_ListVBox
		layerModelList = [layerListBox.itemAt(idx).widget().layerModel for idx in xrange(layerListBox.count())]

		indexForIndex = []
		for index, layerModel in enumerate(layerModelList):
			if layerModel.name == name:
				indexForIndex.append(index)

	def layerFrameClear(self):
		layerListBox = self.ui_ListVBox

		indexesForDelete = range(layerListBox.count())
		indexesForDelete.sort(reverse=True)
		for index in indexesForDelete:
			item = layerListBox.takeAt(index)
			widget = item.widget()
			if widget:
				widget.deleteLater()
		self.lc.clearFocusLayer()

	# Signals

	#Slots
	@QtCore.Slot(SceneController.SceneListModel, SceneController.SceneModel)
	def focusedSceneChanged(self, sceneList=None, sceneModel=None):
		self.checkLayerBtn()

		# title = "레이어 리스트-{0}-{1}".format(str(sceneList.name), str(sceneModel.name))
		#  self.setWindowTitle(self.trUtf8(title))

		self.layerFrameClear()

		layerListModel = sceneModel.layerListModel
		for layerModel in layerListModel:
			self.layerFrameAdd(layerModel)

		self.lc.currentSceneName = sceneModel.name

		self.update()

	@QtCore.Slot(LayerController.LayerListModel, LayerController.LayerModel)
	def layerAdded(self, layerListModel, layerModel):
		print "called layerAdded(self,layerListModel,layerModel):"
		self.layerFrameAdd(layerModel)

	@QtCore.Slot(LayerController.LayerListModel, LayerController.LayerModel)
	def layerDeleted(self, layerListModel, deleted):
		print "called layerDeleted(self,layerListModel,name):"

		layerListBox = self.ui_ListVBox
		layerFrameWidgetList = [layerListBox.itemAt(idx).widget() for idx in xrange(layerListBox.count())]
		layerFrameLayerModelList = [layerFrameWidgetList[idx].layerModel for idx in xrange(layerListBox.count())]

		#indexesForDelete = []
		for idx, layerModel in enumerate(layerFrameLayerModelList):
			if layerModel == deleted:
				#indexesForDelete.append(idx)
				item = layerListBox.takeAt(idx)
				if item: item.widget().deleteLater()
				break
		'''
		indexesForDelete.sort(reverse=True)
		for index in indexesForDelete:
			item = layerListBox.takeAt(index)
			if item:
				item.widget().deleteLater()
		'''
		self.measureScrollArea();

def start():
	dMain = DesignerMain()
	layerList = LayerListDock(dMain)
	if hasattr(dMain,"layerList") and dMain.layerList:
		dMain.removeDockWidget(dMain.layerList)
	dMain.layerList = layerList
	dMain.addDockWidget(QtCore.Qt.LeftDockWidgetArea,layerList)

	existBrowser   = hasattr(dMain,"browser") and dMain.browser
	existLayerList = hasattr(dMain,"layerList") and dMain.layerList
	if existBrowser and existLayerList:
		dMain.tabifyDockWidget(dMain.browser,dMain.layerList)


