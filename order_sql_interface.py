import sqlite3

class OrderSQLInterface():

	def __init__(self, dbPath):
		self.dbPath = dbPath

	def getOrderQueue(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		queue = dbc.execute('SELECT dish FROM WaitingList').fetchall()
		orders = [eval(o[0]) for o in queue]
		return orders

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
			print(current)
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