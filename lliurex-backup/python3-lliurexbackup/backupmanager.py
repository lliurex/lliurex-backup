#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import os
import json
import codecs
import datetime

import xmlrpc.client as n4dclient
import ssl
import shutil
import re
import subprocess



class BackupManager(object):

	def __init__(self,server=None):

		super(BackupManager, self).__init__()

		self.dbg=1
		self.user_validated=False
		self.user_groups=[]
		self.validation=None

		if server!=None:
			self.set_server(server)

		context=ssl._create_unverified_context()
		self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
		self.detect_flavour()	
	
	#def __init__	
	

	def set_server(self,server):	
		
		context=ssl._create_unverified_context()	
		self.n4d=n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
	
	#def set_server
		
	def detect_flavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def detect_flavour

	def validate_user(self,user,password):
		
		ret=self.n4d.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.validation=(user,password)
					
		#return self.user_validated
		
	#def validate_user

	def backup(self,path,services,folders):

		try:
			self.backup_ret=self.n4d.backup(self.validation,"ServerBackupManager",path,services,folders)
			self.backup_ret=[True,self.backup_ret[2]]
			
		except Exception as e:
			self.backup_ret=[False,str(e)]
		
		self._debug("Backup",self.backup_ret)	
		#self.pulsating=False
		
		return False	

	#def backup

	def restore (self,path):

		try:
			self.restore_ret=self.n4d.restore(self.validation,"ServerBackupManager",path)
		except Exception as e:
			self.restore_ret=[False,str(e)]
		
		self._debug("Restore",self.restore_ret)	
		return False		

	#def restore	

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX BACKUP]: "+ str(function) + str(msg))

	#def _debug		

	