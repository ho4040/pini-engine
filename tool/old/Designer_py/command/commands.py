# -*- coding: utf-8 -*-
import sys
import os

from controller.CommandController import *

class Command(object):
	class Component(object):
		class Modify(CommandController.Command):
			def __init__(self, objModel, number, new):
				super(Command.Component.Modify, self).__init__()

				self.objModel = objModel
				self.number = number
				
				old = {}
				dat = self.objModel.components[self.number].data
				for key,value in new.iteritems():
					v = dat.get(key,None)
					if v != None and v != value : 
						old[key] = v
				
				if len(old.keys()) is 0 :
					return 

				self.new = new
				self.old = old

				self.setText("[ Command/Component/Modify ]")
				self.cmdCtrl.Add(self)

			def undo(self):
				self.componentCtrl.Modify(self.objModel,self.number,self.old)

			def redo(self):
				self.componentCtrl.Modify(self.objModel,self.number,self.new)

		class Add(CommandController.Command):
			def __init__(self, objModel, strId):
				super(Command.Component.Add, self).__init__()
				self.objModel = objModel
				self.number = -1
				self.strId = strId

				self.setText("[ Command/Component/Add ]")
				self.cmdCtrl.Add(self)

			def undo(self):
				if self.number == -1:
					return ;
				self.componentCtrl.Remove(self.objModel,self.number)

			def redo(self):
				self.number = self.componentCtrl.Add(self.objModel,self.strId)

		class Remove(CommandController.Command):
			def __init__(self, objModel, number):
				super(Command.Component.Remove, self).__init__()
				self.objModel = objModel
				self.number = number
				self._def = self.objModel.components[self.number]

				self.setText("[ Command/Component/Remove ]")
				self.cmdCtrl.Add(self)

			def undo(self):
				self.componentCtrl.AddInstance(self.objModel,self._def,self.number)

			def redo(self):
				self.componentCtrl.Remove(self.objModel,self.number)

