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
	del e
	raise SystemExit

try:
	import gtk
	import gtksourceview
	import mimetypes
	import os
except ImportError, e:
	print "%s not found!" % e
	raise SystemExit
except Exception, e:
	print str(e)
	raise SystemExit

if gtk.pygtk_version < (2, 4):
	print "PyGtk 2.4 or later required for this program"
	raise SystemExit

#from EditorComponent import KbEditorComponent

class KbEditorComponent(gtk.VBox):
	"""A custom editor component for KatByte. This really isn't a
	widget so much as a wrapper that makes handling the widgets
	nice and easy.

	This component is a test and a hack, so beware. I warned you."""

	def __init__(self, filename = None):
		"""Initializes the custom editor component. If filename
		is None, then an empty editor component will be loaded.
		In the case a filename is specified, an attempt to load
		the file will be made. If unsuccesful, a warning will be
		raised and the empty editor component will be loaded."""

		gtk.VBox.__init__(self)

		# Adding the scrollbars to the VBox
		self.kb_scrollwin = gtk.ScrolledWindow()
		self.add(self.kb_scrollwin)
		self.kb_scrollwin.set_policy(gtk.POLICY_AUTOMATIC,
									gtk.POLICY_AUTOMATIC)

		# Adding the actual SourceView and SourceBuffer widgets
		self.kb_sourcebuffer = gtksourceview.SourceBuffer()
		self.kb_sourceview = gtksourceview.SourceView(self.kb_sourcebuffer)
		self.kb_sourcebuffer.set_highlight(True)
		self.kb_sourceview.set_show_line_numbers(True)
		self.kb_sourceview.set_smart_home_end(True)
		self.kb_scrollwin.add(self.kb_sourceview)

		self.kb_filename = filename
		if self.kb_filename != None:
			if os.path.exists(self.kb_filename):
				self.loadFile(self.kb_filename)
			else:
				print self.kb_filename + " does not exist\n Using None"
		else:
			self.kb_title = "untitled"
		
		self.kb_stylescheme = gtksourceview.source_style_scheme_get_default()
		print "Style: " + str(self.kb_stylescheme.get_tag_style("Oblivion"))
		
		self.main()
		self.show_all()

	def loadFile(self, filename):
		"""Load a file into the SourceBuffer."""
		try:
			codefile = open(filename, 'rb')
			print "opening " + filename
			filetype = mimetypes.guess_type(filename)[0]

			# Prevent errors resulting from files without a filetype
			if filetype == None:
				filetype = "text/plain"

			a = gtksourceview.SourceLanguagesManager().get_language_from_mime_type(filetype)
			self.kb_sourcebuffer.set_language(a)

			self.kb_sourcebuffer.begin_not_undoable_action()
			the_source_code = ""
			# Begins reading the file in line by line; this is preferred
			# to reading in the entire file at once (some files may be
			# larger than the availible RAM)
			for line in codefile:
				the_source_code += line
			self.kb_sourcebuffer.set_text(the_source_code)
			self.kb_sourcebuffer.end_not_undoable_action()
			codefile.close() # close the file or memory leaks will occur
		except Exception, e:
			print str(e)
			del e

	def saveFile(self):
		"""Save the text currently in the buffer to a file. If the
		filename is None, open a dialog to select the file. If not, just
		open the file in write mode and dump the text into the file."""
		if self.kb_filename == None:
			self.kb_saveAs()
		else:
			try:
				# Write the file in binary mode to prevent corrupting
				# binary files on Windows (e.g.: JPEGs, etc.)
				codefile = open(self.kb_filename, 'wb')
				print "saving %s" % self.kb_filename

				# Using get_text() seems to be wasteful overhead
				# Hoperfully, there's an easier way of doing this
				the_source_code = self.kb_sourcebuffer.get_text(
					self.kb_sourcebuffer.get_start_iter(),
					self.kb_sourcebuffer.get_end_iter(),
					False)
				
				codefile.write(the_source_code)
				codefile.close() # close file to prevent memory leaks

				# Reset the modified property so the file looks as if it
				# has not been modified since last save (which happens
				# to have happened a few lines above)
				self.kb_sourcebuffer.set_modified(False)
			except Exception, e:
				print str(e)
				del e

			codefile.close() # just in case ;)

	def saveAs(self):
		"""Opens a FileChooserDialog allowing the user to select a file
		to save to. If a file is selected, the saveFile function is
		called with the selected filename."""
		fc = gtk.FileChooserDialog(title='Save As...',
									parent=None,
									action=gtk.FILE_CHOOSER_ACTION_SAVE,
									buttons=(gtk.STOCK_CANCEL,
										gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN,
										gtk.RESPONSE_OK))
		fc.set_default_response(gtk.RESPONSE_OK)
		response = fc.run()
		if response == gtk.RESPONSE_OK:
			self.kb_filename = fc.get_filename()
			self.kb_title = os.path.basename(self.kb_filename)
			self.saveFile()
			fc.destroy()

	def openFile(self):
		"""Opens a FileChooserDialog allowing the user to select a file
		to open. If a file is selected, the loadFile function is called
		with the selected filename."""
		fc = gtk.FileChooserDialog(title='Open File...',
									parent=None,
									action=gtk.FILE_CHOOSER_ACTION_OPEN,
									buttons=(gtk.STOCK_CANCEL,
										gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN,
										gtk.RESPONSE_OK))
		fc.set_default_response(gtk.RESPONSE_OK)
		response = fc.run()
		if response == gtk.RESPONSE_OK:
			self.kb_filename = fc.get_filename()
			self.kb_title = os.path.basename(self.kb_filename)
			self.loadFile(self.kb_filename)
		fc.destroy()

	def getTitle(self):
		"""Gets the title."""
		if self.kb_filename == None:
			self.kb_title = "untitled"
		else:
			self.kb_title = os.path.basename(self.kb_filename) + " - " + os.path.dirname(self.kb_filename)
		return self.kb_title

	###########################
	# Signal/Callback Functions
	###########################

	def modified_changed(self, data=None):
		"""Prepends an asterisk when the buffer is changed."""
		print "Modification state:" + str(self.kb_sourcebuffer.get_modified())
		if self.kb_sourcebuffer.get_modified():
			try:
				katbyte.notebook.set_tab_label_text(self, "*" + os.path.basename(self.kb_filename))
				#katbyte.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
				katbyte.window.set_title("*" + self.getTitle() + " - KatByte")
			except Exception, e:
				print str(e)
				del e
		else:
			try:
				katbyte.notebook.set_tab_label_text(self, os.path.basename(self.kb_filename))
				#katbyte.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
				katbyte.window.set_title(self.getTitle() + " - KatByte")
			except Exception, e:
				print str(e)
				del e

	def main(self):
		"""Connects all the widgets with their signals."""
		self.kb_sourcebuffer.connect("modified-changed", self.modified_changed)

