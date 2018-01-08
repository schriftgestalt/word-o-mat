# encoding: utf-8

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
import traceback

hasAllModules = True
hasCurrentWrapper = False
try:
	from vanilla import * 
	from robofab.world import CurrentFont
	import WordOMat
	from WordOMat import WordomatWindow
except:
	hasAllModules = False
	print "Exception in word-o-mat import:"
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60

# check for latest version of objectsGS.py
try:
	from objectsGS import RFont
	getGlyph_op = getattr(RFont, "getGlyph", None)
	if callable(getGlyph_op):
		hasCurrentWrapper = True
except:
	print "Exception in word-o-mat import:"
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60

class WordOMat(GeneralPlugin):
	def settings(self):
		self.name = "word-o-mat"
		self.wordomat = None
	
	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
	
	def showWindow(self, sender):
		""" Do something like show a window"""
		if not hasAllModules:
			NSRunAlertPanel("Problem with some modules", "This plugin needs the vanilla, robofab and fontTools module to be installed for python 2.6.", "", "", "")
			return
		if not hasCurrentWrapper:
			NSRunAlertPanel("Problem with some RoboFab wrapper", "Please install the latest version of the file \"objectsGS.py\" from https://github.com/schriftgestalt/Glyphs-Scripts", "", "", "")
			return
		if not self.wordomat or not self.wordomat.w._window:
			self.wordomat = WordomatWindow()
		else:
			self.wordomat.w.show()
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
