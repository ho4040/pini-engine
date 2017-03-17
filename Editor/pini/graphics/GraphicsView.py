# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import math, random

from PySide.QtCore import *
from PySide.QtGui import * 
from PySide.QtWebKit import *

from controller.ProjectController import *
from Noriter.views.NoriterMainWindow import *

class CameraView(QGraphicsItem):
	def __init__(self, view, parent=None):
		super(CameraView, self).__init__(parent)
		self.view = view
		self.updateCamera(50,50,500,400)

	def updateCamera(self,x,y,sx,sy):
		self.camera = {"x":x,"y":y,"w":sx,"h":sy}

	def boundingRect(self):
		size = self.view.size()
		return QRect(0,0,size.width(),size.height())

	def paint(self, painter, option, widget=None):
		mat = self.view.matrix()

		origin  = self.view.mapToScene(QPoint(0,0))
		originX = origin.x()-1
		originY = origin.y()-1
		zeroX = self.camera["x"]
		zeroY = self.camera["y"]
		sizeX = self.camera["w"]
		sizeY = self.camera["h"]
		viewSizeX = self.view.size().width()*1/mat.m11()
		viewSizeY = self.view.size().height()*1/mat.m22()

		r1 = QRect(originX,originY,viewSizeX-originX,zeroY-originY)
		r2 = QRect(originX,zeroY,zeroX-originX,viewSizeY)
		r3 = QRect(zeroX,sizeY,sizeX-zeroX,viewSizeY-sizeY)
		r4 = QRect(sizeX,zeroY,viewSizeX-sizeX,viewSizeY)

		painter.setBrush(QBrush(QColor(0,0,0,200)))
		painter.setPen(QPen(QColor(0,0,0,0)))
		painter.drawRect(r1)
		painter.drawRect(r2)
		painter.drawRect(r3)
		painter.drawRect(r4)

class DesignerScene(QGraphicsScene):
	def __init__(self, view, parent=None):
		super(DesignerScene, self).__init__(parent)

		self._view = view
		self.objList = []
		self.initBackground()
		self.initForeground()

	def initBackground(self):
		pixmap = QPixmap(80, 80)
		painter = QPainter(pixmap)
		painter.fillRect(QRect( 0, 0, 40, 40), QColor(199,199,199))
		painter.fillRect(QRect( 0,40, 40, 40), QColor(221,221,221))
		painter.fillRect(QRect(40, 0, 40, 40), QColor(221,221,221))
		painter.fillRect(QRect(40,40, 40, 40), QColor(199,199,199))
		painter.end()

		self.setBackgroundBrush(QBrush(pixmap))

		self.background = QGraphicsRectItem(0,0,640,480)
		super(DesignerScene,self).addItem(self.background)

		brush = QBrush()
		brush.setColor(QColor(150,150,150,200))
		brush.setStyle(Qt.SolidPattern)

		pen = QPen()
		pen.setStyle(Qt.DashLine)
		pen.setColor(QColor(80,80,80))
		self.background.setBrush(brush)
		self.background.setPen(pen)

	def initForeground(self):
		self.screenMask = CameraView(self._view)
		self.screenMask.setZValue(80000)
		self.addItem(self.screenMask,True)

	def fitInView(self,center=False):
		rect = self.itemsBoundingRect()
		if rect.isNull() : 
			rect = QRect(0,0,1,1)
		if center : 
			w,h = ProjectController().screenWidth,ProjectController().screenHeight
			dw,dh = rect.width() - w,rect.height() - h
			if dw > 0 : rect.setX(rect.x() - dw)
			if dh > 0 : rect.setY(rect.y() - dh)

		self.setSceneRect(rect)

	def setScreenSize(self,width,height):
		self.background.setRect(0,0,width,height)
		self.screenMask.updateCamera(0,0,width,height)

	def clear(self):
		for v in self.objList:
			super(DesignerScene,self).removeItem(v)
		self.objList = []

	def addItem(self,obj,force=None):
		super(DesignerScene,self).addItem(obj)
		if force == None:
			self.objList.append(obj)

	def removeItem(self,obj,force=None):
		super(DesignerScene,self).removeItem(obj)
		if force == None:
			self.objList.remove(obj)

	def rubberbanded(self,x,y,width,height):
		rubberRect = QRect(x,y,width,height)
		for o in self.objList:
			if rubberRect.intersects( o.ctransform.boundingBox() ) :
				o.setSelected(True)
			else:
				o.setSelected(False)

	def updatePosItems(self):
		for o in self.items():
			if o.__class__ == UIObject :
				o.updatePosItem()

	def drawForeground (self,painter,rect ):
		super(DesignerScene, self).drawForeground(painter,rect)

