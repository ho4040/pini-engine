# -*- coding: utf-8 -*-
import sys
import os

from PySide.QtCore import *
from PySide.QtGui import *

class CommandController(QObject):
	class Command(QUndoCommand):
		def __init__(self):
			super(CommandController.Command,self).__init__()
			self.cmdCtrl = CommandController.getInstance()

			from controller.ComponentController import ComponentController
			self.componentCtrl = ComponentController.getInstance()
		def redo(self):
			pass
		def undo(self):
			pass

	#instance
	_instance = None

	@staticmethod
	def getInstance():
		if CommandController._instance == None:
			CommandController._instance = CommandController()
		return CommandController._instance
		
	def __init__(self):
		super(CommandController,self).__init__()
		self.stack = QUndoStack(self)

	def Add(self,cmd):
		self.stack.push(cmd)

	def Undo(self):
		self.stack.undo() 

	def openUndoStack(self):
		self.v = QUndoView(self.stack)
		self.v.show()

def start():
	CommandController().getInstance().openUndoStack()