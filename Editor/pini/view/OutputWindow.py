# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

import os
 
class Console(QtGui.QTextEdit):
	def sizeHint(self):
		return QtCore.QSize(125,0)

	def __init__(self,parent = None):
		super(Console,self).__init__(parent)

class OutputWindow(Window):
	def sizeHint(self):
		return QtCore.QSize(600,500)

	noticed = Signal(unicode,QtGui.QColor)

	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not OutputWindow._instance:
			OutputWindow._instance = super(OutputWindow,cls).__new__(cls,*args,**kwargs)

		return OutputWindow._instance

	def __init__(self,src=None,parent=None):
		if OutputWindow._isInit:
			return 
		OutputWindow._isInit = True
		
		super(OutputWindow,self).__init__(parent)
		self.setWindowTitle(unicode("출력","utf-8"))

	def log(self,text):
		__ = self.console.toPlainText()
		__ += text + "\n"
		self.console.setText(__)
		NoriterMain().statusBar().showMessage(text)
		

	def notice(self,text):
		self.log(text)
		self.noticed.emit(text,QtGui.QColor(160,199,96))

	@LayoutGUI
	def GUI(self):
		self.console = self.Layout.addWidget(Console(self))
