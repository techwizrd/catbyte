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

import sys, os

APP_NAME	= 'katbyte'
APP_VERSION	= '0.1'
__author__	= 'techwizrd'
__email__	= 'theninja@Bluedevs.net'
__version__	= '0.1.5'

if sys.platform == 'linux2':
	# Set process name.  Only works on Linux >= 2.1.57.
	try:
		import dl
		libc = dl.open('/lib/libc.so.6')
		libc.call('prctl', 15, 'katbyte\0', 0, 0, 0) # 15 is PR_SET_NAME
	except:
		pass

try:
	import gtk
	import gobject
	from gtk import gdk
except:
	raise SystemExit

import pygtk

try:
	import gobject
	gobject.threads_init()
except Exception, e:
	print str(e)
	raise SystemExit

if gtk.pygtk_version < (2, 4):
	print "PyGtk 2.4 or later required for this widget"
	raise SystemExit

from EditorComponent import KbEditorComponent

class KatByte:
	def __init__(self):
		self.kb_documents = []

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_size_request(800,600)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_title("untitled - KatByte")

		self.vbox = gtk.VBox()
		self.initializeMenus()
		self.vbox.pack_start(self.menubar, False, False, 0)
		self.initializeNotebook()
		self.vbox.add(self.notebox)
		self.window.add(self.vbox)

		self.main()

	def initializeMenus(self):
		"""Initialize the menus using UIManager."""

		self.uimanager = gtk.UIManager()
		self.menuString = """<ui>
	<menubar name="MenuBar">
		<menu action="File">
			<menuitem action="New"/>
			<separator name="sep1"/>
			<menuitem action="Open"/>
			<menuitem action="Quick Open"/>
			<separator name="sep2"/>
			<menuitem action="Save"/>
			<menuitem action="Save as..."/>
			<separator name="sep3"/>
			<menuitem action="Close Document"/>
			<menuitem action="Quit"/>
		</menu>
	</menubar>
</ui>"""
		try:
			self.uimanager.add_ui_from_string(self.menuString)
			self.actiongroup = gtk.ActionGroup('CatByte')

			self.closeDocumentMenuItem = gtk.Action('Close Document', 'Close Document', 'Close Document', gtk.STOCK_QUIT)
			self.closeDocumentMenuItem.connect("activate", self.closeDocument)
			self.actiongroup.add_action_with_accel(self.closeDocumentMenuItem, "<Control>W")
			
			self.quickOpenMenuItem = gtk.Action('Quick Open', 'Quick Open', 'Quick Open', gtk.STOCK_OPEN)
			self.quickOpenMenuItem.connect("activate", self.quickOpen)
			self.actiongroup.add_action_with_accel(self.quickOpenMenuItem, "<Control><Shift>o")

			self.saveAsMenuItem = gtk.Action('Save as...', 'Save as...', 'Save as...', gtk.STOCK_SAVE)
			self.saveAsMenuItem.connect("activate", self.saveAs)
			self.actiongroup.add_action_with_accel(self.saveAsMenuItem, "<Control><Shift>S")

			self.actiongroup.add_actions([
										('New', gtk.STOCK_NEW, 'New', None, "New File", self.newFile),
										('Open', gtk.STOCK_OPEN, 'Open', None, "Open a File", self.normOpen),
										('Save', gtk.STOCK_SAVE, 'Save', None, "Save File", self.saveFile),
										('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit CatByte', self.destroy),
										('File', None, '_File')
										])
			self.uimanager.insert_action_group(self.actiongroup, 0)

			self.accelgroup = self.uimanager.get_accel_group()
			self.window.add_accel_group(self.accelgroup)
		except Exception, e:
			print str(e)
			print "Menubar could not be initialized"
			raise SystemExit
		self.menubar = self.uimanager.get_widget("/MenuBar")

	def initializeNotebook(self):
		self.notebox = gtk.HPaned()
		self.notebook = gtk.Notebook()
		self.notebook.popup_enable()
		self.notebook.set_scrollable(True)
		self.notebox.add(self.notebook)
		self.newFile(None)
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)

	########################
	# Menu/Toolbar Functions
	########################
	def newFile(self, widget, data = None):
		self.kb_documents.append(KbEditorComponent())
		a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(self.kb_documents[len(self.kb_documents)-1].getTitle()))
		self.notebook.set_current_page(a)

	def normOpen(self, widget, data = None):
		self.kb_documents.append(KbEditorComponent())
		self.kb_documents[len(self.kb_documents)-1].openFile()
		self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(self.kb_documents[len(self.kb_documents)-1].getTitle()))

	def quickOpen(self, widget, data = None):
		pass

	def saveFile(self, widget, data = None):
		self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page())).saveFile()

	def saveAs(self, widget, data = None):
		self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page())).saveAs()

	def closeDocument(self, widget, data = None):
		self.kb_documents.pop(self.notebook.get_current_page())
		self.notebook.remove_page(self.notebook.get_current_page())

	###########################
	# Signal/Callback Functions
	###########################

	def delete_event(self, widget, event, data=None):
		print "delete event occurred"
		return False

	def destroy(self, widget, data=None):
		print "Exiting CatByte"
		gtk.main_quit()

	def main(self):
		"""Connect all the signals and callbacks."""

		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)

		self.window.show_all()

if __name__ == "__main__":
	print "KatByte v%s" % __version__
	katbyte = KatByte()
	gtk.main()