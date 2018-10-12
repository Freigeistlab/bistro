#!/usr/bin/env python3

import re, socket, threading, sys, sqlite3, os, time

class OrderHandler(threading.Thread):

	def __init__(self, recipeHandler, verbose, fakeData):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		self.recipeHandler = recipeHandler
		self.verbose = verbose
		self.newInput = False
		self.fakeData = fakeData
		self.dbPath = os.path.dirname(os.path.abspath(__file__))+'/recipes.db'
		self.setupSocket()

	def getOrderQueue(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		return dbc.execute('SELECT id FROM WaitingList').fetchall()

	def clearOrderQueue(self):
		#delete all entries from order queue
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('DELETE FROM WaitingList');
		db.commit()

	def getNextWaitingDish(self):
		#fetch next dish, remove it from waiting list and return
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		current = dbc.execute('SELECT * FROM Current LIMIT 1').fetchall()
		if current:
			return eval(current[0][1])

		dish = dbc.execute('SELECT * FROM WaitingList LIMIT 1').fetchall()
		if dish:
			dish = dish[0]
			dbc.execute('DELETE FROM WaitingList WHERE id = ' + str(dish[0]));
			db.commit()

			dbc.execute('INSERT INTO Current(dish) VALUES (?)', (dish[1],))
			db.commit()

			return eval(dish[1])


	def appendToOrderQueue(self, dish):
		#append dish to waiting list json.dumps(dish)
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('INSERT INTO WaitingList(dish) VALUES (?)', (str(dish),))
		db.commit()

	def recipeReady(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('DELETE FROM Current');
		db.commit()

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

		return self.getNextWaitingDish()

	def waiting(self):
		return len(self.getOrderQueue())

	def getIpAddress(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

	def reset(self):
		self.clearOrderQueue()

	def receivedNewInput(self):
		res = self.newInput
		self.newInput = False
		return res

	#this function deals with meals that are added by the dashboard
	def addMealPreparation(self, meal, amount):
		print("adding meal to prepare")
		self.getRecipe(meal.split(" "), meal, amount)

	def getRecipe(self, items, order, amount):
		if not self.recipeHandler.isPasta(items[0]):
			print("Error: Ich kenne keine Pasta namens", pasta, ". Vielleicht in der recipe_handler.py eintragen?")
		else: 
			pasta = items[0]

		if not self.recipeHandler.isSauce(items[1]):
			print("Error: Ich kenne keine Sauce namens", items[1], ". Vielleicht in der recipe_handler.py eintragen?")
		else:
			sauce = self.recipeHandler.getRecipe(items[1])

		sauceName = items[1]
		dishName = pasta + " " + sauceName

		items = items[2:]
		extras = ""
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
			"time": time.strftime('%x %X %Z'),
			"order": order,
			"sauce": sauceName,
			"name": dishName,
			"extras": extras.strip(),
			"recipe": [pasta] + sauce + toppings + self.recipeHandler.getDecorationFor(sauceName),
			"preparation": self.recipeHandler.getPreparationFor(sauceName)
		}

		for i in range(0,amount):
			self.appendToOrderQueue(dish)

	def run(self):
		print("Set up your orderbird printer to IP", self.getIpAddress())
		print("Waiting for orders...")

		while True:
			try:
				# accept connections (probably from orderbird or order dashboard)
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

						print("  New order:")
						if self.verbose:
							print(data)

						orders = re.compile("(?<=-{42}\s\x1ba\x00\x1d!\x11)[\s\S]+?(?=\x1d!\x00\n\x1ba\x00\s+\(\d+,\d{2}\)\s\d+,\d{2})").findall(data)
						#orders = re.compile("(?<=-{42}\s)[\w\s-]+").findall(data)

						if self.verbose:
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

							items = re.split('\x1d!\x00\n\x1d!\x11', order)

							for index, item in enumerate(items):
								# remove unnecessary whitespaces and control strings
								items[index] = items[index].strip()

							if self.verbose:
								print("    Items: ", items)

							
							
							self.getRecipe(items, order, amount)

						self.newInput = True

			except:
				print("exception: ", sys.exc_info()[0])