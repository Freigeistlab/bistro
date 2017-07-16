#!/usr/bin/env python3

import threading, gatt

# Static list of tags
# insert mac adress of bluetooth tags
# and matching ingredient here

TAGS = {
	"b0:b4:48:da:b9:e4":"banana",
	"a0:e6:f8:29:21:d9":"lemon",
	"b0:b4:48:da:b8:29":"tomato",
	"a0:e6:f8:29:25:19":"orange",
	"a0:e6:f8:29:21:dd":"basil",
	"a0:e6:f8:47:66:83":"kiwi",
	"a0:e6:f8:47:63:f6":"pasta",
	"a0:e6:f8:47:63:f5":"pasta2",
	"c8:5f:72:65:45:13":"bruschetta",
	"e3:f6:8c:d3:be:37":"caprese",
	"f0:71:a3:2e:b0:72":"olive",
}

class TagManager(gatt.DeviceManager):

	def __init__(self):
		super().__init__(adapter_name='hci0')
		self.start_discovery()
		self.newInput = False
		self.selection = ""

	def device_discovered(self, device):
		if device.mac_address in TAGS:
			self.selection = TAGS[device.mac_address]
			self.newInput = True

	def getSelection(self):
		self.newInput = False
		return self.selection

class BluetoothHandler():

	def __init__(self):
		self.tagManager = TagManager()
		btThread = threading.Thread(name='Bluetooththread', target=self.tagManager.run)
		btThread.start()

	def receivedNewInput(self):
		return self.tagManager.newInput

	def selection(self):
		return self.tagManager.getSelection()