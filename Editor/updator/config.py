# -*- coding: utf-8 -*-

config = None
try:
	from conf import config_dev as config
except ImportError:
	try:
		from conf import config_live as config
	except:
		print "con not find config py"
		pass

