#!/usr/bin/env python3

import threading, serial

SERIAL_PORT = "/dev/ttyUSB0"

class SerialHandler(threading.Thread):

	def __init__(self):
		super().__init__()
		self.__serial = serial.Serial(SERIAL_PORT, 9600, timeout=0.5)
		self.scaleValue = 0
		self.newInput = False

	def run(self):
		while True:
			try:
				line = self.__serial.readline()
				self.scaleValue = float(line[3:8].replace(",","."))
				self.newInput = True
			except:
				self.newInput = False
				

	def getValue(self):
		self.newInput = False
		return self.scaleValue

	def receivedNewInput(self):
		return self.newInput