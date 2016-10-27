#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import math
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import * 

sys.path.append("../Noriter")

from Noriter.views.NoriterMainWindow import *
from Noriter.utils.Settings import Settings
from Noriter.UI.Layout import *
from Noriter.UI.Widget import Widget
from Noriter.views.NoriterMainWindow import * 

from OpenGL.GL import *
from OpenGL.GLU import *

import vector

def u(text):
	return unicode(text,"utf-8")

class Parts(object):
	def __init__(self,name,path,gl):
		self.name = name
		self.gl = gl
		self.x = 0
		self.y = 0
		self.texturePath = path
		self.edgeList = []

		self.EDIT_MODE = 0

		self.pixmap = QPixmap(self.texturePath)
		self.meshes = [
			[[-self.pixmap.width()/2, self.pixmap.height()/2, 0],[self.pixmap.width()/2, self.pixmap.height()/2, 0]],
			[[-self.pixmap.width()/2,-self.pixmap.height()/2, 0],[self.pixmap.width()/2,-self.pixmap.height()/2, 0]],
		]

		self.AddRow()
		self.AddRow()
		self.AddColumn()
		self.AddColumn()

		self.Stabilizing()

	def Selected(self,flag):
		self.isSelcted = flag

	def isPickPoint(self,x,y):
		i=0
		j=0
		for m in self.meshes : 
			j=0
			for v in m : 
				vx = v[0] + self.x
				vy = v[1] + self.y
				if math.fabs(vx-x) < 20 and math.fabs(vy-y) < 20 :
					return (i,j)
				j += 1
			i += 1
		return (-1,-1)

	def isPick(self,x,y):
		pts = self.isPickPoint(x,y)
		if pts[0] >= 0 :
			self.picked_point = pts
			self.EDIT_MODE = 1
			return True
		return False
	
	def ObjectMove(self,x,y): 
		self.last_mouse_pos = [ x-self.x , y-self.y ]
		self.EDIT_MODE = 2

	def MouseMove(self,x,y):
		if self.EDIT_MODE == 1 : 
			pts = self.picked_point
			self.meshes[pts[0]][pts[1]][0] = x - self.x
			self.meshes[pts[0]][pts[1]][1] = y - self.y
		elif self.EDIT_MODE == 2:
			self.x = x - self.last_mouse_pos[0]
			self.y = y - self.last_mouse_pos[1]

	def updateTexture(self):
		self.textureId = self.gl.bindTexture(self.pixmap)

	def updateMesh(self):
		self.yNum = len(self.meshes)
		self.xNum = len(self.meshes[0])

		l1 = [v for v in self.meshes[0]]
		l2 = [v[-1] for v in self.meshes]
		l3 = [v for v in self.meshes[-1]]
		l4 = [v[0]  for v in self.meshes]

		v1 = l1[0]
		v2 = l1[-1]
		v3 = l3[0]
		v4 = l3[-1]

		l1 = l1[1:-1]
		l2 = l2[1:-1]
		l3 = l3[1:-1]
		l4 = l4[1:-1]

		l3.reverse()
		l4.reverse()

		self.edgeList = [v1] + l1 + [v2] + l2 + [v4] + l3 + [v3] + l4

	def AddRow(self) : 
		for v in self.meshes : 
			v1 = v[0]
			v2 = v[1]
			x = (v1[0]+v2[0])/2.0
			y = (v1[1]+v2[1])/2.0
			z = (v1[2]+v2[2])/2.0

			v.insert(1,[x,y,z])
		self.updateMesh()

	def AddColumn(self) : 
		c1 = self.meshes[0]
		c2 = self.meshes[1]
		c = []
		for i in range(0,len(c1)):
			v1 = c1[i]
			v2 = c2[i]
			x = (v1[0]+v2[0])/2.0
			y = (v1[1]+v2[1])/2.0
			z = (v1[2]+v2[2])/2.0

			c.append([x,y,z])

		self.meshes.insert(1,c)
		self.updateMesh()

	def Stabilizing(self):
		for i in range(0,self.yNum) : 
			v = self.meshes[i]
			xTotal = abs(v[0][0]) + abs(v[-1][0])
			xStart = v[0][0]
			for j in range(0,self.xNum) : 
				x = v[j]
				x[0] = xStart + float(xTotal)/float(self.xNum-1)*j

		for i in range(0,self.xNum) : 
			frst = self.meshes[ 0][i]
			last = self.meshes[-1][i]
			yTotal = abs(frst[1]) + abs(last[1])
			yStart = frst[1]
			for j in range(0,self.yNum):
				x = self.meshes[j][i]
				x[1] = yStart - float(yTotal)/float(self.yNum-1)*j

	def draw(self):
		glLoadIdentity()
		glTranslated(self.x, self.y, -10)

		glBindTexture(GL_TEXTURE_2D, self.textureId)

		glColor3f(1,1,1)
		for y in range(0,self.yNum-1) : 
			for x in range(0,self.xNum-1) : 
				v1 = self.meshes[y][x]
				v2 = self.meshes[y][x+1]
				v3 = self.meshes[y+1][x+1]
				v4 = self.meshes[y+1][x]

				_u1 = float(x)/(self.xNum-1)
				_v1 = float(y)/(self.yNum-1)
				_u2 = float(x+1)/(self.xNum-1)
				_v2 = float(y+1)/(self.yNum-1)

				glBegin(GL_QUADS)
				
				glTexCoord2f(_u1, _v1)
				glVertex3f(v1[0],v1[1],v1[2])

				glTexCoord2f(_u2, _v1)
				glVertex3f(v2[0],v2[1],v2[2])

				glTexCoord2f(_u2, _v2)
				glVertex3f(v3[0],v3[1],v3[2])

				glTexCoord2f(_u1, _v2)
				glVertex3f(v4[0],v4[1],v4[2])

				glEnd(); 

		if self.isSelcted : 
			glPointSize(4.0)
			glColor3f(1,0,0)
			glBegin(GL_POINTS)
			for v in self.meshes : 
				for p in v :
					glVertex3f(p[0], p[1],1) 
			glEnd(); 
			glColor3f(1,1,1)

