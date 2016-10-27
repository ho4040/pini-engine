# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide import QtCore,QtGui
from functools import wraps

from Noriter.UI import Widget as nWidget
from Noriter.UI import ListBox as nListBox
from Noriter.UI import Timeline as nTimeline
from Noriter.UI import TabWidget as nTab
from Noriter.UI.Splitter import Splitter

# mainWindow -> dock
# window -> widget

class Layout(object):
	class HBox(QtGui.QHBoxLayout):
		def __init__(self,spacing=0):
			super(Layout.HBox, self).__init__(None)
			self.Layout = Layout.getInstance()
			self.setContentsMargins(0, 0, 0, 0)
			self.setSpacing(spacing)

		def __enter__(self):
			self.Layout.Begin(self)
			return self

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.Layout.End(self)

		def Next(self):
			print "HBox Next"

	class VBox(QtGui.QVBoxLayout):
		def __init__(self,spacing=0):
			super(Layout.VBox, self).__init__(None)
			self.Layout = Layout.getInstance()
			self.setContentsMargins(0, 0, 0, 0)
			self.setSpacing(spacing)

		def __enter__(self):
			self.Layout.Begin(self)
			return self

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.Layout.End(self)

		def Next(self):
			print "HBox Next"
				
	class GridBox(QtGui.QGridLayout):
		def __init__(self,spacing=0):
			super(Layout.GridBox, self).__init__(None)
			self.Layout = Layout.getInstance()
			self.setContentsMargins(0, 0, 0, 0)
			self.setSpacing(spacing)

			self.x = 0
			self.y = 1

		def __enter__(self):
			self.Layout.Begin(self)
			return self

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.Layout.End(self)

		def Next(self):
			self.x = 0
			self.y += 1

		def addWidget(self, widget):
			super(Layout.GridBox, self).addWidget(widget, self.y, self.x)
			self.x += 1

		def addLayout(self, layout):
			super(Layout.GridBox, self).addLayout(layout, self.y, self.x)
			self.x += 1

		def addItem(self, item):
			super(Layout.GridBox, self).addItem(item, self.y, self.x)
			self.x += 1

		def addStretch(self):
			pass

	def __init__(self):
		self.widgetStack = []
		self.layoutStack = []
		self.mainWindow = None
		self.menubars = {}
		self.menuSeparatorCnt = 0

	_instance = None

	@staticmethod
	def getInstance():
		if Layout._instance is None:
			Layout._instance = Layout()
		return Layout._instance

	def OnWidget(self, widget):
		if not hasattr(widget,"_layout"):
			widget._layout = None
			
		if widget._layout is None:
			layout = None
			if isinstance(widget, QtGui.QDockWidget):
				contents = QtGui.QWidget()
				widget.setWidget(contents)

				layout = QtGui.QVBoxLayout(contents)
				layout.setObjectName("dockLayout")
			elif isinstance(widget, QtGui.QMainWindow):
				if self.mainWindow is None:
					self.mainWindow = widget
				else:
					print("ERROR : Layout.OnWidget MainWindow Error")
					return
				self.buildMenu()

				centralwidget = QtGui.QWidget(widget)
				layout = QtGui.QVBoxLayout(centralwidget)

				widget.setCentralWidget(centralwidget)
			elif isinstance(widget, QtGui.QDialog):
				layout = QtGui.QVBoxLayout(widget)
			elif isinstance(widget, QtGui.QWidget):
				layout = QtGui.QVBoxLayout(widget)

			if layout is None:
				print("ERROR : Layout.OnWidget")
				return

			layout.setContentsMargins(2,2,2,2)
			layout.setSpacing(0)
			widget._layout = layout

		self.widgetStack.append(widget)
		self.layoutStack.append([])
		self.Begin(widget._layout)

		return widget._layout

	def Begin(self,box):
		self.layoutStack[-1].append(box)

	def End(self,box):
		lastLayout = self.layoutStack[-1]
		if len(lastLayout) <= 0:
			return

		last = lastLayout[-1]
		if last == box:
			if len(lastLayout) > 1:
				lastLayout[-2].addLayout(last)

			lastLayout.pop()

		if len(lastLayout) == 0:
			self.layoutStack.pop()
			self.widgetStack.pop()

	def Next(self):
		if len(self.layoutStack[-1]) <= 0:
			return
		self.layoutStack[-1][-1].Next()

	@property
	def widget(self):
		if len(self.widgetStack) == 0:
			return None
		return self.widgetStack[-1]

	###################################
	######ui component
	###################################
	def button(self, text, func):
		if self.widget is None: return

		btn = QtGui.QPushButton(self.widget)
		btn.setMinimumSize(0,30)
		btn.setText(unicode(text))
		if func is not None:
			btn.clicked.connect(func)
		self.addWidget(btn)
		return btn

	def label(self,text):
		if self.widget is None: return
		label = QtGui.QLabel(self.widget)
		label.setText(unicode(text))
		label.setStyleSheet("*{background-color:none;}")
		self.addWidget(label)
		return label

	def spacer(self):
		if self.widget is None: return
		self.layoutStack[-1][-1].addStretch()

	def gap(self,gap):
		if self.widget is None: return
		w = QtGui.QWidget(self.widget)
		w.setFixedSize(gap,gap)
		w.setStyleSheet("*{background-color:none;}")
		self.addWidget(w)
		return w

	def slider(self, value, min, max, changed):
		if self.widget is None: return
		s = QtGui.QSlider(self.widget)
		s.setValue(value)
		s.setMaximum(max)
		s.setMinimum(min)
		s.setOrientation(QtCore.Qt.Horizontal)
		if changed is not None:
			s.valueChanged.connect(changed)
		self.addWidget(s)

		return s

	def canvas(self,x,y):
		if self.widget is None: return
		s = nWidget.Widget(self.widget)
		s.setFixedSize(x,y)
		self.addWidget(s)
		return s

	def input(self, text, changed):
		if self.widget is None: return
		s = QtGui.QLineEdit(self.widget)
		s.setText(text)
		if changed is not None:
			s.textChanged.connect(changed)
		self.addWidget(s)
		return s

	def stepper(self, value, changed):
		if self.widget is None: return
		s = QtGui.QSpinBox(self.widget)
		s.setValue(value)
		if changed is not None:
			s.valueChanged.connect(changed)
		self.addWidget(s)
		return s

	def checkbox(self,text, bool, changed):
		if self.widget is None: return
		s = QtGui.QCheckBox(self.widget)
		s.setChecked(bool)
		s.setText(text)
		if changed is not None:
			s.stateChanged.connect(changed)
		self.addWidget(s)
		return s

	def radiobox(self,text, bool, changed):
		if self.widget is None: return
		s = QtGui.QRadioButton(self.widget)
		s.setText(text)
		s.setChecked(bool)
		if changed is not None:
			s.clicked.connect(changed)
		self.addWidget(s)
		return s

	def textedit(self, text, changed):
		if self.widget is None: return
		s = QtGui.QTextEdit(self.widget)
		s.setText(text)
		if changed is not None:
			s.textChanged.connect(changed)
		self.addWidget(s)
		return s

	def listbox(self,factory,data,ori = True):
		if self.widget is None: return
		listbox = nListBox.ListBox(factory,data,ori,self.widget)
		self.addWidget(listbox)
		return listbox

	def timeline(self, data):
		if self.widget is None: return
		timeline = nTimeline.Timeline(data,self.widget)
		self.addWidget(timeline)
		return timeline

	def hline(self):
		if self.widget is None: return
		line = QtGui.QFrame(self.widget)
		line.setFrameStyle(QtGui.QFrame.HLine)
		self.addWidget(line)
		line.setFixedHeight(1)
		return line

	def vline(self):
		if self.widget is None: return
		line = QtGui.QFrame(self.widget)
		line.setFrameStyle(QtGui.QFrame.VLine)
		line.setFixedWidth(1)
		self.addWidget(line)
		return line

	def img(self,path):
		if self.widget is None: return
		label = QtGui.QLabel(self.widget)
		label.setPixmap(QtGui.QPixmap(path))
		label.setScaledContents(True)
		self.addWidget(label)
		return label

	def tab(self):
		if self.widget is None: return 
		t = nTab.TabWidget(self.widget)
		self.addWidget(t)
		return t

	def splitter(self,orientation):
		if self.widget is None: return 
		w = Splitter(self.widget)
		self.addWidget(w)
		return w

	def combo(self,arr,editable=False):
		if self.widget is None: return 
		cb = QtGui.QComboBox(self.widget)
		cb.addItems(arr)
		cb.setEditable(editable)
		self.addWidget(cb)
		return cb

	def clear(self):
		if len(self.layoutStack[-1]) <= 0:
			return False

		last = self.layoutStack[-1][-1]
		self._clear(last)

		return True

	def _clear(self,layout):
		indexes = range(layout.count())
		indexes.sort(reverse=True)
		for index in indexes:
			item = layout.takeAt(index)
			if isinstance(item,QtGui.QLayout) : 
				self._clear(item)
			widget = item.widget()
			if widget: widget.deleteLater()

	##################################
	def addWidget(self, widget):
		if len(self.layoutStack[-1]) <= 0:
			print "addWidget failed!!!!!!"
			return
		last = self.layoutStack[-1][-1]
		last.addWidget(widget)
		return widget

	def addItem(self, item):
		if len(self.layoutStack[-1]) <= 0:
			return
		last = self.layoutStack[-1][-1]
		last.addItem(item)
		return item
	###################################

	def menu(self, text, keyseq, func):
		arr = unicode(text).split("/")
		current = self.menubars
		for _str in arr:
			if _str == "0" : 
				_str = "sep_"+str(self.menuSeparatorCnt)
				self.menuSeparatorCnt += 1
			if _str not in current:
				current[_str] = {}
			current = current[_str]

		current['__func__'] = func
		current['__key__'] = keyseq

		self.buildMenu()

	def buildMenu(self, current=None):
		if self.mainWindow is None:
			return

		if current is None:
			current = self.menubars
			if '__menu__' not in self.menubars:
				menubar = QtGui.QMenuBar()
				self.menubars['__menu__'] = menubar
				self.mainWindow.setMenuBar(menubar)


		for k, v in current.iteritems():
			if isinstance(v, dict):
				if '__menu__' not in current[k]:
					if k.startswith("sep_"):
						current[k]['__menu__'] = 1
						current['__menu__'].addSeparator()

					else:

						b = set(current[k].keys()) - set(("__menu__", "__func__","__key__"))
						if len(b) == 0:
							current[k]['__menu__'] = QtGui.QAction(self.mainWindow)
							current[k]['__menu__'].setObjectName(k)
							current[k]['__menu__'].setText(k)
							if '__key__' in current[k] and current[k]["__key__"] : 
								current[k]['__menu__'].setShortcuts(current[k]["__key__"])

							if '__func__' in current[k]:
								current[k]['__menu__'].triggered.connect(current[k]['__func__'])

							current['__menu__'].addAction(current[k]['__menu__'])
						else:
							current[k]['__menu__'] = QtGui.QMenu(current['__menu__'])
							current[k]['__menu__'].setObjectName(k)
							current[k]['__menu__'].setTitle(k)

							current['__menu__'].addAction(current[k]['__menu__'].menuAction())
				elif k == "0":
					return

				self.buildMenu(v)

def LayoutGUI(func):
	def __(self, *args, **kwargs):
		l = Layout.getInstance().OnWidget(self)
		func(self, *args, **kwargs)
		Layout.getInstance().End(l)
	return __

def MenuBar(text,keyseq=None):
	def wrapper(func):
		Layout.getInstance().menu(text,keyseq, func)
		@wraps(func)
		def __(self, *args, **kwargs):
			return func(self, *args, **kwargs)
		return __

	return wrapper


'''
def OnGUI(arg1,arg2,arg3):
	#print arg1,arg2,arg3
	def wrapper(func):
		#print 'wowinit'
		@wraps(func)
		def _OnGUI(self, *args, **kwargs):
			#print 'self is %s' % self
			#print "Begin", func.__name__
			func(self, *args, **kwargs)
			#print "End", func.__name__
		return _OnGUI
	return wrapper;
'''