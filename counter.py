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

from PIL import Image
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
	'snapshots' : '/home/pi/Photobooth/snapshots/',
    'compositions' : '/home/pi/Photobooth/compositions/',
    'cards' : '/home/pi/Photobooth/cards/',
    'raster' : '/home/pi/Photobooth/raster/',
    'ext' : '.png',
    'width' : 800,
    'height' : 1067,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0'
}

camera = picamera.PiCamera()
camera.resolution = (misc['width'], misc['height'])
camera.preview_fullscreen = False
camera.preview_window = (0,0,800,1067)
camera.hflip = True
camera.start_preview()

overlay = None

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
    
    if overlay != None:
        overlay.terminate()
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])

def counter():
    counter = subprocess.Popen(['/home/pi/raspidmx/spriteview/./spriteview','-b','0','-c','5','-l','5','-m','1000000','-i','0','/home/pi/Photobooth/counter/counter.png'])

def snapshot():
    global camera
    
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    camera.capture(misc['snapshots'] + filename + misc['ext'], format='png')
    
    # MERGING IMAGES
    background = Image.open(misc['snapshots'] + filename + misc['ext'])
    foreground = Image.open(misc['cards'] + str(misc['images'][misc['image']]) + '.png')

    # Image.alpha_composite(background, foreground).save(misc['compositions'] + filename + misc['ext'])
    
    tUpload = threading.Thread(name='upload', target=upload, args=(filename,))
    tUpload.daemon = True
    tUpload.start()

def upload(filename):
	url = api['protocol'] + api['url'] + '/upload'
	files = {'file': open(misc['snapshots'] + filename + misc['ext'], 'rb')}
	data = {'image': misc['image']}
    
	try:
		r = requests.post(url, headers=api['header'], files=files, data=data)
		response = r.json()

		# CHECK FOR HASH
		if 'status' in response:
			hashid = response['status']
            
			# PRINT 
			tPlot = threading.Thread(name='plot', target=plot, args=(hashid,))
			tPlot.daemon = True
			tPlot.start()
            
		del response
		
	except requests.exceptions.RequestException as e:
	    print e
        
def plot(hashid):
    print api['protocol'] + api['url'] + '/' + hashid
 
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
    
    while True:
        print 'READY'
        
        tSetup = threading.Thread(name='setup', target=setup)
        tSetup.daemon = True
        tSetup.start()
        
        tSnapshot = threading.Thread(name='snapshot', target=snapshot)
        tSnapshot.daemon = True
        tSnapshot.start()
        
        sleep(5)
        
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