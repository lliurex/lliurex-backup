#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import sys
import os

from . import settings
import gettext
import threading
import datetime

gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class RestoreBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-backup.css"
		self.main_box=builder.get_object("restore_box")
		self.restorefile_label=builder.get_object("restorefile_label")
		self.restorefile_fc=builder.get_object("restorefile_chooserbutton")
		
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.init_threads()
		self.restore_thread=None

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.restorefile_label.set_name("OPTION_LABEL")		
	#def set_css_info	

	def init_threads(self):

		self.restore_thread=threading.Thread()
		self.restore_thread.daemon=True
		
		GObject.threads_init()	

	#def init_threads		

	def restore_clicked(self,widget):

		path=self.restorefile_fc.get_filename()
		self.core.mainWindow.manage_box_control(False)

		if path==None:
			self.core.mainWindow.manage_message(True,8)
			self.core.mainWindow.manage_box_control(True)
			return
		
		self.core.pulsating=True
		self.core.mainWindow.last_action=1
		GLib.timeout_add(250,self.core.mainWindow.pulse_bar)
		self.core.mainWindow.feedback_label.set_name("WAITING_LABEL")
		self.core.mainWindow.feedback_label.set_text(_("Restoring services..."))
		self.core.mainWindow.feedback_progressbar.show()
		self.restore_thread=threading.Thread(target=self.core.backupmanager.restore,args=(path,))
		self.restore_thread.start()	

	#def restore_clicked
	

#class RestoreBox

from . import Core