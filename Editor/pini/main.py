# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from config import *

Error_Logger = open("ERROR_LOG.txt","w+")
if config.__RELEASE__ == False : 
	sys.path.append("../Noriter")
else:
	# sys.stderr   = Error_Logger
	# sys.stdout   = Error_Logger
	pass

from PySide.QtGui import *
from PySide.QtCore import *
from Noriter.views.NoriterMainWindow import *
from Noriter.utils.Settings import Settings

import os
import json
import urllib2

from view.LoaderView import LoaderWindow

launcher = None
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)

	v = LoaderWindow()
	_exit_ = app.exec_()
	##################
	Error_Logger.close()
	##################
	sys.exit(_exit_)

