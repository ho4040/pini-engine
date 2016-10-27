from PySide import QtCore,QtGui

class Widget(QtGui.QWidget):
	def __init__(self,parent=None):
		super(Widget,self).__init__(parent)
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.dropEnable(True)
		
		from Noriter.UI.Layout import Layout
		self.Layout = Layout.getInstance()

	#signal 
	mouseClick = QtCore.Signal(object,int,int)
	mouseDoubleClick = QtCore.Signal(object,int,int)
	mouseMove = QtCore.Signal(object,int,int)
	mouseRelease = QtCore.Signal(object,int,int)
	mouseWheel = QtCore.Signal(object,int)

	keyPress = QtCore.Signal(object,int)
	keyRelease = QtCore.Signal(object,int)

	dragEnter = QtCore.Signal(object,QtGui.QDragEnterEvent)
	dragLeave = QtCore.Signal(object,QtGui.QDragLeaveEvent)
	dragMove = QtCore.Signal(object,QtGui.QDragMoveEvent)
	drop = QtCore.Signal(object,QtGui.QDropEvent)

	paint = QtCore.Signal(object,QtGui.QPainter)
	resizing = QtCore.Signal(object)

	#customContextMenuRequested
	def dropEnable(self,_b):
		self.setAcceptDrops(_b)

	def dragEnterEvent(self,event):
		super(Widget,self).dragEnterEvent(event)
		self.dragEnter.emit(self,event)
	def dragLeaveEvent(self,event):
		super(Widget,self).dragLeaveEvent(event)
		self.dragLeave.emit(self,event)
	def dragMoveEvent(self,event):
		super(Widget,self).dragMoveEvent(event)
		self.dragMove.emit(self,event)
	def dropEvent(self,event):
		super(Widget,self).dropEvent(event)
		self.drop.emit(self,event)

	def keyPressEvent(self,event):
		super(Widget,self).keyPressEvent(event)
		self.keyPress.emit(self,event.key())
	def keyReleaseEvent(self,event):
		super(Widget,self).keyReleaseEvent(event)
		self.keyRelease.emit(self,event.key())

	def paintEvent(self,event):
		super(Widget,self).paintEvent(event)
		self.paint.emit(self,QtGui.QPainter(self))
	def resizeEvent(self,event):
		super(Widget,self).resizeEvent(event)
		self.resizing.emit(self)
	def mouseDoubleClickEvent(self,event):
		super(Widget,self).mouseDoubleClickEvent(event)
		self.mouseDoubleClick.emit(self,event.pos().x(),event.pos().y())
	def mouseMoveEvent(self,event):
		super(Widget,self).mouseMoveEvent(event)
		self.mouseMove.emit(self,event.pos().x(),event.pos().y())
	def mousePressEvent(self,event):
		super(Widget,self).mousePressEvent(event)
		self.mouseClick.emit(self,event.pos().x(),event.pos().y())
	def mouseReleaseEvent(self,event):
		super(Widget,self).mouseReleaseEvent(event)
		self.mouseRelease.emit(self,event.pos().x(),event.pos().y())
	def wheelEvent(self,event):
		super(Widget,self).wheelEvent(event)
		self.mouseWheel.emit(self,event.delta())
