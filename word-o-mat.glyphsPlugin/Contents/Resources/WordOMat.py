#!/usr/bin/env python
# encoding: utf-8

# Tool for Glyphs to generate test words for type testing, sketching etc.
# Default wordlist ukacd.txt is from http://www.crosswordman.com/wordlist.html
# v1.0 / Nina Stössinger 29.11.2013 / with thanks to Just van Rossum / KABK t]m 1314
# ported by Georg Seifert 11.12.2013
import objc, sys, os, re, traceback
from Foundation import *
from AppKit import *

# make sure all wrapper imports are found
MainBundle = NSBundle.mainBundle()
path = MainBundle.bundlePath()+"/Contents/Scripts"
if not path in sys.path:
	sys.path.append(path)
paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)
path = paths[0]
path = os.path.join(path, "Glyphs/Scripts")
if not path in sys.path:
	sys.path.append(path)
hasAllModules = True
hasCurrentWrapper = False
try:
	from vanilla import * 
	from robofab.world import CurrentFont
	from robofab.interface.all.dialogs import Message
	from random import choice
	from GlyphsApp import Glyphs

	def setup_binding_CheckBox(self, Object, KeyPath, options = objc.nil):
		self._nsObject.subviews()[0].bind_toObject_withKeyPath_options_("value", Object, "values."+KeyPath, options)
	CheckBox.binding = setup_binding_CheckBox

	def setup_binding_Control(self, Object, KeyPath, options = objc.nil):
		self._nsObject.bind_toObject_withKeyPath_options_("value", Object, "values."+KeyPath, options)
	EditText.binding = setup_binding_Control
	ComboBox.binding = setup_binding_Control
	def setup_binding_PopUpButton(self, Object, KeyPath, options = objc.nil):
		self._nsObject.bind_toObject_withKeyPath_options_("selectedIndex", Object, "values."+KeyPath, options)
	PopUpButton.binding = setup_binding_PopUpButton
	
except:
	hasAllModules = False
	print "Exception in import code:"
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60
warned = False

# check for latest version of objectsGS.py
try:
	from objectsGS import RFont
	getGlyph_op = getattr(RFont, "getGlyph", None)
	if callable(getGlyph_op):
		hasCurrentWrapper = True
except:
	print "Exception in import code:"
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60

class wordChecker(object):
	def __init__(self, limitToCharset, fontChars, requiredLetters, requiredGroups, bannedLetters, banRepetitions, minLength, maxLength):
		self.limitToCharset = limitToCharset
		self.fontChars = fontChars
		self.requiredLetters = requiredLetters
		self.requiredGroups = requiredGroups
		self.bannedLetters = bannedLetters
		self.banRepetitions = banRepetitions
		self.minLength = minLength
		self.maxLength = maxLength

	def excludedAll(self, word, charList):
		for c in charList:
			if c in word:
				return False
		return True

	def includedAll(self, word, charList):
		for c in charList:
			if not c in word:
				return False
		return True
	
	def includedAny(self, word, charList):
		if len(charList):
			for c in charList:
				if c in word:
					return True
			return False
		else:
			return True
	
	def includedGroups(self, word, charListList):
		for charList in charListList:
			if not self.includedAny(word, charList):
				return False
		return True
	
	def limitedTo(self, word, charList, condition):
		if condition:
			for c in word:
				if not c in charList:
					return False
			return True
		else:
			return True
	
	def uniqueChars(self, word, condition):
		if condition:
			wordChars = []
			for c in word:
				if c in wordChars:
					return False
				wordChars.append(c)
			return True
		else:
			return True
	
	def checkLength(self, word):
		return self.minLength <= len(word) <= self.maxLength
	
	def checkExisting(self, word, outputList):
		return not word in outputList
	
	def checkWord(self, word, outputWords):
		requirements = [
			(self.checkExisting, [outputWords]),
			(self.limitedTo, [self.fontChars, self.limitToCharset]),
			(self.checkLength, []),
			(self.includedAll, [self.requiredLetters]),
			(self.includedGroups, [self.requiredGroups]),
			(self.excludedAll, [self.bannedLetters]),
			(self.uniqueChars, [self.banRepetitions]),
		]
		for reqFunc, args in requirements:
			if not reqFunc(word, *args):
				return False
		return True


