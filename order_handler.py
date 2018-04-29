#!/usr/bin/env python3

import re, socket, threading, sys

class OrderHandler(threading.Thread):

	def __init__(self, recipeHandler, verbose, fakeData):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		self.recipeHandler = recipeHandler
		self.waitinglist = []
		self.verbose = verbose
		self.newInput = False
		self.fakeData = fakeData
		self.setupSocket()

	def setupSocket(self):
		# sets up the socket to establish the connection to orderbird

		host = '' # meaning all available interfaces on our machine
		port = 9100 # as used by orderbird
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # makes it easier to restart the program
		self.socket.bind((host, port))
		self.socket.listen(1)

	def nextDish(self):
		# returns the next dish in the waitinglist
		# and removes it from there

		if not self.waitinglist:
			return ""

		nextDish = self.waitinglist[0]
		self.waitinglist = self.waitinglist[1:]
		return nextDish

	def waiting(self):
		return len(self.waitinglist)

	def getIpAddress(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

	def reset(self):
		self.waitinglist = []

	def receivedNewInput(self):
		res = self.newInput
		self.newInput = False
		return res

	def run(self):
		print("Set up your orderbird printer to IP", self.getIpAddress())
		print("Waiting for orders...")

		while True:
			try:
				# accept connections (probably from orderbird)
				conn, addr = self.socket.accept()
				print("\n  Connection from: " + str(addr))

				while True:
					data = conn.recv(8192).decode("cp1252")

					if not data:
						break

					elif data == bytes([16, 4, 1, 16, 4, 2, 16, 4, 3, 16, 4, 4]).decode("cp1252"):
						#send check
						conn.send(bytes([22, 18, 18, 18]))

					else:
						print("  Processing data...")
						liste = [55, 34] + [ord(i) for i in data[-8:-4:]] + [0]
						conn.send(bytes(liste))

						if self.fakeData:
							data = """Bon            26 Tischbon
Datum          14:12 31.03.18
Bedient von    Armin Admin 1234
Terminal       iPhone von Michael
Tisch          Theke

------------------------------------------
Penne
   Bolognese
   Mais
   Hackfleisch
   Ohne Tomaten
   Ohne Parmesan
   Coca-Cola
                            (20,90) 20,90
------------------------------------------
Farfalle
    Arrabiata
                            (20,90) 20,90
------------------------------------------
Penne
    Bolognese
                            (20,90) 20,90
------------------------------------------
3x Tagliatelle
   Bolognese
   Mais
   Ohne Hackfleisch
   Ohne Tomaten
   Ohne Parmesan
                            (20,90) 20,90
------------------------------------------
2x Penne
   Arrabiata
   Parmesan
   Salzkartoffeln
   Ohne Chili
   Fanta
                            (23,50) 23,50
------------------------------------------
"""

						print("  New order:")
						if self.verbose:
							print(data)

						orders = re.compile("(?<=-{42}\s)[\w\s-]+").findall(data)

						print("    Orders: ", [o.strip() for o in orders])

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

							items = re.split('\n', order)

							for index, item in enumerate(items):
								# remove unnecessary whitespaces
								items[index] = item.strip()

							dishName = items[0] + " " + items[1]
							extras = ""
							
							if not self.recipeHandler.isPasta(items[0]):
								print("Error: Ich kenne keine Pasta namens", pasta, ". Vielleicht in der recipe_handler.py eintragen?")
							else: 
								pasta = items[0]

							if not self.recipeHandler.isSauce(items[1]):
								print("Error: Ich kenne keine Sauce namens", items[1], ". Vielleicht in der recipe_handler.py eintragen?")
							else:
								sauce = self.recipeHandler.getRecipe(items[1])

							items = items[2:]
							toppings = []

							for item in items:
								if item.startswith("Ohne "):
									if item[5:] in sauce:
										sauce.remove(item[5:])
										extras += " – " + item[5:]
									for ingredient in sauce:
										if item[5:] in ingredient:
											ingredient.remove(item[5:])
											extras += " – " + item[5:]
								elif not self.recipeHandler.isTopping(item):
									print(item,"ist kein Topping. Vielleicht ein Getränk. Ansonsten vielleicht in der recipe_handler.py eintragen?")
								else:
									toppings.append(item)
									extras += " + " + item

							# put together the ordered dish
							dish = {
								"name": dishName,
								"extras": extras.strip(),
								"recipe": [pasta] + sauce + toppings
							}

							for i in range(0,amount):
								self.waitinglist.append(dish)

						self.newInput = True

			except:
				print("exception: ", sys.exc_info()[0])