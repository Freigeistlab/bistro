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
		print("hello")
		# open the website in our default browser
		#webbrowser.open_new_tab("file://" + os.path.realpath("bistro.html"))

		# setup the websocket server - port is 5678 on our local machine
		
		server = websockets.serve(self.bistro, '', 5678)
		self.dashboard_server = websockets.serve(self.echo, '', 443)

		# tell the server to run forever
		asyncio.get_event_loop().run_until_complete(server)
		asyncio.get_event_loop().run_forever()


	@asyncio.coroutine
	def register(self,websocket):
		USERS.add(websocket)
		yield from asyncio.wait([user.send(self.inputHandler.getMessage()) for user in USERS])

	@asyncio.coroutine
	def unregister(self,websocket):
		USERS.remove(websocket)

	@asyncio.coroutine
	def sendMessage(self, message):
		if USERS:
			yield from asyncio.wait([user.send(message) for user in USERS])
			#send message to both dashboard and website

	@asyncio.coroutine
	def getMessage(self):
		if self.inputHandler.newMessage:
			return self.inputHandler.getMessage()
		else:
			return ""

	@asyncio.coroutine
	def bistro(self, websocket, path):
		# in case there's a new message coming from the input handler
		# we want to send it via web sockets to the browser

		yield from self.register(websocket)
		try: 
			while True:
				message = yield from self.getMessage()
				if message:
					yield from self.sendMessage(message)
				yield from  asyncio.sleep(.1)
		finally: 
			yield from self.unregister(websocket)
	
	@asyncio.coroutine
	async def echo(self, websocket, path):
		print("Connected to dashboard")
	    async for message in websocket:
	        print(message)
	        await websocket.send(message)

if __name__ == "__main__":
	# Create the Bistro object that does all the magic
	bistro = Bistro()
