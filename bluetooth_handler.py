#!/usr/bin/env python3

import os, threading, gatt, time, sqlite3

# Static list of all possible tags to be used
# Tags are assigned to their ingredients in a setup routine
# but need to appear in this list in order to be selectable


class TagManager(gatt.DeviceManager):

	def __init__(self):
		super().__init__(adapter_name='hci0')

		self.startupTime = time.time()
		self.newInput = False
		self.selection = ""
		self.selectionTime = time.time()
		self.setup = False
		self.dbPath = os.path.dirname(os.path.abspath(__file__))+'/tags.db'

		self.getTagPool()
		self.start_discovery()

	def getTags(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		tags = dbc.execute('SELECT * FROM Tags').fetchall()
		return dict((tag,ingredient) for tag,ingredient in tags)

	def getTagPool(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		pool = dbc.execute('SELECT * FROM TagPool').fetchall()
		self.tagPool = list(tag[0] for tag in pool)

	def device_discovered(self, device):
		# if we're still setting up,
		# check if the mac address is in our tag pool
		# and in case it's a new tag, add to our used tags
		tags = self.getTags()		
		if self.setup:
			if device.mac_address in self.tagPool and device.mac_address not in tags:
				self.selection = device.mac_address
				self.newInput = True 

		elif device.mac_address in tags and (tags[device.mac_address] != self.selection or time.time() - self.selectionTime > 5):
			self.selection = tags[device.mac_address]
			self.selectionTime = time.time()
			self.newInput = True

	def getSelection(self):
		self.newInput = False
		return self.selection

	def resetSelection(self):
		self.selection = ""

	def beginSetup(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('DELETE FROM Tags')
		db.commit()
		self.setup = True

	def setupReady(self):
		self.setup = False

	def setupTag(self, ingredient, macAddress):
		# assign a tag to its ingredient
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		print("setup",ingredient,"to mac address", macAddress)
		dbc.execute('INSERT INTO Tags VALUES (?,?)', (macAddress, ingredient))
		db.commit()
		print(self.getTags())

class BluetoothHandler():

	def __init__(self):
		self.tagManager = TagManager()
		btThread = threading.Thread(name='Bluetooththread', target=self.tagManager.run)
		btThread.start()

	def setupReady(self):
		self.tagManager.setupReady()

	def beginSetup(self):
		self.tagManager.beginSetup()

	def setupTag(self, ingredient, macAddress):
		self.tagManager.setupTag(ingredient, macAddress)

	def receivedNewInput(self):
		return self.tagManager.newInput

	def selection(self):
		return self.tagManager.getSelection()

	def resetSelection(self):
		return self.tagManager.resetSelection()