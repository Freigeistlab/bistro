#!/usr/bin/env python3

import re, socket, threading, sys

class OrderHandler(threading.Thread):

	def __init__(self):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		host = '' # meaning all available interfaces on our machine
		port = 9100 # as used by orderbird
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # makes it easier to restart the program
		self.socket.bind((host, port))
		self.socket.listen(1)

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

						regex_total = re.compile("Total(\s|\c)*[\d]+,[\d]{2}")
						totals = regex_total.findall(data)

						regex_id = re.compile("(Rechnung Nr\.[\d]?-?[\d]*)")
						ids = regex_id.findall(data)

						regex_date = re.compile("(([\d][\d]).([\d][\d]).([\d][\d][\d][\d]))")
						dates = regex_date.findall(data)

						regex_time = re.compile("(([\d][\d][:][\d][\d]))")
						times = regex_time.findall(data)

						regex_item = re.compile("(([\d])x *([A-Za-z]* .*?)([\d]*,[\d]*) € *([\d]*,[\d]*) €)")
						items = regex_item.findall(data)

						print("Totals: ", totals)
						print("IDs: ", ids)
						print("Dates: ", dates)
						print("Times: ", times)
						print("Items: ", items)


			except:
				print("exception: ", sys.exc_info()[0])