#!/usr/bin/env python
import sys
import math, random

from PySide.QtCore import *
from PySide.QtGui import *

from uic.Ui_UCTransform import *
from uic.Ui_UCRectangle import *
from uic.Ui_UCSprite import *

from utility.QtUtils import *
from controller.ProjectController import *

##########################
## COMPONENTS
##########################
class UIComponent(QObject):
    class UI(QWidget):
        contextMenu = ["Menu","Refresh","Remove"]

        def __init__(self,model,number,parent=None):
            super(UIComponent.UI,self).__init__(parent)
            self.number = number
            self.layerModel = model

            from controller.ComponentController import ComponentController
            self.cc = ComponentController.getInstance()
            self.cc.componentModify.connect(self.dataModified)

            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.uicall_contextMenuEvent)

        @property
        def data(self):
            return self.layerModel.component[self.number]

        def dataEdit(self,dat):
            self.cc.Modify(self.layerModel,self.number,dat)

        def dataModified(self,model,number,old):
            if number == self.number and model == self.layerModel :
                self.updateData(old)

        def updateData(self,old):
            pass

        def uicall_contextMenuEvent(self,pos):
            menu = QtUtils.ContextMenu(UIComponent.UI.contextMenu,self)
            action = menu.exec_(self.mapToGlobal(pos+QPoint(0,20)))     

            if action :
                act = action.text()
                if act == 'Refresh' : pass
                elif act == 'Remove' : 
                    if self.__class__ == UCTransform:
                        return False
                    self.cc.Remove(self.layerModel,self.number)

    def __init__(self,obj,number):
        super(UIComponent,self).__init__()

        if obj : 
            self.object = obj
            self.number = number
            self.layerModel = obj.model
        self.require = []
        self.needless = []

        from controller.ComponentController import ComponentController
        self.cc = ComponentController.getInstance()

        self.cc.componentModify.connect(self.dataModified)

    def dataModified(self,model,number,old):
        if number == self.number and model == self.layerModel :
            self.updateData(old)

    def updateData(self,old):
        pass

    def render(self,painter):
        return False

    def requireTest(self,model):
        requireRet = True
        needlessRet = True
        if self.require :
            for c in self.require :
                if self.cc.HasComponent(model,c) == False :
                    requireRet = False
                    break

        if self.needless :
            for c in self.needless :
                if self.cc.HasComponent(model,c) == True :
                    needlessRet = False
                    break

        return requireRet and needlessRet

    @property
    def data(self):
        return self.layerModel.component[self.number]

    @staticmethod
    def default():
        return {}

#component
class UCTransform(UIComponent):
    class UI(UIComponent.UI,Ui_UCTransform):
        def __init__(self,model,number,parent=None):
            super(UCTransform.UI,self).__init__(model,number,parent)
            self.setupUi(self)

            #connect
            self.ui_X.editingFinished.connect(self.uicall_X)
            self.ui_Y.editingFinished.connect(self.uicall_Y)
            self.ui_Width.editingFinished.connect(self.uicall_W)
            self.ui_Height.editingFinished.connect(self.uicall_H)

            self.updateData({})

        def updateData(self,old):
            self.ui_X.setText(unicode(self.data['x']))
            self.ui_Y.setText(unicode(self.data['y']))
            self.ui_Width.setText(unicode(self.data['width']))
            self.ui_Height.setText(unicode(self.data['height']))

        def uicall_X(self):
            self.dataEdit({'x':int(self.ui_X.text())})
        def uicall_Y(self):
            self.dataEdit({'y':int(self.ui_Y.text())})
        def uicall_W(self):
            self.dataEdit({'width':int(self.ui_Width.text())})
        def uicall_H(self):
            self.dataEdit({'height':int(self.ui_Height.text())})

    def __init__(self,obj,number):
        super(UCTransform,self).__init__(obj,number)
        self.needless.append( UCTransform )

        if obj : 
            obj.ctransform = self

    def updateData(self,old):
        self.object.setX(self.data['x'])
        self.object.setY(self.data['y'])

        if old.get('width',None) or old.get('height',None):
            self.object.update()

            self.object.setFlag(QGraphicsItem.ItemSendsGeometryChanges,False)
            self.object.moveBy(-1,-1)
            self.object.moveBy(1,1)
            self.object.setFlag(QGraphicsItem.ItemSendsGeometryChanges,True)

    def rect(self):
        return QRectF(0,0,self.data['width'],self.data['height'])

    def boundingBox(self):
        return QRect(self.data['x'],self.data['y'],self.data['width'],self.data['height'])

    def move(self,x,y):
        self.cc.Modify(self.layerModel,self.number,{'x':x,'y':y})

    @staticmethod
    def default():
        return {'name':'','x':0,'y':0,'width':100,'height':100}

