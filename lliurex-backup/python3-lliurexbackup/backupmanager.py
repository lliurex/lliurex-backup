#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import os
import json
import codecs
import datetime

import n4d.client
import ssl
import shutil
import re
import subprocess



class BackupManager(object):

	def __init__(self,server=None):

		super(BackupManager, self).__init__()

		self.dbg=0
		self.user_validated=False
		self.user_groups=[]
		self.validation=None

		'''
		if server!=None:
			self.set_server(server)

		context=ssl._create_unverified_context()
		self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
		'''
		self.detect_flavour()	
	
	#def __init__	
	
	'''
	def set_server(self,server):	
		
		context=ssl._create_unverified_context()	
		self.n4d=n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
	
	#def set_server
	'''	
	def detect_flavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def detect_flavour

	def validate_user(self,server,user,password):
		
		try:
			self.client=n4d.client.Client("https://%s:9779"%server,user,password)

			ret=self.client.validate_user()
			self.user_validated,self.user_groups=ret
			ret=self.client.validate_user()
			self.user_validated=ret[0]
			self.user_groups=ret[1]	
			
			if self.user_validated:
				self.ticket=self.client.get_ticket()
				if self.ticket.valid():
					self.client=n4d.client.Client(ticket=self.ticket)
				else:
					self.user_validated=False

		except Exception as e:
			self._debug("Validate user ",str(e))
			self.user_validated=False

		#return self.user_validated
		
	#def validate_user

	def get_basic_services_list(self):

		ret=[]
		try:
			ret=self.client.ServerBackupManager.get_basic_services_list()
			self._debug("get_basic_services_list",str(ret))
			return ret
		except Exception as e:
			self._debug("get_basic_services_list","Error: "+str(e))
			return ret 


	def backup(self,path,services,folders):

		errors=0
		try:
			ret=self.client.ServerBackupManager.backup(path,services,folders)
			
			for item in ret[1]:
				if not ret[1][item][0]:
					errors+=1
			
			self.backup_ret=[True,ret[2],errors]
			self._debug("Backup",ret)	
		
		except Exception as e:
			self.backup_ret=[False,str(e)]
			self._debug("Backup.Error: "+str(e))
		
		#self.pulsating=False
		
		return False	

	#def backup

	def restore (self,path):

		try:
			restore_ret=self.client.ServerBackupManager.restore(path)
			try:
				if restore_ret[0] or not restore_ret[0]:
					self.restore_ret=restore_ret
			except:
				self.restore_ret=[False,str(restore_ret)]
			
		except Exception as e:
			self.restore_ret=[False,str(e)]
		
		self._debug("Restore",self.restore_ret)	
		return False		

	#def restore	

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX BACKUP]: "+ str(function) + str(msg))

	#def _debug		

	