#! /usr/bin/python2.7

import socket, threading

class Server(object):
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(("", 1625))
		print "Successfully bound to port 1625"
		
	def listen(self):
		while True:
			socket, address = self.sock.accept()
			t = threading.Thread(target=communicate, args=(socket,))

	def communicate(self, socket):
		while True:
			message = socket.recv(1024)
			if message[:] == "":
				pass
		
		
	
if __name__ == "__main__":
	server = Server()
	server.listen()