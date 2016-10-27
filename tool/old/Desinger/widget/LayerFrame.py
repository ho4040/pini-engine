import os
import sys

from PySide.QtGui import *
from PySide.QtCore import *

from uic.Ui_LayerFrame import Ui_LayerFrame
from controller.LayerController import LayerController


class LayerFrame(QFrame, Ui_LayerFrame):
	frameSelectedCSS = 'QFrame#LayerFrame {\
                border-style: outset;\
                border-width: 3px;\
                border-color: blue;\
            }'
	isFocusProcessing = False

	# Functions
	def __init__(self, layerModel, layout, parent=None):
		super(LayerFrame, self).__init__(parent)
		self.setupUi(self)

		self.lc = LayerController.getInstance()

		self._layerModel = layerModel
		self._layout = layout
		self.setData(layerModel)

		self.ui_nameInput.textChanged.connect(self.nameTextChanged)
		self.ui_isVisible.stateChanged.connect(self.isVisibleStateChanged)
		self.ui_isLock.stateChanged.connect(self.isLockStateChanged)

		self.lc.focusChanged.connect(self.focusedLayerChanged)

	@property
	def layerModel(self):
		return self._layerModel

	@layerModel.setter
	def layerModel(self, value):
		self._layerModel = value

	def setData(self, layerModel):
		self._layerModel = layerModel

		self.ui_nameInput.setText(layerModel.name)

		isVisible = Qt.Checked if layerModel.isVisible else Qt.Unchecked
		self.ui_isVisible.setCheckState(isVisible)

		isLock = Qt.Checked if layerModel.isLock else Qt.Unchecked
		self.ui_isLock.setCheckState(isLock)

	def toggleSelected(self):
		isSelected = not self.lc.containFocusLayer(self.layerModel)

		beApplyCSS = self.frameSelectedCSS if isSelected else ""
		self.setStyleSheet(beApplyCSS)

	def setSelected(self, value):
		beApplyCSS = self.frameSelectedCSS if value else ""
		self.setStyleSheet(beApplyCSS)

	def setAllSelectValue(self, value):
		layerListBox = self._layout
		for index in range(layerListBox.count()):
			layerFrame = layerListBox.itemAt(index).widget()
			layerFrame.setSelected(value)

	def selectByIndexes(self, indexes, isAppend=True):
		if not isAppend:
			self.setAllSelectValue(False)
			self.lc.clearFocusLayer(False)

		setList = []
		for index in indexes:
			layerFrame = self._layout.itemAt(index).widget()
			layerFrame.setSelected(True)
			if not self.lc.containFocusLayer(layerFrame.layerModel):
				if isAppend:
					self.lc.includeFocusLayer(layerFrame.layerModel)
				else:
					setList.append(layerFrame.layerModel)

		if not isAppend:
			self.lc.setFocusLayer(setList)


	def selectByObject(self, layerFrame, isAppend=True):
		if not isAppend:
			self.setAllSelectValue(False)
			self.lc.clearFocusLayer(False)

		setList = []
		layerFrame.setSelected(True)
		if not self.lc.containFocusLayer(layerFrame.layerModel):
			if isAppend:
				self.lc.includeFocusLayer(layerFrame.layerModel)
			else:
				self.lc.setFocusLayer([layerFrame.layerModel])

		if not isAppend:
			self.lc.setFocusLayer(setList)

	def selectToggleByObject(self, layerFrame):
		layerFrame.toggleSelected()

		if not self.lc.containFocusLayer(layerFrame.layerModel):
			self.lc.includeFocusLayer(layerFrame.layerModel)
		else:
			self.lc.excludeFocusLayer(layerFrame.layerModel)


	def selectByObjectRange(self, layerFrameBegin, layerFrameEnd, isAppend=True):
		if not isAppend:
			self.setAllSelectValue(False)
			self.lc.clearFocusLayer(False)

		layerFrameBeginIndex = self._layout.indexOf(layerFrameBegin)
		layerFrameEndIndex = self._layout.indexOf(layerFrameEnd)

		beginIndex = min(layerFrameBeginIndex, layerFrameEndIndex)
		endIndex = max(layerFrameBeginIndex, layerFrameEndIndex)

		setList = []
		for index in range(beginIndex, endIndex + 1):
			layerFrame = self._layout.itemAt(index).widget()
			layerFrame.setSelected(True)
			if not self.lc.containFocusLayer(layerFrame.layerModel):
				if isAppend:
					self.lc.includeFocusLayer(layerFrame.layerModel)
				else:
					setList.append(layerFrame.layerModel)
		if not isAppend:
			self.lc.setFocusLayer(setList)


	def selectByObjectIndex(self, beginIndex, endIndex, isAppend=True):
		if not isAppend:
			self.setAllSelectValue(False)
			self.lc.clearFocusLayer(False)

		realBeginIndex = min(beginIndex, endIndex)
		realEndIndex = max(beginIndex, endIndex)

		setList = []
		for index in range(realBeginIndex, realEndIndex + 1):
			layerFrame = self._layout.itemAt(index).widget()
			layerFrame.setSelected(True)
			if not self.lc.containFocusLayer(layerFrame.layerModel):
				if isAppend:
					self.lc.includeFocusLayer(layerFrame.layerModel)
				else:
					setList.append(layerFrame.layerModel)
		if not isAppend:
			self.lc.setFocusLayer(setList)


		# Events

	def mousePressEvent(self, event):
		if event.button() != Qt.LeftButton:
			return
		mouseEventModifiers = event.modifiers()

		isControlDown = mouseEventModifiers & Qt.ControlModifier
		isShiftDown = mouseEventModifiers & Qt.ShiftModifier

		if isControlDown and isShiftDown:
			pass
		elif isControlDown:
			print "mouseEventModifiers & QtCore.Qt.ControlModifier"
			self.selectToggleByObject(self)
		elif isShiftDown:
			print "mouseEventModifiers & QtCore.Qt.ShiftModifier"

			beginItem = self.lc.focusLayer[-1:]
			beginItem = beginItem[0]

			for index in range(self._layout.count()):
				item = self._layout.itemAt(index).widget()
				if item.layerModel == beginItem:
					beginItem = item
					break
			beginIndex = self._layout.indexOf(beginItem)
			endIndex = self._layout.indexOf(self)
			print "beginIndex : " + str(beginIndex)
			print "endIndex : " + str(endIndex)
			self.selectByObjectIndex(beginIndex, endIndex, False)
		else:
			self.setAllSelectValue(False)
			self.setSelected(True)
			self.lc.clearFocusLayer(False)
			self.lc.includeFocusLayer(self.layerModel)

	def mouseReleaseEvent(self, event):
		if event.button() != Qt.LeftButton:
			return
		mouseEventModifiers = event.modifiers()

		isControlDown = mouseEventModifiers & Qt.ShiftModifier
		isShiftDown = mouseEventModifiers & Qt.ShiftModifier

		if isControlDown and isShiftDown:
			pass
		elif isControlDown:
			print "mouseEventModifiers & QtCore.Qt.ControlModifier"
		elif isShiftDown:
			print "mouseEventModifiers & QtCore.Qt.ShiftModifier"

	@Slot(list)
	def focusedLayerChanged(self, layerModels):
		if LayerFrame.isFocusProcessing:
			return

		if layerModels and len(layerModels) > 0:
			layerListBox = self._layout
			layerFrameWidgetList = [layerListBox.itemAt(idx).widget() for idx in xrange(layerListBox.count())]
			layerFrameLayerModelList = [layerFrameWidgetList[idx].layerModel for idx in xrange(layerListBox.count())]

			indexesForFocus = []
			for idx, layerModel in enumerate(layerFrameLayerModelList):
				if layerModel in layerModels:
					indexesForFocus.append(idx)

			LayerFrame.isFocusProcessing = True
			self.selectByIndexes(indexesForFocus, False)
			LayerFrame.isFocusProcessing = False
		else:
			self.setAllSelectValue(False)

		self.update()

	def nameTextChanged(self, text):
		LayerController.modifyModelProperty(self._layerModel, "_name", text)

	def isVisibleStateChanged(self, state):
		state = True if state == Qt.Checked else False
		LayerController.modifyModelProperty(self._layerModel, "_isVisible", state)

	def isLockStateChanged(self, state):
		state = True if state == Qt.Checked else False
		LayerController.modifyModelProperty(self._layerModel, "_isLock", state)

