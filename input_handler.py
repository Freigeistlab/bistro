#!/usr/bin/env python3

import threading
import time
from recipe_handler import RecipeHandler

class InputHandler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.recipeHandler = RecipeHandler()
		self.newMessage = False
		self.message = ""

	def run(self):
		while True:
			print("Aktuelles Rezept: " + str(self.recipeHandler.currentRecipe()))
			userInput = input("Bitte Zutat eingeben oder [0.." + str(self.recipeHandler.length()-1) + "] um ein Rezept auszuwählen: ")

			userInt = -1
			try:
				userInt = int(userInput)
			except:
				pass

			if userInt in range(self.recipeHandler.length()):
				self.recipeHandler.selectRecipe(userInt)
				self.assembleMessage()
			elif userInput in self.recipeHandler.ingredients():
				self.recipeHandler.useIngredient(userInput)
				self.assembleMessage()
			else:
				print("Unbekannte Eingabe: " + userInput)

			print("")
			time.sleep(.1)

	def assembleMessage(self):
		self.message = {}

		for i in self.recipeHandler.ingredients():
			if i in self.recipeHandler.currentRecipe():
				if self.recipeHandler.usedIngredients().count(i) == 1 :
					self.message[i] = "neutral"
				elif self.recipeHandler.usedIngredients().count(i) > 1:
					self.message[i] = "error"
				else:
					self.message[i] = "success"
			else:
				if i in self.recipeHandler.usedIngredients():
					self.message[i] = "error"
				else:
					self.message[i] = "neutral"

		self.newMessage = True

	def getMessage(self):
		self.newMessage = False
		return str(self.message).replace("'",'"')