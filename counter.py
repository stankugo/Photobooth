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
import ultrasonic
import picamera
import random

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
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0'
}

overlay = None
counter = None

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
	print 'EXIT'
    
def setup():
    global ready
    global overlay
    
    # CREATE A RANDOM NUMBER
    while (misc['image'] == misc['random']):
        misc['random'] = random.randrange(0,len(misc['images'])-1,1)
        
    misc['image'] = misc['random']
    
    # KILL EXISTING OVERLAY
    if overlay != None:
        overlay.terminate()
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','/home/pi/Photobooth/cards/' + misc['images'][misc['image']] + '.png'])

def counter():
    global counter
    counter = subprocess.Popen(['/home/pi/raspidmx/spriteview/./spriteview','-b','0','-c','5','-l','5','-m','1000000','-i','0','/home/pi/Photobooth/counter/counter.png'])

def snapshot():
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S') + misc['ext']
    camera.capture(stream, format='jpeg', resize=(misc['width'], misc['height']))

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
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
    
    while True:
        print 'READY'
        print misc['images'][misc['image']]
        sleep(1)
        
        # CHECK ULTRASONIC
        # mm = ultrasonic.measure(misc['port'])
        # if mm <= 2000 and ready['setup'] == True:

        # camera.stop_preview()
except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
sys.exit(0)