
from PySide.QtGui import *
from PySide.QtCore import *

from Noriter.UI.Layout import *
from Noriter.UI import NoriterWindow as nWin

class MainWindow (nWin.NoriterWindow, QMainWindow):
	closeSignal = Signal(object,QCloseEvent)

	def __init__(self):
		super(MainWindow, self).__init__()
		QMetaObject.connectSlotsByName(self)
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.show()

	@LayoutGUI
	def GUI(self):
		pass

	def closeEvent(self,event):
		super(MainWindow,self).closeEvent(event)
		self.closeSignal.emit(self,event)