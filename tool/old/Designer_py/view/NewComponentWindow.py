# -*- coding: utf-8 -*-
from PySide import QtGui,QtCore
from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import *

from controller.ComponentController import *

class NewComponentWindow(ModalWindow):
	def __init__(self,parent=None):
		super(NewComponentWindow,self).__init__(parent)
		self.idxText = ""

	@LayoutGUI
	def GUI(self):
		with Layout.HBox():
			self.comp = self.Layout.combo(ComponentController.getInstance().ComponentIds(),True)
			self.Layout.button("Add",self.Add)

	def Add(self):
		self.idxText = self.comp.currentText()
		self.close()

	def exec_(self):
		super(NewComponentWindow,self).exec_()
		return self.idxText