#!/usr/bin/env python3

import re, socket, threading, sys, os, asyncio, functools
from order_sql_interface import OrderSQLInterface
from actions import Action

class OrderHandler(threading.Thread):

	def __init__(self, recipeHandler, verbose, fakeData, websocket):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		self.websocket = websocket
		self.recipeHandler = recipeHandler
		self.verbose = verbose
		self.fakeData = fakeData
		self.dbPath = os.getcwd()+'/database/recipes.db'
		self.orderSQLInterface = OrderSQLInterface(self.dbPath)
		self.setupSocket()
		self.loop = asyncio.get_event_loop()


	def setupSocket(self):
		# sets up the socket to establish the connection to orderbird

		host = '' # meaning all available interfaces on our machine
		port = 9100 # as used by orderbird
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # makes it easier to restart the program

		try:
			self.socket.bind((host, port))
		except OSError:
			print("cannot bind to port", port)
			#print("try running:")
			#print("sudo fuser -k", port, "/tcp")
			os._exit(1)

		self.socket.listen(1)

	def nextDish(self):
		# returns the next dish in the waitinglist
		# and removes it from there
		print("order handler next dish")
		return self.orderSQLInterface.getNextWaitingDish()

	def waiting(self):
		return len(self.orderSQLInterface.getOrderQueue())

	def getIpAddress(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

	def reset(self):
		self.orderSQLInterface.clearOrderQueue()
		#send the message out to all clients
		message = {
			"action": Action.CLEAR_QUEUE.value
		}
		message = str(message).replace("'",'"')
		asyncio.run_coroutine_threadsafe(self.websocket.sendMessage(message), self.loop)

	
	#this function deals with meals that are added by the dashboard
	def addMealPreparation(self, meal, amount):
		print("adding meal to prepare")
		dish = self.recipeHandler.constructRecipe(meal.split(" "), meal)
		for i in range(0,amount):
			print("Appending to order queue")
			self.orderSQLInterface.appendToOrderQueue(dish, False)
			self.sendNewOrderToClients(dish, False)
	
	#directly send out response after successful adding --> TODO: actually check if adding to queue was successful
	def sendNewOrderToClients(self, dish, realOrder):
		
		realOrderBool = 0
		if realOrder:
			realOrderBool = 1
		"""
		self.message = {
			"recipe": self.recipeHandler.currentRecipe(),
			"extras": self.recipeHandler.currentExtras(),
			"preparation": self.recipeHandler.currentPreparation(),
		"""
		print("Dish ", dish)
			

		message = {
			"name": dish["name"],
			"realOrder": realOrderBool,
			"action": Action.NEW_ORDER.value
		}

		message = str(message).replace("'",'"')
		#task = loop.create_task(self.websocket.sendMessage(message))
		#loop.run_until_complete(task)
		##print("is send message co routine ? ", self.websocket.sendMessage)
		#asyncio.run_coroutine_threadsafe(self.websocket.sendMessage, message)
		asyncio.run_coroutine_threadsafe(self.websocket.sendMessage(message), self.loop)
		
		

	def run(self):
		#print("Set up your orderbird #printer to IP", self.getIpAddress())
		print("Waiting for orders...")
		
		#needed for async events (like sending via websocket) that don't need to be awaited
		#asyncio.set_event_loop(asyncio.new_event_loop())

		while True:
			try:
				# accept connections (probably from orderbird or order dashboard)
				conn, addr = self.socket.accept()
				#print("\n  Connection from: " + str(addr))

				while True:
					data = conn.recv(8192).decode("cp1252")

					if not data:
						break

					elif data == bytes([16, 4, 1, 16, 4, 2, 16, 4, 3, 16, 4, 4]).decode("cp1252"):
						#send check
						conn.send(bytes([22, 18, 18, 18]))

					else:
						#print("  Processing data...")
						liste = [55, 34] + [ord(i) for i in data[-8:-4:]] + [0]
						conn.send(bytes(liste))

						if self.fakeData:
							data = bytes([10, 27, 116, 16, 27, 82, 0, 10, 27, 97, 0, 66, 111, 110, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 29, 33, 17, 27, 69, 1, 50, 54, 27, 69, 0, 29, 33, 0, 32, 84, 105, 115, 99, 104, 98, 111, 110, 10, 27, 97, 0, 68, 97, 116, 117, 109, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 48, 49, 58, 52, 55, 32, 50, 53, 46, 48, 53, 46, 49, 56, 10, 27, 97, 0, 66, 101, 100, 105, 101, 110, 116, 32, 118, 111, 110, 32, 32, 32, 32, 65, 114, 109, 105, 110, 32, 65, 100, 109, 105, 110, 32, 49, 50, 51, 52, 10, 27, 97, 0, 84, 101, 114, 109, 105, 110, 97, 108, 32, 32, 32, 32, 32, 32, 32, 105, 80, 104, 111, 110, 101, 32, 118, 111, 110, 32, 77, 105, 99, 104, 97, 101, 108, 10, 27, 97, 0, 84, 105, 115, 99, 104, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 29, 33, 17, 84, 105, 115, 99, 104, 32, 49, 29, 33, 0, 10, 27, 97, 0, 29, 33, 0, 10, 10, 10, 10, 27, 97, 0,
45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 10, 27, 97, 0, 29, 33, 17,
84, 97, 103, 108, 105, 97, 116, 101, 108, 108, 101,
29, 33, 0,
10,
29, 33, 17,
32, 32, 32, 65, 114, 114, 97, 98, 105, 97, 116, 97,
29, 33, 0,
10,
29,
33, 17,
32, 32, 32, 80, 97, 114, 109, 101, 115, 97, 110,
29, 33, 0,
10,
27, 97, 0,
32, 32, 32, 32, 32, 32,
32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 40, 53, 44,
48, 48, 41, 32, 53, 44, 48, 48,
10,
45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
29, 40, 72, 6, 0, 48, 48, 51, 54, 51, 50, 29, 86, 66, 10]).decode("cp1252")
# 							data = """Bon            26 Tischbon
# Datum          14:12 31.03.18
# Bedient von    Armin Admin 1234
# Terminal       iPhone von Michael
# Tisch          Theke

# ------------------------------------------
# Penne
#    Bolognese
#    Mais
#    Hackfleisch
#    Ohne Tomaten
#    Ohne Parmesan
#    Coca-Cola
#                             (20,90) 20,90
# ------------------------------------------
# Farfalle
#     Arrabiata
#                             (20,90) 20,90
# ------------------------------------------
# Penne
#     Bolognese
#                             (20,90) 20,90
# ------------------------------------------
# 3x Tagliatelle
#    Bolognese
#    Mais
#    Ohne Hackfleisch
#    Ohne Tomaten
#    Ohne Parmesan
#                             (20,90) 20,90
# ------------------------------------------
# 2x Penne
#    Arrabiata
#    Parmesan
#    Salzkartoffeln
#    Ohne Chili
#    Fanta
#                             (23,50) 23,50
# ------------------------------------------
# """

						#print("  New order:")
						if self.verbose:
							print(data)
							#pass

						orders = re.compile("(?<=-{42}\s\x1ba\x00\x1d!\x11)[\s\S]+?(?=\x1d!\x00\n\x1ba\x00\s+\(\d+,\d{2}\)\s\d+,\d{2})").findall(data)
						#orders = re.compile("(?<=-{42}\s)[\w\s-]+").findall(data)

						if self.verbose:
							pass
							#print("    Orders: ", [o.strip() for o in orders])

						for order in orders:
							# remove unnecessary whitespaces
							order = order.strip()

							# figure out how many times an item has been ordered
							amount = re.compile("\d+(?=x)").findall(order)
							
							if amount:
								amount = int(amount[0])
								order = order[len(str(amount))+2:]
							else:
								amount = 1

							items = re.split('\x1d!\x00\n\x1d!\x11', order)

							for index, item in enumerate(items):
								# remove unnecessary whitespaces and control strings
								items[index] = items[index].strip()

							if self.verbose:
								pass
								#print("    Items: ", items)
							
							
							dish = self.recipeHandler.constructRecipe(items, order)
							for i in range(0,amount):
								#print("Appending to order queue")
								self.orderSQLInterface.appendToOrderQueue(dish, True)

							self.sendNewOrderToClients(dish, True)
							


			except:
				print("exception: ", sys.exc_info()[0])
