import sys
import math, random

from PySide.QtCore import *
from PySide.QtGui import * 

#from graphics.components import *
from graphics.GraphicsObject import *

from controller.ComponentController import *
from controller.LayerController import *

from graphics.components import *

class DesignerScene(QGraphicsScene):
	def __init__(self, parent=None):
		super(DesignerScene, self).__init__(parent)

		self.componentCtrl = ComponentController.getInstance()
		self.objList = []
		self.initBackground()

	def initBackground(self):
		pixmap = QPixmap(80, 80)
		painter = QPainter(pixmap)
		painter.fillRect(QRect( 0, 0, 40, 40), QColor(199,199,199))
		painter.fillRect(QRect( 0,40, 40, 40), QColor(221,221,221))
		painter.fillRect(QRect(40, 0, 40, 40), QColor(221,221,221))
		painter.fillRect(QRect(40,40, 40, 40), QColor(199,199,199))
		painter.end()

		self.setBackgroundBrush(QBrush(pixmap))

		background = QGraphicsRectItem(0,0,600,300)
		super(DesignerScene,self).addItem(background)

		brush = QBrush()
		brush.setColor(QColor(150,150,150,200))
		brush.setStyle(Qt.SolidPattern)

		pen = QPen()
		pen.setStyle(Qt.DashLine)
		pen.setColor(QColor(80,80,80))
		background.setBrush(brush)
		background.setPen(pen)

	def addItem(self,obj):
		super(DesignerScene,self).addItem(obj)
		self.objList.append(obj)

	def removeItem(self,obj):
		super(DesignerScene,self).removeItem(obj)
		self.objList.remove(obj)

	def addObject(self,objModel):
		obj = UIObject(objModel)
		self.componentCtrl.Add(objModel,'transform');
		
		self.addItem(obj)

	def removeObject(self,objModel):
		o = self.objectWithModel(objModel)
		if o : self.removeItem(o)

	def objectWithModel(self,model):
		for o in self.objList:
			if o.model == model:
				return o
		return None

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


class DesignerView(QGraphicsView):
	MOUSE_DRAG_NONE = 0
	MOUSE_DRAG_OBJECT = 1
	MOUSE_DRAG_RUBBER = 2
	def __init__(self,parent,sceneCtrl):
		super(DesignerView,self).__init__(parent)
		self.fScaleFactor = 1
		self.fScale = 1
		self.mouseDragType = DesignerView.MOUSE_DRAG_NONE

		self.sceneCtrl = sceneCtrl;
		self.layerCtrl = sceneCtrl.layerCtrl;
		self.scene = DesignerScene();
		self.setScene(self.scene);

		#for value in self.sceneModel.layerListModel:
		#    self.scene.addObject(value)

		self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)

		self.applyRuler()

		#connect
		self.layerCtrl.objectAdded.connect(self.OnAddObject)
		self.layerCtrl.objectRemoved.connect(self.OnDeletedObject)
		self.layerCtrl.objectSelected.connect(self.OnSelectObject)

		#LayerController.getInstance().objectRemoved.connect(self.OnDeletedObject)
		#LayerController.getInstance().focusChanged.connect(self.OnFocusObject)

		#ComponentController.getInstance().componentAdded.connect(self.OnAddComponent)
		#ComponentController.getInstance().componentDeleted.connect(self.OnDeleteComponent)
		#ComponentController.getInstance().componentModify.connect(self.OnModifyComponent)

	def OnAddComponent(self,objModel,comp,number):
		o = self.scene.objectWithModel(objModel)
		if o : o.addComponent(ComponentController.getInstance().ComponentInstance(comp),number)
		self.update()

	def OnDeleteComponent(self,objModel,number):
		o = self.scene.objectWithModel(objModel)
		if o : o.deleteComponent(number)
		self.update()

	def OnModifyComponent(self):
		pass

	def OnFocusObject(self,selected):
		if selected == None : return ;

		self.scene.clearSelection()
		for m in selected :
			o = self.scene.objectWithModel(m)
			if o : o.setSelected(True)

	def OnAddObject(self,objectModel):
		self.scene.addObject(objectModel)

	def OnDeletedObject(self,objectModel):
		self.scene.removeObject(objectModel)

	def OnSelectObject(self,objectModels):
		self.scene.clearSelection()
		for m in objectModels:
			o = self.scene.objectWithModel(m)
			if o : o.setSelected(True)

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

	def mousePressEvent(self,event):
		super(DesignerView,self).mousePressEvent(event);

		if len(self.scene.selectedItems()) > 0:
			self.mouseDragType = DesignerView.MOUSE_DRAG_OBJECT
		else:
			self.mouseDragType = DesignerView.MOUSE_DRAG_RUBBER

			self.mouse_origin = event.pos() + DesignerRuler.gap()
			self.rubberBand.setGeometry(QRect(self.mouse_origin, QSize()))
			self.rubberBand.show()

	def mouseMoveEvent (self,event):
		super(DesignerView,self).mouseMoveEvent(event);
		if self.mouseDragType == DesignerView.MOUSE_DRAG_RUBBER :
			pos = event.pos() + DesignerRuler.gap()
			self.rubberBand.setGeometry(QRect(self.mouse_origin,pos).normalized())

	def mouseReleaseEvent (self,event):
		super(DesignerView,self).mouseReleaseEvent(event);

		if self.mouseDragType == DesignerView.MOUSE_DRAG_RUBBER :
			self.rubberBand.hide()

			scenePos = self.mapFromScene(0,0)
			x = self.rubberBand.x() - scenePos.x() - DesignerRuler.RULER_BREADTH
			y = self.rubberBand.y() - scenePos.y() - DesignerRuler.RULER_BREADTH
			w = self.rubberBand.width()
			h = self.rubberBand.height()
			self.scene.rubberbanded(x/self.fScale,y/self.fScale,w/self.fScale,h/self.fScale)

		self.focusUpdate()

	def focusUpdate(self):
		objects = []
		for i in self.scene.selectedItems():
			objects.append(i.model)
		self.layerCtrl.SetSelectObjects(objects)

	def wheelEvent(self,event):
		if event.delta() < 0 :
			if self.fScale <= 0.4 : return
			self.fScale -= 0.1
		else:
			if self.fScale >= 4 : return
			self.fScale += 0.1

		self.setZoom(self.fScale);

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

def start():
	ComponentController.getInstance().Regist("transform",UCTransform)
	ComponentController.getInstance().Regist("rectangle",UCRectangle)
	ComponentController.getInstance().Regist("sprite",UCSprite)
