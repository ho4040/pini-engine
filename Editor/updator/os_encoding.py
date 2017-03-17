from ctypes import cdll
def cp():
	return 'cp' + str(cdll.kernel32.GetACP())