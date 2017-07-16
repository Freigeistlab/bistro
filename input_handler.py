#!/usr/bin/env python3

import threading, time
from recipe_handler import RecipeHandler
from bluetooth_handler import BluetoothHandler
from order_handler import OrderHandler

class InputHandler(threading.Thread):
	def __init__(self):
		# let python do the threading magic
		super().__init__()

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
			if not self.recipeHandler.currentRecipe():
				if self.recipeHandler.selectRecipe(self.orderHandler.nextDish()):
					self.printStatus()
					self.assembleMessage()

			if self.bluetoothHandler.receivedNewInput():
				self.handleBluetoothInput()

	def handleBluetoothInput(self):
		userInput = self.bluetoothHandler.selection()
		print("- ", userInput)

		if userInput in self.recipeHandler.ingredients():
			# entered a valid ingredient
			self.recipeHandler.useIngredient(userInput)
			self.assembleMessage()

		else:
			# everything else
			print("Unbekannte Eingabe: " + userInput)

		print("")
		# wait for 100ms to save resources
		time.sleep(.1)

	def printStatus(self):
		print("\n> Current Recipe: ",
			self.recipeHandler.currentRecipe(),
			self.recipeHandler.currentIngredients(),
			"///", self.orderHandler.waiting(),
			"in waiting list\n")

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
			self.recipeHandler.selectRecipe("")
			self.newMessage = True
			return

		# iterating through all our available ingredients
		for i in self.recipeHandler.ingredients():
			if i in self.recipeHandler.currentIngredients():
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
		