class WordomatWindow:
	def __init__(self):
		# set defaults
		self.requiredGroups = [[], [], []]
		self.outputWords = []
		thisBundle = NSBundle.bundleWithIdentifier_("com.NinaStoessinger.WordOMat")
		fileName = str(thisBundle.pathForResource_ofType_("ukacd", "txt"))
		
		contentLimit = '*****' # If word list file contains a header (e.g. copyright notice), start looking for content after this delimiter
		
		fo = open(fileName)
		lines = fo.read()
		fo.close()
		self.allWords = lines.splitlines()
		try:
			contentStart = self.allWords.index(contentLimit) + 1
			self.allWords = self.allWords[contentStart:]
		except ValueError:
			pass
		
		# preset character groups
		groupPresets = [
			["Ascenders", ["b", "f", "h", "k", "l"]], 
			["Descenders", ["g", "j", "p", "q", "y"]], 
			["Ball-and-Stick", ["b", "d", "p", "q"]], 
			["Arches", ["n", "m", "h", "u"]], 
			["Diagonals", ["v", "w", "x", "y"]]]
		Defaults = NSUserDefaults.standardUserDefaults()
		DefaultsController = NSUserDefaultsController.sharedUserDefaultsController()
		
		defaultpreferences = {
			'com.ninastoessinger.wordCount' : 20,
			'com.ninastoessinger.minLength' : 3,
			'com.ninastoessinger.maxLength' : 10,
			'com.ninastoessinger.mustLetters' : "a, o",
			'com.ninastoessinger.notLetters' : "-",
			'com.ninastoessinger.limitToCharset' : False,
			'com.ninastoessinger.banRepetitions' : False,
			'com.ninastoessinger.randomize' : True,
		}
		Defaults.registerDefaults_(defaultpreferences)
		
		# dialog window
		self.w = FloatingWindow((325, 518), 'word-o-mat')
		interval = 28
		padding = 10
		boxPadding = 3
		y = 10
		
		self.w.basicsBox = Box((padding, y, -padding, interval*3.85))
		self.w.basicsBox.wcText = TextBox((boxPadding, 5, 170, 22), 'Make this many words:')
		self.w.basicsBox.lenTextOne = TextBox((boxPadding, 5 + interval * 1.25, 90, 22), 'Word length:')
		self.w.basicsBox.lenTextTwo = TextBox((141, 5 + interval * 1.25, 20, 22), 'to')
		self.w.basicsBox.lenTextThree = TextBox((212, 5 + interval * 1.25, 80, 22), 'characters')
		self.w.basicsBox.wordCount = EditText((160, 3, 40, 22), '')
		self.w.basicsBox.wordCount.binding(DefaultsController, 'com.ninastoessinger.wordCount')
		self.w.basicsBox.minLength = EditText((95, 3 + interval * 1.25, 40, 22), '')
		self.w.basicsBox.minLength.binding(DefaultsController, 'com.ninastoessinger.minLength')
		self.w.basicsBox.maxLength = EditText((165, 3 + interval * 1.25, 40, 22), '')
		self.w.basicsBox.maxLength.binding(DefaultsController, 'com.ninastoessinger.maxLength')
		self.w.basicsBox.caseLabel = TextBox((boxPadding, 3 + interval * 2.5, 45, 22), 'Case:') 
		self.w.basicsBox.case = PopUpButton((50, 2 + interval * 2.5, -10, 20), ["leave as is", "all lowercase", "Capitalize", "ALL CAPS"])
		self.w.basicsBox.case.binding(DefaultsController, 'com.ninastoessinger.case')
		y += interval*4.2

		self.w.reqBox = Box((padding, y, -padding, interval*8.9))
		labelY = [5, 5 + interval*2.25, 5 + interval*6.375]
		labelText = ["Required characters:", "Groups (require at least one in each group):", "Excluded characters:"]
		for i in range(3):
			setattr(self.w.reqBox, "reqLabel%s" % i, TextBox((boxPadding, labelY[i], -boxPadding, 22), labelText[i]))
		self.w.reqBox.mustLettersBox = EditText((boxPadding, 5 + interval*.8, -boxPadding, 22), '')
		self.w.reqBox.mustLettersBox.binding(DefaultsController, 'com.ninastoessinger.mustLetters')
		self.w.reqBox.notLettersBox = EditText((boxPadding, 5 + interval * 7.175, -boxPadding, 22), '')
		self.w.reqBox.notLettersBox.binding(DefaultsController, 'com.ninastoessinger.notLetters')
		
		y2 = interval*2.25
		attrNameTemplate = "group%sbox"
		for i in range(3):
			j = i+1
			y2 += interval
			optionsList = ["%s: %s" % (key, ", ".join(value)) for key, value in groupPresets]
			if len(self.requiredGroups[i]) > 0:
				optionsList.insert(0, "Current: " + ", ".join(self.requiredGroups[i]))
			attrName = attrNameTemplate % j
			setattr(self.w.reqBox, attrName, ComboBox((boxPadding, y2-3, -boxPadding, 22), optionsList))
			Combo = getattr(self.w.reqBox, attrName)
			Combo.binding(DefaultsController, 'com.ninastoessinger.'+attrName)
		
		y += interval*9.25
		
		self.w.optionsBox = Box((padding, y, -padding, interval*3.125))
		
		chkLabel = ["Limit to characters available in current font", "No repeating characters", "Randomize output"]
		y3 = 0
		self.w.optionsBox.limitToCharset = CheckBox((boxPadding, y3+3, -boxPadding, 22), "Limit to characters available in current font")
		self.w.optionsBox.limitToCharset.binding(DefaultsController, 'com.ninastoessinger.limitToCharset')
		y3 +=interval*.875
		self.w.optionsBox.banRepetitions = CheckBox((boxPadding, y3+3, -boxPadding, 22), "No repeating characters")
		self.w.optionsBox.banRepetitions.binding(DefaultsController, 'com.ninastoessinger.banRepetitions')
		y3 +=interval*.875
		self.w.optionsBox.randomize = CheckBox((boxPadding, y3+3, -boxPadding, 22), "Randomize output")
		self.w.optionsBox.randomize.binding(DefaultsController, 'com.ninastoessinger.randomize')
		
		y += interval*3.5
		self.w.submit = Button((10,y,-10, 22), 'words please!', callback=self.makeWords)
		self.w.open()
		
	def fontCharacters(self, font):
		global warned
		if not font:
			if warned == False:
				Message("No open fonts found; word-o-mat will output to the Output Window.")
				warned = True
			return []
		charset = []
		for g in font:
			charset.append(str(g.name))
		return charset
		
	def getInputString(self, field, stripColon):
		inputString = field.get()
		if not inputString:
			return []
		pattern = re.compile(" *, *| +")
		if stripColon:
			i = inputString.find(":")
			if i != -1:
				inputString = inputString[i+1:]
		result = pattern.split(inputString)
		try:
			result = [str(s) for s in result if s]
		except UnicodeEncodeError:
			print "Sorry! Characters beyond a-z/A-Z are not currently supported. Please adjust your input."
			result = []
		return result
	
	def getIntegerValue(self, field):
		try:
			returnValue = int(field.get())
		except ValueError:
			returnValue = int(field.getPlaceholder())
			field.set(returnValue)
		return returnValue
	
	def makeWords(self, sender=None):
		global warned
		self.f = CurrentFont()
		self.fontChars = self.fontCharacters(self.f)
		self.wordCount = self.getIntegerValue(self.w.basicsBox.wordCount)
		self.minLength = self.getIntegerValue(self.w.basicsBox.minLength)
		self.maxLength = self.getIntegerValue(self.w.basicsBox.maxLength)
		self.case = self.w.basicsBox.case.get()
		self.requiredLetters = self.getInputString(self.w.reqBox.mustLettersBox, False)
		self.requiredGroups[0] = self.getInputString(self.w.reqBox.group1box, True)
		self.requiredGroups[1] = self.getInputString(self.w.reqBox.group2box, True)
		self.requiredGroups[2] = self.getInputString(self.w.reqBox.group3box, True)
		self.bannedLetters = self.getInputString(self.w.reqBox.notLettersBox, False)
		self.bannedLetters.append(" ")
		self.limitToCharset = self.w.optionsBox.limitToCharset.get()
		self.banRepetitions = self.w.optionsBox.banRepetitions.get()
		self.randomize = self.w.optionsBox.randomize.get()
		self.outputWords = [] #initialize/empty
		Defaults = NSUserDefaults.standardUserDefaults()
		Defaults.synchronize()
		checker = wordChecker(self.limitToCharset, self.fontChars, self.requiredLetters, self.requiredGroups, self.bannedLetters, self.banRepetitions, self.minLength, self.maxLength)
		for i in self.allWords:
			if len(self.outputWords) >= self.wordCount:
				break
			else:
				if self.randomize:
					w = choice(self.allWords)
				else:
					w = i
				if self.case == 1:   w = w.lower()
				elif self.case == 2: w = w.title()
				elif self.case == 3: w = w.upper()
				if checker.checkWord(w, self.outputWords):
					self.outputWords.append(w)
		# output
		
		if len(self.outputWords) < 1:
			print "word-o-mat: No matching words found <sad trombone>"
		else:
			outputString = " ".join(self.outputWords)
			try:
				Glyphs.currentDocument.windowController().activeEditViewController().graphicView().setDisplayString_(outputString)
			except:
				Message("No open document found; word-o-mat will output to the Output Window.")
				warned = True
				print "word-o-mat:", outputString
				pass

GlyphsPlugin = objc.protocolNamed('GlyphsPlugin')
class WordOMat(NSObject, GlyphsPlugin):
	
	def init(self):
		self.wordomat = None
		return self
	
	def loadPlugin(self):
		mainMenu = NSApplication.sharedApplication().mainMenu()
		s = objc.selector(self.showWindow,signature='v@:')
		newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(self.title(), s, "" )
		newMenuItem.setTarget_(self)
		
		mainMenu.itemAtIndex_(2).submenu().addItem_(newMenuItem)
	
	def title(self):
		return "word-o-mat"
	
	def interfaceVersion(self):
		return 1
	
	def showWindow(self):
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