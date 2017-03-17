
from PySide.QtCore import *
from PySide.QtGui import *

import shutil
import os
import Image

class FontManager(object) : 
	_instance = None
	_isInit   = False
	def __new__(cls, *args, **kwargs):
		if not FontManager._instance:
			FontManager._instance = super(FontManager,cls).__new__(cls,*args,**kwargs)

		return FontManager._instance

	def __init__(self,src=None,parent=None):
		if FontManager._isInit:
			return 
		FontManager._isInit = True

		super(FontManager,self).__init__()

		self.fonts = {}
		self.reset()

	def reset(self):
		QFontDatabase.removeAllApplicationFonts()
		self.fonts = {}

		self.AddFont("NanumBarunGothic","resource/NanumBarunGothic.ttf")
		self.AddFont("NanumGothicCoding","resource/NanumGothicCoding.ttf")

	def AddFont(self,idx,path):
		if idx in self.fonts : 
			return

		_id = QFontDatabase.addApplicationFont(path)
		family = QFontDatabase.applicationFontFamilies(_id)[0]

		idx = idx.decode("utf-8")
		self.fonts[idx] = family

		return family

	def FontName(self,idx):
		if idx in self.fonts : 
			return self.fonts[idx]
		else:
			for k,v in self.fonts.iteritems():
				return v
			return ""