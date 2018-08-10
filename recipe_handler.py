#!/usr/bin/env python3

import copy

# Static set of sauce recipes. Can be extended.
# Ingredients appearing in sets (such as {"pasta","tomato"}) do not affect
# Note: The basic structure MUST be a list, not a set
# (e.g. the entry "Pasta": {"pasta", "tomato"} is not allowed
# instead use "Pasta": [{"pasta", "tomato"}])

# The list of ingredients is dynamically created from the recipes
# If new ingredients are added here, it will not affect the output in the webbrowser
# To add new ingredients there, see bistro.html file

RECIPES = {
	"Bolognese": {
		"recipe": ["T1", "G1", {"Tomaten","Hackfleisch"}],
		"decoration": ["Basilikum"],
		"preparation": "Mixen"
	},
	"Arrabiata": {
		"recipe": ["T2", "Chili", "Knoblauch", "Tomaten"],
		"decoration": ["Basilikum","Balsamico"],
		"preparation": "Rühren"
	}
}

PASTA = [
	"Penne", "Farfalle", "Tagliatelle", "Spaghetti", "Fussili", "Macaroni"
]

# our sauces: Tomaten, Gemüsebrühe, Weißwein and Sahne.
# all sauces available in 3 portion sizes ranging from 1 to 3
SAUCES = ["T1", "T2", "T3", "G1", "G2", "G3", "W1", "W2", "W3", "S1", "S2", "S3"]

TOPPINGS = [
	"Getrocknete Tomaten", "Mais", "Hackfleisch", "Parmesan", "Salzkartoffeln", "Paprika", "Oliven", "Rucola"
]

DECORATION = [
	"Basilikum", "Balsamico", "Minze"
]


	

class RecipeHandler:
	# The class that handles our recipes and ingredients

	def __init__(self):
		# a little magic happening here:
		# - add all recipes in one flat list
		# - convert it into a set (only distinct elements)
		# - convert it back into a list
		self.__ingredients = dict.fromkeys(list(set(sum(self.flatRecipes(), []) + PASTA + SAUCES + TOPPINGS + DECORATION)))
		self.selectRecipe("")

	def selectRecipe(self, which):
		# use another recipe (that e.g. someone ordered)
		self.__current = 0
		if which:
			self.__sauceName = which["sauce"]
			self.__recipeName = which["name"]
			self.__extras = which["extras"]
			self.__selectedRecipe = which["recipe"]
		else:
			self.__recipeName = ""
			self.__extras = ""
			self.__selectedRecipe = ""
		self.__error = ""
		for i in self.__ingredients:
			self.__ingredients[i] = "neutral"

		if which:
			for i in self.__ingredients:
				if i in self.currentIngredients():
					self.__ingredients[i] = "use"
				elif i in self.ingredientsOfRecipe():
					self.__ingredients[i] = "waiting"
				else:
					self.__ingredients[i] = "neutral"
			return True
		else:
			return False

	def flatIngredientList(self, recipe):
		# return a flat list of the given recipe
		# used to remove the set / list structure
		# necessary for ordered recipes
		l = []
		for i in recipe:
			if type(i) is set:
				for ing in i:
					l.append(ing)
			else:
				l.append(i)
		return l

	def flatRecipes(self):
		# return a flat list of all ingredients of all recipes
		l = []
		for r in RECIPES.values():
			l.append(self.flatIngredientList(r["recipe"]))
		return l

	def ingredientsOfRecipe(self):
		# returns all ingredients required for the currently selected recipe
		# if there is none selected, return an empty list
		if self.__selectedRecipe == "":
			return []
		return self.flatIngredientList(self.__selectedRecipe)

	def currentIngredients(self):
		# returns the ingredient or the ingredients that are to be used right now
		# if there is no recipe selected, return an empty list
		if self.__selectedRecipe == "":
			return []

		try:
			result = self.__selectedRecipe[self.__current]
		except:
			return []

		if not result:
			self.__current += 1
			return self.currentIngredients()
		
		elif type(result) is str:
			return {result}
		
		return result

	def currentRecipe(self):
		return self.__recipeName

	def currentExtras(self):
		return self.__extras

	def currentPreparation(self):
		if (self.__recipeName):
			return RECIPES[self.__sauceName]["preparation"]
		else:
			return ""

	def reset(self):
		self.selectRecipe("")

	def length(self):
		# returns the number of recipes we have
		return len(RECIPES)

	def ingredients(self):
		return self.__ingredients.keys()

	def dishes(self):
		return RECIPES.keys()

	def isPasta(self, pasta):
		return pasta in PASTA

	def isTopping(self, topping):
		return topping in TOPPINGS

	def isSauce(self, sauce):
		return sauce in RECIPES

	def isIngredient(self, ingredient):
		return ingredient in self.ingredients()

	def useIngredient(self, i):
		if self.__ingredients[i] == "use":
			self.__ingredients[i] = "finished"

			if "use" not in self.__ingredients.values():
				self.__current += 1
				for i in self.currentIngredients():
					self.__ingredients[i] = "use"

		else:
			self.__error = i

	def getRecipe(self, name):
		return copy.deepcopy(RECIPES[name]["recipe"])

	def getDecorationFor(self, name):
		return copy.deepcopy(RECIPES[name]["decoration"])

	def getPreparationFor(self, name):
		return RECIPES[name]["preparation"]

	def getIngredientStatus(self):
		return self.__ingredients

	def getError(self):
		error = self.__error
		self.__error = ""
		return error

	def isReady(self):
		# returns if recipe is finished or not to the outer world
		if self.__selectedRecipe == "":
			return False

		return "use" not in self.__ingredients.values() and "waiting" not in self.__ingredients.values()