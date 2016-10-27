#-*- coding: utf-8 -*- 
import locale
import codecs
import os
import json
import gspread
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

	print "========macro========="
	#매크로 코드 생성
	r = 0

	ArgTablePrefix = u'''{| class="wikitable"
| style="width:100px; background-color:#f0f0f0"|매개변수명
| style="width:100px; background-color:#f0f0f0"|인자타입
| style="width:100px; background-color:#f0f0f0"|생략가능
| style="width:100px; background-color:#f0f0f0"|기본값
| style="background-color:#f0f0f0"|설명
'''
	ArgTableSuffix = u"|}"

	r = 0
	macros = []
	for rowraw in macroSheet:
		if r>0:
			row = rowraw

			if row[7] == "FALSE":
				wikiName = row[1]
				f = codecs.open(os.path.join(cwd,"wiki_gen",wikiName+'.txt'), 'w', 'utf-8')

				params = getParamList(paramSheet, enumSheet, wikiName)

				f.write(u"="+wikiName+u" 매크로=\n\n")

				### 매크로 선언문 
				f.write(u"==정의==\n\n")
				f.write(u"<div style='background-color:#fafafa;border:1px solid #dfdfdf;padding: 5px 10px 5px 10px;'>\n")
				f.write(u"["+wikiName)
				for v in params : 
					f.write(u" "+v[1]+u"=[["+v[3]+u"|"+v[2]+u"]]")
				f.write(u"]\n")
				f.write(u"</div>\n")

				### 매크로 설명
				f.write(u"<br>")
				f.write(row[2])
				f.write(u"\n")
				if len(row) > 5 and len(row[5]) > 0 : 
					f.write(u"\n")
					f.write(row[5])
					f.write(u"\n")

				f.write(u"\n")

				#매개변수
				f.write(u"==매개변수==\n\n")
				if len(params)> 0 : 
					f.write(ArgTablePrefix)
					for v in params : 
						f.write(u"|-\n")
						f.write(u"|"+v[1])
						f.write(u"||[["+v[3]+u"|"+v[2]+u"]]")
						f.write(u"||"+(u"불가능" if v[0] == u"1" else u"가능"))
						if v[2] == u"숫자" : 
							f.write(u"||<code>"+v[4]+"</code>")
						else:
							f.write(u"||<code>\""+v[4]+"\"</code>")
						f.write(u"||"+v[5]+u"\n")
					f.write(ArgTableSuffix)
				else:
					f.write(u"<code>["+wikiName+u"]</code>매크로는 매개변수 없으므로 매크로 단독으로 호출하면 됩니다.\n")

				#예제를 넣어주세요....
				f.write(u"\n\n==예제==\n\n")
				if len(row) > 6:
					f.write(row[6])

				f.close()
		r = r+1

def getParamList(paramSheet, enumSheet, macroName):	
	#print "========getParamList========="+macroName
	paramList = [];	
	for row in paramSheet:
		datas = row
		macro =	datas[0]
		if macro == macroName:
			must 		= datas[1]
			name 		= datas[3]
			enumType 	= datas[4]
			defVal 	    = datas[5]
			desc 	    = datas[6]
			desc        = desc.replace("\n","<br>")
			desc        = desc.replace('"',"'")

			enumWiki = getEnumWikiPage(enumSheet,enumType)

			paramList.append([must,name,enumType,enumWiki,defVal,desc])
	return paramList

def getEnumWikiPage(enumSheet,enumName):
	for row in enumSheet:
		datas = row
		enum =	datas[1]
		if enum == enumName:
			return datas[4]
	return "not finded"

main()