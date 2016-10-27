#!/usr/bin/env python
import sys
import math, random

from PySide.QtCore import *
from PySide.QtGui import *

from graphics.components import *

##########################
## UIOBJECT
##########################
class UIObject(QGraphicsItem):
    def __init__(self,model, parent=None):
        super(UIObject, self).__init__(parent)
        self.components = []

        self.model = model
        self.hasMove = False
        #self.ctransform = self.getComponentByType(UCTransform)

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.setToolTip(model.name)

    def addComponent(self,compo,number=None):
        if number == None : 
            number = len(self.components)

        com = compo(self,number)
        self.components.insert(number,com)
        self.sortComponentNumber()

        com.updateData({})

        return com

    def deleteComponent(self,number):
        if len(self.components) <= number : return False

        del self.components[number]
        self.sortComponentNumber()
        
        return True

    def sortComponentNumber(self):
        i = 0
        for c in self.components : 
            c.number = i
            i += 1

    def hasComponent(self,compoClass):
        for c in self.components:
            if isinstance( c , compoClass ):
                return True
        return False

    def getComponentByType(self,compoClass):
        if compoClass == UCTransform : return self.ctransform

        for c in self.components:
            if isinstance( c , compoClass ):
                return c
        return None

    def boundingRect(self):
        return self.ctransform.rect()

    def paint(self, painter, option, widget=None):
        for c in self.components:
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