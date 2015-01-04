#! /usr/bin/python2.7

from gaugette.fonts import arial_16
import RPi.GPIO as GPIO
import time, sys, gaugette.ssd1306, subprocess, socket, hashlib
		
def displaymessage(message1, message2=""):
	led.clear_display()
	led.draw_text3(0, 0, message1, font)
	if message2 != "":
		led.draw_text3(0, 16, message2, font)
	led.display()

def keypadinput():
	input = ""
	starbuffer = ""
		
	try:
		while True:
			if len(input) == 6:
				return input
			else:	
				if len(input) == 0:
					displaymessage("Enter PIN (# to", "backspace)")
				else:
					displaymessage(starbuffer)

				for y in range(3):
					GPIO.output(col[y], 0)
					for x in range(4):
						if GPIO.input(row[x]) == 0:
							input = input[:-1] if (matrix[x][y] == "\b") else input + matrix[x][y]
							starbuffer = "*" * len(input)
							while GPIO.input(row[x]) == 0:
								time.sleep(0.1)
					GPIO.output(col[y], 1)					
	except Exception as e:
		print "Cleaning up", e
		
def inputtohex(input):
	toret = ""
	for x in range(len(input)):
		toret += "%0.2X " % ord(input[x])
	return toret
	
def authenticate(binary):
	try:
		hash = hashlib.sha1(binary).hexdigest()
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((raw_input("Enter IP address of server: "), 1625))
		
		sock.send("[AUTH]\t" + hash)
		response = sock.recv(1024)
		sock.send("[EXIT]")
		if response == "[DONE]":
			return True
		return False
	except (Exception, socket.error) as e:
		displaymessage("Error connecting", "to server")
		time.sleep(2)
		return False
	
def main():
	##
	#  Algorithm:
	#  	> Program asks for PIN code
	#  	> User enters PIN code (has to be 6 digits)
	#	> Program then asks user to tap RFID card (will soon be phone with NFC)
	#	> User taps RFID card
	#	> Program validates to server PIN-RFID combination
	#	> If successful, program logs to server User identity
	#

	try:
		while True:
			GPIO.output(12, 1) # LED is on (must authenticate)
			
			input = inputtohex(keypadinput())
			input = input.strip().split(" ")
			
			displaymessage("Please tap your", "RFID")
			
			params = ["./newcode"] + input
			proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(output, error) = proc.communicate()

			if output != "":
				displaymessage("Authenticating.", "Please wait...")
				if authenticate(str(output)):
					displaymessage("Welcome!")
					print "Successfully authenticated. Welcome!"
					GPIO.output(12, 0)
				else:
					displaymessage("Access Denied")
					print "Access Denied"
			else:
				displaymessage("Error reading card")
			
			time.sleep(5)
	except KeyboardInterrupt:
		led.clear_display()
		led.display()
		GPIO.output(12, 0)
		GPIO.cleanup()
		
if __name__ == '__main__':
	global led, font, col, row
	
	led = gaugette.ssd1306.SSD1306(reset_pin=5, dc_pin=4)
	led.begin()
	font = arial_16

	GPIO.setmode(GPIO.BOARD)
	
	col = [13, 15, 21]
	row = [3, 5, 7, 11]
	matrix = [
		["1", "2", "3"],
		["4", "5", "6"],
		["7", "8", "9"],
		["*", "0", "\b"]
	]
	for c in col:
		GPIO.setup(c, GPIO.OUT)
		GPIO.output(c, 1)
	for r in row:
		GPIO.setup(r, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	GPIO.setup(12, GPIO.OUT)
	
	main()
