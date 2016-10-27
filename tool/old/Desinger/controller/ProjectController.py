# -*- coding: utf-8 -*-

import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *

class ProjectController(QObject):
	class ProjectModel(QObject):pass

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if ProjectController._instance == None:
			ProjectController._instance = ProjectController()

		return ProjectController._instance

	def __init__(self):
		super(ProjectController,self).__init__()

	@property
	def path(self):
		return self._path

	@path.setter
	def path(self,path):
		self._path = path
