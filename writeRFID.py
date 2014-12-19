#! /usr/bin/python2.7

import subprocess, string, random, socket, time

def generateAuthString(length):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def register(authstring, firstname, lastname):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((raw_input("Enter IP address of server: "), 1625))
		
		authstringbuff = authstring
		while True:
			sock.send("[REGISTER]\t" + authstringbuff + "\t" + lastname + "\t" + firstname)
			response = sock.recv(1024)
			if response[:6] == "[DONE]":
				break
			elif response[:6] == "[FAIL]":
				sock.send("[EXIT]")
				sock.close()
				return False
				
			authstringbuff = generateAuthString(16)
		
		sock.send("[EXIT]")
		sock.close()
		return True
	except (Exception, socket.error) as e:
		return False

def main():
	try:
		filein = raw_input("Enter file basis: ")
		PIN = raw_input("Enter your PIN (must be 6 characters): ")
		lastname = raw_input("Enter your last name: ")
		firstname = raw_input("Enter your first name: ")
		authstring = generateAuthString(16)
		
		if(len(PIN) != 6):
			print "PIN must be 6 characters"
			return
		
		fin = open(filein, "r")
		fout = open("tmp.dmp", "w+b")
		filecontents = fin.read()
		for i in range(len(filecontents)):
			byte = i % 16
			block = (i / 16) % 4
			sector = i / 64
			
			if block == 1 and sector == 0:
				fout.write(authstring[byte]) # write random generated auth string
			elif sector == 0 and block == 3 and byte >= 10:
				fout.write(PIN[byte-10]) # writes to sector 1, block 4, bytes 11 - 16
			else:
				fout.write(filecontents[i])
			
		fin.close()
		fout.close()
		
		if register(authstring, firstname, lastname):
			proc = subprocess.Popen(["nfc-mfclassic", "w", "A", "tmp.dmp", filein, "f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(output, error) = proc.communicate()
			print output
		else:
			print "Something went wrong, possibly with connection to the server. Please try again later"
		
		subprocess.Popen(["rm", "tmp.dmp"])
	except KeyboardInterrupt:
		pass
	
if __name__ == "__main__":
	main()
