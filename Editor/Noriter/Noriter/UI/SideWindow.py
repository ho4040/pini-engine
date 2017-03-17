from PySide import QtCore,QtGui

from Noriter.UI.Layout import *
from Noriter.UI import NoriterWindow as nWin

class SideWindow (nWin.NoriterWindow, QtGui.QWidget):
	def __init__(self):
		super(SideWindow, self).__init__()
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

	@LayoutGUI
	def GUI(self):
		pass


