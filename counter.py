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

api = {
	'protocol' : 'http://',
	'url' : 'mhq-verspielt.de',
	'header' : {'user-agent': 'raspberry-pi/photobooth'}
}

ready = {
	'action' : False,
	'snapshot' : False
}

misc = {
	'folder' : '/home/pi/Photobooth/snapshots/',
    'ext' : '.jpg',
    'width' : 1067,
    'height' : 800,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'port' : '/dev/ttyUSB0'
}

overlay, counter

camera = picamera.PiCamera()
camera.resolution = (misc['width'], misc['height'])
camera.preview_fullscreen = False
camera.preview_window = (0,0,1067,800)
camera.hflip = True

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
    global ready
    global overlay
    overlay = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","3","/home/pi/Photobooth/cards/26.png"])
    
def snapshot():
	filename = time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S") + misc['ext']
    camera.capture(stream, format='jpeg', resize=(self.CAMERA_WIDTH, self.CAMERA_HEIGHT))
    
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
        if mm <= 2000 and ready['setup'] == True:
    
    
    
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