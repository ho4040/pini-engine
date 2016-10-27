# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Noriter.UI.Layout import *
from Noriter.UI.Window import Window
from Noriter.views.NoriterMainWindow import * 

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController
from graphics.GraphicsView import *

class VariableViewWindow(Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not VariableViewWindow._instance:
			VariableViewWindow._instance = super(VariableViewWindow,cls).__new__(cls,*args,**kwargs)

		return VariableViewWindow._instance

	def __init__(self):
		if VariableViewWindow._isInit:
			return 
		self.lua = None
		self.searchText = None
		VariableViewWindow._isInit = True
		super(VariableViewWindow,self).__init__(NoriterMain())
		self.setWindowTitle(u"변수 뷰어")
		self.resize(400,300)

	@LayoutGUI
	def GUI(self):
		self.tab = self.Layout.tab()
		with self.tab.tab("프리뷰") : 
			with Layout.VBox():
				with Layout.HBox():
					self.Layout.label("검색")
					self.searchText = self.Layout.input(u"",self.Search)
				self.previewVarList = self.Layout.listbox(self.varListFactory,[])
			
	def Search(self):
		if self.lua : 
			self.previewInfoUpdate(self.lua)

	def varListFactory(self,data):
		with Layout.HBox():
			STR = data[1];
			try:
				STR = unicode(STR);
			except Exception, e:
				STR = "LUA TABLE"
			ID = data[0]
			try:
				ID = unicode(ID);
			except Exception, e:
				ID = "LUA TABLE"

			if ID.startswith(u"___") : 
				ID = ID.replace(u"___",u"[기본값]")
			name=self.Layout.label(ID)
			val = self.Layout.input(STR,None)
			
			name.setFixedWidth(200)
			val.setReadOnly(True)

		return 25

	def previewInfoUpdate(self,lua):
		self.lua = lua
		previewVars = []
		keyword = "" if self.searchText == None else self.searchText.text()
		for k,v in sorted(lua.globals()._LNXG.items()) : 
			if k.find(keyword) >= 0 : 
				previewVars.append([k,v])
		self.previewVarList.data = previewVars

	def remoteVarListUpdate(self):
		pass