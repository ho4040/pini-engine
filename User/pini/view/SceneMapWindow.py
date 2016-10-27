# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PySide.QtGui import *
from PySide.QtCore import *

from Noriter.UI.ModalWindow import ModalWindow 
from Noriter.UI.Window import Window 
from Noriter.utils.Settings import Settings
from Noriter.views.NoriterMainWindow import * 

from controller.ProjectController import ProjectController
from controller.SceneListController import SceneListController

import json
import os

class GraphicsLine(QGraphicsLineItem):
	def __init__(self, obj1, order1, obj2, order2):
		super(GraphicsLine, self).__init__()
		self.obj1 = obj1
		self.obj2 = obj2
		self.order1 = order1
		self.order2 = order2

		obj1.lines.append(self)
		obj2.lines.append(self)

		self.setZValue(101)
		self.currentPath()

	def currentPath(self):
		path = QtGui.QPainterPath()

		pos1 = self.obj1.outputSlotPos(self.order1)
		pos2 = self.obj2.inputSlotPos(self.order2)

		s1 = pos1
		s2 = QPoint(pos2.x(),pos1.y())
		s3 = QPoint(pos1.x(),pos2.y())
		s4 = pos2

		path.moveTo(s1)
		#path.cubicTo(s2,s3,s4)
		path.lineTo(s4)

		self.setLine(s1.x(),s1.y(),s4.x(),s4.y())

		return path

	def shape(self):
		return self.currentPath()

	def paint(self, painter, option, widget=None):
		super(GraphicsLine, self).paint(painter, option, widget)
		pen1 = QPen(QColor(89,89,89))
		pen1.setWidth(3)

		pen2 = QPen(QColor(22,22,22))
		pen2.setWidth(5)

		path = self.currentPath()
		
		painter.setPen(pen2)
		painter.drawPath(path);
		painter.setPen(pen1)
		painter.drawPath(path);


class GraphicsObject(QGraphicsItem):
	def __init__(self, name, obj):
		super(GraphicsObject, self).__init__()

		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setFlag(QGraphicsItem.ItemIsMovable)

		self.background = None

		self.lines = []

		self._height = 25
		self.connects = obj["parse"]["connects"]
		if len(self.connects) > 0 : 
			self._height += len(self.connects)*25

		self.name = name.replace(".scene","")
		# for k in range(0,len(self.connects)):
		# 	self.connects[k] = self.connects[k].replace(".scene","")

		self.initBackground()

	def itemChange(self, change, value):
		if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
			self.scene().update()
			#print "update",len(self.lines)
			#for v in self.lines : 
			#	v.update()			

		return QGraphicsItem.itemChange(self, change, value)

	def initBackground(self):
		background = QFrame()
		labels = QFrame(background)
		background.resize(self.width(),self.height())
		labels.resize(self.width(),20)
		labels.move(0,0)

		background.setStyleSheet("*{background-color:rgba(120,120,120,150)}")
		if self.name == u"메인.lnx" : 
			labels.setStyleSheet("*{background-color:rgba(150,90,90,150)}")
		else:
			labels.setStyleSheet("*{background-color:rgba(90,90,90,150)}")

		radius_tl = 10
		radius_tr = 10
		radius_bl = 10
		radius_br = 10

		width = self.width()-1;
		height = self.height()-1;
		region = QRegion(0, 0, width, height, QRegion.Rectangle);

		#// top left
		rounded = QRegion(0, 0, 2*radius_tl, 2*radius_tl, QRegion.Ellipse);
		corner = QRegion(0, 0, radius_tl, radius_tl, QRegion.Rectangle);
		region = region.subtracted(corner.subtracted(rounded));

		#// top right
		rounded = QRegion(width-2*radius_tr, 0, 2*radius_tr, 2*radius_tr, QRegion.Ellipse);
		corner = QRegion(width-radius_tr, 0, radius_tr, radius_tr, QRegion.Rectangle);
		region = region.subtracted(corner.subtracted(rounded));

		#// bottom right
		rounded = QRegion(width-2*radius_br, height-2*radius_br, 2*radius_br, 2*radius_br, QRegion.Ellipse);
		corner = QRegion(width-radius_br, height-radius_br, radius_br, radius_br, QRegion.Rectangle);
		region = region.subtracted(corner.subtracted(rounded));

		#// bottom left
		rounded = QRegion(0, height-2*radius_bl, 2*radius_bl, 2*radius_bl, QRegion.Ellipse);
		corner = QRegion(0, height-radius_bl, radius_bl, radius_bl, QRegion.Rectangle);
		region = region.subtracted(corner.subtracted(rounded));

		background.setMask(region)

		self.background = QPixmap(self.width(),self.height()); 
		self.background.fill(Qt.transparent);
		background.render(self.background, QPoint(), QRegion(self.boundingBox()));
		
		painter = QPainter(self.background)
		painter.setPen(QPen(QColor(28,28,28)))
		#painter.setBrush(QBrush(QColor(120,120,120,200)))
		rect = self.boundingBox()
		rect.setWidth(rect.width()-1)
		rect.setHeight(rect.height()-1)
		painter.drawRoundedRect(rect, 10.0, 10.0)

	def width(self):
		return self.boundingBox().width()

	def height(self):
		return self.boundingBox().height()

	def boundingBox(self):
		return QRect(0,0,100,self._height)

	def boundingRect(self):
		b = self.boundingBox()
		return QRect(b.x()-2,0,b.width()+5,self._height)
	
	def inputSlotPos(self,order):
		return self.mapToScene(0,35+order*23)
	
	def outputSlotPos(self,order):
		return self.mapToScene(100,35+order*23)

	def paint(self, painter, option, widget=None):
		painter.setPen(QPen(QColor(28,28,28)))
		painter.drawPixmap(QPoint(0,0),self.background)
		painter.drawText(QRect(0,0,self.boundingBox().width(),25),Qt.AlignCenter,self.name)

		c = 0
		for v in self.connects : 
			if v["type"] == "bookmark":
				# 북마크 지점
				painter.setBrush(QBrush(QColor(204,199,43)))
				painter.drawEllipse(QPoint(0,35+c*23),4,4)
				painter.drawText(QPoint(8,40+c*23),v["name"])
			elif v["type"] == "goto":
				# 북마크이동 지점
				painter.setBrush(QBrush(QColor(99,205,95)))
				painter.drawEllipse(QPoint(100,35+c*23),4,4)

				rect = painter.fontMetrics().boundingRect(v["name"])
				painter.drawText(QPoint(92-rect.width(),40+c*23),v["name"])
			elif v["type"] == "script":
				# 스크립트 매크로 지점
				painter.setBrush(QBrush(QColor(99,205,95)))
				painter.drawEllipse(QPoint(100,35+c*23),4,4)

				rect = painter.fontMetrics().boundingRect(v["file"])
				painter.drawText(QPoint(92-rect.width(),40+c*23),v["file"])

			c+=1


