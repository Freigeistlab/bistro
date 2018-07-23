#!/usr/bin/env python3

import asyncio, websockets, webbrowser, os, time, sys, json
from input_handler import InputHandler

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

		# Input handler is a separate thread, needs to be started
		self.inputHandler = InputHandler(verbose, bluetooth, fakeData, setupTags, self)
		self.inputHandler.start()

		# open the website in our default browser
		#webbrowser.open_new_tab("file://" + os.path.realpath("bistro.html"))

		# setup the websocket server - port is 5678 on our local machine
		server = websockets.serve(self.bistro, '', 5678)

		# tell the server to run forever
		asyncio.get_event_loop().run_until_complete(server)
		asyncio.get_event_loop().run_forever()

	async def register(self,websocket):
		USERS.add(websocket)
		await asyncio.wait([user.send(self.inputHandler.getMessage()) for user in USERS])

	async def unregister(self,websocket):
		USERS.remove(websocket)

	async def sendMessage(self, message):
		if USERS:
			await asyncio.wait([user.send(message) for user in USERS])

	async def getMessage(self):
		if self.inputHandler.newMessage:
			return self.inputHandler.getMessage() 
		else:
			return ""

	async def bistro(self, websocket, path):
		# in case there's a new message coming from the input handler
		# we want to send it via web sockets to the browser

		await self.register(websocket)
		try: 
			while True:
				message = await self.getMessage()
				if message:
					await self.sendMessage(message)
				await asyncio.sleep(.1)
		finally: 
			await self.unregister(websocket)


if __name__ == "__main__":
	# Create the Bistro object that does all the magic
	bistro = Bistro()