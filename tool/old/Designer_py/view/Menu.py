# -*- coding: utf-8 -*-
from Noriter.UI.Layout import *
from Noriter.views.NoriterMainWindow import *
from Noriter.utils.Settings import Settings

from controller.SceneListController import SceneListController
from controller.ProjectController import ProjectController

from PySide import QtCore

class Menu(object):
	@MenuBar("File/New Scene")
	def NewScene():
		inst = ProjectController.getInstance()
		if len(inst.path) == 0 : 
			return
		path,ext = QtGui.QFileDialog.getSaveFileName(parent=NoriterMain(),caption="New Scene",dir=inst.sceneDirectory )
		if len(path) > 0:
			fi = QtCore.QFileInfo(path) 
			if len(fi.suffix()) == 0 :
				path = path+".scene"
			elif fi.suffix() != "scene" :
				path = fi.path() + QtCore.QDir.separator() + fi.baseName() + ".scene"

			SceneListController.getInstance().New(path)
			SceneListController.getInstance().Open(path)

	@MenuBar("File/Open Scene")
	def OpenScene():
		inst = ProjectController.getInstance()
		if len(inst.path) == 0 : 
			return
		path,ext = QtGui.QFileDialog.getOpenFileName(parent=NoriterMain(),caption="Open Scene",dir=inst.sceneDirectory )
		if path.startswith( inst.sceneDirectory ) :
			fi = QtCore.QFileInfo(path)
			if fi.suffix() == "scene" :
				SceneListController.getInstance().Open(path)
			else:
				print "can not open scene"
		else:
			print "can not open scene"

