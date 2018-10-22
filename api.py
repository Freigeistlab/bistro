from flask import Flask
from flask_restful import Resource, Api
import threading, os, json, asyncio
from order_sql_interface import OrderSQLInterface
from flask_cors import CORS

#the server that's responsible for handling user interactions from the dashboard
class WebServer(threading.Thread):
	def __init__(self, inputHandler):
		super().__init__()
		self.app = Flask(__name__)
		self.api = Api(self.app)
		CORS(self.app)
		self.dbPath = os.path.dirname(os.path.abspath(__file__))+'/recipes.db'
		self.orderSQLInterface = OrderSQLInterface(self.dbPath)
		self.inputHandler = inputHandler

		@self.app.route('/orders', methods=['GET'])
		def get_orders():
			#return all orders
			orders = self.orderSQLInterface.getOrderQueue()
			
			#print("orders ",orders)
			#orders = [{"order":order[0],"realOrder":order[1]} for order in orders]
			#print(order_names)
			#return "hallo"
			return json.dumps({"orders": list(orders)})

		@self.app.route('/order', methods=['POST'])
		def add_meal_preparation():
			self.inputHandler.orderHandler.addMealPreparation(...,...)
			return 'hello world'

		@self.app.route('/next_ingredient', methods=['GET'])
		def next_ingredient():
			self.inputHandler.orderHandler.addMealPreparation(...,...)
			return 'hello world'

		@self.app.route('/prepared_orders', methods=['GET'])
		def get_prepared_orders():
			#return all prepared orders
			#orders = self.orderSQLInterface.getOrderQueue()
			#access new table
			order_names = [order["order"] for order in orders]
			#print(order_names)
			#return "hallo"
			return json.dumps({"order_names": order_names})

		@self.app.route('/next_order', methods=['GET'])
		def next_order():
			#next_order = self.orderSQLInterface.getOrderQueue()

			#needed for async events (like sending via websocket) that don't need to be awaited
			asyncio.set_event_loop(asyncio.new_event_loop())
			self.orderSQLInterface.recipeReady()
			self.inputHandler.nextRecipe()
			return 'success'

		@self.app.route('/clear_queue', methods=['GET'])
		def clear_queue():
			self.inputHandler.orderHandler.reset()
			print("After Reset")
			return 'hello world'


	def run(self):
		#for debug mode the flask server must run on the main thread
		print("api: Thread id ", threading.current_thread())
		self.app.run(debug=False)
		