class DesignerView(QGraphicsView):
	MOUSE_DRAG_NONE = 0
	MOUSE_DRAG_OBJECT = 1
	MOUSE_DRAG_RUBBER = 2
	def __init__(self,parent):
		super(DesignerView,self).__init__(parent)
		self.fScaleFactor = 1
		self.fScale = 1
		self.mouseDragType = DesignerView.MOUSE_DRAG_NONE

		self.Alt = None

		self.scene = DesignerScene(self);
		self.setScene(self.scene);
		self.scene.view = self

		#########################################
		self.topLayer = QtGui.QGraphicsRectItem(0,0,0,0)
		self.topLayer.setZValue(5000000)
		self.scene.addItem(self.topLayer,True)

		##########
		self.screenInfo = QtGui.QGraphicsRectItem(0,0,130,32)
		self.screenInfo.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0,122)))
		self.screenInfo.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0)))
		self.screenInfo.setZValue(1000)
		self.screenInfo.setPos(10,10)
		self.screenInfo.setParentItem(self.topLayer)

		self.logWindow = QtGui.QGraphicsRectItem(0,0,0,0)
		self.logWindow.setParentItem(self.topLayer)

		def widgetProxy(widget,x=0,y=0):
			proxy = QtGui.QGraphicsProxyWidget()
			proxy.setWidget(widget)
			proxy.setParentItem(self.screenInfo)
			proxy.setZValue(1000)
			proxy.setPos(x,y)
			widget.setStyleSheet("*{background-color:rgba(0,0,0,0);}")
			return proxy

		s = widgetProxy(QtGui.QCheckBox(unicode("화면맞춤","utf-8")),10,10)
		self.FIVCheck = s.widget()
		self.FIVCheck.toggled.connect(self.FIVtoggled)
		self.FIVCheck.setChecked(True)

		s = widgetProxy(QtGui.QPushButton(unicode("중앙","utf-8")),85,6)
		s.widget().clicked.connect(self.screenMoveCenter)

		self.web = QGraphicsWebView(self.screenInfo)
		self.web.setHtml("""
		<script>
			(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
			(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
			})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

			ga('create', 'UA-59101417-4', 'auto');
			ga('send', 'pageview');
		</script>
		""")
		self.web.setContentsMargins(0,0,0,0)

		def loadFinished(ok):
			self.web.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.web.loadFinished.connect(loadFinished)

		def linkClicked(url):
			QDesktopServices.openUrl(url);
		self.web.linkClicked.connect(linkClicked)

		#########################################
		self.screenMoveCenter()

		self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)

		self.verticalScrollBar().valueChanged.connect(self.sliderChange)
		self.horizontalScrollBar().valueChanged.connect(self.sliderChange)
		self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff );
		self.setVerticalScrollBarPolicy ( Qt.ScrollBarAlwaysOff );

		self.logs = []
		self.delCount = 0

	def finished(self):
		self.delCount += 1
		
	def log(self,txt,color):
		for i in range(0,self.delCount):
			self.logs[i].setParentItem(None)
			self.logs[i].animg = None
			self.scene.removeItem(self.logs[i],True)
		self.logs = self.logs[self.delCount:]
		if len(self.logs) > 20 : 
			for i in range(0,len(self.logs)-20):
				self.logs[i].setParentItem(None)
				self.logs[i].animg = None
				self.scene.removeItem(self.logs[i],True)
			self.logs = self.logs[len(self.logs)-20:]

		self.delCount = 0

		text = QGraphicsTextItem(txt)
		text.animg = None
		text.setParentItem(self.logWindow)
		self.logs.append(text)
		text.setPos(0,0)

		i = 0
		for v in self.logs : 
			if v.animg : 
				v.animg.stop()
				v.animg = None

			g = QSequentialAnimationGroup()

			anim1 = QPropertyAnimation(v, "pos");
			anim1.setDuration(600);
			anim1.setStartValue(QPoint(0,v.pos().y()));
			anim1.setEndValue(QPoint(0,-(len(self.logs)-i)*22));

			anim2 = QPropertyAnimation(v, "opacity");
			anim2.setDuration(400);
			anim2.setStartValue(1);
			anim2.setEndValue(0);

			g.addAnimation(anim1)
			g.addPause(500)
			g.addAnimation(anim2)
					
			g.finished.connect(self.finished)
			g.start()

			v.animg = g	
			i += 1

	def screenMoveCenter(self):
		v = self.verticalScrollBar()
		h = self.horizontalScrollBar()
		if self.FIVCheck.isChecked() : 
			v.setValue(0)
			h.setValue(0)
		else:
			v.setValue((v.minimum()+v.maximum())/2)
			h.setValue((h.minimum()+h.maximum())/2)

	def sliderChange(self,change):
		self.topLayerTransform()

	def topLayerTransform(self):
		try:
			self.topLayer.resetTransform()
			self.topLayer.setPos(0,0)

			self.scene.fitInView(not self.FIVCheck.isChecked())

			mat = self.matrix()
			self.topLayer.scale(1 / mat.m11(), 1/ mat.m22())

			p = self.mapToScene(QPoint(0,0))
			self.topLayer.setPos(p.x(),p.y())

			self.logWindow.setPos(0,self.height())
			self.web.setPreferredSize(400,400)
			self.web.setPos(self.width()-420,self.height()-420)

		except Exception, e:
			print "throw ininin",e
		
	def FIVtoggled(self,p):
		if self.FIVCheck.isChecked() == False :
			self.resetTransform()
		self.fitInView()

	def resizeEvent(self,event):
		super(DesignerView,self).resizeEvent(event)
		self.fitInView()

	def fitInView(self):
		if self.FIVCheck.isChecked() : 
			super(DesignerView,self).fitInView(0,0,ProjectController().screenWidth,ProjectController().screenHeight,Qt.KeepAspectRatio)

		self.topLayerTransform()

	def applyRuler(self):
		self.setViewportMargins(DesignerRuler.RULER_BREADTH,DesignerRuler.RULER_BREADTH,0,0)

		gridLayout = QGridLayout()
		gridLayout.setSpacing(0)
		gridLayout.setContentsMargins(0,0,0,0)

		self.horzRuler = DesignerRuler(0)
		self.vertRuler = DesignerRuler(1)

		fake = QWidget()
		fake.setBackgroundRole(QPalette.Window)
		fake.setFixedSize(DesignerRuler.RULER_BREADTH,DesignerRuler.RULER_BREADTH)

		gridLayout.addWidget(fake,0,0)
		gridLayout.addWidget(self.horzRuler,0,1)
		gridLayout.addWidget(self.vertRuler,1,0)
		gridLayout.addWidget(self.viewport(),1,1)

		self.setLayout(gridLayout);

	def mouseMoveEvent (self,event):
		super(DesignerView,self).mousePressEvent(event)
		mat = self.matrix()
		pt = (event.pos() - self.mapFromScene(0,0))
		NoriterMain().statusBar().showMessage("X:["+str(int(pt.x() / mat.m11()))+"] Y:["+str(int(pt.y() / mat.m22()))+"]")

	def keyPressEvent(self,event):
		super(DesignerView,self).keyPressEvent(event)
		if event.key()==Qt.Key_Alt:
			self.Alt = True

	def keyReleaseEvent(self,event):
		if event.key()==Qt.Key_Alt:
			self.Alt = None

	def wheelEvent(self,event):
		if self.Alt:
			if event.delta() < 0 :
				if self.fScale <= 0.4 : return
				self.fScale -= 0.1
			else:
				if self.fScale >= 4 : return
				self.fScale += 0.1

			self.setZoom(self.fScale);
		else:
			super(DesignerView,self).wheelEvent(event)

	def setZoom(self,percentZoom):
		self.scaleBy(percentZoom / self.fScaleFactor);

	def scaleBy(self,factor):
		self.fScaleFactor *= factor;
		self.scale(factor, factor);

