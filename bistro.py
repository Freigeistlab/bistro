#!/usr/bin/env python3

import asyncio, websockets, webbrowser, os, time
from input_handler import InputHandler

class Bistro:
	# Bistro class handles web sockets and holds input handler

	def __init__(self):
		# Input handler is a separate thread, needs to be started
		self.inputHandler = InputHandler()
		self.inputHandler.start()

		# open the website in our default browser
		webbrowser.open_new_tab("file://" + os.path.realpath("bistro.html"))

		# setup the websocket server - port is 5678 on our local machine
		server = websockets.serve(self.bistro, 'localhost', 5678)

		# tell the server to run forever
		asyncio.get_event_loop().run_until_complete(server)
		asyncio.get_event_loop().run_forever()

	@asyncio.coroutine
	def bistro(self, websocket, path):
		# in case there's a new message coming from the input handler
		# we want to send it via web sockets to the browser
		while True:
			if self.inputHandler.newMessage:
				yield from websocket.send(self.inputHandler.getMessage())

			# waiting a bit to save resources
			time.sleep(.1)

if __name__ == "__main__":
	# Create the Bistro object that does all the magic
	bistro = Bistro()