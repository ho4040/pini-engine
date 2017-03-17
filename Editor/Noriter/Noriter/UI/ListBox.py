from PySide import QtCore,QtGui
from Noriter.UI import Widget as nWidget

class ListBox(QtGui.QWidget) : 
	#signal
	changed = QtCore.Signal(list)
	changedIndex = QtCore.Signal(list)
	clicked = QtCore.Signal(int)
	doubleClicked = QtCore.Signal(int)
	def __init__(self,factory,data=None,orien=True,parent=None):
		super(ListBox,self).__init__(parent)
		self._data = data
		self._factory = factory

		self._scroll = QtGui.QScrollArea(self)
		self._scrollWidget = QtGui.QWidget(self)
		
		if orien:
			self._layout = QtGui.QVBoxLayout(self._scrollWidget)
		else:
			self._layout = QtGui.QHBoxLayout(self._scrollWidget)
		self.orientation = orien

		self._scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self._scroll.setWidgetResizable(True)
		self._scroll.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

		self._scroll.setWidget(self._scrollWidget)
		self._scrollWidget.setLayout(self._layout)

		contentlayout = QtGui.QVBoxLayout(self)
		contentlayout.addWidget(self._scroll)
		self.setLayout(contentlayout)

		contentlayout.setContentsMargins(0, 0, 0, 0)
		contentlayout.setSpacing(0)

		self._layout.setContentsMargins(0, 0, 0, 0)
		self._layout.setSpacing(0)

		self.widgets = []
		self.selectedWidgets = []

		self.shift 	= False
		self.alt 	= False

		if self._data is not None:
			self.update()

	@property
	def data(self):
		return self._data
	@data.setter
	def data(self, value):
		self._data = value
		self.update()

	@property
	def factory(self):
		return self._factory
	@factory.setter
	def factory(self,fac):
		self._factory = fac
		self.update()

	def keyPressEvent(self,event):
		self.shift = event.modifiers() == QtCore.Qt.ShiftModifier
		self.alt = event.modifiers() == QtCore.Qt.AltModifier

	def keyReleaseEvent(self,event):
		self.shift = False
		self.alt = False

	def update(self):
		self.removeAllWidget()
		from Noriter.UI.Layout import Layout

		lc = Layout.getInstance()
		area = 0
		for v in self._data:
			widget = nWidget.Widget(self)
			layout = lc.OnWidget(widget)
			
			area += self.generateWidget(v)
			
			lc.End(layout)

			widget.data = v

			self._layout.addWidget(widget)
			widget.mouseClick.connect(self.itemClicked)
			widget.mouseDoubleClick.connect(self.itemDoubleClicked)

			self.widgets.append(widget)

		if self.orientation : 
			self._scrollWidget.setFixedHeight(area)
		else:
			self._scrollWidget.setFixedWidth(area)

	def indexAt(self,widget):
		i=0
		for w in self.widgets:
			if w == widget:
				return i
			i += 1

	def widgetAt(self,i):
		return self.widgets[i]

	def itemDoubleClicked(self,widget,x,y):
		idx = self.indexAt(widget)
		self.selectIndex(idx)

		self.doubleClicked.emit(idx)

	def itemClicked(self,widget,x,y):
		idx = self.indexAt(widget)
		self.selectIndex(idx)

		self.clicked.emit(idx)

	def clearSelected(self):
		for widget in self.selectedWidgets:
			if hasattr(widget,"pal") :
				widget.setPalette(widget.pal)
		self.selectedWidgets = []

	def selectIndices(self,idxs=None):
		if idxs is not None:
			self.clearSelected()
			for i in idxs:
				self.__select__(self.widgetAt(i))

			self.changed.emit(self.selectedWidgets)
			self.changedIndex.emit(idxs)
		else:
			return self.selectedWidgets

	def selectIndex(self,idx=None):
		if idx is not None:
			self.clearSelected()
			self.__select__(self.widgetAt(idx))

			self.changed.emit(self.selectedWidgets)
			self.changedIndex.emit([idx])
		else:
			return self.selectedWidgets

	def __select__(self,widget):
		if not hasattr(widget,"pal") :
			widget.pal = widget.palette();

		Pal = QtGui.QPalette()
		Pal.setColor(QtGui.QPalette.Background, QtGui.QColor(100,100,100,125))
		widget.setAutoFillBackground(True)
		widget.setPalette(Pal)

		self.selectedWidgets.append(widget)

	def generateWidget(self,v):
		if self._factory is not None:
			return self._factory(v)

	def removeAllWidget(self):
		self.widgets = []

		indexes = range(self._layout.count())
		indexes.sort(reverse=True)
		for index in indexes:
			item = self._layout.takeAt(index)
			widget = item.widget()
			if widget: widget.deleteLater()

		self.clearSelected()
