# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Noriter.UI.Layout import *
from Noriter.UI.Window import Window
from Noriter.views.NoriterMainWindow import * 

from view.SceneScriptWindow import SceneScriptWindowManager

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController
from graphics.GraphicsView import *

class DefineSettingWindow(Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not DefineSettingWindow._instance:
			DefineSettingWindow._instance = super(DefineSettingWindow,cls).__new__(cls,*args,**kwargs)

		return DefineSettingWindow._instance

	def __init__(self):
		if DefineSettingWindow._isInit:
			return 
		DefineSettingWindow._isInit = True
		super(DefineSettingWindow,self).__init__(NoriterMain())
		self.setWindowTitle(u"치환설정")
		self.resize(400,300)

		self.defdatas = []
		self.defineList.data = self.defdatas

		self.defineList.changedIndex.connect(self.changedSelected)

		self.updateDefList()
		self.selectedIndices = []

	@LayoutGUI
	def GUI(self):
		self.Layout.clear()

		inst = ProjectController()

		with Layout.VBox():
			with Layout.HBox():
				self.Layout.gap(3)
				self.Layout.label("정의").setAlignment(Qt.AlignHCenter)
				self.Layout.gap(3)
				self.Layout.vline()
				self.Layout.gap(3)
				self.Layout.label("값").setAlignment(Qt.AlignHCenter)
				self.Layout.gap(3)

			self.defineList = self.Layout.listbox(self.varListFactory,[])

			with Layout.HBox():
				self.Layout.gap(1)
				self.Layout.button("△",self.moveUpPressed)
				self.Layout.gap(1)
				self.Layout.button("▽",self.moveDownPressed)
				self.Layout.gap(1)
				self.defInputBox = self.Layout.input("",None)
				self.Layout.gap(1)
				self.valInputBox = self.Layout.input("",None)
				self.Layout.gap(1)
				self.Layout.button("추가",self.addButtonPressed)
				self.Layout.gap(1)
				self.Layout.button("삭제",self.removeButtonPressed)
				self.Layout.gap(1)

	def updateDefList(self,selIdx = None):
		inst = ProjectController()
		lists = inst.defines
		self.defineList.data = lists

		if selIdx != None:
			def doSelectIndex():
				self.defineList.selectIndex(selIdx)

			QTimer.singleShot(1,doSelectIndex)

	def varListFactory(self,data):
		with Layout.HBox():
			STR = data[1];
			try:
				STR = unicode(STR);
			except Exception, e:
				STR = u"(손상된 문자열)"
			ID = data[0]
			try:
				ID = unicode(ID);
			except Exception, e:
				ID = u"(손상된 문자열)"

			self.Layout.gap(3)
			name = self.Layout.label(ID)
			self.Layout.gap(3)
			self.Layout.vline()
			self.Layout.gap(3)
			val  = self.Layout.label(STR)
			self.Layout.gap(3)
			
		return 25

	def changedSelected(self,idx):
		if len(idx) <= 0:
			self.selectedIndices = []
			return
		self.selectedIndices = idx

	def updateList(self,selIdx=None):
		inst = ProjectController()

		active = SceneScriptWindowManager.getInstance().getActive() 
		if active != None:
			active.editor.compileAll()
			active.editor.cursorPositionChanged(None)

		inst.setRebuildFlag()
		self.updateDefList(selIdx)

	def addButtonPressed(self):
		inst = ProjectController()
		defines = inst.defines

		defines.append([self.defInputBox.text(),self.valInputBox.text()])
		inst.defines = defines

		self.updateList()

	def removeButtonPressed(self):
		if len(self.selectedIndices) > 0:
			inst = ProjectController()
			defines = inst.defines
			defines.pop(self.selectedIndices[0])
			inst.defines = defines

			self.updateList()

	def moveUpPressed(self):
		if len(self.selectedIndices) > 0:
			inst = ProjectController()
			defines = inst.defines
			origData = None
			pos = self.selectedIndices[0]
			if pos > 0:
				origData = defines.pop(pos)
				defines.insert(pos-1, origData)
				inst.defines = defines
				self.updateList(pos-1)

	def moveDownPressed(self):
		if len(self.selectedIndices) > 0:
			inst = ProjectController()
			defines = inst.defines
			origData = None
			pos = self.selectedIndices[0]
			if pos < len(defines) - 1:
				origData = defines.pop(pos)
				defines.insert(pos+1, origData)
				inst.defines = defines
				self.updateList(pos+1)
