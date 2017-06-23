#!/usr/bin/env python3

RECIPES = [
	["banana", "kiwi", "orange"],
	["pasta", "tomato", "basil"],
	["lemon", "orange", "kiwi", "banana"],
	["pasta2", "tomato", "basil", "lemon"],
]

class RecipeHandler:
	def __init__(self):
		self.__selectedRecipe = -1
		self.__usedIngredients = []

	def selectRecipe(self, which):
		self.__usedIngredients = []
		self.__selectedRecipe = which
		print("Rezept ausgewählt: " + str(RECIPES[which]))

	def currentRecipe(self):
		if self.__selectedRecipe == -1:
			return []
		return RECIPES[self.__selectedRecipe]

	def length(self):
		return len(RECIPES)

	def ingredients(self):
		# a little magic happening here:
		# - add all recipes in one flat list
		# - convert it into a set (only distinct elements)
		# - convert it back into a list
		return list(set(sum(RECIPES, [])))

	def usedIngredients(self):
		return self.__usedIngredients

	def useIngredient(self, ingredient):
		self.__usedIngredients.append(ingredient)