#! /usr/bin/python2.7

import socket, threading, sqlite3

class Server(object):
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(("", 1625))
		print "Successfully bound to port 1625"
		
	def listen(self):
		while True:
			self.sock.listen(1)
			socket, address = self.sock.accept()
			print "Connected to", address[0]
			t = threading.Thread(target=self.communicate, args=(socket,))
			t.start()

	def communicate(self, socket):
		while True:
			message = socket.recv(1024)
			if message[:6] == "[EXIT]":
				print "Exiting"
				break
			elif message[:10] == "[REGISTER]":
				params = message[11:].split("\t")
				authstring = params[0]
				lastname = params[1]
				firstname = params[2]
				
				try:
					conn = sqlite3.connect('userdatabase.db')
					db = conn.cursor()
					
					db.execute("SELECT count(*) FROM users WHERE authstring = ?", (authstring,))
					count = db.fetchall()
					
					if count[0][0] == 0:
						db.execute("INSERT INTO users(lastname, firstname, authstring) VALUES (?, ?, ?)", (lastname, firstname, authstring))
						conn.commit()
						socket.send("[DONE]")
					else:
						print "Authstring collision"
						socket.send("[RETRY]")
				except Exception, socket.error:
					socket.send("[FAIL]")
if __name__ == "__main__":
	server = Server()
	server.listen()
	