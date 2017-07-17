#!/usr/bin/env python3

# Static list of recipes. Can be extended.
# The list of ingredients is dynamically created from the recipes
# If new ingredients are added here, it will not affect the output in the webbrowser
# To add new ingredients there, see bistro.html file

RECIPES = {
	"Antipasti":["bruschetta","caprese","olive"],
	"Kürbissuppe":["pasta", "tomato", "basil"],
	"Tomatensuppe":["lemon", "orange", "kiwi", "banana"],
	"Fingerfood Platte":["pasta", "tomato", "basil", "lemon"],
}

class RecipeHandler:
	# The class that handles our recipes and ingredients

	def __init__(self):
		self.selectRecipe("")

	def selectRecipe(self, which):
		# use another recipe (that e.g. someone ordered)
		self.__usedIngredients = []
		self.__selectedRecipe = which
		if which:
			return True
		else:
			return False

	def currentIngredients(self):
		# returns the ingredient list for the currently selected recipe
		# if there is none selected, return an empty list
		if self.__selectedRecipe == "":
			return []
		return RECIPES[self.__selectedRecipe]

	def currentRecipe(self):
		return self.__selectedRecipe

	def reset(self):
		self.selectRecipe("")

	def length(self):
		# returns the number of recipes we have
		return len(RECIPES)

	def ingredients(self):
		# a little magic happening here:
		# - add all recipes in one flat list
		# - convert it into a set (only distinct elements)
		# - convert it back into a list
		return list(set(sum(RECIPES.values(), [])))

	def dishes(self):
		return RECIPES.keys()

	def usedIngredients(self):
		# returns the list of used ingredients to access from outside
		return self.__usedIngredients

	def useIngredient(self, ingredient):
		# append an ingredient to the list of used ingredients
		self.__usedIngredients.append(ingredient)

	def isReady(self):
		# returns if recipe is finished or not to the outer world
		if self.__selectedRecipe == "":
			return False
		return set(self.currentIngredients()).issubset(set(self.__usedIngredients))