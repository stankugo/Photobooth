#
#
#
#
#
# IMPORTS
#
#
#
#
#

import sys, traceback, os
import serial, time
import requests
import subprocess
import Queue, threading
# import ultrasonic
import picamera

import urllib2
import httplib

from time import time
from time import sleep
from time import strftime
from serial import Serial
from datetime import datetime

#
#
#
#
#
#   DECLARATIONS
#
#
#
#
#

camera = picamera.PiCamera()

api = {
	'protocol' : 'http://',
	'url' : 'mhq-verspielt.de',
	'header' : {'user-agent': 'raspberry-pi/photobooth'}
}

misc = {
	'folder' : '/home/pi/Photobooth/snapshots/',
    'ext' : '.jpg',
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'port' : '/dev/ttyUSB0'
}

overlay, counter

#
#
#
#
#
#   DEFINITIONS
#
#
#
#
#

def cleanupAndExit():
	print "EXIT"
    
def setup():
    global overlay
    overlay = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","3","/home/pi/Photobooth/cards/26.png"])
    
def snapshot():
	filename = time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S") + misc['ext']
    
def upload(filename):
	url = api['protocol'] + api['url'] + '/upload'
	files = {'file': open(misc['folder'] + filename + misc['ext'], 'rb')}
    
	try:
		r = requests.post(url, headers=api['header'], files=files)
		print r.text
		response = r.json()

		# CHECK FOR SUCCESS
		if 'status' in response:
			print response['status']
		del response
		
	except requests.exceptions.RequestException as e:
	    print e
 
#
#
#
#
#
#   MAIN LOOP
#
#
#
#
#       

try:
    
    # GET ULTRASONIC DATA
    serialPort = "/dev/ttyUSB0"
    maxRange = 5000
    sleepTime = 5
    minMM = 9999
    maxMM = 0
    
	while True:
	
		# CHECK ULTRASONIC
        mm = ultrasonic.measure(misc['port'])
		# if GPIO.input(11) == False and ready['action'] == True:
    
    camera.resolution = (1067, 800)
    camera.preview_fullscreen = False
    camera.preview_window = (0,0,1067,800)
    camera.hflip = True
    
    camera.start_preview()
    p = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","3","/home/pi/Photobooth/cards/26.png"])
    
    time.sleep(5)
    
    c = subprocess.Popen(["/home/pi/raspidmx/spriteview/./spriteview","-b","0","-c","5","-l","5","-m","1000000","-i","0","/home/pi/Photobooth/counter/counter.png"])
    
    time.sleep(10)
    
    camera.stop_preview()
    p.terminate()    
except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
finally:
    camera.close()
sys.exit(0)