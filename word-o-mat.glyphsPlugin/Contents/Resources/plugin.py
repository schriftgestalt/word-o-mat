# encoding: utf-8

from __future__ import print_function, unicode_literals

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################

import traceback
import sys
import objc
from Foundation import NSString, NSLog
from AppKit import NSMenuItem
from GlyphsApp import Glyphs, EDIT_MENU
from GlyphsApp.plugins import GeneralPlugin

hasAllModules = True
try:
	NSLog("__import 1")
	from vanilla import * 
	NSLog("__import 2")
	import WordOMat
	NSLog("__import 3")
	from WordOMat import WordomatWindow
	NSLog("__import 4")
except:
	import traceback
	NSLog(traceback.format_exc())
	hasAllModules = False
	NSLog("Exception in word-o-mat import:")
	print('-'*60)
	#traceback.print_exc(file=sys.stdout)
	print('-'*60)

class WordOMat(GeneralPlugin):
	@objc.python_method
	def settings(self):
		self.name = u"word-o-mat"
		self.wordomat = None
	
	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
	
	def showWindow_(self, sender):
		""" Do something like show a window"""
		if not hasAllModules:
			Message("Problem with some modules", "This plugin needs the vanilla module to be installed for python 2.7.")
			return
		if not self.wordomat or not self.wordomat.w._window:
			self.wordomat = WordomatWindow()
		else:
			self.wordomat.w.show()
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
