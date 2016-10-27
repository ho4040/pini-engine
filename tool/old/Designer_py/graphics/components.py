#!/usr/bin/env python
import sys
import math, random

from Noriter.UI.Widget import Widget
from Noriter.UI.Layout import *
from Noriter.utils.Utils import Utils

from PySide.QtCore import *
from PySide.QtGui import *

#from utility.QtUtils import *
from controller.ProjectController import *
from command.commands import *

##########################
## COMPONENTS
##########################
class UIComponent(QObject):
    class UI(Widget):
        contextMenu = ["Menu","Refresh","Remove"]
        def __init__(self,model,number,parent=None):
            super(UIComponent.UI,self).__init__(parent)
            self.GUI()

            self.objectModel = model
            self.number = number

            from controller.ComponentController import ComponentController
            self.componentCtrl = ComponentController.getInstance()
            self.componentCtrl.componentModify.connect(self.dataModified)

            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.uicall_contextMenuEvent)

        @property
        def data(self):
            return self.objectModel.components[self.number].data

        def dataEdit(self,dat):
            Command.Component.Modify(self.objectModel,self.number,dat)

        def dataModified(self,model,number,old):
            if number == self.number and model == self.objectModel :
                self.updateData(old)

        def updateData(self,old):
            pass

        def uicall_contextMenuEvent(self,pos):
            menu = Utils.ContextMenu(UIComponent.UI.contextMenu,self)
            action = menu.exec_(self.mapToGlobal(pos))     

            if action :
                act = action.text()
                if act == 'Refresh' : pass
                elif act == 'Remove' : 
                    if self.objectModel.components[self.number].__class__ == UCTransform:
                        return False
                    Command.Component.Remove(self.objectModel,self.number)
        
    def __init__(self,objModel):
        super(UIComponent,self).__init__()

        self.object = None
        self.number = None
        self.objectModel = None
        
        self.require = []
        self.needless = []

        if objModel : 
            self.object = objModel.uiobject
            self.number = 0
            self.objectModel = objModel

        self.data = self.default()

        from controller.ComponentController import ComponentController
        self.componentCtrl = ComponentController.getInstance()
        self.componentCtrl.componentModify.connect(self.dataModified)

    def dataModified(self,model,number,new,old):
        if number == self.number and model == self.objectModel :
            for k,v in new.items():
                self.data[k] = v
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
                if self.componentCtrl.HasComponent(model,c) == False :
                    requireRet = False
                    break

        if self.needless :
            for c in self.needless :
                if self.componentCtrl.HasComponent(model,c) == True :
                    needlessRet = False
                    break

        return requireRet and needlessRet

    def serialize(self):
        return self.data

    @staticmethod
    def default():
        return {}

#component
class UCTransform(UIComponent):
    class UI(UIComponent.UI):
        def __init__(self,model,number,parent=None):
            super(UCTransform.UI,self).__init__(model,number,parent)
            self.updateData({})

        @LayoutGUI
        def GUI(self):
            self.Layout.label("Transform")
            self.Layout.hline()
            with Layout.GridBox():
                self.Layout.label("name")
                self.ui_Name = self.Layout.input("",self.uicall_Name)
                self.Layout.Next()

                self.Layout.label("x")
                self.ui_X = self.Layout.input("",self.uicall_X)
                self.Layout.Next()

                self.Layout.label("y")
                self.ui_Y = self.Layout.input("",self.uicall_Y)
                self.Layout.Next()

                self.Layout.label("width")
                self.ui_Width = self.Layout.input("",self.uicall_W)
                self.Layout.Next()

                self.Layout.label("height")
                self.ui_Height = self.Layout.input("",self.uicall_H)
                self.Layout.Next()

        def updateData(self,old):
            self.ui_Name.setText(unicode(self.data['name']))
            self.ui_X.setText(unicode(self.data['x']))
            self.ui_Y.setText(unicode(self.data['y']))
            self.ui_Width.setText(unicode(self.data['width']))
            self.ui_Height.setText(unicode(self.data['height']))

        def uicall_Name(self):
            self.dataEdit({'name':self.ui_Name.text()})
        def uicall_X(self):
            self.dataEdit({'x':float(self.ui_X.text())})
        def uicall_Y(self):
            self.dataEdit({'y':float(self.ui_Y.text())})
        def uicall_W(self):
            self.dataEdit({'width':float(self.ui_Width.text())})
        def uicall_H(self):
            self.dataEdit({'height':float(self.ui_Height.text())})

    def __init__(self,objModel):
        super(UCTransform,self).__init__(objModel)
        self.needless.append( UCTransform )
        if self.object : self.object.ctransform = self

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
        Command.Component.Modify(self.objectModel,self.number,{'x':x,'y':y})

    @staticmethod
    def default():
        return {'name':'object','x':0,'y':0,'width':100,'height':100}

#component
class UCRectangle(UIComponent):
    class UI(UIComponent.UI):
        def __init__(self,model,number,parent=None):
            super(UCRectangle.UI,self).__init__(model,number,parent)
            self.updateData({})

        @LayoutGUI
        def GUI(self):
            self.Layout.label("Rectangle")
            self.Layout.hline()
            with Layout.GridBox():
                self.Layout.label("R")
                self.ui_R = self.Layout.input("",self.uicall_R)

                self.Layout.label("G")
                self.ui_G = self.Layout.input("",self.uicall_G)

                self.Layout.label("B")
                self.ui_B = self.Layout.input("",self.uicall_B)

                self.Layout.label("A")
                self.ui_A = self.Layout.input("",self.uicall_A)

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

    def __init__(self,obj):
        super(UCRectangle,self).__init__(obj)
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
    class UI(UIComponent.UI):
        def __init__(self,model,number,parent=None):
            super(UCSprite.UI,self).__init__(model,number,parent)
            self.updateData({})

        @LayoutGUI
        def GUI(self):
            self.Layout.label("Sprite")
            self.Layout.hline()
            with Layout.GridBox():
                self.Layout.label("R")
                self.ui_R = self.Layout.input("",self.uicall_R)

                self.Layout.label("G")
                self.ui_G = self.Layout.input("",self.uicall_G)

                self.Layout.label("B")
                self.ui_B = self.Layout.input("",self.uicall_B)

                self.Layout.label("A")
                self.ui_A = self.Layout.input("",self.uicall_A)

            with Layout.HBox():
                self.Layout.label("src")
                self.ui_Src = self.Layout.input("",None)
                self.Layout.button("...",self.uicall_find)

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
            resPath = Utils.GetResourcePath(self)
            if len(resPath) > 0:
                self.ui_Src.setText(resPath)
                self.dataEdit({'src':resPath})

    def __init__(self,objModel):
        super(UCSprite,self).__init__(objModel)
        self.require.append( UCTransform )
        self.origin = None

        if self.object : 
            self.projectCtrl = ProjectController.getInstance()
            self.readImage()

    def readImage(self):
        if len(self.data['src']) > 0 : 
            self.origin = QImage(self.projectCtrl.path + self.data['src'])
            self.generateColorImage()

    def updateData(self,old):
        if 'src' in old:
            if len(self.data['src']) == 0 : 
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