class KatByte:
	def __init__(self):
		self.kb_documents = []

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_default_size(700, 700)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_title("untitled - KatByte")
		
		try:
			self.window.set_icon_from_file(os.path.dirname(__file__) + "/katbyte.svg")
		except Exception, e:
			print str(e)
			del e

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
		<menu action="Help">
			<menuitem action="About"/>
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
										('C++ Source File', None, 'C++ Source File', None, 'Create a new C++ file', self.newCppTemplate),
										('D Source File', None, 'D Source File', None, 'Create a new D file', self.newDTemplate),
										('Java Source File', None, 'Java Source File', None, 'Create a new Java file', self.newJavaTemplate),
										('Pascal Source File', None, 'Pascal Source File', None, 'Create a new Pascal file', self.newPascalTemplate),
										('PHP Source File', None, 'PHP Source File', None, 'Create a new PHP file', self.newPhpTemplate),
										('Python Source File', None, 'Python Source File', None, 'Create a new Python file', self.newPythonTemplate),
										('Ruby Source File', None, 'Ruby Source File', None, 'Create a new Ruby file', self.newRubyTemplate),
										('HTML Source File', None, 'HTML Source File', None, 'Create a new HTML file', self.newHtmlTemplate),
										('LaTeX Source File', None, 'LaTeX Source File', None, 'Create a new LaTeX file', self.newLatexTemplate),
										('New (with Template)', None, 'New (with Template)'),
										('About', gtk.STOCK_ABOUT ,'_About', None, 'About KatByte', self.showAboutDialog),
										('Help', None, '_Help'),
										])
			self.uimanager.insert_action_group(self.actiongroup, 0)

			self.accelgroup = self.uimanager.get_accel_group()
			self.window.add_accel_group(self.accelgroup)
		except Exception, e:
			print str(e)
			print "Menubar could not be initialized"
			del e
			raise SystemExit
		self.menubar = self.uimanager.get_widget("/MenuBar")

	def initializeNotebook(self):
		"""Initializes the notebook and sets it's settings."""
		self.notebox = gtk.HPaned()
		self.notebook = gtk.Notebook()
		self.notebook.popup_enable()
		self.notebook.set_scrollable(True)
		self.notebox.add(self.notebook)
		self.newFile(None)
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)

	def getCurrentEditor(self):
		"""Gets the current editor widget from the gtk.Notebook"""
		return self.notebook.get_nth_page(self.notebook.get_current_page())
	
	def getNewestDocument(self):
		"""Gets the most recently added Editor Component from the kb_documents"""
		return self.kb_documents[len(self.kb_documents)-1]

	########################
	# Menu/Toolbar Functions
	########################
	def newFile(self, widget, data = None):
		"""Creates a new file and appends it to the gtk.Notebook and kb_documents"""
		self.kb_documents.append(KbEditorComponent())
		#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled"))
		a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled"))
		self.notebook.set_current_page(a)
		self.getNewestDocument().kb_filename = "untitled"
		#self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
		self.window.set_title("untitled - KatByte")

		#Wasteful way of setting properties of all tabs
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)
			x.kb_sourceview.modify_font(pango.FontDescription('monospace 8'))
			x.kb_sourceview.set_wrap_mode(gtk.WRAP_WORD)

	def normOpen(self, widget, data = None):
		"""Open a file."""
		try:
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].openFile()
			self.getNewestDocument().openFile()
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(os.path.basename(self.kb_documents[len(self.kb_documents)-1].kb_filename)))
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label(os.path.basename(self.getNewestDocument().kb_filename)))
			self.notebook.set_current_page(a)
			#self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
			self.window.set_title(self.getNewestDocument().getTitle() + " - KatByte")
		except Exception, e:
			print str(e)
			del e

		#Wasteful way of setting properties of all tabs
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)
			x.kb_sourceview.modify_font(pango.FontDescription('monospace 8'))
			x.kb_sourceview.set_wrap_mode(gtk.WRAP_WORD)
	
	def argOpen(self, filename = None):
		"""Used for opening files given from the command line."""
		try:
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].kb_filename = filename
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label(os.path.basename(self.kb_documents[len(self.kb_documents)-1].kb_filename)))
			self.getNewestDocument().kb_filename = filename
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label(os.path.basename(self.getNewestDocument().kb_filename)))
			self.notebook.set_current_page(a)
			self.window.set_title(self.kb_documents[len(self.kb_documents)-1].getTitle() + " - KatByte")
		except Exception, e:
			print str(e)
			del e
		
		#Wasteful way of setting properties of all tabs
		for x in self.kb_documents:
			self.notebook.set_tab_reorderable(x, True)
			x.kb_sourceview.modify_font(pango.FontDescription('monospace 8'))
			x.kb_sourceview.set_wrap_mode(gtk.WRAP_WORD)

	def quickOpen(self, widget, data = None):
		pass

	def saveFile(self, widget, data = None):
		"""Saves the current file"""
		#self.kb_documents[self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page()))].saveFile()
		self.getCurrentEditor().saveFile()

	def saveAs(self, widget, data = None):
		"""Prompts the user for the filename with a dialog, and then proceeds to
		save that file"""
		#self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page())).saveAs()
		#self.kb_documents[self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page()))].saveAs()
		self.getCurrentEditor().saveAs()

	def closeDocument(self, widget, data = None):
		"""Removes the current document from the gtk.Notebook and kb_documents"""
		if self.notebook.get_n_pages() != 0:
			a = self.getCurrentEditor().kb_filename
			if a == None:
				print "closing untitled"
			else:
				print "closing " + a
			self.kb_documents.pop(self.notebook.get_current_page())
			self.notebook.remove_page(self.notebook.get_current_page())
		else:
			print "No documents to close"
	
	def showAboutDialog(self, widget, data=None):
		aboutkb = gtk.AboutDialog()
		aboutkb.set_name("KatByte")
		aboutkb.set_program_name("KatByte")
		aboutkb.set_version(__version__)
		aboutkb.set_comments("KatByte is a an open-source code editor built with a miminalist interface. KatByte is intended for both quickly editing files on the fly, as well as use as an actual IDE. Thank you for choosing KatByte.")
		aboutkb.set_copyright(u"Copyright (c) 2009 techwizrd")
		#TODO: get the copyright to say &#169 , the real copyriht symbol
		# I want to do it without changing the file encoding
		a = open(os.path.dirname(__file__)+"/LICENSE")
		b = ""
		for x in a:
			b += x
		a.close()
		aboutkb.set_license(b)
		aboutkb.set_wrap_license(False)
		aboutkb.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.dirname(__file__)+"/katbyte.png"))
		a = open(os.path.dirname(__file__)+"/AUTHORS")
		b = ""
		for x in a:
			b += x
		a.close()
		del a
		del b
		aboutkb.set_authors(x.split("\n"))
		aboutkb.show_all()
			
	###########################
	# Functions for Templates
	###########################
	
	def newCTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.c")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.c"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.c"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.c - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newCppTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.cpp")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			self.getNewestDocument().loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.cpp"))
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.cpp"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.cpp - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newDTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.d")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.d"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.d"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.d - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newJavaTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.java")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.java"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.java"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.java - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newPascalTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.pas")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.pas"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.pas"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.pas - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newPhpTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.php")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.php"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.php"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.php - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newPythonTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.py")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.py"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.py"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.py - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newRubyTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.rb")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.rb"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.rb"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.rb - KatByte")
		except Exception, e:
			print str(e)
			del e

	def newHtmlTemplate(self, widget, data=None):
		try:
			filename = os.path.abspath(os.path.dirname(__file__) + "/template/template.html")
			#print "trying to open: " + filename
			#print "exists: " + str(os.path.exists(filename))
			self.kb_documents.append(KbEditorComponent())
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.html"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.html"))
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
			#self.kb_documents[len(self.kb_documents)-1].loadFile(filename)
			#a = self.notebook.append_page(self.kb_documents[len(self.kb_documents)-1], gtk.Label("untitled.tex"))
			self.getNewestDocument().loadFile(filename)
			a = self.notebook.append_page(self.getNewestDocument(), gtk.Label("untitled.tex"))
			self.notebook.set_current_page(a)
			self.window.set_title("untitled.tex - KatByte")
		except Exception, e:
			print str(e)
			del e

	###########################
	# Signal/Callback Functions
	###########################

	def delete_event(self, widget, event, data=None):
		print "delete event occurred"
		return False

	def destroy(self, widget, data=None):
		print "Exiting CatByte"
		gtk.main_quit()

	def updateTitle(self, widget, event, data = None):
		"""Updates the title when the tab is changed."""
		#print "updateTitle data: " + str(data)
		#self.window.set_title(self.kb_documents[self.kb_documents.index(self.notebook.get_nth_page(self.notebook.get_current_page()))].getTitle() + " - KatByte")
		self.window.set_title(self.notebook.get_nth_page(data).getTitle() + " - KatByte")

	def main(self):
		"""Connect all the signals and callbacks."""

		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.notebook.connect("switch-page", self.updateTitle)

		self.window.show_all()

if __name__ == "__main__":
	print "KatByte v" + __version__
	katbyte = KatByte()
	a = os.path.dirname(__file__)
	print a
	for x in sys.argv[1:]:
		katbyte.argOpen(x)
	gtk.main()


