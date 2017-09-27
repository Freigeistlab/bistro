#!/usr/bin/env python3

import re, socket, threading, sys

class OrderHandler(threading.Thread):

	def __init__(self, verbose):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		self.waitinglist = []
		self.verbose = verbose
		self.newInput = False
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

						print("  New order:")
						if self.verbose:
							print(data)

						totals = re.compile("(?<=Total)\s+€\s\d+,\d{2}|(?<=Total)\s+\d+,\d{2}\s€").findall(data)
						ids = re.compile("(?<=Bill no\.)\d+-\d+|(?<=Rechnung Nr\.)\d+-\d+").findall(data)
						dates = re.compile("\d{2}\.\d{2}\.\d{4}").findall(data)
						times = re.compile("\d{2}\:\d{2}\:\d{2}").findall(data)
						items = re.compile("\d+x\s+[\w\s\']+\s+(?=€\s\d+,\d{2})|\d+x\s+[\w\s\']+\s+(?=\d+,\d{2}\s€)").findall(data)

						# for now using only items, but the rest should already be extracted properly
						print("    Totals: ", [i.strip() for i in totals])
						print("    Bill ID: ", ids)
						print("    Date: ", dates)
						print("    Time: ", times)
						print("    Items: ", [i.strip() for i in items])

						for item in items:
							# remove unnecessary whitespaces
							item = item.strip()
							# figure out how many times an item has been ordered
							amount = int(re.match("\d+(?=x)", item).group(0))
							# find out which dish has been ordered
							dish = item[len(str(amount))+2:]

							for i in range(0,amount):
								self.waitinglist.append(dish)

						self.newInput = True

			except:
				print("exception: ", sys.exc_info()[0])