#! /usr/bin/python2.7

import socket, threading, sqlite3, hashlib

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

	def communicate(self, sock):
		while True:
			message = sock.recv(1024)
			if message[:6] == "[EXIT]":
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
						sock.send("[DONE]")
					else:
						print "Authstring collision"
						sock.send("[RETRY]")
						
					conn.close()
				except Exception, socket.error:
					sock.send("[FAIL]")
			elif message[:6] == "[AUTH]":
				hash = message[7:]
				try:
					conn = sqlite3.connect('userdatabase.db')
					db = conn.cursor()
					
					db.execute("SELECT userid, authstring FROM users")
					rows = db.fetchall()
					
					found = False
					for row in rows:
						convert = self.tohexadecimal(row[1])
						currhash = hashlib.sha1(convert).hexdigest()
						if currhash == hash:
							self.log(row[0])
							sock.send("[DONE]")
							found = True
						
					if not found:
						sock.send("[FAIL]")
						
					conn.close()
				except (Exception, socket.error) as e:
					sock.send("[FAIL]")
					
	def tohexadecimal(self, string):
		toret = ""
		for x in range(0, len(string)):
			toret += "%0.2x" % ord(string[x])
		return toret
		
	def log(self, userid):
		try:
			conn = sqlite3.connect('userdatabase.db')
			db = conn.cursor()
			
			db.execute("INSERT INTO logs(userid) values (?)", (userid,))
			conn.commit()
			conn.close()
		except Exception:
			print "Something went wrong with logging"

	def close(self):
		self.sock.close()

if __name__ == "__main__":
	server = Server()
	try:
		server.listen()
	except (KeyboardInterrupt, Exception, socket.error):
		server.close()
	