#component
class UCRectangle(UIComponent):
    class UI(UIComponent.UI,Ui_UCRectangle):
        def __init__(self,model,number,parent=None):
            super(UCRectangle.UI,self).__init__(model,number,parent)
            self.setupUi(self)

            #connect
            self.ui_R.editingFinished.connect(self.uicall_R)
            self.ui_G.editingFinished.connect(self.uicall_G)
            self.ui_B.editingFinished.connect(self.uicall_B)
            self.ui_A.editingFinished.connect(self.uicall_A)

            self.updateData({})

        def updateData(self,dat):
            self.ui_R.setText(unicode(self.data['r']))
            self.ui_G.setText(unicode(self.data['g']))
            self.ui_B.setText(unicode(self.data['b']))
            self.ui_A.setText(unicode(self.data['a']))

        def uicall_R(self):
            self.dataEdit({'r':int(self.ui_R.text())})
        def uicall_G(self):
            self.dataEdit({'g':int(self.ui_G.text())})
        def uicall_B(self):
            self.dataEdit({'b':int(self.ui_B.text())})
        def uicall_A(self):
            self.dataEdit({'a':int(self.ui_A.text())})

    def __init__(self,obj,number):
        super(UCRectangle,self).__init__(obj,number)
        self.require.append( UCTransform )
        self.needless.append( UCRectangle )

    def updateData(self,old):
        self.object.update()

    def render(self,painter):
        painter.fillRect(self.object.ctransform.rect(), 
                         QColor(self.data['r'],self.data['g'],self.data['b'],self.data['a']))
        return True

    @staticmethod
    def default():
        return {'r':255,'g':255,'b':255,'a':255}
        
#component
class UCSprite(UIComponent):
    class UI(UIComponent.UI,Ui_UCSprite):
        def __init__(self,model,number,parent=None):
            super(UCSprite.UI,self).__init__(model,number,parent)
            self.setupUi(self)

            #connect
            self.ui_R.editingFinished.connect(self.uicall_R)
            self.ui_G.editingFinished.connect(self.uicall_G)
            self.ui_B.editingFinished.connect(self.uicall_B)
            self.ui_A.editingFinished.connect(self.uicall_A)
            self.ui_find.clicked.connect(self.uicall_find)

            self.updateData({})

        def updateData(self,dat):
            self.ui_Src.setText(self.data['src'])
            self.ui_R.setText(unicode(self.data['r']))
            self.ui_G.setText(unicode(self.data['g']))
            self.ui_B.setText(unicode(self.data['b']))
            self.ui_A.setText(unicode(self.data['a']))

        def uicall_R(self):
            self.dataEdit({'r':int(self.ui_R.text())})
        def uicall_G(self):
            self.dataEdit({'g':int(self.ui_G.text())})
        def uicall_B(self):
            self.dataEdit({'b':int(self.ui_B.text())})
        def uicall_A(self):
            self.dataEdit({'a':int(self.ui_A.text())})
        def uicall_find(self):
            resPath = QtUtils.GetResourcePath(self)
            if len(resPath) > 0:
                self.ui_Src.setText(resPath)
                self.dataEdit({'src':resPath})
            
    def __init__(self,obj,number):
        super(UCSprite,self).__init__(obj,number)
        self.require.append( UCTransform )
        self.origin = None

        if obj : 
            self.pc = ProjectController.getInstance()
            self.readImage()

    def readImage(self):
        if len(self.data['src']) > 0 : 
            self.origin = QImage(self.pc.path + self.data['src'])
            self.generateColorImage()

    def updateData(self,old):
        if 'src' in old:
            if len(self.data['src']) == 0 : 
                print "updatedata",self.data['src']
                self.origin = None
            else:
                self.readImage()
        else:
            self.generateColorImage()
        self.object.update()

    def generateColorImage(self):
        if self.origin == None : return 

        c = QImage(self.origin.rect().width(),self.origin.rect().height(),QImage.Format_ARGB32_Premultiplied)
        self.color = QImage(self.origin.rect().width(),self.origin.rect().height(),QImage.Format_ARGB32_Premultiplied)
        
        c.fill(QColor(self.data['r'],self.data['g'],self.data['b']));
        painter = QPainter(self.color);

        painter.fillRect(self.origin.rect(),Qt.transparent);
        painter.drawImage(0, 0, c);

        painter.setCompositionMode(QPainter.CompositionMode_Multiply);
        painter.drawImage(0, 0, self.origin);

        painter.setCompositionMode(QPainter.CompositionMode_DestinationOver);
        painter.end();

        self.color.setAlphaChannel(self.origin.alphaChannel());

    def render(self,painter):
        if self.origin:
            w = self.object.ctransform.rect().width()
            h = self.object.ctransform.rect().height()
            painter.drawImage(QRect(0,0,int(w),int(h)),self.color,self.origin.rect())
        return True

    @staticmethod
    def default():
        return {'r':255,'g':255,'b':255,'a':255,'src':''}


