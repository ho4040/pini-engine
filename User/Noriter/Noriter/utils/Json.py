import json
import copy

class Json(object):
	@staticmethod
	def parse(str):
		return json.loads(data);
	
	@staticmethod
	def stringify(obj,bePretty=True,exceptList=[]):
		obj = copy.copy(obj)
		if exceptList and len(exceptList) > 0:
			for exceptedKey in exceptList:
				if exceptedKey in obj.__dict__:
					delattr(obj,exceptedKey)

		encoderParams = {}
		encoderParams["default"] = lambda o: o.__dict__
		if bePretty:
			encoderParams["indent"]     = 4
			encoderParams["separators"] = (',', ': ')
			encoderParams["sort_keys"]  = True

		return json.JSONEncoder(**encoderParams).encode(obj)