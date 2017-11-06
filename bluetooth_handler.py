#!/usr/bin/env python3

import threading, gatt

TAG_POOL = [
	"b0:b4:48:da:b9:e4",
	"a0:e6:f8:29:21:d9",
	"b0:b4:48:da:b8:29",
	"a0:e6:f8:29:25:19",
	"a0:e6:f8:29:21:dd",
	"a0:e6:f8:47:66:83",
	"a0:e6:f8:47:63:f6",
	"a0:e6:f8:47:63:f5",
	"c8:5f:72:65:45:13",
	"e3:f6:8c:d3:be:37",
	"f0:71:a3:2e:b0:72",
]

class TagManager(gatt.DeviceManager):

	def __init__(self):
		super().__init__(adapter_name='hci0')

		self.newInput = False
		self.selection = ""
		self.setup = True
		self.tags = {}

		self.start_discovery()

	def device_discovered(self, device):
		if self.setup:
			if device.mac_address in TAG_POOL and device.mac_address not in self.tags:
				self.selection = device.mac_address
				self.newInput = True 
		elif device.mac_address in self.tags and self.tags[device.mac_address] != self.selection:
			self.selection = self.tags[device.mac_address]
			self.newInput = True

	def getSelection(self):
		self.newInput = False
		return self.selection

	def setupReady(self):
		self.setup = False

	def setupTag(self, ingredient, macAddress):
		print("setup",ingredient,"to mac address", macAddress)
		self.tags[macAddress] = ingredient;
		print(self.tags)

class BluetoothHandler():

	def __init__(self):
		self.tagManager = TagManager()
		btThread = threading.Thread(name='Bluetooththread', target=self.tagManager.run)
		btThread.start()

	def setupReady(self):
		self.tagManager.setupReady()

	def setupTag(self, ingredient, macAddress):
		self.tagManager.setupTag(ingredient, macAddress)

	def receivedNewInput(self):
		return self.tagManager.newInput

	def selection(self):
		return self.tagManager.getSelection()