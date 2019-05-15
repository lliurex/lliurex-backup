#!/usr/bin/env python3

import sys
import os


from . import MainWindow
from . import BackupBox
from . import RestoreBox
from . import LoginBox
from . import backupmanager
from . import settings

class Core:
	
	singleton=None
	DEBUG=True
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):

	
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/lliurex-backup.ui"
		
		self.backupmanager=backupmanager.BackupManager()
		self.loginBox=LoginBox.LoginBox()
		self.backupBox=BackupBox.BackupBox()
		self.restoreBox=RestoreBox.RestoreBox()
		self.mainWindow=MainWindow.MainWindow()

		self.mainWindow=MainWindow.MainWindow()

		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
