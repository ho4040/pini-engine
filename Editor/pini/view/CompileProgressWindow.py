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

class CompileProgressWindow(ModalWindow):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not CompileProgressWindow._instance:
			CompileProgressWindow._instance = super(CompileProgressWindow,cls).__new__(cls,*args,**kwargs)

		return CompileProgressWindow._instance

	def __init__(self,parent):
		if CompileProgressWindow._isInit:
			return 
		CompileProgressWindow._isInit = True

		self.currentText = ""
		self.nextText = ""
		super(CompileProgressWindow,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.setWindowTitle(u"컴파일 중")

		QTimer.singleShot(100,self.update)

	@LayoutGUI
	def GUI(self):
		self.Layout.clear()
		with Layout.HBox():
			self.Layout.gap(20)

			with Layout.VBox():
				self.Layout.gap(20)
				self.Layout.label("코드를 컴파일 중입니다.")
				self.Layout.gap(20)
				self.Layout.label(self.currentText)
				self.Layout.gap(20)
			self.Layout.gap(20)

	def setText(self,text):
		self.nextText = text
		pass

	def update(self):
		if self.currentText != self.nextText:
			self.currentText = self.nextText
			self.GUI()
		QTimer.singleShot(100,self.update)
