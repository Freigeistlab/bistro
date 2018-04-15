#!/usr/bin/env python3

import threading, time, serial, random

SERIAL_PORT = "/dev/ttyUSB0"

class SerialHandler(threading.Thread):

	def __init__(self):
		super().__init__()
		self.scaleValue = 0
		self.newInput = False
		try: 
			self.__serial = serial.Serial(SERIAL_PORT, 9600, timeout=0.5)
		except:
			print("Could not find scales at given port " + SERIAL_PORT + ". Maybe change port in serial_handler.py?")

	def run(self):
		while True:
			try:
				line = self.__serial.readline()
				self.scaleValue = float(line[3:8].replace(",","."))
				self.newInput = True
			except:
				self.newInput = False
				#self.scaleValue = random.random() * 6
				#self.newInput = True
				#time.sleep(.5)
			time.sleep(.1)
				

	def getValue(self):
		self.newInput = False
		return self.scaleValue

	def receivedNewInput(self):
		return self.newInput