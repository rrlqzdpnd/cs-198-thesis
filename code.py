#! /usr/bin/python2.7

from gaugette.fonts import arial_16
import RPi.GPIO as GPIO
import time, sys, gaugette.ssd1306, subprocess

def keypadinput():
	input = ""
	starbuffer = ""
		
	try:
		while True:
			if len(input) == 6:
				print ""
				return input
			else:	
				if len(input) == 0:
					led.clear_display()
					led.draw_text3(0, 0, "Enter PIN (# to", font)
					led.draw_text3(0, 16, " backspace):", font)
					led.display()
				else:
					led.clear_display()
					led.draw_text3(0, 8, starbuffer, font)
					led.display()

				for y in range(3):
					GPIO.output(col[y], 0)
					for x in range(4):
						if GPIO.input(row[x]) == 0:
							input += matrix[x][y]
							starbuffer = "*" * len(input)
							sys.stdout.write("*")
							sys.stdout.flush()
							while GPIO.input(row[x]) == 0:
								time.sleep(0.1)
					GPIO.output(col[y], 1)					
	except KeyboardInterrupt as e:
		print "Cleaning up", e
	except Exception as e:
		print "Cleaning up", e
	
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

	input = keypadinput()
	
	
	
	print "You typed:", input
		
	led.clear_display()
	led.draw_text3(0, 0, "Please tap your", font)
	led.draw_text3(0, 16, "RFID", font)
	led.display()
	
	proc = subprocess.Popen("./newcode", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(output, error) = proc.communicate()
	
	print output
	if output != "":
		led.clear_display()
		led.draw_text3(0, 0, "Welcome!", font)
		led.draw_text3(0, 16, "", font)
		led.display()
		time.sleep(5)
		
	
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
	GPIO.output(12, 1)
	
	main()
