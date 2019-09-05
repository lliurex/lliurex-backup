#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib


import signal
import os
import subprocess
import json
import sys
import time
import threading

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import settings
import gettext
_ = gettext.gettext

class MainWindow:
	
	def __init__(self,sync_folder=None):

		self.core=Core.Core.get_core()

		self.services=[(_("LliureX Server basic services"),"Hostname, Network, DNSmasq, Proxy, LDAP, Samba",True,-1,"ServerBackupManager"),
		("Apache",_("HTTP Server"),False,0,"ApacheManager"),
		("CUPS",_("Printing service"),False,0,"CupsManager"),
		("MySQL",_("MySQL Database"),False,0,"MysqlManager"),
		("NFS",_("NFS configuration"),False,0,"NfsManager"),
		("Moodle",_("Moodle"),False,0,"MoodleManager"),
		("PMB",_("Pmb"),False,0,"PmbManager")]

		self.services_list={}
		self.pulsating=False
		self.last_action=-1
		

	#def init

	def load_gui(self):
		
		gettext.textdomain(settings.TEXT_DOMAIN)
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-backup.css"
				
		self.stack_window= Gtk.Stack()
		self.stack_window.set_transition_duration(750)
		self.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_window.set_margin_top(0)
		self.stack_window.set_margin_bottom(0)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("LliureX Backup")
		self.main_window.resize(700,750)
		self.main_box=builder.get_object("main_box")
		self.banner_box=builder.get_object("banner_box")
		
		self.options_box=builder.get_object("options_box")
		self.backup_eventbox=builder.get_object("backup_eventbox")
		self.backup_label=builder.get_object("backup_label")
		self.restore_eventbox=builder.get_object("restore_eventbox")
		self.restore_label=builder.get_object("restore_label")

		self.feedback_label=builder.get_object("feedback_label")
		self.feedback_progressbar=builder.get_object("feedback_progressbar")

		self.help_button=builder.get_object("help_button")
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_APPLY,Gtk.IconSize.MENU)
		self.backup_button=builder.get_object("backup_button")
		self.backup_button.set_image(image)
		self.restore_button=builder.get_object("restore_button")
		self.restore_button.set_image(image)
		self.stack_window.add_titled(self.core.loginBox,"loginBox","Login Box")
		self.stack_window.add_titled(self.options_box, "optionsBox", "Options Box")
		self.stack_window.show_all()
		self.main_box.pack_start(self.stack_window,True,True,0)

		self.stack_opt= Gtk.Stack()
		self.stack_opt.set_transition_duration(750)
		self.stack_opt.set_halign(Gtk.Align.FILL)
		self.stack_opt.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

		self.stack_opt.add_titled(self.core.backupBox,"backupBox","Backup Box")
		self.stack_opt.add_titled(self.core.restoreBox, "restoreBox", "Restore Box")

		self.stack_opt.show_all()
		self.options_box.pack_start(self.stack_opt,True,True,5)

		
	
		self.set_css_info()
		self.init_threads()
		self.connect_signals()
		self.core.loginBox.login_button.grab_focus()
		self.main_window.show_all()
		self.stack_window.set_transition_type(Gtk.StackTransitionType.NONE)
		self.stack_window.set_visible_child_name("loginBox")
		self.restore_button.hide()
		self.feedback_label.set_text("")
		self.feedback_progressbar.hide()

		
	#def load_gui


	def init_threads(self):

		GObject.threads_init()

	#def init_threads

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		self.backup_label.set_name("MAIN_LABEL_ENABLED")
		self.restore_label.set_name("MAIN_LABEL_DISABLED")
		self.banner_box.set_name("BANNER-BOX")

	#def set_css_info	
				
	def connect_signals(self):

		self.main_window.connect("destroy",self.quit)
		self.backup_eventbox.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		self.backup_eventbox.connect("button-press-event",self.label_clicked,0)
		self.restore_eventbox.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		self.restore_eventbox.connect("button-press-event",self.label_clicked,1)
		self.help_button.connect("clicked",self.help_clicked)
		self.backup_button.connect("clicked",self.core.backupBox.backup_clicked)
		self.restore_button.connect("clicked",self.core.restoreBox.restore_clicked)	

	#def connect_signals	

	def load_info(self):
	
		cont=0
		for item in self.services:
			cont+=1
			self.services_list[cont]=item

	#def load_info	
		
	def label_clicked(self,widget,event,option):

		self.feedback_label.set_text("")
		
		if option==0:
			self.restore_button.hide()
			self.backup_button.show()
			self.stack_opt.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
			self.stack_opt.set_visible_child_name("backupBox")
			self.backup_label.set_name("MAIN_LABEL_ENABLED")
			self.restore_label.set_name("MAIN_LABEL_DISABLED")
		else:
			self.restore_button.show()
			self.backup_button.hide()
			self.stack_opt.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
			self.stack_opt.set_visible_child_name("restoreBox")
			self.backup_label.set_name("MAIN_LABEL_DISABLED")
			self.restore_label.set_name("MAIN_LABEL_ENABLED")

	#def label_clicked		


	def pulse_bar(self):

		self.feedback_progressbar.pulse()

		if self.last_action==0:
			if self.core.backupBox.backup_thread.is_alive():
				return True

			elif self.core.backupmanager.backup_ret!=None:
				if self.core.backupmanager.backup_ret[0]:
					self.last_action=0
					self.manage_message(False,4,self.core.backupmanager.backup_ret[1])
				else:
					self.manage_message(True,5,self.core.backupmanager.backup_ret[1])

				self.feedback_progressbar.hide()
				self.pulsating=False
				self.manage_box_control(True)		
				
				return False

		if self.last_action==1:

			if self.core.restoreBox.restore_thread.is_alive():
				return True

			elif self.core.backupmanager.restore_ret!=None:
				if self.core.backupmanager.restore_ret[0]:
					self.last_action=1
					self.manage_message(False,9)
				else:
					self.manage_message(True,10,self.core.backupmanager.restore_ret[1])

				self.feedback_progressbar.hide()
				self.pulsating=False
				self.manage_box_control(True)		
				return False

		
		return self.pulsating

	#def pulse_bar	

	def manage_message(self,error,code,data=None):

		msg=self.get_msg(code)
		if data!=None:
			msg=msg%data
		
		if error:
			self.feedback_label.set_name("MSG_ERROR_LABEL")
		else:
			self.feedback_label.set_name("MSG_CORRECT_LABEL")	

		self.feedback_label.set_text(msg)

	#def manage_message		


	def get_msg(self,code):

		msg_test=""
		if code==1:
			msg_text=_("%s or its parent path is already in the backup list")
		elif code==2:
			msg_text=_("The selected folder has been edited successfully")
		elif code==3:
			msg_text=_("The selected folder has been added to the backup list")
		elif code==4:
			msg_text=_("Backup file created successfully: \n%s")
		elif code==5:
			msg_text=_("Creation of backup file failed: \n%s")	
		elif code==6:
			msg_text=_("The selected folder has been removed to the backup list")
		elif code==7:
			msg_text=_("You must select a directory to save the generated backup")
		elif code==8:
			msg_text=_("You must select a restoration file")
		elif code==9:
			msg_text=_("Restoration complete sucessfully")
		elif code==10:
			msg_text=_("Restoration failed: \n%s")	
		elif code==11:
			msg_text=_("%s folder can not be added to the backup list")	

		return msg_text

	#def get_msg

	def manage_box_control(self,sensitive):	

		self.main_box.set_sensitive(sensitive)
		self.core.backupBox.main_box.set_sensitive(sensitive)
		self.core.restoreBox.main_box.set_sensitive(sensitive)

	#def manage_box_control	

	def help_clicked(self,widget):

		lang=os.environ["LANG"]

		if 'ca_ES' in lang:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX-Backup-en-Bionic_va'
		else:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX-Backup-en-Bionic'

		os.system(cmd)

	#def help_clicked	
	
	
	def quit(self,widget):

		Gtk.main_quit()	

	#def quit	

	def start_gui(self):
		
		GObject.threads_init()
		Gtk.main()
		
	#def start_gui


	
#class MainWindow

from . import Core
