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


class BackupBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-backup.css"
		self.main_box=builder.get_object("backup_box")
		self.addfolder_button=builder.get_object("addfolder_button")
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_ADD,Gtk.IconSize.MENU)
		self.addfolder_button.set_image(image)
		self.services_box=builder.get_object("services_box")
		self.scrolledwindow=builder.get_object("scrolledwindow")
		self.services_list_vp=builder.get_object("services_list_viewport")
		self.services_list_box=builder.get_object("services_list_box")
		self.target_label=builder.get_object("target_label")
		self.backupfile_chooserbutton=builder.get_object("backupfile_chooserbutton")
		
		self.manage_service_image=self.core.rsrc_dir+"manage_service.svg"

		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.init_threads()
		self.connect_signals()
		self.backup_ret=None
		
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.target_label.set_name("OPTION_LABEL")
					
	#def set_css_info	

	def init_threads(self):

		self.backup_thread=threading.Thread()
		self.backup_thread.daemon=True
		
		GObject.threads_init()	

	#def init_threads		

	def connect_signals(self):

		self.addfolder_button.connect("clicked",self.on_service_clicked)

	#def connect_signals	
			
	def init_services_list(self):
	
		tmp=self.core.backupBox.services_list_box.get_children()
		for item in tmp:
			self.services_list_box.remove(item)

	#def init_services_list
			

	def draw_service(self,search,args=None):

		self.init_services_list()
		self.services_list=self.core.mainWindow.services_list 
			
		cont=len(self.services_list)
		for item in self.services_list:
			self.new_service_box(item,cont)
			cont-=1
		

	#def draw_service		

	def new_service_box(self,serviceId,cont,args=None):

		hbox=Gtk.HBox()
				
		vbox_service=Gtk.VBox()
		vbox_service.id=serviceId
		hbox_service_data=Gtk.HBox()
		hbox_service_description=Gtk.VBox()
		service_name=Gtk.Label()
		service_name.set_text(self.services_list[serviceId][0])
		service_name.set_margin_left(10)
		service_name.set_margin_right(5)
		service_name.set_margin_top(0)
		service_name.set_margin_bottom(0)
		service_name.set_width_chars(40)
		service_name.set_max_width_chars(40)
		service_name.set_xalign(-1)
		service_name.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		service_name.set_name("SERVICE_NAME")
		service_name.set_valign(Gtk.Align.START)

		service_desc=Gtk.Label()
		service_desc.set_text(self.services_list[serviceId][1])
		service_desc.set_margin_left(10)
		service_desc.set_margin_right(5)
		service_desc.set_margin_top(5)
		service_desc.set_margin_bottom(0)
		service_desc.set_width_chars(40)
		service_desc.set_max_width_chars(40)
		service_desc.set_xalign(-1)
		service_desc.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		service_desc.set_name("SERVICE_DESC")
		service_desc.set_valign(Gtk.Align.START)

		hbox_service_description.pack_start(service_name,False,False,1)
		hbox_service_description.pack_end(service_desc,False,False,1)

		
		backup_button=Gtk.CheckButton()
		backup_button.set_halign(Gtk.Align.CENTER)
		backup_button.set_valign(Gtk.Align.CENTER)
		backup_button.set_margin_top(5)
		backup_button.set_margin_right(5)
		

		if self.services_list[serviceId][2]:
			backup_button.set_active(True)
			backup_button.set_tooltip_text(_("Click to not include in the backup"))
		else:
			backup_button.set_active(False)
			backup_button.set_tooltip_text(_("Click to include in the backup"))

				
		backup_button.connect("toggled",self.service_toggled,hbox)

		manage_service=Gtk.Button()
		manage_image_service=Gtk.Image.new_from_file(self.manage_service_image)
		manage_service.add(manage_image_service)
		manage_service.set_margin_top(5)
		manage_service.set_margin_right(10)
		manage_service.set_halign(Gtk.Align.CENTER)
		manage_service.set_valign(Gtk.Align.CENTER)

		if self.services_list[serviceId][3]!=1:
			manage_service.set_name("DEFAULT_ITEM_BUTTON")
			manage_service.set_tooltip_text(_("Default service. Unable to manage it"))
		else:
			manage_service.set_name("EDIT_ITEM_BUTTON")
			manage_service.set_tooltip_text(_("Manage service"))
			manage_service.connect("clicked",self.manage_service_options,hbox)
			popover = Gtk.Popover()
			manage_service.popover=popover
			vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

			change_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
			change_box.set_margin_left(10)
			change_box.set_margin_right(10)
			change_eb=Gtk.EventBox()
			change_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
			change_eb.connect("button-press-event", self.change_service_clicked,hbox)
			change_eb.connect("motion-notify-event", self.mouse_over_popover)
			change_eb.connect("leave-notify-event", self.mouse_exit_popover)
			change_label=Gtk.Label()
			change_label.set_text(_("Change the folder"))
			change_eb.add(change_label)
			change_eb.set_name("POPOVER_OFF")
			change_box.add(change_eb)

			remove_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
			remove_box.set_margin_left(10)
			remove_box.set_margin_right(10)
			remove_eb=Gtk.EventBox()
			remove_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
			remove_eb.connect("button-press-event", self.remove_service_clicked,hbox)
			remove_eb.connect("motion-notify-event", self.mouse_over_popover)
			remove_eb.connect("leave-notify-event", self.mouse_exit_popover)
			remove_label=Gtk.Label()
			remove_label.set_text(_("Remove the folder of the list"))
			remove_eb.add(remove_label)
			remove_eb.set_name("POPOVER_OFF")
			remove_box.add(remove_eb)


			vbox.pack_start(change_box, True, True,8)
			vbox.pack_start(remove_box,True,True,8)
			vbox.show_all()
			popover.add(vbox)
			popover.set_position(Gtk.PositionType.BOTTOM)
			popover.set_relative_to(manage_service)

		hbox_service_data.pack_start(hbox_service_description,False,False,5)
		hbox_service_data.pack_end(manage_service,False,False,5)
		hbox_service_data.pack_end(backup_button,False,False,5)

		service_separator=Gtk.Separator()
		service_separator.set_margin_top(5)
		service_separator.set_margin_left(10)
		service_separator.set_margin_right(10)

		if cont!=1:
			service_separator.set_name("SEPARATOR")
		else:
			service_separator.set_name("WHITE_SEPARATOR")	

		vbox_service.pack_start(hbox_service_data,False,False,5)
		vbox_service.pack_end(service_separator,False,False,5)

		hbox.pack_start(vbox_service,True,True,5)
		hbox.show_all()
		hbox.set_halign(Gtk.Align.FILL)

		self.services_list_box.pack_start(hbox,False,False,1)
		self.services_list_box.queue_draw()
		self.services_list_box.set_valign(Gtk.Align.FILL)
		hbox.queue_draw()	

	#def new_service_box	

	def service_toggled(self,widget,hbox):

		serviceId=hbox.get_children()[0].id
		tmp_service=list(self.core.mainWindow.services_list[serviceId])
		status=not tmp_service[2]
		if status:
			hbox.get_children()[0].get_children()[0].get_children()[1].set_tooltip_text(_("Click to not include in the backup"))
		else:
			hbox.get_children()[0].get_children()[0].get_children()[1].set_tooltip_text(_("Click to include in the backup"))

		tmp_service[2]=status
		self.core.mainWindow.services_list[serviceId]=tuple(tmp_service)

	#def service_toggled 	

	def manage_service_options(self,button,hbox,event=None):
	
		button.popover.show()

	#def manage_site_options

	def on_service_clicked(self, widget):

		self.show_folder_dialog()


	#def on_file_clicked	

	def show_folder_dialog(self,hbox=None):

		dialog = Gtk.FileChooserDialog(_("Please choose a folder"), None,
			Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))


		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			folder_clicked=dialog.get_filename()
			self.add_folder_clicked(folder_clicked,hbox)	
		dialog.destroy()	

	#def show_folder_dialog		


	def add_folder_clicked(self,folder_clicked,hbox):

		serviceId=""
		if folder_clicked!=None:
			if hbox!=None:
				serviceId=hbox.get_children()[0].id
			for item in self.core.mainWindow.services_list:
				if item==serviceId:
					pass
				else:	
					if folder_clicked.startswith(self.core.mainWindow.services_list[item][0]):	
						self.core.mainWindow.manage_message(True,1,folder_clicked)
						return
					else:
						if folder_clicked.startswith("/home"):
							self.core.mainWindow.manage_message(True,11,folder_clicked)
							return	

			if hbox!=None:
				tmp_service=list(self.core.mainWindow.services_list[serviceId])
				tmp_service[0]=folder_clicked
				self.core.mainWindow.services_list[serviceId]=tuple(tmp_service)
				self.core.mainWindow.manage_message(False,2)
			else:
				order=max(self.core.mainWindow.services_list.keys())+1
				tmp_service=(folder_clicked,_("Custom directory"),True,1,"NetFoldersManager")
				self.core.mainWindow.services_list[order]=tmp_service
				self.core.mainWindow.manage_message(False,3)
				
			self.draw_service(False)
	
	#def add_folder_clicked

	def change_service_clicked(self,widget,even,hbox):

		self.show_folder_dialog(hbox)

	#def change_service_clicked 	


	def remove_service_clicked(self,widget,event,hbox):

		serviceId=hbox.get_children()[0].id
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "LliureX Backup")
		dialog.format_secondary_text(_("Do you want delete the folder of the list?"))
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:
			self.core.mainWindow.manage_message(False,6)
			self.core.mainWindow.services_list.pop(serviceId)
			self.draw_service(False)

	#def remove_service_clicked	

	def backup_clicked(self,widget):

		self.core.mainWindow.manage_box_control(False)

		path=self.backupfile_chooserbutton.get_filename()
		
		if path==None:
			self.core.mainWindow.manage_message(True,7)
			self.core.mainWindow.manage_box_control(True)
			return

		folder_list=[]
		service_list=[]
		use_basics=False

		for item in self.core.mainWindow.services_list:
			if self.core.mainWindow.services_list[item][2]:
				class_name=self.core.mainWindow.services_list[item][4]
				if class_name=="ServerBackupManager":
					use_basics=True
				else:
					service_list.append(class_name)
				if self.core.mainWindow.services_list[item][3]!=1:
					print("n4d.backup %s"%class_name)
				else:
					folder_list.append(self.core.mainWindow.services_list[item][0])	

		if use_basics:
			try:
				server_basics=self.core.backupmanager.client.ServerBackupManager.get_basic_services_list()
			except:
				server_basics=[]
			for service in service_list:
				if service not in server_basics:
					server_basics.append(service)	

			service_list=server_basics		
		if len(folder_list)>0:
			if "NetFoldersManager" not in service_list:
				service_list.append("NetFoldersManager")
		else:
			folder_list=None

		self.core.mainWindow.last_action=0
		self.core.pulsating=True
		GLib.timeout_add(250,self.core.mainWindow.pulse_bar)
		self.core.mainWindow.feedback_label.set_name("WAITING_LABEL")
		self.core.mainWindow.feedback_label.set_text(_("Creating backup file..."))
		self.core.mainWindow.feedback_progressbar.show()
		self.backup_thread=threading.Thread(target=self.core.backupmanager.backup,args=(path,service_list,folder_list))
		self.backup_thread.start()

	#def backup_clicked

	
	def mouse_over_popover(self,widget,event=None):

		widget.set_name("POPOVER_ON")

	#def mouser_over_popover	

	def mouse_exit_popover(self,widget,event=None):

		widget.set_name("POPOVER_OFF")		
	
	#def mouse_exit_popover

#class BackupBox

from . import Core