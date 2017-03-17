# -*- coding: utf-8 -*-

import os
import re
fw = open("lang.csv","w")
p = re.compile("\".*[가-힣ㄱ-ㅎㅏ-ㅣ]+.*\"")
for root, dirs, files in os.walk(".", topdown=False):
	for name in files:
		path = os.path.join(root, name).replace("\\","/")
		if os.path.splitext(path)[1] == ".py" :
			f = open(path,"r")
			data = f.read()
			f.close()
			#print data

			for m in p.finditer(data):
				print name,m.start(), m.group().decode("utf8")
				fw.write(name)
				fw.write(",")
				fw.write(str(m.start()))
				fw.write(",")
				fw.write(m.group())
				fw.write("\n")


fw.close()