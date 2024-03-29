#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import sys
import os
import gettext
import threading
from . import settings


gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class LoginBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-backup.css"

		self.login_box=builder.get_object("login_box")
		self.login_button=builder.get_object("login_button")
		self.user_entry=builder.get_object("user_entry")
		self.password_entry=builder.get_object("password_entry")
		self.server_ip_entry=builder.get_object("server_ip_entry")
		self.login_msg_box=builder.get_object("login_msg_box")
		self.login_error_img=builder.get_object("login_error_img")
		self.login_msg_label=builder.get_object("login_msg_label")

		self.pack_start(self.login_box,True,True,0)

		self.set_css_info()
		self.connect_signals()
		self.init_threads()
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.user_entry.set_name("CUSTOM-ENTRY")
		self.password_entry.set_name("CUSTOM-ENTRY")
		self.server_ip_entry.set_name("CUSTOM-ENTRY")
		self.login_msg_box.set_name("HIDE_BOX")		
	#def set_css_info	

	def connect_signals(self):
		
		self.login_button.connect("clicked",self.login_clicked)
		self.user_entry.connect("activate",self.entries_press_event)
		self.password_entry.connect("activate",self.entries_press_event)
		self.server_ip_entry.connect("activate",self.entries_press_event)

	#def connect_signals

	def init_threads(self):
		
		GObject.threads_init()

	#def init_threads	

	def entries_press_event(self,widget):
		
		self.login_clicked(None)
		
	#def entries_press_event
	
	
	def login_clicked(self,widget):
		
		self.login_msg_box.set_name("HIDE_BOX")
		self.login_error_img.hide()
		user=self.user_entry.get_text()
		password=self.password_entry.get_text()
		server=self.server_ip_entry.get_text()
	
		'''	
		# HACK
		
		user="lliurex"
		password="lliurex"
		server="172.20.9.246"
		'''

		if server=="":
			#self.core.backupmanager.set_server(server)
			server='server'		
		
		self.login_msg_label.set_text(_("Validating user..."))
		self.login_msg_label.set_halign(Gtk.Align.CENTER)
		self.login_button.set_sensitive(False)
		self.validate_user(server,user,password)	


	#def login_clicked	
	
	def validate_user(self,server,user,password):
		
		
		t=threading.Thread(target=self.core.backupmanager.validate_user,args=(server,user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	
	def validate_user_listener(self,thread):
			
		error=False
		if thread.is_alive():
			return True
				
		self.login_button.set_sensitive(True)
		if not self.core.backupmanager.user_validated:
			error=True

		else:
			group_found=False
			for g in ["sudo","admins","teachers"]:
				if g in self.core.backupmanager.user_groups:
					group_found=True
					break
					
			if group_found:
				self.login_msg_label.set_text("")
				
				self.core.mainWindow.load_info()
				self.core.backupBox.draw_service(False)
				self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.core.mainWindow.stack_window.set_visible_child_name("optionsBox")
				self.core.mainWindow.stack_opt.set_visible_child_name("backupBox")
							
			else:
				error=True
			
		if error:
			self.login_msg_box.set_name("ERROR_BOX")
			self.login_msg_label.set_name("FEEDBACK_LABEL")
			self.login_error_img.show()
			self.login_msg_label.set_text(_("Invalid user"))
			#self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user")+"</span>")
			self.login_msg_label.set_halign(Gtk.Align.START)

		return False
			
	#def validate_user_listener
	

#class LoginBox

from . import Core