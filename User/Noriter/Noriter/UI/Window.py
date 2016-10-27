from PySide import QtCore,QtGui

from Noriter.UI.Layout import *
from Noriter.UI import NoriterWindow as nWin

class Window (nWin.NoriterWindow, QtGui.QDockWidget):
	def __init__(self,parent=None):
		self.backgroundColor = QtGui.QColor(81,81,81)

		super(Window, self).__init__(parent)
		QtCore.QMetaObject.connectSlotsByName(self)
		
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.setParent(self.Layout.mainWindow)
		self.setFloating(True)
		self.show()

	@LayoutGUI
	def GUI(self):
		pass

	def paintEvent( self, e ):
		painter = QtGui.QPainter(self)
		painter.setBrush(self.backgroundColor)
		if self.isFloating() :
			painter.drawRect(-1,-1,self.width()+2,self.height()+2)
		else: 
			painter.drawRect(-1,10,self.width()+2,self.height()+2)
			
			pen = painter.pen()
			pen.setColor(QtGui.QColor(0,0,0))
			painter.setPen(pen)

			painter.drawLine(0,5,0,self.height())
			painter.drawLine(self.width()-1,5,self.width()-1,self.height())
			painter.drawLine(0,self.height(),self.width(),self.height())
		
		painter.end()
		painter = None

		super(Window,self).paintEvent(e);

	def setBackgroundColor(color):
		self.backgroundColor = color
		self.update()