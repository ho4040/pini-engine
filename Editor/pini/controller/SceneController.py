# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import json

from PySide.QtCore import *
from PySide.QtGui import *

class SceneController(QObject):
	def __init__(self):
		super(SceneController,self).__init__()
		self.path = ""
		self.view = None
		self.needSave = False
		
	def Load(self,path):
		self.path = path
		fp = QFile(path)
		fp.open(QIODevice.ReadOnly | QIODevice.Text)

		fin = QTextStream(fp)
		fin.setCodec("UTF-8")

		self.plainText = fin.readAll()

		fin = None
		fp.close()

	def Save(self,plainText):
		fp = QFile(self.path)
		print ("Save..." + self.path)
		fp.open(QIODevice.WriteOnly | QIODevice.Text)
		
		out = QTextStream(fp)
		out.setCodec("UTF-8")
		out.setGenerateByteOrderMark(False)
		out<<plainText
		out = None
		fp.close()

		self.needSave = False

