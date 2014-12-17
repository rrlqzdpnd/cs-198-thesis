#! /usr/bin/python2.7

import subprocess

def main():
	filein = raw_input("Enter file basis: ")
	PIN = raw_input("Enter your PIN (must be 6 characters): ")
	
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
		
		if sector == 0 and block == 3 and byte >= 10:
			fout.write(PIN[byte-10]) # writes to sector 1, block 4, bytes 11 - 16
		else:
			fout.write(filecontents[i])
		
	fin.close()
	fout.close()
	
	proc = subprocess.Popen(["nfc-mfclassic", "w", "A", "tmp.dmp", filein, "f"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(output, error) = proc.communicate()
	print output
	
	# subprocess.Popen(["rm", "tmp.dmp"])
	
if __name__ == "__main__":
	main()