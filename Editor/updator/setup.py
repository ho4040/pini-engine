# -*- coding: utf-8 -*-
from setuptools import setup
import os,sys

sys.stderr = sys.stdout
sys.path.append(os.path.join("..","Noriter"))

platform_options = dict()

DATA = []
if sys.platform == "win32":
	# python setup.py py2exe
	import py2exe
	DATA = [
		os.path.dirname(os.path.abspath(__file__))+'\..\dlls\msvcr90.dll',
		os.path.dirname(os.path.abspath(__file__))+'\..\dlls\msvcp90.dll',
	]
	platform_options = {
		"windows": [{
			"script": "main.py",
			"icon_resources": [(1, "icon.ico")],
			"dest_base": "Updator"
		}],
		"zipfile": None,
		"setup_requires": ["py2exe"],
		"options": {
			"py2exe": {
				"bundle_files": 3,
				"packages":["email","requests","pycparser","cffi","pygit2"],
				"excludes":["conf.config_dev"],
				"dll_excludes": ["w9xpopen.exe",
								 "msvcr71.dll",
								 "MSVCP90.dll"],
				"compressed": True
			}
		}
	}
elif sys.platform == "darwin":
	# python setup.py py2app
	platform_options = {
		"setup_requires": ["py2app"],
		"app": ["main.py"],
		"options": {
			"py2app": {
				"argv_emulation": True
				#"iconfile": "window_icon.icns"
			}
		}
	}
else:
	# python setup.py install
	platform_options = {
		"scripts": ["main.py"]
	}
	
setup(name="Updator distribute",
	  description=unicode("피니엔진을 업데이트 해주는 업데이터입니다.","utf-8"),
	  version="0.0.1",
	  data_files = DATA,
	  **platform_options)