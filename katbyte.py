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

import pygtk, pango

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
		self.window.set_default_size(800,600)
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
			<menu action="New (with Template)">
			    <menuitem action="C Source File"/>
			    <menuitem action="C++ Source File"/>
			    <menuitem action="D Source File"/>
			    <menuitem action="Java Source File"/>
			    <menuitem action="Pascal Source File"/>
			    <menuitem action="PHP Source File"/>
			    <menuitem action="Python Source File"/>
			    <menuitem action="Ruby Source File"/>
			    <menuitem action="HTML Source File"/>
			    <menuitem action="LaTeX Source File"/>
			</menu>
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
										('File', None, '_File'),
										('C Source File', None, 'C Source File', None, 'Create a new C file', self.newCTemplate),
										('C++ Source File', None, 'C++ Source File', None, 'Create a new C++ file', self.newCTemplate),
										('D Source File', None, 'D Source File', None, 'Create a new D file', self.newDTemplate),
										('Java Source File', None, 'Java Source File', None, 'Create a new Java file', self.newJavaTemplate),
										('Pascal Source File', None, 'Pascal Source File', None, 'Create a new Pascal file', self.newPascalTemplate),
										('PHP Source File', None, 'PHP Source File', None, 'Create a new PHP file', self.newPhpTemplate),
										('Python Source File', None, 'Python Source File', None, 'Create a new Python file', self.newPythonTemplate),
										('Ruby Source File', None, 'Ruby Source File', None, 'Create a new Ruby file', self.newRubyTemplate),
										('HTML Source File', None, 'HTML Source File', None, 'Create a new HTML file', self.newHtmlTemplate),
										('LaTeX Source File', None, 'LaTeX Source File', None, 'Create a new LaTeX file', self.newLatexTemplate),
										('New (with Template)', None, 'New (with Template)')
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
		a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled"))
		self.notebook.set_current_page(a)
		self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")

		#Wasteful way of setting properties of all tabs
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)
			x.kb_sourceview.modify_font(pango.FontDescription('monotype 8'))
			x.kb_sourceview.set_wrap_mode(gtk.WRAP_WORD)

	def normOpen(self, widget, data = None):
		try:
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].openFile()
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(os.path.basename(self.kb_documents[len(self.kb_documents)-1].kb_filename)))
			self.notebook.set_current_page(a)
			self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
		except Exception, e:
			print str(e)

		#Wasteful way of setting properties of all tabs
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)
			x.kb_sourceview.modify_font(pango.FontDescription('monotype 8'))
			x.kb_sourceview.set_wrap_mode(gtk.WRAP_WORD)
	
	def argOpen(self, filename = None):
		"""Used for opening files given from the command line."""
		try:
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].kb_filename = filename
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(os.path.basename(self.kb_documents[len(self.kb_documents)-1].kb_filename)))
			self.notebook.set_current_page(a)
			self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
		except Exception, e:
			print str(e)

	def quickOpen(self, widget, data = None):
		pass

	def saveFile(self, widget, data = None):
		self.kb_documents[self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page()))].saveFile()

	def saveAs(self, widget, data = None):
		self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page())).saveAs()

	def closeDocument(self, widget, data = None):
		if self.notebook.get_n_pages() != 0:
			a = self.notebook.get_nth_page(self.notebook.get_current_page()).kb_filename
			if a == None:
				print "closing untitled"
			else:
				print "closing " + a
			self.kb_documents.pop(self.notebook.get_current_page())
			self.notebook.remove_page(self.notebook.get_current_page())
		else:
			print "No documents to close"
			
	###########################
	# Functions for Templates
	###########################
	
	def newCTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.c")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.c"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.c KatByte")
		except Exception, e:
			print str(e)

	def newCppTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.cpp")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.cpp"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.cpp - KatByte")
		except Exception, e:
			print str(e)

	def newDTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.d")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.d"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.d - KatByte")
		except Exception, e:
			print str(e)

	def newJavaTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.java")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.java"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.java - KatByte")
		except Exception, e:
			print str(e)

	def newPascalTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.pas")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.pas"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.pas - KatByte")
		except Exception, e:
			print str(e)

	def newPhpTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.php")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.php"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.php - KatByte")
		except Exception, e:
			print str(e)

	def newPythonTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.py")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.py"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.py - KatByte")
		except Exception, e:
			print str(e)

	def newRubyTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.rb")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.rb"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.rb - KatByte")
		except Exception, e:
			print str(e)

	def newHtmlTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.html")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.html"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.html - KatByte")
		except Exception, e:
			print str(e)

	def newLatexTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.d")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.tex"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.tex - KatByte")
		except Exception, e:
			print str(e)

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
	a = os.path.dirname(__file__)
	print a
	for x in sys.argv[1:]:
		katbyte.argOpen(x)
	gtk.main()


