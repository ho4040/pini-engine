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

class AboutPiniWindow(ModalWindow):
	def __init__(self,parent):
		super(AboutPiniWindow,self).__init__(parent)

		self._layout.setContentsMargins(5, 5, 5, 5)
		self._layout.setSpacing(4)

		self.modify = False

	@LayoutGUI
	def GUI(self):
		self.Layout.label(self.trUtf8("<b>피니엔진 오픈소스 버전</b>"))

		compilerVersion = ""
		try:
			versionDir = os.path.join("..","pini_ver.inf")
			fp = QFile(versionDir)
			fp.open(QIODevice.ReadOnly | QIODevice.Text)

			fin = QTextStream(fp)
			fin.setCodec("UTF-8")

			compilerVersion = fin.readAll()

			fin = None
			fp.close()
		except Exception, e:
			pass

		with Layout.HBox(5):
			self.Layout.img("resource/logoIcon64.png").setFixedSize(80,80)

			with Layout.VBox(5):
				self.Layout.label(self.trUtf8("Client version hash : ") + compilerVersion)
				self.Layout.gap(10)
				self.Layout.label(self.trUtf8("Copyrightⓒ 2014-2015 Nooslab"))
				self.Layout.gap(10)
				self.Layout.label(self.trUtf8("이 프로그램은 누구나 자유롭게 사용할 수 있습니다."))
				# self.Layout.gap(10)
				# self.Layout.label(self.trUtf8("Special Thanks To"))
				# self.Layout.label(self.trUtf8("블루"))
				# self.Layout.label(self.trUtf8("하언"))
				# self.Layout.label(self.trUtf8(""))
				# self.Layout.label(self.trUtf8(""))
				pass
				
	def Modified(self):
		self.modify = True
		self.close()

	def exec_(self):
		super(AboutPiniWindow,self).exec_()
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
