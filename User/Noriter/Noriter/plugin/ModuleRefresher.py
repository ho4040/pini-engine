import os
import sys
sys.dont_write_bytecode = True
import types
import importlib
import py_compile as compiler
import collections

from PySide.QtCore import *

class ModuleRefresher(object):
	codeSuffix     = "py"
	complieSuffix  = "pyc"
	optimizeSuffix = "pyo"
	byteSuffix = [complieSuffix,optimizeSuffix]
	moduleSuffix = list([codeSuffix]) #+ byteSuffix

	def __init__(self,basePath = None):
		super(ModuleRefresher,self).__init__()

		self._fsw = QFileSystemWatcher()
		self._fsw.directoryChanged.connect(self.OnDirectoryChanged)
		self._fsw.fileChanged.connect(self.OnFileChanged)

		self.basePath = basePath
		self.watchedModules = {}

		if self.basePath:
			self.setPath(self.basePath)

	def addReference(self,path):
		if not os.path.isdir(path):
			return

		sys.path.append(path)

	def checkSuffixPriority(self,files):
		moduleDict = collections.OrderedDict()

		for file in files:
			fileInfo      = QFileInfo(file)
			suffix        = fileInfo.suffix()
			if not suffix in self.moduleSuffix:
				continue
			path          = fileInfo.path()
			baseName      = fileInfo.completeBaseName()
			withoutSuffix = os.path.join(path,baseName)

			suffixList = moduleDict.get(withoutSuffix,[])
			suffixList.append(suffix)

			moduleDict[withoutSuffix] = suffixList

		for withoutSuffix,suffixList in moduleDict.items():
			del moduleDict[withoutSuffix]
			withoutSuffix = os.path.abspath(withoutSuffix)
			moduleDict[withoutSuffix] = suffixList

		return moduleDict

	def packageFirstSort(self,paths):
		def functor(lhs,rhs):
			packageLhs = lhs.replace(os.sep,'.')
			packageRhs = rhs.replace(os.sep,'.')

			lhsDepth = len(packageLhs.split('.'))
			rhsDepth = len(packageRhs.split('.'))

			return cmp(lhsDepth,rhsDepth)
		paths.sort(cmp=functor)

		sortedList = []
		for idx,path in enumerate(paths):
			path = os.path.abspath(path)
			pathInfo = QFileInfo(path)
			baseName = pathInfo.baseName()
			if pathInfo.baseName().lower() == "__init__":
				sortedList.insert(0,path)
			else:
				sortedList.append(path)

		return sortedList

	def setPath(self,path):
		if not os.path.isdir(path):
			return
		# watch self directory
		path = os.path.abspath(path)
		self.basePath = path
		self.checkAndWatch(path)

		# add plugin path
		index = path.rfind(os.sep)
		name  = path[index+len(os.sep):]

		plugins = types.ModuleType(str(name))
		plugins.__path__ =  [path]
		sys.modules[name] = plugins

		# walk in plugin path and watch all modules
		for root,dirs,files in os.walk(path):
			dirs = [os.path.join(root,dir) for dir in dirs]
			self.checkAndWatch(dirs)

			files = [os.path.join(root,file) for file in files]
			files = self.packageFirstSort(files)

			QDir.addSearchPath("extern", root );

			for modulePath in files:
				######################################################
				'''
				byteModulePath = self.checkAndCompile(modulePath)
				if byteModulePath:
					self.loadModule(byteModulePath)
				'''
				######################################################
				self.checkAndWatch(modulePath)
				self.loadModule(modulePath)


	def clearPath(self):
		files       = self._fsw.files()
		directories = self._fsw.directories()

		if len(files) > 0:
			self._fsw.removePaths(files)
		if len(directories) > 0:
			self._fsw.removePaths(directories)

		self.basePath = None
		self.watchedModules = {}

	def moduleNameFromPath(self,path):
		fileInfo = QFileInfo(path)

		withoutSuffix = os.path.join(fileInfo.path(),fileInfo.baseName())
		withoutSuffix = os.path.abspath(withoutSuffix)

		moduleName = None

		if not self.basePath:
			return moduleName

		basePath = self.basePath
		index = basePath.rfind(os.sep)
		basePath = basePath[0:index + len(os.sep)]

		index = withoutSuffix.find(basePath)
		if index != -1:
			moduleName = withoutSuffix[index+len(basePath):]
			moduleName = moduleName.replace(os.sep,'.')

			if moduleName[:1] == '.':
				moduleName = moduleName[1:]
			if moduleName[-1:] == '.':
				moduleName = moduleName[:-1]

		return moduleName

	def packageNameFromPath(self,path):
		moduleName = self.moduleNameFromPath(path)
		if not moduleName:
			return moduleName

		index = moduleName.rfind('.')
		packageName = moduleName[:index]

		return packageName

	def callStart(self,module):
		if module:
			if hasattr(module,'start'):
				startFunc = getattr(module,'start')
				if type(startFunc) == types.FunctionType:
					startFunc()

	def loadModule(self,path):
		moduleName  = self.moduleNameFromPath(path)
		packageName = self.packageNameFromPath(path)

		if moduleName == None or packageName == None:
			return None

		module = None
		try:
			isWatched = moduleName in self.watchedModules
			if moduleName in sys.modules:
				if not isWatched:
					reload(sys.modules[moduleName])
					module = sys.modules[moduleName]
					self.callStart(module)
			else:
				module = importlib.import_module(moduleName,packageName)
				# module = __import__(moduleName)


			if module:
				if not isWatched:
					self.callStart(module)
				self.watchedModules[moduleName] = module
		except Exception as e:
				print str(e)

		return module

	def reloadModule(self,path):
		moduleName  = self.moduleNameFromPath(path)
		packageName = self.packageNameFromPath(path)

		if moduleName == None or packageName == None:
			return None

		module = None
		if moduleName in sys.modules:
			module = sys.modules[moduleName]
			try:
				reload(module)
				self.callStart(module)
			except Exception as e:
				print str(e)

		return module

	def changeSuffix(self,path,suffix):
		moduleInfo = QFileInfo(path)
		suffixLen  = len(moduleInfo.completeSuffix() + os.extsep)
		withoutSuffix = path[:-suffixLen]

		result = withoutSuffix + os.extsep + suffix
		result = os.path.abspath(result)
		return  result

	def checkAndCompile(self,modulePath):
		codeModulePath = self.changeSuffix(modulePath,self.codeSuffix)
		byteModulePath = self.changeSuffix(modulePath,self.complieSuffix)

		existCode = os.path.isfile(codeModulePath)
		existByte = os.path.isfile(byteModulePath)

		if existCode and existByte:
			self.compile(modulePath)
			self.checkAndWatch(codeModulePath)
			self.checkAndWatch(byteModulePath)
		if existCode and not existByte:
			self.checkAndWatch(codeModulePath)
		elif not existCode and not existByte:
			byteModulePath = None

		if byteModulePath:
			self.checkAndWatch(byteModulePath)
		return byteModulePath

	def compile(self,src):
		srcInfo = QFileInfo(src)

		if srcInfo.completeSuffix() != self.codeSuffix:
			return

		dest = self.changeSuffix(src,self.complieSuffix)
		error = self.changeSuffix(src,"error")
		try:
			compiler.compile(file=src,cfile=dest,dfile=error,doraise=True)
		except compiler.PyCompileError as e:
			print str(e)
		except Exception as e:
			print str(e)

	def checkAndWatch(self,paths,postWatched = None,preWatched = None):
		if isinstance(paths,basestring):
			paths = [paths]

		for path in paths:
			isFile = os.path.isfile(path)
			isDir  = os.path.isdir(path)

			if not isFile and not isDir:
				continue
			path = os.path.abspath(path)

			compareList = None
			if isFile:
				compareList = self._fsw.files()
			elif isDir:
				compareList = self._fsw.directories()

			isWatched = path in compareList

			if not isWatched:
				checkPostWatched = postWatched and type(postWatched) == types.FunctionType
				checkPreWatched  = preWatched and type(preWatched) == types.FunctionType

				if checkPreWatched:
					preWatched(path)

				self._fsw.addPath(path)

				if checkPostWatched:
					postWatched(path)
	'''
	def OnDirectoryChanged (self,path):
		print "OnDirectoryChanged :"
		print path

		moduleNames        = set()
		watchedModuleNames = set(self.watchedModules.keys())
		for root,dirs,files in os.walk(path):
			files = [os.path.join(root,file) for file in files]
			files = self.packageFirstSort(files)
			moduleNames |= set([self.moduleNameFromPath(file) for file in files])

		removedModules = watchedModuleNames - moduleNames
		for moduleName in removedModules:
			if moduleName in self.watchedModules:
				del self.watchedModules[moduleName]

		for root,dirs,files in os.walk(path):
			dirs = [os.path.join(root,dir) for dir in dirs]
			self.checkAndWatch(dirs)

			files = [os.path.join(root,file) for file in files]
			files = self.packageFirstSort(files)

			for file in files:
				fileInfo = QFileInfo(file)
				suffix   = fileInfo.completeSuffix()
				if suffix != self.codeSuffix and suffix != self.byteSuffix:
					continue

				if not file in self._fsw.files():
					byteModulePath = self.checkAndCompile(file)
					if byteModulePath:
						self.loadModule(byteModulePath)
	
	def OnFileChanged (self,path):
		print "OnFileChanged :"
		print path

		path = os.path.abspath(path)
		fileInfo = QFileInfo(path)
		if not fileInfo.suffix() in self.moduleSuffix:
			return

		if os.path.exists(path):
			if fileInfo.suffix() == self.codeSuffix:
				self.compile(path)
			elif fileInfo.suffix() == self.complieSuffix:
				self.reloadModule(path)
		else:
			dir = os.path.dirname(path)

			for root,dirs,files in os.walk(dir):
				for file in files:
					file = os.path.join(root,file)
					file = os.path.abspath(file)
					fileInfo = QFileInfo(file)
					if not fileInfo.suffix() in self.moduleSuffix:
						continue

					if not file in self._fsw.files():
						byteModulePath = file
						if fileInfo.suffix() == self.codeSuffix:
							byteModulePath = self.checkAndCompile(file)
						if byteModulePath:
							self.loadModule(byteModulePath)
	'''
	def OnDirectoryChanged (self,path):
		moduleNames        = set()
		watchedModuleNames = set(self.watchedModules.keys())
		for root,dirs,files in os.walk(path):
			files = [os.path.join(root,file) for file in files]
			files = self.packageFirstSort(files)
			moduleNames |= set([self.moduleNameFromPath(file) for file in files])


		basePath = self.basePath
		index = basePath.rfind(os.sep)
		basePath = basePath[0:index + len(os.sep)]
		index = path.find(basePath)
		basePath = path[index+len(basePath):]
		basePackage = basePath.replace(os.sep,'.')

		watchedModuleNames = list(watchedModuleNames)
		selected = []
		for watchedModuleName in watchedModuleNames:
			index = watchedModuleName.find(basePackage)
			if index != -1:
				selected.append(watchedModuleName)
		watchedModuleNames = set(selected)

		removedModules = watchedModuleNames - moduleNames
		for moduleName in removedModules:
			if moduleName in self.watchedModules:
				del self.watchedModules[moduleName]

		for root,dirs,files in os.walk(path):
			dirs = [os.path.join(root,dir) for dir in dirs]
			self.checkAndWatch(dirs)

			files = [os.path.join(root,file) for file in files]
			files = self.packageFirstSort(files)

			for file in files:
				fileInfo = QFileInfo(file)
				suffix   = fileInfo.completeSuffix()
				if suffix != self.codeSuffix and suffix != self.byteSuffix:
					continue

				if not file in self._fsw.files():
					self.checkAndWatch(file)
					self.loadModule(file)

	def OnFileChanged (self,path):
		path = os.path.abspath(path)
		fileInfo = QFileInfo(path)
		if not fileInfo.suffix() in self.moduleSuffix:
			return

		if os.path.exists(path):
			self.reloadModule(path)
		else:
			dir = os.path.dirname(path)

			for root,dirs,files in os.walk(dir):
				for file in files:
					file = os.path.join(root,file)
					file = os.path.abspath(file)
					fileInfo = QFileInfo(file)
					if not fileInfo.suffix() in self.moduleSuffix:
						continue

					if not file in self._fsw.files():
						self.checkAndWatch(file)
						self.loadModule(file)
