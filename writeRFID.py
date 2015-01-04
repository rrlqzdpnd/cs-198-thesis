#! /usr/bin/python2.7

import subprocess, string, random, socket, time, random
		
def inputtohex(input):
	toret = ""
	for x in range(len(input)):
		toret += "%0.2X" % ord(input[x])
	return toret

def generateAuthString(length):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def register(firstname, lastname):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((raw_input("Enter IP address of server: "), 1625))
		
		authstringbuff = generateAuthString(16)
		while True:
			sock.send("[REGISTER]\t" + authstringbuff + "\t" + lastname + "\t" + firstname)
			response = sock.recv(1024)
			if response == "[DONE]":
				break
			elif response == "[FAIL]":
				sock.send("[EXIT]")
				sock.close()
				return (False, "")
				
			authstringbuff = generateAuthString(16)
		
		sock.send("[EXIT]")
		sock.close()
		return (True, authstringbuff)
	except (Exception, socket.error) as e:
		sock.send("[EXIT]")
		sock.close()
		return (False, "")
		
def appendtoparams(params, keys):
	parambuff = params
	for x in keys:
		string = inputtohex(''.join(chr(y) for y in x))
		parambuff.append("-k")
		parambuff.append(string)
	
	return parambuff

def main():
	global keys
	
	try:
		print "Please keep your RFID over the reader throughout the whole process"
		old_PIN = raw_input("Enter your old PIN (leave blank if this is a new card): ")
		PIN = raw_input("Enter your new PIN (must be 6 characters): ")
		lastname = raw_input("Enter your last name: ")
		firstname = raw_input("Enter your first name: ")
		keyA = random.choice(keys)
		
		if len(PIN) != 6 or (old_PIN and len(old_PIN) != 6):
			print "PIN must be 6 characters"
			return
		
		params = ["mfoc", "-O", "old.dmp"]
		if old_PIN != "":
			params.append("-k")
			params.append(inputtohex(old_PIN))
		params = appendtoparams(params, keys)	
		
		# print ' '.join(x for x in params)
		proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(output, error) = proc.communicate()
		
		success = register(firstname, lastname)
		if success[0]:
			fin = open("old.dmp", "r")
			fout = open("new.dmp", "w+b")
			filecontents = fin.read()
			for i in range(len(filecontents)):
				byte = i % 16
				block = (i / 16) % 4
				sector = i / 64
				
				if block == 1 and sector == 0:
					fout.write(success[1][byte]) # write random generated auth string
				elif sector == 0 and block == 3:
					if byte <= 5:
						fout.write(chr(keyA[byte])) # write keyA to sector 1, block 4, bytes 0 - 5
					elif byte >= 10:
						fout.write(PIN[byte-10]) # writes keyB (PIN) to sector 1, block 4, bytes 11 - 16
					else: 
						fout.write(filecontents[i])
				else:
					fout.write(filecontents[i])
				
			fin.close()
			fout.close()

			params = ["nfc-mfclassic", "w", "A", "new.dmp", "old.dmp", "f"]
			proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(output, error) = proc.communicate()
			print output
		else:
			print "Something went wrong, possibly with connection to the server. Please try again later"
		
		subprocess.Popen(["rm", "old.dmp", "new.dmp"])
	except KeyboardInterrupt:
		pass
	
if __name__ == "__main__":
	global keys
	
	keys = [
		[0x50, 0x49, 0x4e, 0x41, 0x44, 0x4f],
		[0x31, 0x32, 0x31, 0x32, 0x31, 0x32]
	]

	main()
