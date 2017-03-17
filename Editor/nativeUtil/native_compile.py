import subprocess
import os
import sys

cwd = os.path.abspath(os.path.dirname(__file__))
if len(cwd) == 0:
	cwd = "."

def myjoin(*args):
	path = os.path.join(*args)
	path = os.path.abspath(path)
	return path

def PROCESS(_arg,**sub):
	sub["stdout"] = subprocess.PIPE
	sub["stdin"] = subprocess.PIPE
	sub["shell"] = True
	fse = sys.getfilesystemencoding()
	_arg = [arg.encode(fse) if isinstance(arg,unicode) else arg for arg in _arg]
	proc = subprocess.Popen(_arg, **sub )
	try:
		out, err = proc.communicate()
		return out
	except Exception, e:
		print("!!\n")
		return None

arg = [
	"g++", 
	"-DGPP_FOR_PYTHON=1"
	'-E',
	'-dM',
	"-shared",
	"-std=c++11",
	"*.cpp",
	"-o", myjoin(cwd,"../pini/native.so")
]


if __name__ == "__main__":
	print(">")
	PROCESS(arg)
	print("<")
