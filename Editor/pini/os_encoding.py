from ctypes import cdll
import platform
def cp():
	if platform.system() == "Darwin" : 
		return 'utf-8'
	else:
		return 'cp' + str(cdll.kernel32.GetACP())