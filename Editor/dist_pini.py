# -*- coding: utf-8 -*-
import os,sys,shutil
import zipfile,glob,subprocess
import traceback

def u(text):
	return unicode(text,"utf-8")

def myjoin(*args):
	path = os.path.join(*args)
	path = os.path.abspath(path)
	return path

def luaCompileWithLuac(desc,path):
	try:
		for dirname, dirnames, filenames in os.walk(path):
			print "current dirname >> " + dirname.replace(path, '')
			for filename in filenames:
				currentFileName = os.path.join(dirname, os.path.basename(filename));


				if '.lua' in filename:
					execuateCommand = "luac -s -o " + currentFileName + " " + currentFileName;
					os.system(execuateCommand);
				else:
					shutil.copy(currentFileName,output);

		print desc + " lua compile finish"
	except:
		print desc + " lua compile fail"

def luaCompileWithCocos(desc,path):
	try:
		execuateCommand = "cocos luacompile -s {0} -d {0}".format(path)
		os.system(execuateCommand);

		print desc + " lua compile finish"
	except:
		print desc + " lua compile fail"

try:
	option = {
		"stdout":subprocess.PIPE,
		"stderr":subprocess.PIPE
	}

	cwd = os.path.abspath(os.path.dirname(__file__))
	print "c",cwd,__file__
	if len(cwd) == 0:
		cwd = "."

	sys.path.append(myjoin(cwd,"..","novel"))
	from android_compile import compile_run
	from android_compile import orientation_portrait
	from android_compile import orientation_landscape

	dist_root = myjoin(cwd,"pini_distribute")
	pini_root = myjoin(cwd,"pini")
	updator_root = myjoin(cwd,"updator")

	if sys.platform == "darwin" : 
		pass
	else:
		os.chdir(cwd)

		if os.path.exists(dist_root) : 
			shutil.rmtree(dist_root)

		os.chdir(pini_root)
		proc = subprocess.Popen(["python","setup.py","py2exe"],**option)
		out, err = proc.communicate()
		errcode = proc.returncode

		print out,err,errcode

		shutil.move(myjoin(os.curdir,"dist"), dist_root )
		shutil.rmtree(myjoin(os.curdir,"build"))

		shutil.copyfile(myjoin(os.curdir,"atl.so"),myjoin(dist_root,"atl.so"))
		shutil.copyfile(myjoin(os.curdir,"libgcc_s_dw2-1.dll"),myjoin(dist_root,"libgcc_s_dw2-1.dll"))
		shutil.copyfile(myjoin(os.curdir,"libstdc++-6.dll"),myjoin(dist_root,"libstdc++-6.dll"))

		shutil.copytree(myjoin(os.curdir,"resource"),myjoin(dist_root,"resource"))
		shutil.copytree(myjoin(os.curdir,"imageformats"),myjoin(dist_root,"imageformats"))
		shutil.copytree(myjoin(os.pardir,os.pardir,"novel","VisNovel","src"), myjoin(dist_root,"lua"))
		shutil.copytree(myjoin(os.pardir,os.pardir,"novel","window64"), myjoin(dist_root,"window"))
		
		try:
			shutil.rmtree(myjoin(dist_root,"window","src"))
		except Exception, e:
			pass
		try:
			shutil.rmtree(myjoin(dist_root,"window","res"))
		except Exception, e:
			pass
		shutil.copytree(myjoin(os.pardir,os.pardir,"novel","VisNovel","src"),myjoin(dist_root,"window","src"))
		shutil.copytree(myjoin(os.pardir,os.pardir,"novel","VisNovel","res"),myjoin(dist_root,"window","res"))

		# launcher lua compile - dist_root+"\\window\\src"
		launcher_lua = myjoin(dist_root,"window","src")
		luaCompileWithCocos("launcher",launcher_lua)

		### tool lua compile - dist_root+"\\lua"
		tool_lua = myjoin(dist_root,"lua")
		luaCompileWithLuac("tool",tool_lua)

		### cocos lua remove 
		for root, dirs, files in os.walk(myjoin(dist_root,"window","src"), topdown=False):
			for name in files:
				path = os.path.join(root, name).replace("\\","/")
				p,ext= os.path.splitext(path) 
				if ext == ".lua" : 
					print "remove plain-lua ",path
					os.remove(path)

		#################################################################
		### android compile
		orientation_portrait()
		compile_run(False,True,False,"-portrait.apk")

		orientation_landscape()
		compile_run(False,True,False,"-landscape.apk",True)
		#################################################################

		apkdistpath = myjoin(dist_root,"resource","android")
		shutil.rmtree(apkdistpath)
		os.mkdir(apkdistpath)

		srcapk1 = myjoin(dist_root,"..","..","novel","android","PiniRemote-portrait.apk")
		srcapk2 = myjoin(dist_root,"..","..","novel","android","PiniRemote-landscape.apk")
		distapk1= myjoin(apkdistpath,"PiniRemote-portrait.apk")
		distapk2= myjoin(apkdistpath,"PiniRemote-landscape.apk")

		shutil.copy(srcapk1,distapk1)
		shutil.copy(srcapk2,distapk2)

		distapk1 = myjoin(dist_root,"..","pini","resource","android","PiniRemote-portrait.apk")
		distapk2 = myjoin(dist_root,"..","pini","resource","android","PiniRemote-landscape.apk")
		try:
			os.remove(distapk1)
		except Exception, e:
			pass
		try:
			os.remove(distapk2)
		except Exception, e:
			pass

		shutil.copy(srcapk1,distapk1)
		shutil.copy(srcapk2,distapk2)
		
		#################################################################
		os.chdir(updator_root)
		proc = subprocess.Popen(["python","setup.py","py2exe"],**option)
		out, err = proc.communicate()
		errcode = proc.returncode

		print out,err,errcode

		os.chdir(myjoin(updator_root,"dist"))

		#myjoin(os.pardir,os.pardir,"novel","VisNovel","src")
		if os.path.exists(myjoin(os.curdir,"resource")) : 
			shutil.rmtree(myjoin(os.curdir,"resource"))
		if os.path.exists(myjoin(os.curdir,"pygit2")) : 
			shutil.rmtree(myjoin(os.curdir,"pygit2"))

		shutil.copytree(myjoin(os.pardir,"resource"),myjoin(os.curdir,"resource"))
		shutil.copytree(myjoin(os.pardir,"pygit2"), myjoin(os.curdir,"pygit2"))

		'''
		_zip = zipfile.ZipFile(myjoin(os.pardir,os.pardir,"pini_launcher.zip"), 'w')
		for root, dirs, files in os.walk(os.curdir, topdown=False):
			for name in files:
				path = os.path.join(root, name).replace("\\","/")
				_zip.write(path)
		_zip.close()
		'''

		os.chdir(updator_root)
		#shutil.rmtree(myjoin(os.curdir,"dist"))
		nsisMaster = myjoin(os.curdir,"nsis","Master")
		if os.path.isdir(nsisMaster) :
			shutil.rmtree(nsisMaster)
		shutil.move(myjoin(os.curdir,"dist"),nsisMaster)
		shutil.rmtree(myjoin(os.curdir,"build"))

		shutil.copyfile("nsis/Master/Updator.exe","../Updator.exe")

		os.rename("nsis/Master/Updator.exe",u("nsis/Master/피니엔진.exe"))
		shutil.copytree("../pini/imageformats","nsis/Master/imageformats")

		os.system("..\\pini\\nsis\\makensis.exe nsis\\Master.nsi")

		try:
			os.remove("../PiniInstaller.exe")
		except Exception, e:
			pass
		os.rename("nsis/installer.exe","../PiniInstaller.exe")
		shutil.rmtree(nsisMaster)

except Exception, e:
	print e
	traceback.print_exc()