class GLWidget(QGLWidget):
	def __init__(self, parent):
		super(GLWidget,self).__init__(parent)

		self.setFocusPolicy(Qt.StrongFocus)
		self.focus_move = None
		self.selectedPart = None
		self.OnSpaceKey = False
		self.clearColor = Qt.black
		self.parts = []

	def updateParts(self,parts):
		self.parts = parts

	def minimumSizeHint(self):
		return QSize(550, 50)

	def initializeGL(self):
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_CULL_FACE)
		glEnable(GL_TEXTURE_2D)

		for v in self.parts : 
			v.updateTexture()

		self.update_timer = QTimer(self)
		self.update_timer.timeout.connect(self.updateGL)
		self.update_timer.start(40)

	def paintGL(self):
		self.qglClearColor(self.clearColor)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		for v in self.parts : 
			v.draw()

	def resizeGL(self, width, height):
		side = min(width, height)
		glViewport(0,0,width,height)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0,width,height,0, 4.0, 15.0)
		glMatrixMode(GL_MODELVIEW)

	def setSelect(self,data):
		for v in self.parts : 
			v.Selected(False)
		self.selectedPart = data
		self.selectedPart.Selected(True)

	def keyPressEvent(self,e) : 
		if e.key() == Qt.Key_Space : 
			self.OnSpaceKey = True
		super(GLWidget,self).keyPressEvent(e)

	def keyReleaseEvent(self,e) : 
		if e.key() == Qt.Key_Space : 
			self.OnSpaceKey = False
		super(GLWidget,self).keyReleaseEvent(e)

	def mousePressEvent(self, e):
		self.focus_move = None
		if self.selectedPart : 
			if self.OnSpaceKey : 
				self.selectedPart.ObjectMove(e.x(),e.y())
				self.focus_move = self.selectedPart
			else:
				if self.selectedPart.isPick(e.x(),e.y()) : 
					self.focus_move = self.selectedPart

	def mouseMoveEvent(self, e):
		if self.focus_move : 
			self.focus_move.MouseMove(e.x(),e.y())

	def mouseReleaseEvent(self, e):
		self.focus_move = None

class Window(Widget):
	def __init__(self, parent=None):
		super(Window,self).__init__(parent)

		self.GUI()
		self.parts = [
			Parts("Face","aa.png",self.glview),
			Parts("Eye_Left","aa.png",self.glview),
			Parts("Eye_Right","aa.png",self.glview)
		]
		self.partsList.data = self.parts
		self.glview.updateParts(self.parts)
	
		self.partsList.changed.connect(self.changedSelected)

	@LayoutGUI
	def GUI(self):
		splitter = self.Layout.splitter(0)
		with splitter.split():
			self.glview = self.Layout.addWidget(GLWidget(self))
		with splitter.split():
			self.partsList = self.Layout.listbox(self.factory,[])

	def factory(self,data) :
		self.Layout.label(data.name)
		return 20

	def changedSelected(self,idx):
		data = idx[0].data
		self.glview.setSelect(data)

if __name__ == "__main__":
	app = QApplication(sys.argv)

	m = NoriterMain()
	m.resize(800,600)
	m.move(50,50)
	m.SetMain(Window(m))

	sys.exit(app.exec_())
