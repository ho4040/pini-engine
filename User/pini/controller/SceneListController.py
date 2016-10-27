# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import json

from PySide.QtCore import *
from PySide.QtGui import *

from .SceneController import SceneController
from controller.ProjectController import ProjectController
from Noriter.utils.Json import Json
from Noriter.utils.Settings import Settings

class SceneListController(QObject):
	SceneLoaded = Signal( SceneController )
	SceneOpen = Signal( SceneController )
	SceneSave = Signal( SceneController )

	def __init__(self):
		super(SceneListController,self).__init__()
		self.sceneList = {}

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if SceneListController._instance == None:
			SceneListController._instance = SceneListController()
		return SceneListController._instance

	def Load(self,path):
		if QFile(path).exists() :
			sc = SceneController()
			sc.Load(path)

			self.sceneList[path] = sc
			self.SceneLoaded.emit(self.sceneList[path])

			return True
		return False

	def Open(self,path):
		inst = ProjectController()
		# ProjectController().compileProj(True)
		ProjectController().compileProj()
		curDir = QDir(ProjectController().path)
		with Settings("PROJECT_USER_SETTING") :
			with Settings(inst.path) :
				#temp파일은 2번파일 최신 연 파일은 3번파일 이렇게 되면 꼬이니까 temp파일 삭제해줌.
				try:
					os.remove(os.path.join(".","tmp_save_1"))
				except Exception, e:
					pass
				try:
					os.remove(os.path.join(".","tmp_save_2"))
				except Exception, e:
					pass
				Settings()["lastSceneLoaded"] = curDir.relativeFilePath(path)

		#if not path in self.sceneList:
		if not self.Load(path) :
			return

		self.SceneOpen.emit(self.sceneList[path])

	def New(self,path):
		fp = QFile(path)
		fp.open(QIODevice.WriteOnly)
		fp.write("")
		fp.close()

