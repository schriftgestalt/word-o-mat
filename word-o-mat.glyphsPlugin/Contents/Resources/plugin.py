# encoding: utf-8

from __future__ import print_function

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

from GlyphsApp import *
from GlyphsApp.plugins import *
import traceback, sys
from Foundation import NSString
hasAllModules = True
try:
	from vanilla import * 
	import WordOMat
	from WordOMat import WordomatWindow
except:
	hasAllModules = False
	print("Exception in word-o-mat import:")
	print('-'*60)
	traceback.print_exc(file=sys.stdout)
	print('-'*60)

class WordOMat(GeneralPlugin):
	def settings(self):
		self.name = u"word-o-mat"
		self.wordomat = None
	
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
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
