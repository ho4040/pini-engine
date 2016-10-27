#-*- coding: utf-8 -*- 
import locale
import shutil
import json
import gspread
import codecs
import os
from oauth2client.client import SignedJwtAssertionCredentials

cwd = os.path.abspath(os.path.dirname(__file__))
if len(cwd) == 0:
	cwd = "."


def main():
	json_key = json.load(open('piniProject_key.json'))
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

	gc = gspread.authorize(credentials)

	doc = gc.open("libdef_kr")

	enumSheet = doc.worksheet("enum").get_all_values()
	macroSheet = doc.worksheet("macro").get_all_values()
	paramSheet = doc.worksheet("param").get_all_values()

	f = codecs.open(os.path.join(cwd,'libdef.lnx'), 'w', 'utf-8')

	f.write(u"#######################################\n")
	f.write(u"##자동생성된 파일입니다. 수정불가.\n")
	f.write(u"#######################################\n\n")

	print "========enum========="
	#매개변수 열거형 코드 생성
	r = 0
	enumNames = []
	for row in enumSheet:
		if r>0:
			datas = row

			eName = datas[1]
			if eName : 
				bWrite = datas[2]
				content = []
				print datas[5]
				if datas[5] : 
					c = 0
					while True:
						n = None
						d = None
						try:
							n = datas[5+2*c]
							d = datas[5+2*c+1]
						except Exception, e:
							pass
						if n == None or n == "" : 
							break
						content.append('{"'+n+'"|"'+d+'"}')
						c += 1

					content = "|".join(content)
				else:
					content = ""

				if bWrite == "TRUE":
					enumNames.append("~"+eName+"{"+content+"}")
					print eName;
				else:
					print eName + " is passed";
		else:
			enumNames.append(u"#매개변수 타입 목록\n")
		r = r+1
	f.write("\n".join(enumNames))


	print "========macro========="
	#매크로 코드 생성
	r = 0

	macros = []
	for row in macroSheet:
		if r>0:
			datas = row

			if datas[7] == "FALSE":
				mName = datas[1]
				pre = "!"+mName+"{"
				head = getMacroDesc(macroSheet, mName)
				body = getParamList(paramSheet, mName)
				post = "}\n"
				content="\n".join([pre, head, body, post])
				macros.append(content)
				print(mName)
		else:
			macros.append(u"\n\n#매크로 목록\n")
		r = r+1

	f.write("\n".join(macros))

	print "=========macro to lua=========="
	luaFuncList = []
	r=0	
	for row in macroSheet:
		if r>0:
			datas = row

			if len(datas) > 4 and datas[4] != "":
				mName = datas[1]
				luaFunc = datas[4]
				print mName
				#print type(luaFunc)
				luaFuncList.append(u"@매크로 "+mName+u':\n\t[['+luaFunc+u']]\n')
		else:
			luaFuncList.append(u"#매크로 루아함수 목록\n\n")
		r = r+1

	f.write("\n".join(luaFuncList))

	f.close()

	path1 = os.path.join(cwd,".","libdef.lnx")
	path2 = os.path.join(cwd,"..","..","User","pini","resource","proj_default","module","libdef.lnx")
	
	try:
		os.remove(path2)
	except Exception, e:
		pass

	shutil.copyfile(path1,path2)


def getMacroDesc(macroSheet, macroName):
	#print "========getMacroDesc========="+macroName
	baseURL = 'http://nooslab.com/piniengine/wiki/index.php?title='
		
	for row in macroSheet:
		datas = row
		name = datas[1]
		if name == macroName:
			desc = datas[2] if datas[2] else ""
			wikiPage = datas[3]
			title = "<p class='title'>"+name+"</p>"
			link = "<a href='"+baseURL+wikiPage+u"'>..자세히</a>"
			return '\t"'+"".join([title,desc,link])+'"|'



def getParamList(paramSheet, macroName):	
	#print "========getParamList========="+macroName
	paramList = [];	
	for row in paramSheet:
		datas = row
		macro =	datas[0]
		if macro == macroName:
			must 		= datas[1]
			name 		= datas[3]
			enumType 	= datas[4]
			defVal   	= datas[5]
			desc        = datas[6]
			desc        = desc.replace("\n","<br>")
			desc        = desc.replace('"',"'")

			if enumType == unicode("숫자", "utf-8"):
				if defVal == unicode("", "utf-8"):
					defVal = unicode("0", "utf-8")
				paramList.append( '{'+ "| ".join([must, name, '""', defVal, '"'+desc+'"'])+'}')
			elif enumType == unicode("문자열", "utf-8"):
				paramList.append( '{'+ "| ".join([must, name, '""', '"'+defVal+'"', '"'+desc+'"'])+'}')
			else:			
				paramList.append( '{'+ "| ".join([must, name, '"'+enumType+'"', '"'+defVal+'"', '"'+desc+'"'])+'}')

	ret = "\t"+"|\n\t".join(paramList)
	return ret

main()