#!/usr/bin/env python
import sys
import math, random

from PySide.QtCore import *
from PySide.QtGui import *

from graphics.components import *
from controller.ComponentController import ComponentController

##########################
## UIOBJECT
##########################
class UIObject(QGraphicsItem):
    def __init__(self,model, parent=None):
        super(UIObject, self).__init__(parent)

        self.model = model
        self.hasMove = False
        self.ctransform = self.getComponentByType(UCTransform)

        self.model.uiobject = self

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.componentCtrl = ComponentController.getInstance() 
        self.componentCtrl.componentAdded.connect( self.OnAddComponent )
        self.componentCtrl.componentDeleted.connect( self.OnDeleteComponent )

        #self.setToolTip(model.name)

    def serialize(self):
        obj = { "components" : [] }
        for comp in self.model.components:
            obj["components"].append( comp.serialize() )
        return obj

    def OnAddComponent(self,model,comp):
        if model == self.model :
            model.sortNumber()
            comp.updateData({})

    def OnDeleteComponent(self,compModel,idx):
        if compModel.objectModel == self.model :
            self.model.sortNumber()
            self.update()

    def deleteComponent(self,number):
        if len(self.model.components) <= number :
            return False
        return True

    def hasComponent(self,compoClass):
        for c in self.model.components:
            if isinstance( c , compoClass ):
                return True
        return False

    def getComponentByType(self,compoClass):
        #if compoClass == UCTransform : return self.ctransform
        for c in self.model.components:
            if isinstance( c , compoClass ):
                return c
        return None

    def boundingRect(self):
        return self.ctransform.rect()

    def paint(self, painter, option, widget=None):
        for c in self.model.components:
            c.render(painter)

        self.drawSelectedLine(painter)
    
    def drawSelectedLine(self,painter):
        if self.isSelected():
            painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
            painter.drawRect(self.ctransform.rect())

    def mouseReleaseEvent(self,event):
        super(UIObject,self).mouseReleaseEvent(event)
        self.scene().updatePosItems()

    def updatePosItem(self):
        if self.hasMove:
            self.ctransform.move(self.x(),self.y())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            self.hasMove = True

        return QGraphicsItem.itemChange(self, change, value)


