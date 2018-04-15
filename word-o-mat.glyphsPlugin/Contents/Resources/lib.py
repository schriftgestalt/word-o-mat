# coding=utf-8

"""
Some missing API
"""

import objc, traceback
from Foundation import NSBundle, NSObject, NSUserDefaults
from AppKit import NSApplication, NSMenuItem
from vanilla import * 

from GlyphsApp import Glyphs, Message


__all__ = ["CurrentFont", "Message", "registerExtensionDefaults", "getExtensionDefault", "setExtensionDefault", "ExtensionBundle", "addObserver", "removeObserver", "AccordionView", "OpenSpaceCenter"]


def CurrentFont():
	return Glyphs.font

def registerExtensionDefaults(keyValues):
	NSUserDefaults.standardUserDefaults().registerDefaults_(keyValues)
def getExtensionDefault(key, default = None):
	value = NSUserDefaults.standardUserDefaults().objectForKey_(key)
	if value is None:
		return default
	return value
def setExtensionDefault(key, value):
	NSUserDefaults.standardUserDefaults().setObject_forKey_(value, key)

def ExtensionBundle(title):
	path = __file__
	bundlePath = path[:path.find("/Contents/Resources/")]
	bundle = NSBundle.bundleWithPath_(bundlePath)
	return bundle

def getResourceFilePath(self, filename):
	return self.pathForResource_ofType_(filename, "txt")
NSBundle.getResourceFilePath = getResourceFilePath

def addObserver(a, b, c):
	pass
def removeObserver(a, b):
	pass

class AccordionView(Group):
	
	def __init__(self, posSize, accItems):
		self._setupView(self.nsViewClass, posSize)
		padd = 12
		y = 2
		idx = 0
		for accItem in accItems:
			
			if idx > 0:
				line = HorizontalLine((padd, y - 1, -padd, 1))
				setattr(self, "line%d"%idx, line)
				y += 2
			label = TextBox((padd, y, -padd, 22), accItem["label"], sizeStyle="small")
			setattr(self, "title%d"%idx, label)
			y += 16
			height = accItem["size"]
			panel = Group((0, y, 250, height))
			setattr(self, "panel%d"%idx, panel)
			panel.view = accItem["view"]
			y += height
			idx+=1

def OpenSpaceCenter(font):
	currentTab = font.currentTab
	if not currentTab:
		font.newTab()
		currentTab = font.currentTab
	return currentTab
	
def __setRaw__(self, text):
	self.graphicView().setDisplayString_(text)
GSEditViewController = objc.lookUpClass("GSEditViewController")
GSEditViewController.setRaw = __setRaw__