class DesignerRuler(QWidget):
	RULER_BREADTH = 20

	@staticmethod
	def gap():
		return QPoint(DesignerRuler.RULER_BREADTH,DesignerRuler.RULER_BREADTH)

	def __init__(self,rulerType,parent=None):
		super(DesignerRuler,self).__init__(parent)
		self.rulerType = rulerType
		self.origin = 0
		self.rulerUnit = 1
		self.rulerZoom = 1
		self.drawFont = False

	def paintEvent(self,event):
		painter = QPainter(self);
		pen = QPen(QColor(130,130,130),0);

		painter.setRenderHints(QPainter.TextAntialiasing | QPainter.HighQualityAntialiasing)
		painter.setPen(pen);
		rulerRect = self.rect();

		painter.fillRect(rulerRect,QColor(60,60,60));

		self.drawAScaleMeter(painter,rulerRect,25,(rulerRect.height() if self.rulerType == 0 else rulerRect.width())/2);
		self.drawAScaleMeter(painter,rulerRect,50,(rulerRect.height() if self.rulerType == 0 else rulerRect.width())/4);

		self.drawFont = True
		self.drawAScaleMeter(painter,rulerRect,100,0);
		self.drawFont = False

	def drawAScaleMeter(self,painter, rulerRect, scaleMeter, startPositoin):
		isHorzRuler = 0 == self.rulerType
		scaleMeter = scaleMeter * self.rulerUnit * self.rulerZoom

		rulerStartMark = rulerRect.left() if isHorzRuler else rulerRect.top()
		rulerEndMark = rulerRect.right() if isHorzRuler else rulerRect.bottom()

		if self.origin >= rulerStartMark and self.origin <= rulerEndMark :
			self.drawFromOriginTo(painter, rulerRect, self.origin, rulerEndMark, 0, scaleMeter, startPositoin)
			self.drawFromOriginTo(painter, rulerRect, self.origin, rulerStartMark, 0, -scaleMeter, startPositoin)
		elif self.origin < rulerStartMark :
			tickNo = int((rulerStartMark - self.origin) / scaleMeter)
			self.drawFromOriginTo(painter, rulerRect, self.origin + scaleMeter * tickNo, rulerEndMark, tickNo, scaleMeter, startPositoin)
		elif self.origin > rulerEndMark :
			tickNo = int((self.origin - rulerEndMark) / scaleMeter)
			self.drawFromOriginTo(painter, rulerRect, self.origin - scaleMeter * tickNo, rulerStartMark, tickNo, -scaleMeter, startPositoin)

	def drawFromOriginTo(self,painter, rulerRect, startMark, endMark, startTickNo, step, startPosition):
		isHorzRuler = 0 == self.rulerType
		iterate = 0
		for current in range(startMark,endMark,step):
			x1 = current if isHorzRuler else rulerRect.left() + startPosition
			y1 = rulerRect.top() + startPosition if isHorzRuler else current
			x2 = current if isHorzRuler else rulerRect.right()
			y2 = rulerRect.bottom() if isHorzRuler else current
			painter.drawLine(QLineF(x1,y1,x2,y2))

			if self.drawFont :
				rt = QRect(x1 + 1,y1 + (7 if isHorzRuler else 0),50,50)
				painter.drawText(rt,str(int((qAbs(int(step) * startTickNo))/self.rulerZoom)))
				startTickNo += 1
				iterate += 1
