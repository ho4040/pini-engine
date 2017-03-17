# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import math

M_PI_2 = math.pi/2.0
M_PI = math.pi
def interpolation(t,o1,o2):
	return round(( 1 - t )*o1 + t*o2,2)

def linear(time) : 
	return time

def sineEaseIn(time):
	return -1 * math.cos(time * M_PI_2) + 1
	
def sineEaseOut(time) : 
	return math.sin(time * M_PI_2)
	
def sineEaseInOut(time) : 
	return -0.5 * (math.cos(M_PI * time) - 1)

def EaseImmediately(time):
	if time >= 1 : 
		return 1
	return 0

#########################################
## types
line_Interval = [
	u"위치X",
	u"위치Y",
	u"크기X",
	u"크기Y",
	u"회전",
	u"색상R",
	u"색상G",
	u"색상B",
	u"색상A",
]
line_Interval_Default = [
	0,
	0,
	1,
	1,
	0,
	255,
	255,
	255,
	255
]

line_Instant = [
	u"매크로",
	u"루아",
	u"이미지",
]
line_type = line_Interval + line_Instant

############################################
#### ease type!
line_ease = [
	u"기본",
	u"사인인",
	u"사인아웃",
	u"사인인아웃",
	u"즉시",
]

##############################################
#### set type
line_increment = [
	u"증가",
	u"변경",
]

from ctypes import *
atl = cdll.LoadLibrary("ATL.so") 

atl.getNumberVal.restype = c_float
atl.getNumberSetVal.restype = c_float
atl.getNumberSet.restype = c_float
atl.isValue.restype = c_bool
atl.getFrame.restype = c_int
atl.getMaxFrame.restype = c_int
atl.getMarkedFrames.restype = c_char_p
atl.getStringVal.restype = c_char_p

atl.registAnimation.argtypes = [c_char_p]
atl.getMarkedFrames.argtypes = [c_char_p,c_int]
atl.getFrame.argtypes = [c_char_p,c_int,c_int,c_char_p,c_char_p]
atl.getMaxFrame.argtypes = [c_char_p,c_int]
atl.isExists.argtypes = [c_char_p]
atl.numNode.argtypes = [c_char_p]

atl.registStringValue.argtypes = [c_char_p,c_char_p,c_char_p]
atl.registNumberValue.argtypes = [c_char_p,c_char_p,c_float]
atl.deleteNodeValue.argtypes = [c_char_p]

def FAL_REGIST(json):
	atl.registAnimation(json)
def FAL_GETFRAME(idx,node,frame,nodeName,_hash):
	return atl.getFrame(idx,node,frame,nodeName,_hash)
def FAL_GETVALUE(frame,key):
	return atl.getNumberVal(frame,key), atl.getNumberSetVal(frame,key), atl.getNumberSet(frame, key)
def FAL_GETSTRVALUE(frame,key):
	return atl.getStringVal(frame,key).decode("mbcs")
def FAL_ISVALUE(frame,key):
	return atl.isValue(frame,key)
def FAL_DELETEFRAME(frame):
	atl.deleteFrame(frame)
def FAL_MAXFRAME(idx,node):
	return atl.getMaxFrame(idx,node)
def FAL_MARKEDFRAMES(idx,node):
	frames = atl.getMarkedFrames(idx,node)
	frames = frames.split(",")
	if len(frames) > 0 :
		frames = frames[0:-1]

	frames = [int(v) for v in frames]
	return frames
def FAL_ISEXISTS(idx):
	return atl.isExists(idx)
def FAL_NUMNODE(idx):
	return atl.numNode(idx)
def FAL_REGISTSTRINGVALUE(node,idx,value):
	atl.registStringValue(node,idx,value)
def FAL_REGISTNUMBERVALUE(node,idx,value):
	atl.registNumberValue(node,idx,value)
def FAL_DELETENODEVALUE(node):
	atl.deleteNodeValue(node)
def FAL_CLEARFRAME(): 
	atl.clearFrame()
