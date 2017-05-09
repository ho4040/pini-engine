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

class FundingListWindow(ModalWindow):
	def __init__(self,parent):
		super(FundingListWindow,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.modify = False

	def listFactory(self,data):
		label = self.Layout.label(data)
		return 20

	@LayoutGUI
	def GUI(self):
		self.Layout.label(self.trUtf8("<b>피니엔진 오픈소스 후원자 </b>"))
		self.Layout.listbox(self.listFactory,[
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
			"xxxx님",
		])

				
	def Modified(self):
		self.modify = True
		self.close()

	def exec_(self):
		super(FundingListWindow,self).exec_()
		try:
			if self.modify : 
				w = int(self.w.text())
				h = int(self.h.text())
				proCtrl = ProjectController()
				proCtrl.screenWidth = w
				proCtrl.screenHeight = h
				proCtrl.orientation = self.orientation.isChecked()
				#proCtrl.fullscreen = self.fullscreen.isChecked()
		except Exception, e:
			pass
