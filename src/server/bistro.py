#!/usr/bin/env python3

import asyncio, websockets, webbrowser, os, time, sys, json
from input_handler import InputHandler
from flask import Flask
from flask_restful import Resource, Api
from api import WebServer
from recipe_handler import RecipeHandler
from actions import Action

USERS = set()

class Bistro:
	# Bistro class handles web sockets and holds input handler

	def __init__(self):
		verbose = False
		bluetooth = True
		fakeData = False
		setupTags = False
		self.usercount =0

		for arg in sys.argv:
			if arg == "--verbose":
				verbose = True
			if arg == "--no-bluetooth":
				bluetooth = False
			if arg == "--fake-data":
				fakeData = True
			if arg == "--setup":
				setupTags = True

		self.recipeHandler = RecipeHandler()


		# Input handler is a separate thread, needs to be started
		self.inputHandler = InputHandler(verbose, bluetooth, fakeData, setupTags, self, self.recipeHandler)
		self.inputHandler.start()
		
		# open the website in our default browser
		#webbrowser.open_new_tab("file://" + os.path.realpath("bistro.html"))

		#init the webserver which is necessary for handling user interactions from the dashboard
		self.webserver = WebServer(self.inputHandler)
		self.webserver.start()
		
		# setup the websocket server - port is 5678 on our local machine
		
		server = websockets.serve(self.bistro, '', 5678)
		#self.dashboard_server = websockets.serve(self.echo, '', 443)

		# tell the server to run forever
		asyncio.get_event_loop().run_until_complete(server)
		asyncio.get_event_loop().run_forever()


	@asyncio.coroutine
	def register(self,websocket):
		USERS.add(websocket)
		#await asyncio.wait([user.send(self.inputHandler.getMessage()) for user in USERS])
		#send current order out to new websocket
		message = self.inputHandler.assembleMessage(Action.INIT)
		yield from asyncio.wait([websocket.send(message)])

	@asyncio.coroutine
	def unregister(self,websocket):
		USERS.remove(websocket)

	@asyncio.coroutine
	def sendMessage(self, message):
		
		if USERS:
			print("Sending message to users ", message)
			yield from asyncio.wait([user.send(message) for user in USERS])
			print("message sent")
			#send message to both dashboard and website

	#TODO: do we still need that method?
	"""@asyncio.coroutine
	def getMessage(self):
		if self.inputHandler.newMessage:
			return self.inputHandler.getMessage()
		else:
			return """

	@asyncio.coroutine
	def bistro(self, websocket, path):
		# in case there's a new message coming from the input handler
		# we want to send it via web sockets to the browser
		yield from self.register(websocket)
		print("Connected to websocket")
		while True:
			message = yield from websocket.recv()
			json_msg = json.loads(message)
			#print(json_msg.action, " " , json_msg.meal, " ", json_msg.amount)
			if json_msg["action"]=="prepare_order":
				print(json_msg["meal"])
				self.inputHandler.orderHandler.addMealPreparation(json_msg["meal"], json_msg["amount"])

			#await websocket.send(message)

if __name__ == "__main__":
	# Create the Bistro object that does all the magic
	bistro = Bistro()