class GraphicsScene(QGraphicsScene):
	def __init__(self, parent=None):
		super(GraphicsScene, self).__init__(parent)
		self.initBackground()

	def initBackground(self):
		s = 150
		pixmap = QPixmap(s, s)
		painter = QPainter(pixmap)
		painter.fillRect(QRect( 0, 0, s, s), QColor(57,57,57))
		
		pen = QPen(QColor(45,45,45))
		pen1 = QPen(QColor(32,32,32))
		pen1.setWidth(2)
		
		painter.setPen(pen)
		for i in range(0,5) : 
			x = s / 5 * i
			y = s / 5 * i
			if i == 4 : 
				painter.setPen(pen1)
			painter.drawLine(x,0,x,s)
			painter.drawLine(0,y,s,y)
		painter.end()

		self.setBackgroundBrush(QBrush(pixmap))

		'''
		self.background = QGraphicsRectItem(0,0,640,480)
		self.addItem(self.background)

		brush = QBrush()
		brush.setColor(QColor(150,150,150,200))
		brush.setStyle(Qt.SolidPattern)

		pen = QPen()
		pen.setStyle(Qt.DashLine)
		pen.setColor(QColor(80,80,80))
		self.background.setBrush(brush)
		self.background.setPen(pen)
		'''

class GraphicsView(QGraphicsView):
	def __init__(self, parent=None):
		super(GraphicsView, self).__init__(parent)

		self.scene = GraphicsScene()
		self.setScene(self.scene)

		self.objs = []
		self.main = None

	def clearObj(self) :
		self.scene.clear()
		self.objs = []
		self.main = None

	def addObj(self, name, obj) : 
		go = GraphicsObject(name, obj)
		self.scene.addItem(go)

		if name == "main" : 
			self.main = (name,go)
		go.setZValue(100)
		self.objs.append((name,go))

	def findObj(self,targetinfo,prefer):
		if targetinfo["type"] == "script":
			for v in self.objs : 
				if v[0] == targetinfo["file"]: 
					return v,0

		elif targetinfo["type"] == "goto":
			# 먼저 같은 파일을 먼저 검색합니다
			i=0
			for n in prefer[1].connects:
				if n["type"] == "bookmark" and n["name"] == targetinfo["name"]:
					return prefer,i
				i+=1

			for v in self.objs :
				i=0
				for n in v[1].connects:
					if n["type"] == "bookmark" and n["name"] == targetinfo["name"]:
						return v,i
					i+=1
		return None,0

	def arrangement(self):
		objList = self.objs[:]

		maxY = 0
		for v in self.objs :
			x,y,w,h = v[1].x(),v[1].y(),v[1].width(),v[1].height()
			if v in objList :
				v[1].setPos(x,maxY)
				y = maxY

			if y+h > maxY : 
				maxY = y+h

			i = 0
			for c in v[1].connects : 
				n,j = self.findObj(c,v)
				if n :#and n in objList :
					n[1].setPos(x+w+50,y)

					y += 20
					
					if y > maxY : 
						maxY = y

					line = GraphicsLine(v[1],i,n[1],j)
					self.scene.addItem(line)

					if n in objList : 
						del objList[objList.index(n)]

				i+=1

			if len(v[1].connects) > 0 : 
				if v in objList : 
					del objList[objList.index(v)]

		x,y = 0,maxY
		for v in objList : 
			v[1].setPos(x,y)
			x += v[1].width()+50

