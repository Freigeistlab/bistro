#!/usr/bin/env python3

import asyncio
import websockets
from recipe_handler import RecipeHandler

async def bistro(websocket, path):
	while True:
		ingredient = input("Bitte Zutat eingeben: ")
		if ingredient in recipeHandler.currentRecipe():
			await websocket.send(ingredient)

if __name__ == "__main__":
	recipeHandler = RecipeHandler()

	server = websockets.serve(bistro, 'localhost', 5678)

	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()