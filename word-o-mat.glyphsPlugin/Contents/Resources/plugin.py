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
import objc
from Foundation import NSLog
from AppKit import NSMenuItem
from GlyphsApp import Glyphs, EDIT_MENU, Message
from GlyphsApp.plugins import GeneralPlugin

hasAllModules = True
try:
	# NSLog("__import 1")
	import vanilla  # noqa: F401
	# NSLog("__import 2")
	import WordOMat  # noqa: F401
	# NSLog("__import 3")
	from WordOMat import WordomatWindow
	# NSLog("__import 4")
except:
	NSLog(traceback.format_exc())
	hasAllModules = False
	NSLog("Exception in word-o-mat import:")
	print('-' * 60)
	#traceback.print_exc(file=sys.stdout)
	print('-' * 60)


class WordOMatPlugin(GeneralPlugin):
	@objc.python_method
	def settings(self):
		self.name = "word-o-mat"
		self.wordomat = None

	@objc.python_method
	def start(self):
		if Glyphs.buildNumber >= 3320:
			from GlyphsApp.UI import MenuItem
			newMenuItem = MenuItem(self.name, action=self.showWindow_, target=self)
		elif Glyphs.buildNumber >= 3311:
			newMenuItem = NSMenuItem(self.name, callback=self.showWindow_, target=self)
		else:
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
