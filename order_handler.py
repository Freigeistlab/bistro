#!/usr/bin/env python3

import re, socket, threading, sys

class OrderHandler(threading.Thread):

	def __init__(self):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		self.waitinglist = []

		host = '' # meaning all available interfaces on our machine
		port = 9100 # as used by orderbird
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # makes it easier to restart the program
		self.socket.bind((host, port))
		self.socket.listen(1)

	def nextDish(self):
		if not self.waitinglist:
			return ""

		nextDish = self.waitinglist[0]
		self.waitinglist = self.waitinglist[1:]
		return nextDish

	def run(self):
		while True:
			try:
				conn, addr = self.socket.accept()
				print("Connection from: " + str(addr))

				while True:
					print("Receiving data...")
					data = conn.recv(8192).decode("cp1252")

					if not data:
						break

					elif data == bytes([16, 4, 1, 16, 4, 2, 16, 4, 3, 16, 4, 4]).decode("cp1252"):
						conn.send(bytes([22, 18, 18, 18]))
						print("send check")

					else:
						print("Processing data...")
						liste = [55, 34] + [ord(i) for i in data[-8:-4:]] + [0]
						conn.send(bytes(liste))

						print("=== New order ===")
						print(data)

						totals = re.compile("(?<=Total)\s+€\s\d+,\d{2}").findall(data)

						regex_id = re.compile("(?<=Bill no\.)\d+-\d+")
						ids = regex_id.findall(data)

						regex_date = re.compile("\d{2}\.\d{2}\.\d{4}")
						dates = regex_date.findall(data)

						regex_time = re.compile("\d{2}\:\d{2}\:\d{2}")
						times = regex_time.findall(data)

						regex_item = re.compile("\d+x\s+[\w\s\']*\s+(?=€\s\d+,\d{2})")
						items = regex_item.findall(data)

						# for now using only items, but rest is extracted properly already
						print("Totals: ", totals)
						print("Bill ID: ", ids)
						print("Date: ", dates)
						print("Time: ", times)
						print("Items: ", items)

						for item in items:
							# remove unnecessary whitespaces
							item = item.strip()
							# figure out how many times an item has been ordered
							amount = int(re.match("\d+(?=x)", item).group(0))
							# find out which dish has been ordered
							dish = item[len(str(amount))+2:]

							for i in range(0,amount):
								self.waitinglist.append(dish)

						print(self.waitinglist)

			except:
				print("exception: ", sys.exc_info()[0])