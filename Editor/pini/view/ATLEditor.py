# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from Noriter.UI.Timeline import *
from Noriter.UI.Layout import *
from Noriter.UI.Window import Window
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController

import json

class ATLGraphicsObject(QGraphicsItem):
	def __init__(self, name, obj):
		super(ATLGraphicsObject,self).__init__()

		self.background = None
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setFlag(QGraphicsItem.ItemIsMovable)

	def boundingBox(self):
		return QRect(0,0,130,25)

	def boundingRect(self):
		b = self.boundingBox()
		return b

	def paint(self, painter, option, widget=None):
		painter.drawRect(self.boundingRect())
		painter.setPen(QPen(QColor(255,255,255)))
		painter.drawText(QRect(0,0,130,25),Qt.AlignCenter,u"GRAPHICS_OBJECT")

	def mouseMoveEvent(self, e):
		super(ATLGraphicsObject,self).mouseMoveEvent(e)
		# print "ATLGraphicsObject.mouseMoveEvent() called."

	def mousePressEvent(self, e):
		super(ATLGraphicsObject,self).mousePressEvent(e)
		# print "ATLGraphicsObject.mousePressEvent() called."

	def mouseReleaseEvent(self, e):
		super(ATLGraphicsObject,self).mouseReleaseEvent(e)
		# print "ATLGraphicsObject.mouseReleaseEvent() called."


class ATLGraphicsScene(QGraphicsScene):
	def __init__(self, parent=None):
		super(ATLGraphicsScene,self).__init__(parent)
		self.initBackground()

	def initBackground(self):
		s = 200
		pixmap = QPixmap(s, s)
		painter = QPainter(pixmap)
		painter.fillRect(QRect( 0, 0, s, s), QColor(57,57,57))
		
		pen = QPen(QColor(45,45,45))
		pen1 = QPen(QColor(32,32,32))
		pen1.setWidth(2)
		
		painter.setPen(pen)
		gridSize = 10
		for i in range(0,gridSize) : 
			x = s / gridSize * i
			y = s / gridSize * i
			if i == gridSize - 1 : 
				painter.setPen(pen1)
			painter.drawLine(x,0,x,s)
			painter.drawLine(0,y,s,y)
		painter.end()

		self.setBackgroundBrush(QBrush(pixmap))


class ATLGraphicsView(QGraphicsView):
	def __init__(self, parent=None):
		super(ATLGraphicsView,self).__init__(parent)

		self.scene = ATLGraphicsScene()
		self.setScene(self.scene)

		go = ATLGraphicsObject("Test", None)
		self.scene.addItem(go)

class ATLEditor(Window):
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not ATLEditor._instance:
			ATLEditor._instance = super(ATLEditor,cls).__new__(cls,*args,**kwargs)

		return ATLEditor._instance

	def __init__(self):
		if ATLEditor._isInit:
			return 

		self.timelineMap = []
		ATLEditor._isInit = True
		super(ATLEditor,self).__init__(NoriterMain())
		self.setWindowTitle(u"애니메이션 편집기")
		self.resize(400,300)

	@LayoutGUI
	def GUI(self):
		self.Layout.clear()

		with Layout.VBox():
			self.graphicsView = ATLGraphicsView()

			self.splitter = self.Layout.splitter(None)
			self.splitter.setOrientation(Qt.Vertical)
			self.splitter.addWidget(self.graphicsView)
			self.timeline = nTimeline.Timeline(self.timelineMap)
			self.timeline.changed.connect(self.onChanged)
			self.splitter.addWidget(self.timeline)


	def onChanged(self):
		print "ATLEditor.onChanged() called"

	def parseObj(self,obj):
		animations = []

		for v in obj : 
			if v["t"] == 10 : # 애니메이션 
				frameKeys = json.loads(v["json"])

				for node in frameKeys["nodes"]:
					frames = []

					for frame in node["frames"]:
						frames.append((int(frame["frame"]),frame["stmts"]))

					animations.append({
						"name":frameKeys["name"] + u"." + str(int(node["idx"])),
						"frames":frames
					})

		return animations

	def refreshData(self):
		self.timelineMap = []

		PROJPATH = ProjectController().path
		OBJECTPATH = (PROJPATH + "/build/obj/").replace("\\","/")
		for root, dirs, files in os.walk(OBJECTPATH, topdown=False):
			for name in files:
				fullpath = os.path.join(root, name).replace("\\","/")
				if fullpath.find("libdef") == -1:
					idx =  fullpath.replace(OBJECTPATH+"scene/","")

					fp = QFile(fullpath)
					fp.open(QIODevice.ReadOnly | QIODevice.Text)

					fin = QTextStream(fp)
					fin.setCodec("UTF-8")

					obj = json.loads(fin.readAll())

					fin = None
					fp.close()

					self.timelineMap = self.timelineMap + self.parseObj(obj)

		self.timeline.data = self.timelineMap


