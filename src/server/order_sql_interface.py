import sqlite3, json

class OrderSQLInterface():

	def __init__(self, dbPath):
		self.dbPath = dbPath

	def getOrderQueue(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		queue = dbc.execute('SELECT dish, realOrder FROM WaitingList').fetchall()
		
		orders = [dict([("realOrder",o[1]),("name",eval(o[0])["order"])]) for o in queue]

		return orders

	def clearOrderQueue(self):
		#delete all entries from order queue
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('DELETE FROM WaitingList')
		dbc.execute('DELETE FROM Current')
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

	"""def getDishForId(self, id):
		dish = dbc.execute('SELECT * FROM WaitingList WHERE id = ' + id + ' LIMIT 1').fetchall()
		return eval(dish[1])"""


	def appendToOrderQueue(self, dish, realOrder):
		#append dish to waiting list json.dumps(dish)
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		boolRealOrder = 0
		if realOrder: 
			boolRealOrder = 1
		dbc.execute('INSERT INTO WaitingList(dish, realOrder) VALUES (?,?)', (str(dish),boolRealOrder))
		db.commit()

	def getPreparedOrders(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		queue = dbc.execute('SELECT dish FROM WaitingList WHERE realOrder == 0').fetchall()
		orders = [eval(o[0]) for o in queue]
		return orders
	def recipeReady(self):
		db = sqlite3.connect(self.dbPath)
		dbc = db.cursor()
		dbc.execute('DELETE FROM Current');
		db.commit()