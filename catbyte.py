#!/usr/bin/env python
#
# Copyright (C) 2009 techwizrd <theninja@Bluedevs.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import sys

APP_NAME	= 'catbyte'
APP_VERSION	= '0.1'
__author__	= 'techwizrd'
__email__	= 'theninja@Bluedevs.net'
__version__	= '0.1'

if sys.platform == 'linux2':
	# Set process name.  Only works on Linux >= 2.1.57.
	try:
		import dl
		libc = dl.open('/lib/libc.so.6')
		libc.call('prctl', 15, 'catbyte\0', 0, 0, 0) # 15 is PR_SET_NAME
	except:
		pass

try:
	import pygtk
	pygtk.require('2.0')
except ImportError:
	print "PyGTK 2.0 not found!"
	raise SystemExit
try:
	import gobject
	gobject.threads_init()
except Exception, e:
	print str(e)
	raise SystemExit
try:
	import gtk
	import gtksourceview
	import mimetypes
	import os
	#import gettext
except ImportError, e:
	print "%s found!" % e
	raise SystemExit
except Exception, e:
	print str(e)
	raise SystemExit

class CatByte:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_size_request(800,600)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_title("CatByte")
		
		self.initializeMenus()
		self.initializeNotebook()
		self.vbox = gtk.VBox()
		self.vbox.pack_start(self.menubar, False, False, 0)
		self.vbox.add(self.notebox)
		self.window.add(self.vbox)
		self.window.show_all()
		self.main()

	def initializeMenus(self):
		self.uimanager = gtk.UIManager()
		try:
			self.uimanager.add_ui_from_file("./menus.xml")
			self.actiongroup = gtk.ActionGroup('CatByte')
			self.actiongroup.add_actions([
										('New', gtk.STOCK_NEW, 'New', None, "New File", self.newFile),
										('Open', gtk.STOCK_OPEN, 'Open', None, "Open a File", self.normOpen),
										('Quick Open', None, 'Quick _Open', None, "Quickly Open a File", self.quickOpen),
										('Save', gtk.STOCK_SAVE, 'Save', None, "Save File", self.saveFile),
										('Save as...', None, 'Save as...', None, "Save as...", self.saveAs),
										('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit CatByte', gtk.main_quit),
										('File', None, '_File')
										])
			self.uimanager.insert_action_group(self.actiongroup, 0)
			self.accelgroup = self.uimanager.get_accel_group()
			self.window.add_accel_group(self.accelgroup)
		except Exception, e:
			print str(e)
			sys.exit(1)
		self.menubar = self.uimanager.get_widget("/MenuBar")

	def initializeToolbar(self):
		pass

	def initializeNotebook(self):
		self.notebox = gtk.HPaned()
		self.notebook = gtk.Notebook()
		self.notebook.popup_enable()
		self.notebook.set_scrollable(True)
		self.notebox.add(self.notebook)
		self.documents = []
		a = EditorPart()
		self.documents.append(a)
		self.notebook.append_page(a.vbox, gtk.Label(a.title))
		self.notebook.get_current_page()

	def initializeSidebar(self):
		pass
	
	########################
	# Menu/Toolbar Functions
	########################
	def newFile(self, widget, data = None):
		pass
	
	def normOpen(self, widget, data = None):
		pass
	
	def quickOpen(self, widget, data = None):
		pass
	
	def saveFile(self, widget, data = None):
		pass
	
	def saveAs(self, widget, data = None):
		pass

#	def delete_event(self, widget, event, data=None):
#		#print "delete event occurred"
#		return False

#	def destroy(self, widget, data=None):
#		print "Exiting CatByte"
#		gtk.main_quit()

	def main(self):
		self.window.connect("delete_event", gtk.main_quit)
		self.window.connect("destroy", gtk.main_quit)

class EditorPart:
	def __init__(self, filename = None):
		self.vbox = gtk.VBox()
		self.scrollwin = gtk.ScrolledWindow()
		self.vbox.add(self.scrollwin)
		self.scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sourcebuffer = gtksourceview.SourceBuffer()
		self.sourceview = gtksourceview.SourceView(self.sourcebuffer)
		self.sourcebuffer.set_highlight(True)
		self.sourceview.set_show_line_numbers(True)
		self.sourceview.set_smart_home_end(True)
		self.scrollwin.add(self.sourceview)
		self.vbox.show_all()
		self.filename = filename
		if self.filename != None:
			self.title = self.filename
			try:
				codefile = open(filename, 'r')
				a = gtksourceview.SourceLanguagesManager().get_language_from_mime_type(mimetypes.guess_type(filename)[0])
				self.sourcebuffer.set_language(a)
				self.sourcebuffer.begin_not_undoable_action()
				self.sourcebuffer.set_text(codefile.read())
				self.sourcebuffer.end_not_undoable_action()
				codefile.close()
			except Exception, e:
				print str(e)
		else:
			self.title = "untitled"

if __name__ == "__main__":
	print "CatByte v%s" % __version__
	catbyte = CatByte()
	gtk.main()
