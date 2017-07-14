#!/usr/bin/env python3

import threading, time
from recipe_handler import RecipeHandler
from bluetooth_handler import BluetoothHandler
from order_handler import OrderHandler

class InputHandler(threading.Thread):
	def __init__(self):
		# let python do the threading magic
		super().__init__()

		# create our recipe handler and tag manager objects
		self.recipeHandler = RecipeHandler()
		self.bluetoothHandler = BluetoothHandler()
		self.orderHandler = OrderHandler()
		self.orderHandler.start()

		# nothing to send yet
		self.newMessage = False

	def run(self):
		# check user inputs and evaluate which action to take
		# will run infinetly and wait for inputs

		while True:
			if self.bluetoothHandler.receivedNewInput():
				self.handleInput()

	def handleInput(self):
		print("Aktuelles Rezept: " + str(self.recipeHandler.currentRecipe()))
		userInput = self.bluetoothHandler.selection()
		print(userInput)

		# try to convert the input into a number
		userInt = -1
		try:
			userInt = int(userInput)
		except:
			pass

		if userInt in range(self.recipeHandler.length()):
			# we got a number in the range of our recipes - selecting a new one
			self.recipeHandler.selectRecipe(userInt)
			self.assembleMessage()

		elif userInput in self.recipeHandler.ingredients():
			# entered a valid ingredient
			self.recipeHandler.useIngredient(userInput)
			self.assembleMessage()

		elif userInput == "reset":
			# go back to zero
			print("Resetting program...")
			self.recipeHandler.selectRecipe(-1)
			self.assembleMessage()

		else:
			# everything else
			print("Unbekannte Eingabe: " + userInput)

		print("")
		# wait for 100ms to save resources
		time.sleep(.1)

	def assembleMessage(self):
		# assemble the message to be sent to the web browser
		# it takes the form of a JSON object looking something like this:
		# {
		#	banana: "neutral",
		#	tomato: "success",
		#	basil: "error",
		#	...
		# }

		self.message = {}

		# if the recipe is finished, blink for a bit and reset
		if self.recipeHandler.isReady():
			for i in self.recipeHandler.ingredients():
				self.message[i] = "blink" #blinking
			self.recipeHandler.selectRecipe(-1)
			self.newMessage = True
			return

		# iterating through all our available ingredients
		for i in self.recipeHandler.ingredients():
			if i in self.recipeHandler.currentRecipe():
				if self.recipeHandler.usedIngredients().count(i) == 1:
					# we used a required ingredient exactly once
					self.message[i] = "neutral" #grey

				elif self.recipeHandler.usedIngredients().count(i) > 1:
					# we tried using a required ingredients multiple times
					self.message[i] = "error" #red

				else:
					# we still need to use an ingredient
					self.message[i] = "success" #green

			else:
				if i in self.recipeHandler.usedIngredients():
					# not required but tried to use it
					self.message[i] = "error" #red

				else:
					# not required and not used
					self.message[i] = "neutral" #grey

		self.newMessage = True

	def getMessage(self):
		# distributing the message to the outer world
		self.newMessage = False
		# modifying the message so that javascript in the browser can understand it:
		return str(self.message).replace("'",'"')
		