## 빈파일이면 obj파일 생성이 안됨.
## obj파일만 있고 scene파일은 삭제해버리면 못찾음, 연결 안되었다고 경고처리해줘야할듯?
## scene이 없고 obj는 있는 경우
## obj는 있고 scene은 없는 경우
## 실시간 수정. obj파일이 수정 되면 다시 리로드하게. 

class SceneMapWindow(Window):
	def sizeHint(self):
		return QSize(600,500)

	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not SceneMapWindow._instance:
			SceneMapWindow._instance = super(SceneMapWindow,cls).__new__(cls,*args,**kwargs)

		return SceneMapWindow._instance

	def __init__(self,parent=None):
		if SceneMapWindow._isInit:
			return 
		SceneMapWindow._isInit = True
		
		super(SceneMapWindow,self).__init__(parent)
		self.setWindowTitle(u"씬맵")

	def parseObj(self,obj):
		connects = []
		scriptCallValue = ""
		scriptCallRun = True
		imageCallValue = "__VOID__"

		connects.append({"type":"bookmark","name":u"#진입"})

		for v in obj : 
			if v["t"] == 1 and v["L"] == u"스크립트.실행" : #인자
				if v["R"]["t"] == 2 :
					scriptCallRun = v["R"]["v"] == u"예"
			elif v["t"]==1 and v["L"] == u"스크립트.파일명" : #인자
				if v["R"]["t"] == 2 : 
					scriptCallValue = v["R"]["v"]
			elif v["t"]==1 and v["L"] == u"이미지.북마크이동" : #인자
				if v["R"]["t"] == 2 :
					imageCallValue = v["R"]["v"]
			elif v["t"] == 5 : # 매크로 호출
				if v["name"] == u"스크립트":
					if scriptCallRun:
						connects.append({"type":"script","file":scriptCallValue})
					else:
						scriptCallRun = True
				elif v["name"] == u"대화":
					for ext in v["extend"]:
						if ext["t"]==0 and ext["v"]["name"] == u"연결":
							connects.append({"type":"goto","name":ext["v"]["args"][0][1:-1]})
				elif v["name"] == u"이미지":
					if imageCallValue != "__VOID__":
						connects.append({"type":"goto","name":imageCallValue})
						imageCallValue = "__VOID__"
			elif v["t"] == 3 : # 북마크
				connects.append({"type":"bookmark","name":v["name"]})
			elif v["t"] == 4 : # 북마크이동
				connects.append({"type":"goto","name":v["goto"]["v"]})
			elif v["t"] == 11 : # 하이퍼북마크
				connects.append({"type":"goto","name":v["goto"]["v"]})

		return {"connects":connects}

	def refreshMap(self):
		self.view.clearObj()

		self.objMap = {}
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

					self.objMap[idx+".lnx"] = {"obj":obj,"parse":self.parseObj(obj)}

		####build!
		for k,v in self.objMap.iteritems():
			self.view.addObj( k.replace(".obj","") , v )

		self.view.arrangement()

	@LayoutGUI
	def GUI(self):
		self.view = self.Layout.addWidget(GraphicsView(self))
