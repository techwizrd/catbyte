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

class CatByte:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_default_size(800,600)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_title("untitled - CatByte")
		
