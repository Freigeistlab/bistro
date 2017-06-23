#!/usr/bin/env python3

RECIPES = [
	["Banane", "Kiwi", "Orange"],
	["Pasta", "Tomate", "Basilikum"],
	["Zitrone", "Orange", "Kiwi", "Banane"]
]

class RecipeHandler:
	def __init__(self):
		self.selectedRecipe = 0

	def selectRecipe(self, which):
		self.selectedRecipe = which

	def currentRecipe(self):
		return RECIPES[0]