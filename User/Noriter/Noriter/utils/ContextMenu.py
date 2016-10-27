from PySide.QtCore import Qt,QPoint,Signal
from PySide.QtGui  import QWidget,QAction,QMenu

class ContextMenu(QMenu):
	#Signal
	itemClicked = Signal(QWidget,QAction)

	def __init__(self,arr,parent=None):
		super(ContextMenu,self).__init__(parent)

		self.setTitle(self.tr(arr[0]))

		if isinstance(parent,QWidget):
			self.setParent(parent)
			parent.setContextMenuPolicy(Qt.CustomContextMenu)
			parent.customContextMenuRequested.connect(self.mousePressed)

		def traverseForInit(arr,target):
			for item in arr[1:]:
				if isinstance(item,list):
					target.addMenu(ContextMenu(item,target))
				elif isinstance(item,basestring):
					target.addAction(QAction(target.tr(item), target))
				elif isinstance(item,tuple):
					title,data = item
					action = QAction(target.tr(title), target)
					action.setData(data)
					target.addAction(action)
				else:
					target.addSeparator()

		traverseForInit(arr,self)

	def show(self,pos=None,relativeWidget=None):
		if not pos:
			pos = QPoint(0,0)

		parentWidget = self.parentWidget()
		if relativeWidget:
			parentWidget = relativeWidget
		if parentWidget:
			pos = parentWidget.mapToGlobal(pos)

		action = self.exec_(pos)
		if action:
			self.itemClicked.emit(self,action)

	def mousePressed(self,pos):
		self.show()




