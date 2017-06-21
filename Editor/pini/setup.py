# -*- coding: utf-8 -*-
from setuptools import setup
import os,sys

sys.stderr = sys.stdout

sys.path.append(os.path.join("..","Noriter"))

platform_options = dict()
'''
# ... 
setup( 
	windows=[{"scripts": "run.py", "icon_resources": [(1, "resources/window_icon.ico")], "dest_base": "myfirstapp"}], 
	 )# ... setup( # ... windows=[{"scripts": "run.py", "icon_resources": [(1, "resources/window_icon.ico")], "dest_base": "myfirstapp"}], # .. )

'''


if sys.platform == "win32":
	# python setup.py py2exe
	try:
		# py2exe 0.6.4 introduced a replacement modulefinder.
		# This means we have to add package paths there, not to the built-in
		# one.  If this new modulefinder gets integrated into Python, then
		# we might be able to revert this some day.
		# if this doesn't work, try import modulefinder
		try:
			import py2exe.mf as modulefinder
		except ImportError:
			import modulefinder
		import win32com, sys
		for p in win32com.__path__[1:]:
			modulefinder.AddPackagePath("win32com", p)
		for extra in ["win32com.shell"]: #,"win32com.mapi"
			__import__(extra)
			m = sys.modules[extra]
			for p in m.__path__[1:]:
				modulefinder.AddPackagePath(extra, p)
	except ImportError:
		# no build path setup, no worries.
		pass

	from distutils.core import setup
	import py2exe
	
	platform_options = {
		"console": [{
			"script": "main.py",
			"icon_resources": [(1, "icon.ico")],
			"dest_base": "PiniEngine",
		}],
		"zipfile": None,
		"setup_requires": ["py2exe"],
		"options": {
			"py2exe": {
				"bundle_files": 3,
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
	
setup(name="PiniEngine",
	  description=unicode("피니엔진 실행파일입니다!","utf-8"),
	  version="0.0.1",
	  **platform_options)