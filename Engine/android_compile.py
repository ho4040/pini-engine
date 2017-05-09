import os
import shutil
import xml.etree.ElementTree as ET

cwd = os.path.abspath(os.path.dirname(__file__))
if len(cwd) == 0:
	cwd = "."

def myjoin(*args):
	path = os.path.join(*args)
	path = os.path.abspath(path)
	return path

android_XML = myjoin(cwd,"VisNovel","frameworks","runtime-src","proj.android","AndroidManifest.xml")
CONFIG_JSON = myjoin(cwd,"VisNovel","config.json")

def orientation_landscape() : 
	doc = ET.parse(android_XML)
	ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
	root = doc.getroot()
	root.attrib["package"] = "com.nooslab.pini_remote_landscape"

	# activites = root.find("application").findall("activity")
	# for v in activites :
	# 	if v.attrib["{http://schemas.android.com/apk/res/android}name"] == "org.cocos2dx.lua.AppActivity" :  
	# 		v.attrib["{http://schemas.android.com/apk/res/android}screenOrientation"] = "landscape"

	doc.write(android_XML, encoding="utf-8", xml_declaration=True)
	data = ""
	with open(CONFIG_JSON,"r") as f :
		data = f.read().replace('"isLandscape": false,','"isLandscape": true,');

	with open(CONFIG_JSON,"w") as f :
		f.write(data);

def orientation_portrait() : 
	doc = ET.parse(android_XML)
	ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
	root = doc.getroot()
	root.attrib["package"] = "com.nooslab.pini_remote"
	
	# activites = root.find("application").findall("activity")
	# for v in activites :
	# 	if v.attrib["{http://schemas.android.com/apk/res/android}name"] == "org.cocos2dx.lua.AppActivity" :  
	# 		v.attrib["{http://schemas.android.com/apk/res/android}screenOrientation"] = "portrait"

	doc.write(android_XML, encoding="utf-8", xml_declaration=True)
	data = ""
	with open(CONFIG_JSON,"r") as f :
		data = f.read().replace('"isLandscape": true,','"isLandscape": false,');

	with open(CONFIG_JSON,"w") as f :
		f.write(data);

def compile_run(debug=False,repeat=True,TestRun=False, suffix=".apk", b=False):
	try:
		str_mode = "release"
		distapk = myjoin(cwd,"VisNovel","publish","android","pini_remote-release-signed.apk")
		if debug : 
			distapk = myjoin(cwd,"VisNovel","simulator","android","pini_remote-debug.apk")
			str_mode = "debug"

		print myjoin(cwd,"VisNovel")

		javafile = myjoin(cwd,"VisNovel","frameworks","runtime-src","proj.android","src","org","cocos2dx","lua","AlarmReceive.java")
		content = ""
		with open(javafile, 'r') as content_file:
			content = content_file.read()

		if b : 
			content = content.replace("import com.nooslab.pini_remote.R;","import com.nooslab.pini_remote_landscape.R;")
		else:
			content = content.replace("import com.nooslab.pini_remote_landscape.R;","import com.nooslab.pini_remote.R;")

		with open(javafile, 'w') as content_file:
			content_file.write(content)

		configfile = myjoin(cwd,"VisNovel","src","config.json")
		content = ""
		with open(configfile, 'r') as content_file:
			content = content_file.read()

		if b :
			content = content.replace("\"isLandscape\": false", "\"isLandscape\": true")
		else:
			content = content.replace("\"isLandscape\": true", "\"isLandscape\": false")

		with open(configfile, 'w') as content_file:
			content_file.write(content)

		#"com.nooslab.pini_remote"

		print "cocos compile -s "+myjoin(cwd,"VisNovel")+" -p android -m "+str_mode+" --ap android-14 --compile-script 0"
		print os.system("cocos compile -s "+myjoin(cwd,"VisNovel")+" -p android -m "+str_mode+" --ap android-14 --compile-script 0")

		newapk = myjoin(cwd,"android","PiniRemote"+suffix)

		shutil.copyfile(distapk,newapk)
		try:
			os.remove(distapk)
			
			if debug == False : 
				shutil.rmtree(myjoin(cwd,"VisNovel","publish"))
			else:
				shutil.rmtree(myjoin(cwd,"VisNovel","simulator"))
				
		except Exception, e:
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
			print e
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

		if TestRun : 
			path = os.environ['ANDROID_SDK_ROOT']
			if path :
				adbpath = myjoin(path,"platform-tools","adb.exe"); 
				adbpath = "\"" + adbpath + "\""
				print os.system(adbpath+" uninstall com.nooslab.pini_remote_landscape")
				print os.system(adbpath+" install "+newapk)
				print os.system(adbpath+" shell am start -a android.intent.action.MAIN -n com.nooslab.pini_remote_landscape/org.cocos2dx.lua.AppActivity")
				print os.system('adb logcat | findstr "cocos2d-x"')
			else:
				print os.system("E:\\android-sdk-windows\\platform-tools\\adb.exe uninstall com.nooslab.pini_remote")
				print os.system("E:\\android-sdk-windows\\platform-tools\\adb.exe install "+newapk)
				print os.system("E:\\android-sdk-windows\\platform-tools\\adb.exe shell am start -a android.intent.action.MAIN -n com.nooslab.pini_remote/org.cocos2dx.lua.AppActivity")
				print os.system("E:\\android-sdk-windows\\platform-tools\\adb.exe logcat")
			#os.system("C:\\Users\\reve\\android-sdk-windows\\platform-tools\\adb.exe logcat > log.txt")
	except Exception, e:
		print "***************************************"
		print e
		print "***************************************"
		if repeat : 
			compile_run()

if __name__ == "__main__":
	#orientation_portrait();
	#compile_run(True,False,False,"-portrait.apk")

	orientation_landscape();
	compile_run(False,False,True,"-landscape.apk",True)

	#orientation_portrait();
	#compile_run(True,False,True,"-portrait.apk")
