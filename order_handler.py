#!/usr/bin/env python3

import re, socket, threading, sys

class OrderHandler(threading.Thread):

	def __init__(self):
		# let python do the threading magic
		super(OrderHandler, self).__init__()

		host = '' # meaning all available interfaces on our machine
		port = 9100 # as used by orderbird
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((host, port))
		self.socket.listen(1)

	def run(self):
		while True:
			try:
				conn, addr = self.socket.accept()
				print("Connection from: " + str(addr))

				while True:
					print("Receiving data...")
					data = conn.recv(8192).decode("latin-1")

					if not data:
						break

					elif data == bytes([16, 4, 1, 16, 4, 2, 16, 4, 3, 16, 4, 4]).decode("latin-1"):
						conn.send(bytes([22, 18, 18, 18]))
						print("send check")

					else:
						print("Processing data...")
						liste = [55, 34] + [ord(i) for i in data[-8:-4:]] + [0]
						conn.send(bytes(liste))

						print("=== New order ===")



			except:
				print("exception: ", sys.exc_info()[0])