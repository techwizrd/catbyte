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

import os, sys

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

try:
	import gtk
	import gtksourceview
	import mimetypes
	import os
except ImportError, e:
	print "%s found!" % e
	raise SystemExit
except Exception, e:
	print str(e)
	raise SystemExit

if gtk.pygtk_version < (2, 4):
	print "PyGtk 2.4 or later required for this widget"
	raise SystemExit

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

		self.show_all()

	def loadFile(self, filename):
		"""Load a file into the SourceBuffer."""
		try:
			codefile = open(filename, 'rb')
			print "opening %s" % self.kb_filename
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

				# Using get_text() seems to be wasteful overhead and
				# uneeded as we are grabbing the entire file, not a
				# slice (in which case we would have used get_slice)
				the_source_code = self.kb_sourcebuffer.text
				
				codefile.write(the_source_code)
				codefile.close() # close file to prevent memory leaks

				# Reset the modified property so the file looks as if it
				# has not been modified since last save (which happens
				# to have happened a few lines above)
				self.kb_sourcebuffer.set_modified(False)
			except Exception, e:
				print str(e)

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
		fc.destroy()
		if response == gtk.RESPONSE_OK:
			self.kb_filename = fc.get_filename()
			self.title = os.path.basename(self.kb_filename)
			self.saveFile()

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
		fc.destroy()
		if response == gtk.RESPONSE_OK:
			self.kb_filename = fc.get_filename()
			self.title = os.path.basename(self.kb_filename)
			#catbyte.notebook.set_tab_label_text(self.vbox, self.title)
			self.loadFile(self.kb_filename)

if __name__ == "__main__":
	print "This is a demo of the KbEditorComponent PyGTK Widget."
	print "This program is meant to be used in your program."

	window = gtk.Window()
	window.set_title("KbEditorComponent Demo Program")
	window.set_size_request(400,400)
	window.add(KbEditorComponent("EditorComponent.py"))
	window.connect("delete_event", gtk.main_quit)
	window.connect("destroy", gtk.main_quit)
	window.show_all()

	gtk.main()
