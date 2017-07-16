#!/usr/bin/env python3

import threading

class KeyboardHandler(threading.Thread):

	def __init__(self):
		super().__init__()
		self.userInput = ""
		self.newInput = False

	def run(self):
		while True:
			self.userInput = input()
			self.newInput = True

	def getInput(self):
		self.newInput = False
		return self.userInput

	def receivedNewInput(self):
		return self.newInput