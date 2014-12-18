#! /usr/bin/python2.7

import subprocess, string, random

def generateAuthString(length):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def main():
	filein = raw_input("Enter file basis: ")
	PIN = raw_input("Enter your PIN (must be 6 characters): ")
	lastname = raw_input("Enter your last name: ")
	firstname = raw_input("Enter your first name: ")
	
	if(len(PIN) != 6):
		print "PIN must be 6 characters"
		return
	
	fin = open(filein, "r")
	fout = open("tmp.dmp", "w+b")
	filecontents = fin.read()
	authstring = generateAuthString(16)
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
	
	proc = subprocess.Popen(["nfc-mfclassic", "w", "A", "tmp.dmp", filein, "f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(output, error) = proc.communicate()
	print output
	
	subprocess.Popen(["rm", "tmp.dmp"])
	
if __name__ == "__main__":
	main()